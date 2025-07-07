from flask_restx import Api
from .task_list_controller import api as task_list_api
from .task_detail_controller import api as task_detail_api
from .task_complete_controller import api as task_complete_api
from .tag_controller import api as tag_api
from .subtask_controller import api as subtask_api


def register_controllers(app):
    """
    Register all controllers with the Flask app
    """
    api = Api(app, title='Resollect Task API', version='1.0', description='Task management API')
    
    # Register all namespaces
    api.add_namespace(task_list_api)
    api.add_namespace(task_detail_api)
    api.add_namespace(task_complete_api)
    api.add_namespace(tag_api)
    api.add_namespace(subtask_api)
    
    return api 