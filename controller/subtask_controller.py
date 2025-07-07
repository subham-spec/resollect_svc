from log import logger
from flask import make_response, jsonify
from config_mapping.mapping import SuccessResponse, ErrorResponse
from flask_restx import Namespace, Resource
from services.subtask_service import SubTaskService


api = Namespace("resollect/tasks")

@api.route('/<string:id>/generate-subtasks')
class SubTaskGenerationResource(Resource):
    def post(self, id):
        """
            Generate sub-tasks for a parent task using AI
            Click on the "Try it out" button to see the response.
            Enter the task ID in the input field and click on the "Execute" button to see the response.
            This API call will generate sub-tasks for a parent task using AI.
        """
        try:
            subtask_service = SubTaskService()
            
            # Check if task exists and get its details
            parent_task = subtask_service.task_collection.find_one({"_id": id})
            if not parent_task:
                error_response = ErrorResponse(
                    errorCode=404,
                    errorResponse=f"Task with id {id} not found"
                )
                return make_response(jsonify(error_response.to_dict()), 404)
            
            # Check if task already has sub-tasks
            existing_subtasks = subtask_service.get_subtasks_for_task(id)
            if existing_subtasks:
                error_response = ErrorResponse(
                    errorCode=400,
                    errorResponse=f"Task {id} already has {len(existing_subtasks)} sub-tasks. Cannot generate new ones."
                )
                return make_response(jsonify(error_response.to_dict()), 400)
            
            # Generate sub-tasks using AI
            title = parent_task.get('title', '')
            description = parent_task.get('description', '')
            
            created_subtasks = subtask_service.generate_subtasks_for_task(id, title, description)
            
            if not created_subtasks:
                error_response = ErrorResponse(
                    errorCode=500,
                    errorResponse=f"Failed to generate sub-tasks for task {id}"
                )
                return make_response(jsonify(error_response.to_dict()), 500)
            
            success_response = SuccessResponse(
                successCode=200,
                successResponse=f"Successfully generated {len(created_subtasks)} sub-tasks for task {id}"
            )
            
            return make_response(jsonify({
                "success": success_response.to_dict(),
                "subtasks": created_subtasks
            }), 200)
            
        except Exception as e:
            logger.error(f"Error generating sub-tasks for task {id}: {e}")
            error_response = ErrorResponse(
                errorCode=500,
                errorResponse=f"Failed to generate sub-tasks: {str(e)}"
            )
            return make_response(jsonify(error_response.to_dict()), 500)


@api.route('/<string:id>/subtasks')
class SubTaskListResource(Resource):
    def get(self, id):
        """
            Get all sub-tasks for a parent task
            Click on the "Try it out" button to see the response.
            Enter the task ID in the input field and click on the "Execute" button to see the response.
            This API call will get all the sub-tasks for a parent task.
            This API call will return the parent task ID, the sub-tasks and the total count of sub-tasks.
            This API call will return the sub-tasks in the following format:
            {
                "parent_task_id": "123",
                "subtasks": [
                    {
                        "id": "123",
                        "title": "Sub-task 1",
        """
        try:
            subtask_service = SubTaskService()
            
            # Check if task exists
            parent_task = subtask_service.task_collection.find_one({"_id": id})
            if not parent_task:
                error_response = ErrorResponse(
                    errorCode=404,
                    errorResponse=f"Task with id {id} not found"
                )
                return make_response(jsonify(error_response.to_dict()), 404)
            
            # Get sub-tasks
            subtasks = subtask_service.get_subtasks_for_task(id)
            
            return make_response(jsonify({
                "parent_task_id": id,
                "subtasks": subtasks,
                "total_count": len(subtasks)
            }), 200)
            
        except Exception as e:
            logger.error(f"Error getting sub-tasks for task {id}: {e}")
            error_response = ErrorResponse(
                errorCode=500,
                errorResponse=f"Failed to get sub-tasks: {str(e)}"
            )
            return make_response(jsonify(error_response.to_dict()), 500)


@api.route('/subtask/<string:id>/parent')
class SubTaskParentResource(Resource):
    def get(self, id):
        """
            Get the parent task for a sub-task
            Click on the "Try it out" button to see the response.
            Enter the sub-task ID in the input field and click on the "Execute" button to see the response.
            This API call will get the parent task for a sub-task.
            This API call will return the parent task ID and the parent task title.
            This API call will return the parent task in the following format:
            {
                "subtask_id": "123",
        """
        try:
            subtask_service = SubTaskService()
            
            # Check if sub-task exists
            subtask = subtask_service.task_collection.find_one({"_id": id})
            if not subtask:
                error_response = ErrorResponse(
                    errorCode=404,
                    errorResponse=f"Sub-task with id {id} not found"
                )
                return make_response(jsonify(error_response.to_dict()), 404)
            
            if not subtask.get('is_subtask'):
                error_response = ErrorResponse(
                    errorCode=400,
                    errorResponse=f"Task {id} is not a sub-task"
                )
                return make_response(jsonify(error_response.to_dict()), 400)
            
            # Get parent task
            parent_task = subtask_service.get_parent_task(id)
            
            if not parent_task:
                error_response = ErrorResponse(
                    errorCode=404,
                    errorResponse=f"Parent task not found for sub-task {id}"
                )
                return make_response(jsonify(error_response.to_dict()), 404)
            
            return make_response(jsonify({
                "subtask_id": id,
                "parent_task": parent_task
            }), 200)
            
        except Exception as e:
            logger.error(f"Error getting parent task for sub-task {id}: {e}")
            error_response = ErrorResponse(
                errorCode=500,
                errorResponse=f"Failed to get parent task: {str(e)}"
            )
            return make_response(jsonify(error_response.to_dict()), 500) 