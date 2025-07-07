from log import logger
from copy import deepcopy
import uuid
from datetime import datetime
from flask import request, make_response, jsonify
from config_mapping import get_schema
from config_mapping.mapping import TaskPostCall, TaskListQuery, TaskListResponse, SuccessResponse, ErrorResponse
from constants import (
    INPUT_TASK_PRIORITY_FINALIZER, INPUT_TASK_SYSTEM_TEMPLATE, TASK_HANDLER_COLLECTION
)
from llms.GPT import GPT4O1InferEngine
from flask_restx import Namespace, Resource
from flask_accepts import accepts, responds
from mongodb.mongo_template import mongo_client, MongoTemplate
from mongodb.mongo_operations import addnewTask, getTasks
from .controller_helper import *
from services.tag_service import TagService
from llms import hugging_face

api = Namespace("resollect/tasks")

@api.route("/task")
class TaskListResource(Resource):
    @accepts(api=api, use_swagger=True)
    def get(self):
        """
            List all tasks, whatever are there in the database and created so far.
            Click on the "Try it out" button to see the response.
            Click on the "Execute" button to see the response.
        """
        try:
            # Get query parameters - try flask-accepts first, fallback to manual parsing
            if hasattr(request, 'parsed_obj') and request.parsed_obj:
                query_params = request.parsed_obj
            else:
                # Manual parsing of query parameters
                query_params = TaskListQuery(
                    ordering=request.args.get('ordering'),
                    priority=request.args.get('priority'),
                    status=request.args.get('status'),
                    completed=request.args.get('completed', type=bool)
                )
            
            logger.info(f"Query parameters: {query_params.to_dict()}")
            
            # Validate that at least one filter parameter is provided
            # if not query_params.has_any_filter():
            #     error_response = ErrorResponse(
            #         errorCode=400,
            #         errorResponse="At least one query parameter must be provided (ordering, priority, status, or completed)"
            #     )
            #     return make_response(jsonify(error_response.to_dict()), 400)
            
            task_collection = mongo_client['brs-db'][TASK_HANDLER_COLLECTION]
            
            # Initialize tag service
            tag_service = TagService()
            
            # Handle tag filtering
            task_ids = None
            if query_params.tag:
                task_ids = tag_service.get_tasks_by_tag(query_params.tag)
                if not task_ids:
                    # No tasks found with this tag, return empty result
                    response = TaskListResponse(
                        tasks=[],
                        total_count=0
                    )
                    return make_response(jsonify(response.to_dict()), 200)
            
            # Build filters
            filters = {}
            if query_params.priority:
                filters['priority'] = query_params.priority
            if query_params.status:
                filters['status'] = query_params.status
            if query_params.completed is not None:
                filters['completed'] = query_params.completed
            
            # Get tasks from database
            tasks = getTasks(task_collection, filters, query_params.ordering, task_ids)
            
            # Convert ObjectId to string for JSON serialization and add tags
            for task in tasks:
                if '_id' in task:
                    task['_id'] = str(task['_id'])
                if 'created_at' in task and task['created_at']:
                    task['created_at'] = task['created_at'].isoformat()
                if 'updated_at' in task and task['updated_at']:
                    task['updated_at'] = task['updated_at'].isoformat()
                
                # Add tags to task
                task_tags = tag_service.get_task_tags(task['_id'])
                task['tags'] = task_tags
            
            # Create response
            response = TaskListResponse(
                tasks=tasks,
                total_count=len(tasks)
            )
            
            return make_response(jsonify(response.to_dict()), 200)
            
        except Exception as e:
            logger.error(f"Error while retrieving tasks: {e}")
            error_response = ErrorResponse(
                errorCode=500,
                errorResponse=f"Failed to retrieve tasks: {str(e)}"
            )
            return make_response(jsonify(error_response.to_dict()), 500)

    @accepts(schema=get_schema(TaskPostCall), api=api, use_swagger=True)
    def post(self):
        """
            This API call will create a new task to check its priority.
            Create a new task with the given title, description and deadline. [title, description, deadline] You only need to provide the title, description and deadline.
            Click on the "Execute" button to see the response.
        """
        mapping_request: TaskPostCall = request.parsed_obj
        request_id = mapping_request.requestId if mapping_request.requestId and len(mapping_request.requestId) > 0 else str(uuid.uuid4())
        logger.info(f"Received a request for task creation with ID: {request_id}")

        task = mapping_request.inputStr
        title = mapping_request.title

        try: 
            tag_service = TagService()
            formatted_prompt = INPUT_TASK_PRIORITY_FINALIZER.format(title=title, description=task)
            response = hugging_face.call_hugging_face(formatted_prompt)
            
            generated_tags = tag_service.generate_tags_for_task(title, task)
            inserted_request = create_task_object(mapping_request, response, generated_tags)
            
            # Getting the collection in which data needs to be inserted
            task_collection = mongo_client['brs-db'][TASK_HANDLER_COLLECTION]
            
            insertion_response = addnewTask(task_collection, inserted_request)
            if insertion_response:
                # Associate tags with the task
                tag_service.associate_tags_with_task(request_id, generated_tags)
                
                success_response = SuccessResponse(
                    successCode=200,
                    successResponse=f"Task is successfully submitted with id: {request_id} and tags: {generated_tags}",
                )
                return make_response(jsonify(success_response.to_dict()), 200)
            else:
                error_response = ErrorResponse(
                    errorCode=400,
                    errorResponse=f"This with id: {request_id} failed to submit"
                )
                return make_response(jsonify(error_response.to_dict()), 400)

        except Exception as e:
            logger.error(f"Getting exception while storing the task as : {e}")
            error_response = ErrorResponse(
                    errorCode=401,
                    errorResponse=f"This with id: {request_id} failed to submit with error: {e}"
                )
            return make_response(jsonify(error_response.to_dict()), 401)


# @api.route('/debug/ids')
# class TaskDebugResource(Resource):
#     def get(self):
        """
            Debug endpoint to list all task IDs
        """
        try:
            task_collection = mongo_client['brs-db'][TASK_HANDLER_COLLECTION]
            
            # Get all tasks and return only their IDs
            tasks = list(task_collection.find({}, {"_id": 1, "title": 1}))
            
            # Convert ObjectId to string
            for task in tasks:
                if '_id' in task:
                    task['_id'] = str(task['_id'])
            
            return make_response(jsonify({"task_ids": tasks}), 200)
            
        except Exception as e:
            logger.error(f"Error while retrieving task IDs: {e}")
            error_response = ErrorResponse(
                errorCode=500,
                errorResponse=f"Failed to retrieve task IDs: {str(e)}"
            )
            return make_response(jsonify(error_response.to_dict()), 500) 