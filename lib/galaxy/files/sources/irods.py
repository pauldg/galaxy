"""
File Source plugin for the Integrated Rule-Oriented Data System (iRODS)
"""

try:
    from fs.irodsfs import iRODSFS
except ImportError:
    iRODSFS = None

try:
    import irods
    import irods.keywords as kw
    from irods.exception import (
        CollectionDoesNotExist,
        DataObjectDoesNotExist,
    )
    from irods.session import iRODSSession
except ImportError:
    irods = None

import logging
import os
import shutil
import ssl
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional

from galaxy.util import (
    ExecutionTimer,
    mapped_chars,
    string_as_bool,
    unlink,
)
from . import FilesSourceOptions
from ._caching_base import CachingConcreteObjectStore
from ._pyfilesystem2 import PyFilesystem2FilesSource


def remove_prefix(prefix, string):
    if string.startswith(prefix):
        string = string[len(prefix) :]
    return string


class iRODSFilesSource(PyFilesystem2FilesSource):
    plugin_type = "irods"
    required_module = iRODSFS
    required_package = "fs.irodsfs"

    def _open_fs(self, user_context=None, opts: Optional[FilesSourceOptions] = None):
        props = self._serialization_props(user_context)

        host = props.pop("host", "") or ""
        zone = props.pop("zone", "") or ""
        username = props.pop("username", "") or ""
        password = props.pop("password", "") or ""

        alt_space_fqn_separators = [mapped_chars["@"]] if "@" in mapped_chars else None

        handle = iRODSFS(
            host,
            zone,
            username,
            password,
        )
        return handle


__all__ = ("iRODSFilesSource",)
