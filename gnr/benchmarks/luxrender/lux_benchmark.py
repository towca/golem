import os

from gnr.renderingtaskstate import RenderingTaskDefinition
from gnr.renderingdirmanager import get_benchmarks_path, find_task_script
from gnr.task.luxrendertask import build_lux_render_info, LuxRenderOptions

lux_task_path = os.path.join(get_benchmarks_path(), "luxrender", "lux_task")

def query_benchmark_task_definition():
    definition = RenderingTaskDefinition()
    definition.tasktype = "LuxRender"
    definition.max_price = 100
    definition.renderer = "LuxRender"
    definition.output_file = "/tmp/out.png"
    definition.main_scene_file = os.path.join(lux_task_path, "schoolcorridor.lxs")
    definition.resolution = [100, 100]
    definition.output_format = "png"
    definition.renderer_options = LuxRenderOptions()
    definition.renderer_options.haltspp = 5
    definition.renderer_options.halttime = 0
    definition.task_id = u"{}".format("lux_benchmark")
    definition.full_task_timeout = 10000
    definition.subtask_timeout = 10000
    definition.main_program_file = u"{}".format(find_task_script("docker_luxtask.py"))
    definition.optimize_total = False
    definition.resources = find_resources()
    definition.resources.add(os.path.normpath(definition.main_program_file))
    return definition

def find_resources():
    selection = []
    for root, dirs, files in os.walk(lux_task_path):
        for name in files:
            selection.append(os.path.join(root, name))
    return set(selection)
