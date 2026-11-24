import logging
import time
from typing import Any

import pytest

from galaxy.util.sentry import (
    scrub_breadcrumb,
    scrub_event,
    scrub_options,
    scrub_string,
)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("Unknown user jane.doe+galaxy@example.org", "Unknown user [email]"),
        ("a@example.org, b@sub.example.co.uk", "[email], [email]"),
        ("'jane@example.org'", "'[email]'"),
        ("GET /api/users?f_email=jane%40example.org", "GET /api/users?f_email=[email]"),
        ("jöhn@exämple.org", "[email]"),
        ("request from 203.0.113.7", "request from [ip]"),
        ("request from 203.0.113.7.", "request from [ip]."),
        ("forwarded for 203.0.113.7, 198.51.100.2", "forwarded for [ip], [ip]"),
        ("connect to 203.0.113.7:8080", "connect to [ip]:8080"),
        ("request from 2001:db8::7 failed", "request from [ip] failed"),
        ("client ::ffff:203.0.113.7", "client [ip]"),
        ("GET /api/histories?key=0123abcd&view=summary", "GET /api/histories?key=[Filtered]&view=summary"),
        ("GET /api/datasets?api_key=0123abcd", "GET /api/datasets?api_key=[Filtered]"),
        ("GET /api/datasets?API_KEY=0123abcd", "GET /api/datasets?API_KEY=[Filtered]"),
        ("GET /api/datasets?apikey=0123abcd", "GET /api/datasets?apikey=[Filtered]"),
        (
            "POST /token?access_token=0123abcd&id_token=4567ef",
            "POST /token?access_token=[Filtered]&id_token=[Filtered]",
        ),
        ("Cookie: galaxysession=0123abcd; theme=dark", "Cookie: galaxysession=[Filtered]; theme=dark"),
        ("[b'cookie', b'galaxysession=0123abcd']", "[b'cookie', b'galaxysession=[Filtered]']"),
        ("next=%2Fgalaxysession%3D0123abcd", "next=%2Fgalaxysession%3D[Filtered]"),
        ('{"key": "0123abcd", "name": "x"}', '{"key": "[Filtered]", "name": "x"}'),
        ("{'refresh_token': '0123abcd'}", "{'refresh_token': '[Filtered]'}"),
        ("Authorization: Bearer 0123abcd", "Authorization: [Filtered]"),
        ("[b'authorization', b'Bearer 0123abcd']", "[b'authorization', b'Bearer [Filtered]']"),
        ("x-api-key: 0123abcd", "x-api-key: [Filtered]"),
    ],
)
def test_scrub_string_masks_personal_data(value, expected):
    assert scrub_string(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "samtools 1.21 failed",
        "samtools@1.21",
        "@sentry/vue@8.1.0",
        "toolshed.g2.bx.psu.edu/repos/iuc/bwa/bwa/0.7.18",
        "999.1.1.1 is not an address",
        "started at 12:30:45",
        "galaxy.jobs.runners::queue",
        "a::b and dead::beef",
        "KeyError: 'dbkey'",
        "dbkey=hg38 and {'dbkey': 'hg38'}",
        "keys=id,name",
        "max_tokens=1024 tokenizer=bert keyword=foo monkey=banana",
        "user@localhost",
        "sha256:4f5c0d9e8b7a6f5e4d3c2b1a0f9e8d7c",
    ],
)
def test_scrub_string_keeps_other_text(value):
    assert scrub_string(value) == value


def test_scrub_string_is_fast_on_large_values():
    # Job output can be large, and is scrubbed inside the request that reports the error.
    for value in ("ACGT" * 250_000, "a" * 1_000_000, "a@" * 500_000, "key" * 300_000):
        start = time.monotonic()
        scrub_string(value)
        assert time.monotonic() - start < 2


def test_scrub_event_removes_user_and_request_details():
    event: dict[str, Any] = {
        "user": {"id": "42", "email": "jane@example.org", "username": "jane", "ip_address": "203.0.113.7"},
        "request": {
            "url": "https://galaxy.example.org/api/users/current",
            "query_string": "key=0123abcd",
            "cookies": {"galaxysession": "abc"},
            "data": {"email": "jane@example.org", "password": "secret"},
            "env": {"REMOTE_ADDR": "203.0.113.7"},
            "headers": {
                "X-Forwarded-For": "203.0.113.7",
                "X-Real-IP": "203.0.113.7",
                "Authorization": "Bearer 0123abcd",
                "Cookie": "galaxysession=abc",
                "Content-Type": "application/json",
            },
        },
    }
    scrub_event(event)
    assert "user" not in event
    request = event["request"]
    assert "cookies" not in request
    assert "data" not in request
    assert "env" not in request
    assert request["query_string"] == "key=[Filtered]"
    for header in ("X-Forwarded-For", "X-Real-IP", "Authorization", "Cookie"):
        assert request["headers"][header] == "[Filtered]"
    assert request["headers"]["Content-Type"] == "application/json"


