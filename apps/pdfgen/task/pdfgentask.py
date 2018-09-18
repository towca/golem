import decimal
import logging
import math
import operator
import os
import random
import string
from copy import copy
from typing import Optional
from shutil import copyfile
from typing import Type, Optional, Dict, Any
from PyPDF2 import PdfFileMerger, PdfFileReader

import enforce
from ethereum.utils import denoms
from golem_messages.message import ComputeTaskDef

from apps.core.task.coretask import (CoreTask,
                                     CoreTaskBuilder,
                                     CoreTaskTypeInfo)
from golem.core.common import HandleKeyError, timeout_to_deadline, to_unicode, \
    string_to_timeout
from apps.pdfgen.pdfgenenvironment import PDFgenTaskEnvironment
from apps.pdfgen.task.pdfgentaskstate import PDFgenTaskDefaults, PDFgenTaskOptions
from apps.pdfgen.task.pdfgentaskstate import PDFgenTaskDefinition
from apps.pdfgen.task.verifier import PDFgenTaskVerifier
from golem.task.taskbase import Task 
from golem.task.taskclient import TaskClient
from golem.task.taskstate import SubtaskStatus

logger = logging.getLogger("apps.pdfgen")

def unique_string_generator(size=4, length=4):
    ret = set()
    charset = string.ascii_letters + string.punctuation + string.digits

    while len(ret) != size:
        uniq_string = "".join(random.choice(charset) for x in range(length))
        if uniq_string in ret:
            continue
        else:
            ret.add(uniq_string)
    return ret

class PDFgenTaskTypeInfo(CoreTaskTypeInfo):
    def __init__(self):
        super().__init__(
            "PDFgen",
            PDFgenTaskDefinition,
            PDFgenTaskDefaults(),
            PDFgenTaskOptions,
            PDFgenTaskBuilder
        )


@enforce.runtime_validation(group="pdfgen")
class PDFgenTask(CoreTask):
    ENVIRONMENT_CLASS = PDFgenTaskEnvironment
    VERIFIER_CLASS = PDFgenTaskVerifier

    def __init__(self,
                 total_tasks: int,
                 task_definition: PDFgenTaskDefinition,
                 root_path=None,
                 owner=None):
        super().__init__(
            owner=owner,
            task_definition=task_definition,
            root_path=root_path,
            total_tasks=total_tasks
        )
        self.resource_data_list = os.listdir(
            os.path.join(self.task_definition.tmp_dir, "data"))

        # Only single file as a resource input is allowed, more than one will
        # result in ambiguity on what to load
        assert len(self.resource_data_list) == 1

        res_file = os.path.join(self.task_definition.tmp_dir, 
                                "data",
                                self.resource_data_list[0])
        with open(res_file, 'r') as f:
            content = f.read().split()
            
        def split(a, n):
            k, m = divmod(len(a), n)
            return [a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]

        self.chunks = split(content, self.total_tasks)

        assert len(self.chunks) == self.total_tasks, 'input is too small for such number of subtasks'

        self.task_chunk_id_map = {}
        self.uniq_strings = unique_string_generator(self.total_tasks)

    def short_extra_data_repr(self, extra_data):
        return "PDFgentask extra_data: {}".format(extra_data)

    def resend_failed_tasks(self):
        for sub in self.subtasks_given.values():
            if sub['status'] in [SubtaskStatus.failure, SubtaskStatus.restarted]:
                sub['status'] = SubtaskStatus.resent
                self.num_failed_subtasks -= 1

    def _extra_data(self, perf_index=0.0) -> ComputeTaskDef:
        subtask_id = self.create_subtask_id()

        self.task_chunk_id_map[subtask_id] = self.last_task

        extra_data = {
            "output_name": 'output{}.pdf'.format(self.uniq_strings.pop()),
            "content": '\n'.join(self.chunks[self.last_task])
        }

        self.last_task += 1

        return self._new_compute_task_def(subtask_id,
                                          extra_data,
                                          perf_index=perf_index)

    def query_extra_data(self,
                         perf_index: float,
                         num_cores: int = 1,
                         node_id: Optional[str] = None,
                         node_name: Optional[str] = None) -> Task.ExtraData:
        logger.debug("Query extra data on pdfgentask")

        ctd = self._extra_data(perf_index)
        sid = ctd['subtask_id']

        #FIXME Is this necessary?
        self.subtasks_given[sid] = copy(ctd['extra_data'])
        self.subtasks_given[sid]["status"] = SubtaskStatus.starting
        self.subtasks_given[sid]["perf"] = perf_index
        self.subtasks_given[sid]["node_id"] = node_id
        self.subtasks_given[sid]["node_id"] = node_id
        self.subtasks_given[sid]["shared_data_files"] = \
            self.task_definition.shared_data_files
        self.subtasks_given[sid]["subtask_id"] = sid
        self.resend_failed_tasks()
        
        return self.ExtraData(ctd=ctd)

    def write_merged_pdf(self, results):
        merger = PdfFileMerger()

        # Merge in appropriate order
        import pdb; pdb.set_trace()
        sorted_subtasks_ids = sorted(results.keys(), key=lambda x: self.task_chunk_id_map[x])
        for subtask_id in sorted_subtasks_ids:
            f = open(results[subtask_id][0], 'rb')
            merger.append(PdfFileReader(f))

        merger.write(self.task_definition.output_file)
        logger.info("PDFgen task finished, results stored in: {}".format(self.task_definition.output_file))

    def accept_results(self, subtask_id, result_files):
        super().accept_results(subtask_id, result_files)
        node_id = self.subtasks_given[subtask_id]['node_id']
        TaskClient.assert_exists(node_id, self.counting_nodes).accept()
        self.num_tasks_received += 1

        if not self.needs_computation():
            self.write_merged_pdf(self.results)

    def query_extra_data_for_test_task(self) -> ComputeTaskDef:
        exd = self._extra_data()
        return exd

    @classmethod
    def get_output_path(cls, dictionary, definition):
        if 'output_file' in dictionary:
            return dictionary['output_file']
        else:
            return "."

