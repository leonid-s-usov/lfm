from mock import patch

from . import BaseTest
from lfm import deploy


class TestDeploy(BaseTest):

	@patch('lfm.deploy.tempfile.mkdtemp', side_effect=['tmpdir'] * 5)
	@patch('lfm.deploy.os.path.isdir', side_effect=[True, False])
	@patch('lfm.deploy.clip.echo')
	@patch('lfm.deploy.utils.delete_resource')
	@patch('lfm.deploy.handle_gist')
	@patch('lfm.deploy.handle_repo')
	@patch('lfm.deploy.handle_directory')
	@patch('lfm.deploy.handle_file')
	@patch('lfm.deploy.handle_s3')
	def test_run(self, h_s3, h_file, h_dir, h_repo, h_gist, dr, echo, isdir, mkdtemp):
		def run_h_test(f, path, src, dest):
			deploy.run(path, 'stuff')
			f.assert_called_with(src, dest, 'stuff')
			dr.assert_called_with('tmpdir')

		run_h_test(h_gist, 'gist:user/gid', 'gid', 'tmpdir')
		run_h_test(h_repo, 'gh:user/repo', 'git@github.com:user/repo.git', 'tmpdir/repo')
		run_h_test(h_s3, 's3:bucket', 'bucket', 'tmpdir')
		run_h_test(h_dir, 'some/dir', 'some/dir', 'tmpdir/dir')
		run_h_test(h_file, 'some-file', 'some-file', 'tmpdir/some-file')
