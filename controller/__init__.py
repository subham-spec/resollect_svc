from flask_restx import Api
from controller import task_list_controller as tlc
from controller import task_detail_controller as tdc
from controller import task_complete_controller as tcc
from controller import tag_controller as tc
from controller import subtask_controller as sc
from controller import main_controller as mc

def register_routes(api: Api):
    api.add_namespace(tdc.api)
    api.add_namespace(tlc.api)
    api.add_namespace(tcc.api)
    api.add_namespace(tc.api)
