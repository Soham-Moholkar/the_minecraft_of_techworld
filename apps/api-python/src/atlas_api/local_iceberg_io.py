"""Local-only Iceberg Arrow FileIO with native Windows long-path support.

Imported lazily by the catalog only when lakehouse extras are enabled. All table
locations are derived from trusted local catalog configuration, never HTTP input.
"""

import os
from urllib.parse import unquote

from pyiceberg.io.pyarrow import PyArrowFileIO
from pyiceberg.typedef import EMPTY_DICT, Properties


class LocalIcebergFileIO(PyArrowFileIO):
    @staticmethod
    def parse_location(
        location: str,
        properties: Properties = EMPTY_DICT,
    ) -> tuple[str, str, str]:
        scheme, netloc, path = PyArrowFileIO.parse_location(location, properties)
        if scheme != "file" or (netloc and not (os.name == "nt" and netloc.endswith(":"))):
            raise ValueError("local lakehouse cannot access remote filesystems")
        path = unquote(path)
        if os.name == "nt":
            if path.startswith("/") and len(path) > 2 and path[2] == ":":
                path = path[1:]
            # Arrow's Windows filesystem does not always inherit Python's long
            # path manifest. Extended native paths avoid MAX_PATH failures for
            # generated manifest names in deeply nested learner workspaces.
            if not path.startswith("//?/"):
                path = "//?/" + os.path.abspath(path).replace("\\", "/")
        return scheme, netloc, path
