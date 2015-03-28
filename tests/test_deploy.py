from mock import patch

from . import BaseTest
from lfm import deploy


class TestDeploy(BaseTest):

	@patch('lfm.deploy.clip.echo')
	@patch('lfm.deploy.utils.delete_resource')
	@patch('lfm.deploy.tempfile.mkdtemp', side_effect=['tmpdir'] * 4)
	@patch('lfm.deploy.utils.uri_type', side_effect=['directory', 'file', 'repo', 'gist'])
	@patch('lfm.deploy.download.run', side_effect=[['foo', 'bar'], ['baz']])
	@patch('lfm.deploy.shutil.copyfile')
	@patch('lfm.deploy.dir_util.copy_tree')
	@patch('lfm.deploy.deploy_dir')
	@patch('lfm.deploy.deploy_file')
	def test_run(self, d_file, d_dir, copy_tree, copyfile, *args):
		# Directory
		deploy.run('some/dir', 'stuff')
		copy_tree.assert_called_with('some/dir', 'tmpdir')
		d_dir.assert_called_with('tmpdir', 'stuff')
		# File
		deploy.run('some-file', 'stuff')
		copyfile.assert_called_with('some-file', 'tmpdir/some-file')
		d_file.assert_called_with('tmpdir/some-file', 'stuff')
		# Multi-file download
		deploy.run('gh:user/repo', 'stuff')
		d_dir.assert_called_with('tmpdir', 'stuff')
		# Single file download
		deploy.run('gist:user/gid', 'stuff')
		d_file.assert_called_with('tmpdir/baz', 'stuff')
