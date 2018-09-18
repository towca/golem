import os
import uuid
from unittest import TestCase
from unittest.mock import patch

from apps.pdfgen.pdfgenenvironment import PDFgenTaskEnvironment
from apps.pdfgen.task.pdfgentask import (
    PDFgenTaskDefaults,
    PDFgenTaskBuilder,
    PDFgenTaskTypeInfo, PDFgenTask)
from apps.pdfgen.task.pdfgentaskstate import PDFgenTaskDefinition, PDFgenTaskOptions
from golem.core.common import get_golem_path
from golem.network.p2p.node import Node
from golem.testutils import PEP8MixIn, TempDirFixture
from golem.tools.assertlogs import LogTestCase


class TestPDFgenTask(TempDirFixture, LogTestCase, PEP8MixIn):
    PEP8_FILES = [
        'apps/pdfgen/task/pdfgentask.py',
    ]

    def _get_new_pdfgen(self):
        td = PDFgenTaskDefinition(PDFgenTaskDefaults())
        td.task_id = str(uuid.uuid4())
        td.resources = [os.path.join(get_golem_path(), "apps", "pdfgen", "test_data", "input.txt")]
        td.add_to_resources()
        dt = PDFgenTask(1, td, "root/path", Node())
        return dt, td

    def test_constants(self):
        assert PDFgenTask.ENVIRONMENT_CLASS == PDFgenTaskEnvironment

    def test_init(self):
        dt, td = self._get_new_pdfgen()
        assert isinstance(dt, PDFgenTask)

    def test_extra_data(self):
        dt, td = self._get_new_pdfgen()
        data = dt.query_extra_data(0.0)
        exd = data.ctd['extra_data']

        with open(td.shared_data_files[0], 'r') as f:
            content = f.read()

        assert exd["content"] == content
        assert exd["output_name"].startswith('output')
        assert exd["output_name"].endswith('.pdf')

    def test_accept_results(self):
        dt, td = self._get_new_pdfgen()
        node_id = "Node"
        data = dt.query_extra_data(0.0, node_id=node_id)

        subtask_id = data.ctd['subtask_id']
        dt.accept_results(subtask_id, [])

        assert dt.num_tasks_received == 1
        assert dt.counting_nodes[node_id]._accepted == 1

        with self.assertRaises(KeyError):
            dt.accept_results("nonexistingsubtask", [])

        with self.assertRaises(Exception):
            dt.accept_results(subtask_id, [])

class TestPDFgenTaskTypeInfo(TestCase):
    def test_init(self):
        tti = PDFgenTaskTypeInfo()
        assert tti.name == "PDFgen"
        assert tti.options == PDFgenTaskOptions
        assert isinstance(tti.defaults, PDFgenTaskDefaults)
        assert tti.task_builder_type == PDFgenTaskBuilder
        assert tti.definition == PDFgenTaskDefinition
