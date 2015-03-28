import json
import os
import clip

from mock import patch

from . import BaseTest
from lfm import utils


class TestUtils(BaseTest):

	def test_directory(self):
		cwd = os.getcwd()
		with utils.directory('tests'):
			self.assertEqual(os.getcwd(), os.path.join(cwd, 'tests'))
		self.assertEqual(os.getcwd(), cwd)

	@patch('lfm.utils.os.path.isfile', side_effect=[True, False])
	@patch('lfm.utils.os.path.isdir', side_effect=[True])
	@patch('lfm.utils.os.remove')
	@patch('lfm.utils.shutil.rmtree')
	def test_delete_resource(self, rmtree, remove, isdir, isfile):
		utils.delete_resource('folder')
		remove.assert_called_with('folder')
		utils.delete_resource('directory')
		rmtree.assert_called_with('directory', ignore_errors=True)

	@patch('lfm.utils.clip.echo')
	@patch('lfm.utils.os.path.isfile', side_effect=[True] + [False] * 4)
	@patch('lfm.utils.os.path.isdir', side_effect=[True] + [False] * 5)
	def test_uri_type(self, isdir, isfile, _):
		valid_types = [
			('some/dir', 'directory'),
			('some-file', 'file'),
			('s3:bucket', 's3'),
			('gist:user/gid', 'gist'),
			('gh:user/repo', 'repo')
		]
		for e in valid_types:
			self.assertEqual(utils.uri_type(e[0]), e[1])
		with self.assertRaises(clip.ClipExit):
			utils.uri_type('blargh bloog')


class TestFrontMatter(BaseTest):

	fixtures = [
		'fm-js-1.js',          # JavaScript single-line comment block
		'fm-js-2.js',          # JavaScript multi-line comment
		'fm-js-3.js',          # JavaScript multi-line sanity check
		'fm-coffee-1.coffee',  # CoffeeScript
	]

	def _find_fm_test(self, name):
		prefix, ext = os.path.splitext(name)
		actual = self.load_fixture(name)
		expected = self.load_fixture('{}-find-expected{}'.format(prefix, ext))
		self.assertEqual(utils.find_front_matter(actual, ext[1:]), expected)

	def _parse_fm_test(self, name):
		prefix, ext = os.path.splitext(name)
		actual = self.load_fixture(name)
		expected = json.loads(self.load_fixture('fm-parse-expected.json'))
		self.assertEqual(utils.parse_front_matter(actual, ext[1:]), expected)

	def test_find_front_matter(self):
		for fixture in self.fixtures:
			self._find_fm_test(fixture)

	def test_parse_front_matter(self):
		for fixture in self.fixtures:
			self._parse_fm_test(fixture)

	def test_load_front_matter(self):
		expected = json.loads(self.load_fixture('fm-parse-expected.json'))
		for fixture in self.fixtures:
			self.assertEqual(utils.load_front_matter(self.get_fixture_path(fixture)), expected)

	def test_front_matter_errors(self):
		# Unrecognized file extension
		self.assertEqual(utils.find_front_matter('boop', '.cake'), '')
		self.assertEqual(utils.parse_front_matter('boop', '.cake'), {})