class PDFgenTaskBuilder(CoreTaskBuilder):
    TASK_CLASS = PDFgenTask

    @classmethod
    def build_dictionary(cls, definition: PDFgenTaskDefinition):
        return super().build_dictionary(definition)

    @classmethod
    def build_minimal_definition(cls, task_type: PDFgenTaskTypeInfo, dictionary):
        definition = task_type.definition()
        definition.options = task_type.options()
        definition.task_type = task_type.name
        definition.resources = set(dictionary['resources'])
        definition.total_subtasks = int(dictionary['subtasks'])
        definition.main_program_file = task_type.defaults.main_program_file
        return definition

    @classmethod
    def build_definition(cls,  # type: ignore
                         task_type: PDFgenTaskTypeInfo,
                         dictionary: Dict[str, Any],
                         minimal=False):
        # dictionary comes from the GUI
        if not minimal:
            definition = cls.build_full_definition(task_type, dictionary)
        else:
            definition = cls.build_minimal_definition(task_type, dictionary)
        definition.add_to_resources()
        return definition

    @classmethod
    def get_output_path(cls, dictionary, definition):
        if 'output_file' in dictionary:
            return dictionary['output_file']
        else:
            return "output.pdf"

    @classmethod
    def build_full_definition(cls,
                              task_type: PDFgenTaskTypeInfo,
                              dictionary: Dict[str, Any]):
        definition = cls.build_minimal_definition(task_type, dictionary)
        definition.task_name = dictionary['name']
        definition.max_price = \
            int(decimal.Decimal(dictionary['bid']) * denoms.ether)

        definition.full_task_timeout = string_to_timeout(
            dictionary['timeout'])
        definition.subtask_timeout = string_to_timeout(
            dictionary['subtask_timeout'])
        definition.output_file = cls.get_output_path(dictionary, definition)
        definition.estimated_memory = dictionary.get('estimated_memory', 0)
        return definition



# comment that line to enable type checking
enforce.config({'groups': {'set': {'pdfgen': False}}})