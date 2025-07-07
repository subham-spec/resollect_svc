from config_mapping.mapping import TaskSchema
from flask import make_response, jsonify
from dataclasses import asdict
from services.tag_service import TagService


def create_task_object(request_dict, llm_response, tags=None):
    """
        It helps in create a object of Task Schema which needs to be stored into the db.
    """
    task_object = TaskSchema(
        _id=request_dict.requestId,
        title=request_dict.title,
        description=request_dict.inputStr,
        deadline=request_dict.deadline,
        priority=llm_response,
        tags=tags or []
    )

    return asdict(task_object)
