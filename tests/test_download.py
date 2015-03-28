import json

from mock import Mock, mock_open, patch

from . import BaseTest
from lfm import download


mock_gist = json.dumps({
	'files': {
		'foo': {
			'content': 'baz'
		},
		'bar': {
			'content': 'qux'
		}
	}
})


class MockS3Object:

	def __init__(self, _key, _body):
		self.key = _key
		self.m = Mock()
		self.m.read.side_effect = [_body, '']

	def get(self):
		return {
			'Body': self.m
		}

mock_s3 = [
	MockS3Object('foo/a', 'foo a body'),
	MockS3Object('foo/b/c', 'foo nested body'),
	MockS3Object('foo', 'It was the best of times')
]


class TestDownload(BaseTest):

	@patch('lfm.download.clip.echo')
	@patch('lfm.download.urllib2.urlopen')
	def test_download_gist(self, urlopen, _):
		m = Mock()
		m.read.side_effect = [mock_gist]
		urlopen.return_value = m
		with patch('__builtin__.open', mock_open()) as file_mock:
			ret = download.download_gist('9001', 'some/dir')
			self.assertEqual(ret, ['foo', 'bar'])
			file_mock.assert_any_call('some/dir/foo', 'w')
			file_mock.assert_any_call('some/dir/bar', 'w')
			write = file_mock().write
			write.assert_any_call('baz')
			write.assert_any_call('qux')

	@patch('lfm.download.clip.echo')
	@patch('lfm.download.boto3')
	def test_download_s3(self, boto, _):
		m = Mock()
		m.objects.all.return_value = mock_s3
		boto.resource.return_value.Bucket.return_value = m
		with patch('__builtin__.open', mock_open()) as file_mock:
			ret = download.download_s3('my_bucket/foo', 'some/dir')
			self.assertEqual(ret, ['a', 'b/c', 'foo'])
			file_mock.assert_any_call('some/dir/a', 'wb')
			file_mock.assert_any_call('some/dir/b/c', 'wb')
			file_mock.assert_any_call('some/dir/foo', 'wb')
			write = file_mock().write
			write.assert_any_call('foo a body')
			write.assert_any_call('foo nested body')
			write.assert_any_call('It was the best of times')
