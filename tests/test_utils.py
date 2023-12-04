from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock

from app.utils import find_containing_match_safe, get_pack_details


class TestUtils(unittest.TestCase):

    # Tests for utils.find_containing_match_safe
    def test_find_containing_match_safe_found(self):
        entries = ['abc123', 'def456', 'ghi789']
        self.assertEqual(find_containing_match_safe('abc', entries), 'abc123')

    def test_find_containing_match_safe_not_found(self):
        entries = ['abc123', 'def456', 'ghi789']
        self.assertIsNone(find_containing_match_safe('xyz', entries))

    def test_find_containing_match_safe_empty_entries(self):
        self.assertIsNone(find_containing_match_safe('abc', []))

    def mock_subprocess_run(*args, **kwargs):
        if 'verify-pack' in args[0]:
            return MagicMock(stdout=b'verify_pack_output')
        elif 'rev-list' in args[0]:
            return MagicMock(stdout=b'rev_list_output')

    @patch('your_module.subprocess.run', side_effect=mock_subprocess_run)
    @patch('your_module.Path.stat')
    def test_get_pack_details(mock_stat, mock_run):
        mock_stat.return_value.st_size = 1234
        pack_details = get_pack_details(Path("/test/repo"), "test_pack")

        # Assertions depend on your implementation details
        assert pack_details.name == "test_pack"
        assert pack_details.size_in_packfile == 1234
        # Add more assertions based on the expected behavior
