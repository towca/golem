import os
from unittest import TestCase
from unittest.mock import patch

from apps.pdfgen.pdfgenenvironment import PDFgenTaskEnvironment
from apps.pdfgen.task.pdfgentaskstate import PDFgenTaskDefaults, \
    PDFgenTaskOptions, PDFgenTaskDefinition
from golem.core.common import get_golem_path
from golem.resource.dirmanager import list_dir_recursive
from golem.testutils import PEP8MixIn, TempDirFixture


class TestPDFgenTaskDefaults(TestCase):
    def test_init(self):
        td = PDFgenTaskDefaults()
        assert isinstance(td, PDFgenTaskDefaults)
        assert isinstance(td.options, PDFgenTaskOptions)

        assert td.code_dir == os.path.join(get_golem_path(), "apps", "pdfgen", "resources", "code_dir")
        assert td.default_subtasks == 1
        assert td.output_file == "output.pdf"
        assert td.shared_data_files == ["input.txt"]


class TestPDFgenTaskOptions(TestCase):
    def test_option(self):
        opts = PDFgenTaskOptions()
        assert isinstance(opts, PDFgenTaskOptions)
        assert isinstance(opts.environment, PDFgenTaskEnvironment)


class TestPDFgenTaskStateStyle(TestCase, PEP8MixIn):
    PEP8_FILES = [
        "apps/pdfgen/task/pdfgentaskstate.py"
    ]


class TestPDFgenTaskDefinition(TempDirFixture):
    def test_init(self):
        td = PDFgenTaskDefinition()
        assert isinstance(td, PDFgenTaskDefinition)
        assert isinstance(td.options, PDFgenTaskOptions)
        assert td.code_dir == os.path.join(get_golem_path(), "apps", "pdfgen", "resources", "code_dir")
        assert isinstance(td.resources, set)

        defaults = PDFgenTaskDefaults()
        tdd = PDFgenTaskDefinition(defaults)
        assert tdd.code_dir == os.path.join(get_golem_path(), "apps", "pdfgen", "resources", "code_dir")
        for c in list_dir_recursive(tdd.code_dir):
            assert os.path.isfile(c)
        assert tdd.total_subtasks == 1
        assert tdd.shared_data_files == ["input.txt"]

    def test_add_to_resources(self):
        td = PDFgenTaskDefinition(PDFgenTaskDefaults())
        td.resources = {os.path.join(get_golem_path(), "apps", "pdfgen", "test_data", "input.txt")}
        assert os.path.isfile(list(td.resources)[0])
        with patch("tempfile.mkdtemp", lambda: self.tempdir):
            td.add_to_resources()
            assert os.path.isdir(td.tmp_dir)
            assert isinstance(td.resources, set)
            assert td.tmp_dir == self.tempdir
            assert os.path.isdir(os.path.join(td.tmp_dir, "code"))
            assert os.path.isdir(os.path.join(td.tmp_dir, "data"))
            assert os.path.commonpath(list(td.resources)) == self.tempdir
            assert td.resources == set(list_dir_recursive(td.tmp_dir))
