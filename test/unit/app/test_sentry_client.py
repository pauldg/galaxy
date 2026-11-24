"""Check what Galaxy's Sentry client sends, with and without sentry_scrub_personal_data."""

import json
import logging
from types import SimpleNamespace
from typing import (
    Any,
    cast,
)

import pytest

sentry_sdk = pytest.importorskip("sentry_sdk")

from sentry_sdk.transport import Transport  # noqa: E402

from galaxy.app import SentryClientMixin  # noqa: E402
from galaxy.config import CommonConfigurationMixin  # noqa: E402
from galaxy.tools.evaluation import ToolTemplatingException  # noqa: E402

log = logging.getLogger("galaxy.test.sentry")

EMAIL = "jane.doe@example.org"
IPV4 = "203.0.113.7"
IPV6 = "2001:db8::7"
API_KEY = "0123abcd4567ef"
BEARER = "9876fedcba5432"
USERNAME = "janedoe_galaxy"
USER_ID = 424242


class CapturingTransport(Transport):
    def __init__(self, options=None):
        super().__init__(options)
        self.events: list[dict] = []
        self.items: list[dict] = []
        self.types: set[str] = set()

    def capture_envelope(self, envelope):
        for item in envelope.items:
            payload = item.payload.json
            if payload is None:
                continue
            self.items.append(payload)
            self.types.add(item.type)
            if item.type == "event":
                self.events.append(payload)

    def flush(self, timeout, callback=None):
        pass

    def kill(self):
        pass


class SentryApp(SentryClientMixin):
    is_webapp = False

    def __init__(self, scrub, traces_sample_rate=0.0):
        self.config = cast(
            Any,
            SimpleNamespace(
                sentry_dsn="https://public@sentry.invalid/1",
                sentry_event_level="ERROR",
                sentry_traces_sample_rate=traces_sample_rate,
                sentry_ca_certs=None,
                sentry_scrub_personal_data=scrub,
                version_major="26.2",
                version_minor="dev0",
            ),
        )


@pytest.fixture
def capture_events():
    def configure(scrub, traces_sample_rate=0.0):
        SentryApp(scrub, traces_sample_rate).configure_sentry_client()
        transport = CapturingTransport()
        sentry_sdk.get_client().transport = transport
        return transport

    yield configure
    sentry_sdk.flush()
    sentry_sdk.init()


def check_user_lookup():
    # Captured as stack frame variables unless those are turned off.
    email = EMAIL  # noqa: F841
    username = USERNAME  # noqa: F841
    user_id = USER_ID  # noqa: F841
    raise ValueError(f"No user {EMAIL} from {IPV4}")


def send_events():
    sentry_sdk.set_user({"id": str(USER_ID), "email": EMAIL, "username": USERNAME, "ip_address": IPV4})
    log.info("%s - GET /api/users/current?key=%s", IPV4, API_KEY)
    log.info("Authorization: Bearer %s", BEARER)
    log.error("Login failed for %s from %s", EMAIL, IPV6)
    try:
        check_user_lookup()
    except ValueError:
        sentry_sdk.capture_exception()


def test_scrubbed_events_carry_no_personal_data(capture_events):
    transport = capture_events(scrub=True)
    send_events()
    assert len(transport.events) == 2
    for event in transport.events:
        assert "user" not in event
        serialized = json.dumps(event)
        for value in (EMAIL, IPV4, IPV6, API_KEY, BEARER, USERNAME, str(USER_ID)):
            assert value not in serialized
    # sentry-sdk 3 also sends log records as separate items.
    assert not any(value in json.dumps(transport.items) for value in (EMAIL, API_KEY, BEARER, USERNAME))
    logentry = transport.events[0]["logentry"]
    assert logentry["message"] == "Login failed for %s from %s"
    assert list(logentry["params"]) == ["[email]", "[ip]"]
    frames = transport.events[1]["exception"]["values"][0]["stacktrace"]["frames"]
    assert frames[-1]["function"] == "check_user_lookup"
    assert not any(frame.get("vars") for frame in frames)