def test_scrub_event_masks_nested_strings_and_keys():
    event: dict[str, Any] = {
        "logentry": {"message": "No user jane@example.org from 203.0.113.7"},
        "exception": {"values": [{"type": "ValueError", "value": "jane@example.org is not allowed"}]},
        "breadcrumbs": {"values": [{"message": "203.0.113.7 - GET /api/users/current?key=0123abcd", "level": "info"}]},
        "tags": {"remote": "2001:db8::7"},
        "contexts": {"job": {"jane@example.org": 1}},
        "extra": {
            "addresses": ("jane@example.org", "198.51.100.2"),
            "celery-job": {"task_name": "purge", "args": [42], "kwargs": {"user_id": 42}},
        },
    }
    scrub_event(event)
    assert event["logentry"] == {"message": "No user [email] from [ip]"}
    assert event["exception"]["values"][0]["value"] == "[email] is not allowed"
    assert event["breadcrumbs"]["values"][0]["message"] == "[ip] - GET /api/users/current?key=[Filtered]"
    assert event["tags"]["remote"] == "[ip]"
    assert event["contexts"]["job"] == {"[email]": 1}
    assert event["extra"]["addresses"] == ["[email]", "[ip]"]
    assert event["extra"]["celery-job"] == {"task_name": "purge", "args": "[Filtered]", "kwargs": "[Filtered]"}


def hook(item, hint):
    return item


def test_scrub_options_for_sentry_sdk_2():
    supported = {"before_send", "before_send_transaction", "send_default_pii", "include_local_variables"}
    options = scrub_options(supported, hook)
    assert options == {
        "before_send_transaction": hook,
        "before_breadcrumb": scrub_breadcrumb,
        "send_default_pii": False,
        "include_local_variables": False,
    }


def test_scrub_options_for_sentry_sdk_3():
    supported = {"before_send", "before_send_span", "before_send_log", "before_send_metric", "data_collection"}
    options = scrub_options(supported, hook)
    assert options["before_send_span"] is hook
    assert options["before_send_log"] is hook
    assert options["before_send_metric"] is hook
    assert "before_send_transaction" not in options
    data_collection = options["data_collection"]
    assert data_collection["user_info"] is False
    assert data_collection["stack_frame_variables"] is False
    assert data_collection["url_query_params"] == {"mode": "off"}
    assert data_collection["queues"] is False


class _User:
    def __str__(self):
        return "User(jane@example.org)"


def test_scrub_event_scrubs_log_arguments():
    event: dict[str, Any] = {
        "logentry": {
            "message": "Login failed for %s from %s with key=%s",
            "params": (_User(), "203.0.113.7", "0123abcd"),
            "formatted": "Login failed for User(jane@example.org) from 203.0.113.7 with key=0123abcd",
        }
    }
    scrub_event(event)
    assert event["logentry"] == {
        "message": "Login failed for %s from %s with key=%s",
        "params": ["User([email])", "[ip]", "0123abcd"],
        "formatted": "Login failed for User([email]) from [ip] with key=[Filtered]",
    }


def test_scrub_event_scrubs_named_log_arguments():
    event: dict[str, Any] = {"logentry": {"message": "Login failed for %(user)s", "params": {"user": _User()}}}
    scrub_event(event)
    assert event["logentry"]["params"] == {"user": "User([email])"}


def test_scrub_event_scrubs_log_arguments_in_log_items():
    # sentry-sdk 3 sends log records as separate items.
    item: dict[str, Any] = {
        "body": "Login failed for jane@example.org from 203.0.113.7",
        "attributes": {
            "sentry.message.template": "Login failed for %s from %s",
            "sentry.message.parameter.0": "jane@example.org",
            "sentry.message.parameter.1": "203.0.113.7",
            "logger.name": "galaxy.auth",
        },
    }
    scrub_event(item)
    assert item["body"] == "Login failed for [email] from [ip]"
    assert item["attributes"] == {
        "sentry.message.template": "Login failed for %s from %s",
        "sentry.message.parameter.0": "[email]",
        "sentry.message.parameter.1": "[ip]",
        "logger.name": "galaxy.auth",
    }


def test_scrub_breadcrumb_scrubs_log_messages():
    record = logging.LogRecord("galaxy.auth", logging.INFO, __file__, 1, "Login by %s", ("jane@example.org",), None)
    crumb = scrub_breadcrumb({"message": record.getMessage(), "category": "galaxy.auth"}, {"log_record": record})
    assert crumb == {"message": "Login by [email]", "category": "galaxy.auth"}
    crumb = scrub_breadcrumb({"message": "GET /api?key=0123abcd from 203.0.113.7"}, {})
    assert crumb == {"message": "GET /api?key=[Filtered] from [ip]"}


def test_scrub_event_keeps_tool_tags():
    event: dict[str, Any] = {
        "tags": {
            "tool": "toolshed.g2.bx.psu.edu/repos/devteam/picard/picard_MarkDuplicates/3.1.1.0",
            "tool.version": "3.1.1.0",
            "remote": "203.0.113.7",
        }
    }
    scrub_event(event)
    assert event["tags"] == {
        "tool": "toolshed.g2.bx.psu.edu/repos/devteam/picard/picard_MarkDuplicates/3.1.1.0",
        "tool.version": "3.1.1.0",
        "remote": "[ip]",
    }
