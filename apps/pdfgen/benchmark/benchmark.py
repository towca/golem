import uuid
import tempfile
from os.path import join
from pathlib import Path

from apps.core.benchmark.benchmarkrunner import CoreBenchmark
from apps.pdfgen.pdfgenenvironment import PDFgenTaskEnvironment
from apps.pdfgen.task.pdfgentask import PDFgenTask
from apps.pdfgen.task.pdfgentaskstate import PDFgenTaskDefinition, \
    PDFgenTaskDefaults
from apps.pdfgen.task.verifier import PDFgenTaskVerifier
from golem.core.common import get_golem_path
from golem_verificator.verifier import SubtaskVerificationState

APP_DIR = join(get_golem_path(), 'apps', 'pdfgen')


class PDFgenTaskBenchmark(CoreBenchmark):
    def __init__(self):
        self._normalization_constant = 1000  # TODO tweak that. issue #1356
        self.pdfgen_task_path = join(get_golem_path(),
                                    "apps", "pdfgen", "test_data")
        td = self._task_definition = PDFgenTaskDefinition(PDFgenTaskDefaults())

        td.task_id = str(uuid.uuid4())
        self.task_definition.output_file = join(tempfile.gettempdir(),
                                                "output.pdf")
        td.main_program_file = PDFgenTaskEnvironment().main_program_file
        td.resources = {join(self.pdfgen_task_path, f) for f in td.shared_data_files}
        td.add_to_resources()

        self.verification_options = {}
        verification_data = dict()
        self.verification_options["subtask_id"] = "PDFgenBenchmark"
        verification_data['subtask_info'] = self.verification_options
        self.verifier = PDFgenTaskVerifier(verification_data)

    @property
    def normalization_constant(self):
        return self._normalization_constant

    @property
    def task_definition(self):
        return self._task_definition

    def verify_result(self, result):
        sd = self.verification_options.copy()

        results = [filepath for filepath in result
                   if Path(filepath).suffix.lower() == '.result']

        verification_data = dict()
        verification_data["subtask_info"] = sd
        verification_data["results"] = results

        self.verifier.start_verification(verification_data)

        return self.verifier.state == SubtaskVerificationState.VERIFIED