def test_bare_values_in_log_arguments_are_sent(capture_events):
    # A bare secret or username passed to a log call has nothing that marks it as one.
    transport = capture_events(scrub=True)
    log.info("Rejected API key %s for %s", BEARER, USERNAME)
    log.error("Login failed")
    serialized = json.dumps(transport.events[0])
    assert BEARER in serialized
    assert USERNAME in serialized


def test_scrubbed_tool_templating_fingerprint(capture_events):
    # The fingerprint and tags for tool templating errors are set from the raw exception.
    transport = capture_events(scrub=True)
    try:
        try:
            raise NameError(f"cannot find 'jane' for {EMAIL}")
        except NameError as cause:
            raise ToolTemplatingException(
                f"Error occurred while building command for tool {EMAIL}",
                tool_id="cat1",
                tool_version="3.1.1.0",
                is_latest=True,
            ) from cause
    except ToolTemplatingException:
        sentry_sdk.capture_exception()
    assert len(transport.events) == 1
    event = transport.events[0]
    assert event["fingerprint"][:2] == ["Error occurred while building command for tool [email]", "3.1.1.0"]
    assert event["tags"]["tool_id"] == "cat1"
    assert event["tags"]["tool_version"] == "3.1.1.0"
    assert EMAIL not in json.dumps(event)


def test_unscrubbed_events_still_carry_personal_data(capture_events):
    # Without the option nothing changes, which also shows the test above sees the data.
    transport = capture_events(scrub=False)
    send_events()
    serialized = json.dumps(transport.events)
    for value in (EMAIL, IPV4, BEARER, USERNAME, str(USER_ID)):
        assert value in serialized
    frames = transport.events[1]["exception"]["values"][0]["stacktrace"]["frames"]
    assert frames[-1]["vars"]["username"] == f"'{USERNAME}'"


def test_scrubbed_request_carries_no_personal_data(capture_events):
    starlette = pytest.importorskip("starlette")
    from starlette.applications import Starlette
    from starlette.routing import Route
    from starlette.testclient import TestClient

    assert starlette
    transport = capture_events(scrub=True, traces_sample_rate=1.0)

    def fail(request):
        raise RuntimeError("request failed")

    client = TestClient(Starlette(routes=[Route("/api/users/current", fail)]), raise_server_exceptions=False)
    response = client.get(
        f"/api/users/current?key={API_KEY}&f_email=jane.doe%40example.org",
        headers={
            "X-Forwarded-For": IPV4,
            "X-Real-IP": IPV4,
            "Cookie": "galaxysession=abc",
            "Authorization": f"Bearer {BEARER}",
            "X-Api-Key": API_KEY,
        },
    )
    assert response.status_code == 500
    sentry_sdk.flush()
    assert len(transport.events) == 1
    event = transport.events[0]
    request = event["request"]
    assert "env" not in request
    assert "cookies" not in request
    # The trace of the request is sent too, as a transaction (sentry-sdk 2) or as spans (sentry-sdk 3).
    assert transport.types & {"transaction", "span"}
    serialized = json.dumps(transport.items)
    for value in (IPV4, API_KEY, BEARER, "galaxysession=abc", "jane.doe%40example.org", "jane.doe@example.org"):
        assert value not in serialized
    if "span" in transport.types:
        assert "http.query" not in serialized


@pytest.mark.parametrize("scrub, public_dsn", [(False, "https://public@sentry.invalid/1"), (True, None)])
def test_public_dsn_only_without_scrubbing(scrub, public_dsn):
    config = CommonConfigurationMixin()
    config.sentry_dsn = "https://public:secret@sentry.invalid/1"
    config.sentry_scrub_personal_data = scrub
    assert config.sentry_dsn_public == public_dsn
