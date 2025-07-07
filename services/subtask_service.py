import json
import uuid
from typing import List, Optional
from datetime import datetime, timedelta
from log import logger
from config_mapping.mapping import TaskSchema
from constants import TASK_HANDLER_COLLECTION, SUBTASK_GENERATION_PROMPT, SUBTASK_SYSTEM_TEMPLATE
from llms.GPT import GPT4O1InferEngine
from mongodb.mongo_template import MongoTemplate
from services.tag_service import TagService

mongo_client = MongoTemplate.create_moongo_client()

class SubTaskService:
    def __init__(self):
        self.task_collection = mongo_client['brs-db'][TASK_HANDLER_COLLECTION]
        self.tag_service = TagService()

    def generate_subtasks_for_task(self, parent_task_id: str, title: str, description: str) -> List[dict]:
        """
        Generate sub-tasks for a parent task using AI
        """
        try:
            logger.info(f"Generating sub-tasks for parent task: {parent_task_id}")
            
            # Generate sub-tasks using AI
            formatted_prompt = SUBTASK_GENERATION_PROMPT.format(title=title, description=description)
            
            # For now, use a mock response. In production, uncomment the next line:
            # response = GPT4O1InferEngine.process_text_input(formatted_prompt, SUBTASK_SYSTEM_TEMPLATE)
            response = '["Research mountain destinations", "Check team availability", "Book accommodations", "Plan transportation", "Create itinerary"]'  # Mock response
            
            # Parse the JSON response
            subtask_titles = json.loads(response)
            
            if not isinstance(subtask_titles, list):
                logger.error(f"Invalid sub-task response format: {response}")
                return []
            
            # Validate that all sub-task titles are strings
            valid_subtask_titles = [title for title in subtask_titles if isinstance(title, str)]
            
            logger.info(f"Generated {len(valid_subtask_titles)} sub-tasks for task '{title}'")
            
            # Create sub-task objects
            created_subtasks = []
            for i, subtask_title in enumerate(valid_subtask_titles):
                subtask = self._create_subtask(parent_task_id, subtask_title, i + 1)
                if subtask:
                    created_subtasks.append(subtask)
            
            return created_subtasks
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI sub-task response: {e}")
            return []
        except Exception as e:
            logger.error(f"Error generating sub-tasks: {e}")
            return []

    def _create_subtask(self, parent_task_id: str, title: str, order: int) -> Optional[dict]:
        """
        Create a sub-task and store it in the database
        """
        try:
            # Generate sub-task ID
            subtask_id = str(uuid.uuid4())
            
            # Set deadline to 7 days from now (or inherit from parent)
            parent_task = self.task_collection.find_one({"_id": parent_task_id})
            if parent_task and parent_task.get('deadline'):
                try:
                    parent_deadline = datetime.fromisoformat(parent_task['deadline'].replace('Z', '+00:00'))
                    # Set sub-task deadline to 2 days before parent deadline
                    subtask_deadline = parent_deadline - timedelta(days=2)
                except:
                    subtask_deadline = datetime.now() + timedelta(days=7)
            else:
                subtask_deadline = datetime.now() + timedelta(days=7)
            
            # Create sub-task object
            subtask_schema = TaskSchema(
                _id=subtask_id,
                title=title,
                description=f"Sub-task {order}: {title}",
                deadline=subtask_deadline.isoformat(),
                priority="Medium",  # Default priority for sub-tasks
                completed=False,
                status="Pending",
                tags=[],
                parent_task_id=parent_task_id,
                is_subtask=True
            )
            
            # Store in database
            subtask_dict = subtask_schema.to_dict()
            self.task_collection.insert_one(subtask_dict)
            
            logger.info(f"Created sub-task: {title} with ID: {subtask_id}")
            
            # Generate tags for the sub-task
            generated_tags = self.tag_service.generate_tags_for_task(title, subtask_schema.description)
            if generated_tags:
                self.tag_service.associate_tags_with_task(subtask_id, generated_tags)
                subtask_dict['tags'] = generated_tags
            
            return subtask_dict
            
        except Exception as e:
            logger.error(f"Error creating sub-task: {e}")
            return None

    def get_subtasks_for_task(self, parent_task_id: str) -> List[dict]:
        """
        Get all sub-tasks for a parent task
        """
        try:
            # Find all sub-tasks for the parent
            subtasks = list(self.task_collection.find({
                "parent_task_id": parent_task_id,
                "is_subtask": True
            }).sort("created_at", 1))  # Sort by creation date
            
            # Convert ObjectId to string and add tags
            for subtask in subtasks:
                if '_id' in subtask:
                    subtask['_id'] = str(subtask['_id'])
                if 'created_at' in subtask and subtask['created_at']:
                    subtask['created_at'] = subtask['created_at'].isoformat()
                if 'updated_at' in subtask and subtask['updated_at']:
                    subtask['updated_at'] = subtask['updated_at'].isoformat()
                
                # Add tags to sub-task
                task_tags = self.tag_service.get_task_tags(subtask['_id'])
                subtask['tags'] = task_tags
            
            return subtasks
            
        except Exception as e:
            logger.error(f"Error getting sub-tasks for task {parent_task_id}: {e}")
            return []

    def get_parent_task(self, subtask_id: str) -> Optional[dict]:
        """
        Get the parent task for a sub-task
        """
        try:
            subtask = self.task_collection.find_one({"_id": subtask_id})
            if not subtask or not subtask.get('parent_task_id'):
                return None
            
            parent_task = self.task_collection.find_one({"_id": subtask['parent_task_id']})
            if parent_task:
                # Convert ObjectId to string
                if '_id' in parent_task:
                    parent_task['_id'] = str(parent_task['_id'])
                if 'created_at' in parent_task and parent_task['created_at']:
                    parent_task['created_at'] = parent_task['created_at'].isoformat()
                if 'updated_at' in parent_task and parent_task['updated_at']:
                    parent_task['updated_at'] = parent_task['updated_at'].isoformat()
                
                # Add tags to parent task
                task_tags = self.tag_service.get_task_tags(parent_task['_id'])
                parent_task['tags'] = task_tags
                
                return parent_task
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting parent task for sub-task {subtask_id}: {e}")
            return None

    def update_parent_task_progress(self, parent_task_id: str) -> bool:
        """
        Update parent task completion status based on sub-tasks
        """
        try:
            # Get all sub-tasks for the parent
            subtasks = self.get_subtasks_for_task(parent_task_id)
            
            if not subtasks:
                return False
            
            # Calculate completion percentage
            total_subtasks = len(subtasks)
            completed_subtasks = sum(1 for subtask in subtasks if subtask.get('completed', False))
            completion_percentage = (completed_subtasks / total_subtasks) * 100
            
            # Update parent task status
            update_data = {
                "updated_at": datetime.now()
            }
            
            if completion_percentage == 100:
                update_data["completed"] = True
                update_data["status"] = "Completed"
            elif completion_percentage > 0:
                update_data["status"] = "In Progress"
            else:
                update_data["status"] = "Pending"
            
            # Update the parent task
            result = self.task_collection.update_one(
                {"_id": parent_task_id},
                {"$set": update_data}
            )
            
            logger.info(f"Updated parent task {parent_task_id} progress: {completion_percentage}% complete")
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating parent task progress: {e}")
            return False 