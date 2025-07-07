from log import logger
from datetime import datetime
from flask import make_response, jsonify
from constants import TASK_HANDLER_COLLECTION
from flask_restx import Namespace, Resource
from mongodb.mongo_template import MongoTemplate
from services.subtask_service import SubTaskService
from config_mapping.mapping import SuccessResponse, ErrorResponse


api = Namespace("resollect/tasks")

mongo_client = MongoTemplate.create_moongo_client()
@api.route('/<string:id>/complete')
class TaskCompleteResource(Resource):
    def post(self, id):
        """
        Mark task as completed.
        Args:
            id (str): The unique identifier of the task. Which is the task ID and is a string.
            ID exists in the database.
            ID is a valid task ID.
            ID is a valid task ID.
        """
        try:
            task_collection = mongo_client['brs-db'][TASK_HANDLER_COLLECTION]
            subtask_service = SubTaskService()
            
            # Check if task exists
            existing_task = task_collection.find_one({"_id": id})
            if not existing_task:
                error_response = ErrorResponse(
                    errorCode=404,
                    errorResponse=f"Task with id {id} not found"
                )
                return make_response(jsonify(error_response.to_dict()), 404)
            
            # Update task to completed status
            result = task_collection.update_one(
                {"_id": id},
                {
                    "$set": {
                        "completed": True,
                        "status": "Completed",
                        "updated_at": datetime.now()
                    }
                }
            )
            
            if result.modified_count > 0:
                # If this is a sub-task, update parent task progress
                if existing_task.get('is_subtask') and existing_task.get('parent_task_id'):
                    subtask_service.update_parent_task_progress(existing_task['parent_task_id'])
                    success_response = SuccessResponse(
                        successCode=200,
                        successResponse=f"Sub-task {id} marked as completed and parent task progress updated"
                    )
                else:
                    success_response = SuccessResponse(
                        successCode=200,
                        successResponse=f"Task {id} marked as completed successfully"
                    )
                
                return make_response(jsonify(success_response.to_dict()), 200)
            else:
                error_response = ErrorResponse(
                    errorCode=400,
                    errorResponse=f"Failed to mark task {id} as completed"
                )
                return make_response(jsonify(error_response.to_dict()), 400)
                
        except Exception as e:
            logger.error(f"Error while marking task {id} as completed: {e}")
            error_response = ErrorResponse(
                errorCode=500,
                errorResponse=f"Failed to mark task as completed: {str(e)}"
            )
            return make_response(jsonify(error_response.to_dict()), 500) 