from pathlib import Path
import subprocess
from typing import Iterable, Optional

from app.constants import GIT_PACKS_PATH
from app.models import FileSystemInfo, DirectoryInfo, GitObjectType, GitRevListOutputColumn, GitVerifyPackOutputColumn


def generate_node(name: str, size_in_packfile: int, is_file: bool) -> FileSystemInfo:
    return FileSystemInfo(name, size_in_packfile) if is_file else DirectoryInfo(name, size_in_packfile)


def find_containing_match_safe(substring: str, entries: Iterable[str]) -> Optional[str]:
    entry = next((entry for entry in entries if substring in entry), None)
    return entry


def get_pack_details(repo_path: Path, pack_file_name: str) -> DirectoryInfo:
    pack_file_dir: Path = repo_path / GIT_PACKS_PATH
    pack_file_path_no_ext: Path = pack_file_dir / pack_file_name
    pack_file_size: int = (pack_file_path_no_ext.with_suffix('.pack')).stat().st_size

    root_pack_data = DirectoryInfo(pack_file_name, pack_file_size)

    verify_pack_cmd = ['git', 'verify-pack', '-v', str(pack_file_path_no_ext.with_suffix('.idx'))]
    verify_pack_result_raw = subprocess.run(verify_pack_cmd, stdout=subprocess.PIPE).stdout.decode('utf-8')
    verify_pack_result_lines = verify_pack_result_raw.splitlines()

    rev_list_cmd = ['git', 'rev-list', '--objects', '--all']
    rev_list_result_raw = subprocess.run(rev_list_cmd, cwd=repo_path, stdout=subprocess.PIPE).stdout.decode('utf-8')
    rev_list_result_lines = rev_list_result_raw.splitlines()

    for verify_pack_result_line in verify_pack_result_lines:
        verify_pack_result_line_split = verify_pack_result_line.split()

        sha = verify_pack_result_line_split[GitVerifyPackOutputColumn.SHA]
        obj_type = verify_pack_result_line_split[GitVerifyPackOutputColumn.TYPE]

        if ((obj_type == GitObjectType.BLOB) and (rev_list_result_line := find_containing_match_safe(sha, rev_list_result_lines))):
            rev_list_result_line_split = rev_list_result_line.split()

            file_path = rev_list_result_line_split[GitRevListOutputColumn.FILE_PATH]
            size_in_packfile = int(
                verify_pack_result_line_split[GitVerifyPackOutputColumn.SIZE_IN_PACKFILE])

            file_path_split = file_path.split('/')
            file_path_depth = len(file_path_split)

            parent_node = root_pack_data

            for i, current_node_name in enumerate(file_path_split):
                if current_node_name in parent_node.children:
                    parent_node.children[current_node_name].size_in_packfile += size_in_packfile
                else:
                    parent_node.children[current_node_name] = generate_node(
                        current_node_name, size_in_packfile, i == file_path_depth - 1)

                parent_node = parent_node.children[current_node_name]

    return root_pack_data
