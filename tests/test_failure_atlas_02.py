import tempfile, pathlib, unittest
from vyronforge_failure_atlas.contracts import AtlasRefusal, gate_file_operation, validate_relative_path
class FileSystemBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=pathlib.Path(self.tmp.name)
    def test_simple_relative(self):self.assertEqual(validate_relative_path(self.root,'source/code.py')['status'],'VALIDATED_REFERENCE_ONLY')
    def test_absolute_path_fails(self):
        with self.assertRaises(AtlasRefusal):validate_relative_path(self.root,r'X:\workspace')
    def test_parent_escape_fails(self):
        with self.assertRaises(AtlasRefusal):validate_relative_path(self.root,'../escape')
    def test_reserved_win_name_fails(self):
        with self.assertRaises(AtlasRefusal):validate_relative_path(self.root,'output/NUL')
    def test_missing_root_fails(self):
        with self.assertRaises(AtlasRefusal):validate_relative_path(self.root/'not-existing','file')
    def test_symlink_fails(self):
        try:(self.root/'link').symlink_to(self.root,target_is_directory=True)
        except (OSError,NotImplementedError):self.skipTest('symlink creation unsupported')
        with self.assertRaises(AtlasRefusal):validate_relative_path(self.root,'link/test.txt')
    def test_mock_reparse_denied_on_any_host(self):
        from unittest import mock
        with mock.patch.object(pathlib.Path,'is_symlink',autospec=True,side_effect=lambda p: p.name=='junction'):
            with self.assertRaises(AtlasRefusal):validate_relative_path(self.root,'junction/file')
    def test_delete_refused_even_owner_flag(self):self.assertEqual(gate_file_operation(action='DELETE',path_safe=True,readiness=True,owner_grant=True),'DENY_MUTATION_NOT_SUPPORTED')
    def test_read_is_not_execution(self):self.assertEqual(gate_file_operation(action='READ',path_safe=True,readiness=True,owner_grant=False),'READ_REFERENCE_ONLY_NO_EXECUTION_AUTHORITY')
