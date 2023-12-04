from enum import IntEnum, Enum
from typing import Dict


class DataSizeSymbolPrefix(str, Enum):
    KILO = 'K'
    MEGA = 'M'
    GIGA = 'G'
    TERA = 'T'


class GitObjectType(str, Enum):
    """
    See: https://git-scm.com/docs/git#Documentation/git.txt-lttypegt
    """
    BLOB = 'blob'
    TREE = 'tree'
    COMMIT = 'commit'
    TAG = 'tag'


class GitVerifyPackOutputColumn(IntEnum):
    """
    See https://git-scm.com/docs/git-verify-pack#_output_format
    """
    SHA = 0
    TYPE = 1
    SIZE = 2
    SIZE_IN_PACKFILE = 3
    OFFSET_IN_PACKFILE = 4


class GitRevListOutputColumn(IntEnum):
    """
    See https://git-scm.com/docs/git-rev-list
    """
    SHA = 0
    FILE_PATH = 1


class FileSystemInfo():
    def __init__(self, name: str, size_in_packfile: int) -> None:
        self.name: str = name
        self.size_in_packfile: int = size_in_packfile


class DirectoryInfo(FileSystemInfo):
    def __init__(self, name: str, size_in_packfile: int) -> None:
        super().__init__(name, size_in_packfile)
        self.children: Dict[str, FileSystemInfo] = {}
