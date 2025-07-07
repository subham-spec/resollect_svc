from log import logger
from datetime import datetime
from flask import request, make_response, jsonify
from config_mapping.mapping import SuccessResponse, ErrorResponse
from constants import TASK_HANDLER_COLLECTION
from flask_restx import Namespace, Resource
from mongodb.mongo_template import MongoTemplate
from services.tag_service import TagService
from services.subtask_service import SubTaskService


api = Namespace("resollect/tasks")

mongo_client = MongoTemplate.create_moongo_client()

@api.route('/<string:id>')
class TaskDetailResource(Resource):
    def get(self, id):
        """
            Get single task by ID
        """
        try:
            task_collection = mongo_client['brs-db'][TASK_HANDLER_COLLECTION]
            
            logger.info(f"Searching for task with ID: {id}")
            
            # Find task by ID
            task = task_collection.find_one({"_id": id})
            
            logger.info(f"Task found: {task}")
            
            if not task:
                error_response = ErrorResponse(
                    errorCode=404,
                    errorResponse=f"Task with id {id} not found"
                )
                return make_response(jsonify(error_response.to_dict()), 404)
            
            # Initialize services
            tag_service = TagService()
            subtask_service = SubTaskService()
            
            # Convert ObjectId to string for JSON serialization
            if '_id' in task:
                task['_id'] = str(task['_id'])
            if 'created_at' in task and task['created_at']:
                task['created_at'] = task['created_at'].isoformat()
            if 'updated_at' in task and task['updated_at']:
                task['updated_at'] = task['updated_at'].isoformat()
            
            # Add tags to task
            task_tags = tag_service.get_task_tags(task['_id'])
            task['tags'] = task_tags
            
            # Add sub-tasks if this is a parent task
            if not task.get('is_subtask', False):
                subtasks = subtask_service.get_subtasks_for_task(task['_id'])
                task['subtasks'] = subtasks
                task['subtask_count'] = len(subtasks)
            else:
                # If this is a sub-task, add parent task info
                parent_task = subtask_service.get_parent_task(task['_id'])
                if parent_task:
                    task['parent_task'] = {
                        'id': parent_task['_id'],
                        'title': parent_task['title']
                    }
            
            return make_response(jsonify(task), 200)
            
        except Exception as e:
            logger.error(f"Error while retrieving task {id}: {e}")
            error_response = ErrorResponse(
                errorCode=500,
                errorResponse=f"Failed to retrieve task: {str(e)}"
            )
            return make_response(jsonify(error_response.to_dict()), 500)

    def put(self, id):
        """
            Update task by ID
        """
        try:
            task_collection = mongo_client['brs-db'][TASK_HANDLER_COLLECTION]
            
            # Check if task exists
            existing_task = task_collection.find_one({"_id": id})
            if not existing_task:
                error_response = ErrorResponse(
                    errorCode=404,
                    errorResponse=f"Task with id {id} not found"
                )
                return make_response(jsonify(error_response.to_dict()), 404)
            
            # Get update data from request body
            update_data = request.get_json()
            if not update_data:
                error_response = ErrorResponse(
                    errorCode=400,
                    errorResponse="No update data provided"
                )
                return make_response(jsonify(error_response.to_dict()), 400)
            
            # Add updated_at timestamp
            update_data['updated_at'] = datetime.now()
            
            # Update the task
            result = task_collection.update_one(
                {"_id": id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                success_response = SuccessResponse(
                    successCode=200,
                    successResponse=f"Task {id} updated successfully"
                )
                return make_response(jsonify(success_response.to_dict()), 200)
            else:
                error_response = ErrorResponse(
                    errorCode=400,
                    errorResponse=f"Failed to update task {id}"
                )
                return make_response(jsonify(error_response.to_dict()), 400)
                
        except Exception as e:
            logger.error(f"Error while updating task {id}: {e}")
            error_response = ErrorResponse(
                errorCode=500,
                errorResponse=f"Failed to update task: {str(e)}"
            )
            return make_response(jsonify(error_response.to_dict()), 500)

    def delete(self, id):
        """
            Delete task by ID
        """
        try:
            task_collection = mongo_client['brs-db'][TASK_HANDLER_COLLECTION]
            
            # Check if task exists
            existing_task = task_collection.find_one({"_id": id})
            if not existing_task:
                error_response = ErrorResponse(
                    errorCode=404,
                    errorResponse=f"Task with id {id} not found"
                )
                return make_response(jsonify(error_response.to_dict()), 404)
            
            # Delete the task
            result = task_collection.delete_one({"_id": id})
            
            if result.deleted_count > 0:
                success_response = SuccessResponse(
                    successCode=200,
                    successResponse=f"Task {id} deleted successfully"
                )
                return make_response(jsonify(success_response.to_dict()), 200)
            else:
                error_response = ErrorResponse(
                    errorCode=400,
                    errorResponse=f"Failed to delete task {id}"
                )
                return make_response(jsonify(error_response.to_dict()), 400)
                
        except Exception as e:
            logger.error(f"Error while deleting task {id}: {e}")
            error_response = ErrorResponse(
                errorCode=500,
                errorResponse=f"Failed to delete task: {str(e)}"
            )
            return make_response(jsonify(error_response.to_dict()), 500) 