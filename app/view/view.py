"""
This module provides utilities to format and display information about Git pack files.

Output Format:
===================================================================================================
[vX.Y.Z]
Repo: /path/to/repo
Root SHA: sample_root_sha
Snapshot Timestamp: sample_timestamp
===================================================================================================

Name                    Pct          Size
----                    ---          ----

pack1.pack              XX.XX%       XX.XX MB
  folder1               XX.XX%       XX.XX MB
    file1.txt           XX.XX%       XX.XX KB
    file2.txt           XX.XX%       XX.XX KB
  folder2               XX.XX%       XX.XX MB
pack2.pack              XX.XX%       XX.XX MB
... and so on ...

Note: Replace X.Y.Z with the script version and XX.XX with actual percentages and sizes.

"""

from pathlib import Path
from typing import List

from app.constants import DATA_SIZE_MULTIPLIER, SCRIPT_VERSION
from app.models import DirectoryInfo, FileSystemInfo, DataSizeSymbolPrefix
from app.view.constants import BYTE_ABBREV, DECIMAL_DIGITS, TABLE_COLUMN_SPACING, TAB_SIZE


def format_bytes(size: int) -> str:
    n: int = 0

    while size > DATA_SIZE_MULTIPLIER:
        size /= DATA_SIZE_MULTIPLIER
        n += 1

    size = round(size, DECIMAL_DIGITS)
    byte_prefix: str = '' if n == 0 else list(DataSizeSymbolPrefix)[n - 1]
    return (f'{size} {byte_prefix}{BYTE_ABBREV}')


test = {
    0: 'five',
    1: 'two',
    2: 'four'
}


def format_tree_info(node: FileSystemInfo, depth: int, pack_file_size: int, min_byte_threshold: int) -> str:
    size_in_packfile: int = node.size_in_packfile
    node_info: str = ''

    if (size_in_packfile >= min_byte_threshold):
        name_formatted: str = ' ' * (TAB_SIZE * depth) + node.name

        total_pct_of_packfile: float = round(
            size_in_packfile / pack_file_size * 100, DECIMAL_DIGITS)
        total_size_in_packfile_readable: str = format_bytes(
            size_in_packfile)

        node_info = TABLE_COLUMN_SPACING.format(
            name_formatted, f'{total_pct_of_packfile}%', total_size_in_packfile_readable) + '\n'

        # Add child info, sorted by size
        if isinstance(node, DirectoryInfo):
            children_sorted = dict(sorted(node.children.items(
            ), key=lambda item: item[1].size_in_packfile, reverse=True))
            for child_node_name in children_sorted:
                node_info += format_tree_info(
                    children_sorted[child_node_name], depth + 1, pack_file_size, min_byte_threshold)

    return node_info


def get_header(timestamp: str, root_sha: str, repo_path: Path) -> str:
    HEADER_WIDTH: int = 99
    HEADER_DIVIDER_CHAR: str = '='
    HEADER_DIVIDER: str = HEADER_DIVIDER_CHAR * HEADER_WIDTH

    header: str = f'{HEADER_DIVIDER}\n'

    header += f'[v{SCRIPT_VERSION}]\n'
    header += f'Repo: {repo_path}\n'
    header += f'Root SHA: {root_sha}'
    header += f'Snapshot Timestamp: {timestamp}\n'

    header += f'{HEADER_DIVIDER}\n\n'

    return header


def get_content(pack_data: List[DirectoryInfo], min_byte_threshold: int) -> str:
    content = TABLE_COLUMN_SPACING.format(
        'Name', 'Pct', 'Size') + '\n'

    # Write Size-Sorted Pack(s) Details
    content += TABLE_COLUMN_SPACING.format(
        '----', '---', '----') + '\n\n'

    for pack in pack_data:
        tree_info_formatted = format_tree_info(
            pack, 0, pack.size_in_packfile, min_byte_threshold)
        content += f'{tree_info_formatted}\n'

    return content


def get_display(timestamp: str, root_sha: str, repo_path: Path, pack_data: List[DirectoryInfo], min_byte_threshold: int) -> str:
    display = get_header(timestamp, root_sha, repo_path)
    display += get_content(pack_data, min_byte_threshold)

    return display
