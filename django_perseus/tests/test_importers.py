from django.conf import settings

from django_perseus.importers import BaseImporter
from django_perseus.utils import find_importers
from testapp2.importers import TestImporter
from .utils import is_file, is_dir

import os
import shutil


class TestImporters:

    def setup(self):
        if not os.path.isdir(settings.TEST_STATIC):
            os.makedirs(settings.TEST_STATIC)

    def create_dummy_files(self):
        base_path = settings.TEST_STATIC
        dir1 = os.path.abspath(os.path.join(base_path, 'dir'))
        dir2 = os.path.abspath(os.path.join(base_path, 'dir', 'subdir'))
        os.makedirs(dir1)
        os.makedirs(dir2)
        os.makedirs(os.path.abspath(os.path.join(base_path, 'emptydir')))
        os.makedirs(os.path.abspath(os.path.join(base_path, 'unused')))
        open(os.path.abspath(os.path.join(base_path, 'test1.txt')), 'a').close()
        open(os.path.abspath(os.path.join(dir1, 'test2.txt')), 'a').close()
        open(os.path.abspath(os.path.join(dir2, 'test3.txt')), 'a').close()
        open(os.path.abspath(os.path.join(base_path, 'unused.txt')), 'a').close()

    def test_find_importers(self):
        importer_classes = find_importers()
        assert len(importer_classes) == 1
        assert importer_classes[0] == TestImporter

    def test_importer_import_specific(self, settings):
        '''
        Test specific imports in source_dir
        '''
        self.create_dummy_files()

        class DummyImporter(BaseImporter):
            target_dir = 'PERSEUS_SOURCE_DIR'
            source_dir = 'TEST_STATIC'
            sub_dirs = [
                'test1.txt',
                'dir',
                'emptydir',
            ]

        DummyImporter()

        source_dir = settings.PERSEUS_SOURCE_DIR
        assert is_dir(source_dir, 'dir')
        assert is_dir(source_dir, 'dir', 'subdir')
        assert is_dir(source_dir, 'emptydir')

        assert is_file(source_dir, 'test1.txt')
        assert is_file(source_dir, 'dir', 'test2.txt')
        assert is_file(source_dir, 'dir', 'subdir', 'test3.txt')

        assert not is_file(source_dir, 'unused.txt')
        assert not is_dir(source_dir, 'unused')

    def test_importer_import_all(self):
        '''
        Test that asterix (*) imports all files and sub directories of source_dir
        '''
        self.create_dummy_files()

        class DummyImporter(BaseImporter):
            target_dir = 'PERSEUS_SOURCE_DIR'
            source_dir = 'TEST_STATIC'
            sub_dirs = [
                '*'
            ]

        DummyImporter()

        source_dir = settings.PERSEUS_SOURCE_DIR
        assert is_dir(source_dir, 'dir')
        assert is_dir(source_dir, 'dir', 'subdir')
        assert is_dir(source_dir, 'emptydir')

        assert is_file(source_dir, 'test1.txt')
        assert is_file(source_dir, 'dir', 'test2.txt')
        assert is_file(source_dir, 'dir', 'subdir', 'test3.txt')

        assert is_file(source_dir, 'unused.txt')
        assert is_dir(source_dir, 'unused')

    def teardown(self):
        if os.path.isdir(settings.TEST_STATIC):
            shutil.rmtree(settings.TEST_STATIC)
