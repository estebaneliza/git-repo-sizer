#!/usr/bin/env python3

"""
Generates a directory tree size analysis of a git packfile and writes it to a text file.

There are several ways to breakdown an analysis of a git packfile --
here we take a file(blob)-first approach and generate a directory tree
for all files tracked in repo history, saving sizes and outputting
results to a text file. A user can specify a particular output
path, pack file, repo path, and minimum byte threshold for analysis.
For more information see: https://git-scm.com/book/en/v2/Git-Internals-Packfiles

  Usage example:

  git_pack_sizer.py --output path_to_output --pack pack_file_name --repo path_to_repo --threshold 0
"""

import argparse
import datetime
from pathlib import Path
import subprocess
import sys
from typing import IO, Iterator, List

from app import constants
from app import models
from app import utils
from app.view import view


def main():
    exit_status: constants.ExitStatus = constants.ExitStatus.SUCCESS

    WILDCARD: str = '*'

    DEFAULT_OUTPUT_PATH: Path = Path('./')
    DEFAULT_PACK_FILE: str = WILDCARD
    DEFAULT_REPO_PATH: Path = Path('./')
    DEFAULT_MIN_BYTE_THRESHOLD: int = 0

    parser = argparse.ArgumentParser('Generates a directory tree size analysis of a git packfile and writes it to a text file.')
    parser.add_argument('--output',
                        type=str,
                        required=False,
                        help=f'path to store the output file containing pack size results.  default = \'{DEFAULT_OUTPUT_PATH}\'',
                        default=DEFAULT_OUTPUT_PATH)

    parser.add_argument('--pack',
                        type=str,
                        required=False,
                        help=f'name of packfile to analyze.  default = \'{DEFAULT_PACK_FILE}\'',
                        default=DEFAULT_PACK_FILE)

    parser.add_argument('--repo',
                        type=str,
                        required=False,
                        help=f'path of repo to analyze.  default = \'{DEFAULT_REPO_PATH}\'',
                        default=DEFAULT_REPO_PATH)

    parser.add_argument('--threshold',
                        type=int,
                        required=False,
                        help=f'minimum byte size requirement to save to results.  default = \'{DEFAULT_MIN_BYTE_THRESHOLD}\'',
                        default=DEFAULT_MIN_BYTE_THRESHOLD)

    args = parser.parse_args()

    output_path: Path = Path(args.output)
    repo_path: Path = Path(args.repo)
    pack_file_name: str = args.pack
    min_byte_threshold: int = args.threshold

    print(
        f'Retrieving pack details for {pack_file_name} (this can take several minutes)...')

    # Retrieve pack details
    pack_data: List[models.DirectoryInfo] = []
    if pack_file_name == WILDCARD:
        files: Iterator[Path] = (repo_path / constants.GIT_PACKS_PATH).glob('*.pack')
        for file in files:
            print(file)
            pack_details: models.DirectoryInfo = utils.get_pack_details(repo_path, file.stem)
            pack_data.append(pack_details)
    else:
        pack_details: models.DirectoryInfo = utils.get_pack_details(repo_path, pack_file_name)
        pack_data.append(pack_details)

    print('Pack(s) successfully parsed, writing results to output file...')

    # Format pack details to user-friendly output
    timestamp: datetime.datetime = datetime.datetime.now()
    git_head_result = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    root_sha: str
    if git_head_result.returncode != 0:
        exit_status = constants.ExitStatus.ERROR
        print(f'Error executing command: {git_head_result.stderr.decode("utf-8")}')
        sys.exit(exit_status)
    else:
        root_sha = git_head_result.stdout.decode('utf-8')

    formatted_view: str = view.get_display(timestamp, root_sha, repo_path.resolve(), pack_data, min_byte_threshold)

    output_file: IO[str]
    output_file_path: Path = output_path / constants.OUTPUT_FILE_NAME
    try:
        with output_file_path.open('w+') as output_file:
            output_file.write(formatted_view)
    except FileNotFoundError:
        exit_status = constants.ExitStatus.ERROR

        print(f'Error: Could not find directory {output_path}. Please ensure the path exists.')
        sys.exit(exit_status)
    except IOError as e:
        exit_status = constants.ExitStatus.ERROR

        print(f'Error writing to file: {e}')
        sys.exit(exit_status)

    print(f'Results saved to {output_file_path.resolve()}')

    sys.exit(exit_status.value)


if __name__ == '__main__':
    main()
