import uuid
from os.path import join
from pathlib import Path

from apps.core.benchmark.benchmarkrunner import CoreBenchmark
from apps.raspa.raspaenvironment import RaspaTaskEnvironment
from apps.raspa.task.raspatask import RaspaTask
from apps.raspa.task.raspataskstate import RaspaTaskDefinition, \
    RaspaTaskDefaults
from apps.raspa.task.verifier import RaspaTaskVerifier
from golem.core.common import get_golem_path
from golem_verificator.verifier import SubtaskVerificationState

APP_DIR = join(get_golem_path(), 'apps', 'raspa')


class RaspaTaskBenchmark(CoreBenchmark):
    def __init__(self):
        self._normalization_constant = 1000  # TODO tweak that. issue #1356
        self.raspa_task_path = join(get_golem_path(),
                                    "apps", "raspa", "test_data")
        td = self._task_definition = RaspaTaskDefinition(RaspaTaskDefaults())

        td.task_id = str(uuid.uuid4())
        td.shared_data_files = [join(self.raspa_task_path, x) for x in
                                td.shared_data_files]
        td.main_program_file = RaspaTaskEnvironment().main_program_file
        td.resources = {join(self.raspa_task_path, "simulation.input")}
        td.add_to_resources()

        self.verification_options = {"result": "Hello world!"}
        verification_data = dict()
        self.verification_options["subtask_id"] = "RaspaBenchmark"
        verification_data['subtask_info'] = self.verification_options
        self.verifier = RaspaTaskVerifier(verification_data)

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

