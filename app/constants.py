from enum import Enum


DATA_SIZE_MULTIPLIER: int = 2**10  # i.e. 1024
GIT_PACKS_PATH: str = '.git/objects/pack/'
OUTPUT_FILE_NAME: str = 'git_pack_size_details.txt'
SCRIPT_VERSION: str = '1.0'


class ExitStatus(Enum):
    SUCCESS = 0
    ERROR = 1
