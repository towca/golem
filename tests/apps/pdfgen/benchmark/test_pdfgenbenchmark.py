import os
from unittest.mock import patch

from apps.pdfgen.benchmark.benchmark import PDFgenTaskBenchmark
from apps.pdfgen.task.pdfgentaskstate import PDFgenTaskDefinition, PDFgenTaskOptions

from golem.testutils import TempDirFixture


class TestPDFgenBenchmark(TempDirFixture):
    def setUp(self):
        super().setUp()
        self.bench = PDFgenTaskBenchmark()

    def test_is_instance(self):
        self.assertIsInstance(self.bench, PDFgenTaskBenchmark)
        self.assertIsInstance(self.bench.task_definition, PDFgenTaskDefinition)
        self.assertIsInstance(self.bench.task_definition.options, 
                              PDFgenTaskOptions)

    def test_task_settings(self):
        self.assertTrue(os.path.isdir(self.bench.pdfgen_task_path))

        self.assertEquals(
            os.path.basename(self.bench.task_definition.output_file),
                            "output.pdf")

        self.assertTrue(all(os.path.isfile(x) for x
                            in self.bench.task_definition.shared_data_files))

        self.assertTrue(os.path.isfile(
            self.bench.task_definition.main_program_file))
         