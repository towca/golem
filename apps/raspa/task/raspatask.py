import logging
import os
import random
from copy import copy
from typing import Optional

import enforce
from golem_messages.message import ComputeTaskDef

from apps.core.task.coretask import (CoreTask,
                                     CoreTaskBuilder,
                                     CoreTaskTypeInfo)
from apps.raspa.raspaenvironment import RaspaTaskEnvironment
from apps.raspa.task.raspataskstate import RaspaTaskDefaults, RaspaTaskOptions
from apps.raspa.task.raspataskstate import RaspaTaskDefinition
from apps.raspa.task.verifier import RaspaTaskVerifier
from golem.task.taskbase import Task
from golem.task.taskclient import TaskClient
from golem.task.taskstate import SubtaskStatus

logger = logging.getLogger("apps.raspa")


class RaspaTaskTypeInfo(CoreTaskTypeInfo):
    def __init__(self):
        super().__init__(
            "Raspa",
            RaspaTaskDefinition,
            RaspaTaskDefaults(),
            RaspaTaskOptions,
            RaspaTaskBuilder
        )


@enforce.runtime_validation(group="raspa")
class RaspaTask(CoreTask):
    ENVIRONMENT_CLASS = RaspaTaskEnvironment
    VERIFIER_CLASS = RaspaTaskVerifier

    def __init__(self,
                 total_tasks: int,
                 task_definition: RaspaTaskDefinition,
                 root_path=None,
                 owner=None):
        super().__init__(
            owner=owner,
            task_definition=task_definition,
            root_path=root_path,
            total_tasks=total_tasks
        )

    def short_extra_data_repr(self, extra_data):
        return "Raspatask extra_data: {}".format(extra_data)

    def _extra_data(self, perf_index=0.0) -> ComputeTaskDef:
        subtask_id = self.create_subtask_id()
        extra_data = {
            "echo": "Hello Raspa task"
        }

        return self._new_compute_task_def(subtask_id,
                                          extra_data,
                                          perf_index=perf_index)

    def query_extra_data(self,
                         perf_index: float,
                         num_cores: int = 1,
                         node_id: Optional[str] = None,
                         node_name: Optional[str] = None) -> Task.ExtraData:
        logger.debug("Query extra data on raspatask")

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

        return self.ExtraData(ctd=ctd)

    def accept_results(self, subtask_id, result_files):
        super().accept_results(subtask_id, result_files)
        node_id = self.subtasks_given[subtask_id]['node_id']
        TaskClient.assert_exists(node_id, self.counting_nodes).accept()
        self.num_tasks_received += 1
        logger.info("Raspa task finished, results stored in: {}".format(self.tmp_dir))

    def query_extra_data_for_test_task(self) -> ComputeTaskDef:
        exd = self._extra_data()
        return exd


class RaspaTaskBuilder(CoreTaskBuilder):
    TASK_CLASS = RaspaTask

    @classmethod
    def build_dictionary(cls, definition: RaspaTaskDefinition):
        return super().build_dictionary(definition)

    @classmethod
    def build_full_definition(cls, task_type: RaspaTaskTypeInfo, dictionary):
        return super().build_full_definition(task_type, dictionary)

# comment that line to enable type checking
enforce.config({'groups': {'set': {'raspa': False}}})
