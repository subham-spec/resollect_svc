import json
import uuid
from typing import List, Optional
from log import logger
from config_mapping.mapping import TagSchema, TaskTagSchema
from constants import TAG_COLLECTION, TASK_TAG_COLLECTION, TASK_TAG_GENERATION_PROMPT, TASK_TAG_SYSTEM_TEMPLATE
from llms.GPT import GPT4O1InferEngine
from mongodb.mongo_template import MongoTemplate

mongo_client = MongoTemplate.create_moongo_client()

class TagService:
    def __init__(self):
        self.tag_collection = mongo_client['brs-db'][TAG_COLLECTION]
        self.task_tag_collection = mongo_client['brs-db'][TASK_TAG_COLLECTION]

    def generate_tags_for_task(self, title: str, description: str) -> List[str]:
        """
        Generate tags for a task using AI
        """
        try:
            formatted_prompt = TASK_TAG_GENERATION_PROMPT.format(title=title, description=description)
            
            # For now, use a mock response. In production, uncomment the next line:
            # response = GPT4O1InferEngine.process_text_input(formatted_prompt, TASK_TAG_SYSTEM_TEMPLATE)
            response = '["Work", "Urgent"]'  # Mock response
            
            # Parse the JSON response
            tags = json.loads(response)
            
            if not isinstance(tags, list):
                logger.error(f"Invalid tag response format: {response}")
                return []
            
            # Validate that all tags are strings
            valid_tags = [tag for tag in tags if isinstance(tag, str)]
            
            logger.info(f"Generated tags for task '{title}': {valid_tags}")
            return valid_tags
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI tag response: {e}")
            return []
        except Exception as e:
            logger.error(f"Error generating tags: {e}")
            return []

    def get_or_create_tag(self, tag_name: str) -> Optional[str]:
        """
        Get existing tag or create new one, returns tag ID
        """
        try:
            # Normalize tag name (lowercase for consistency)
            normalized_name = tag_name.lower()
            
            # Check if tag exists
            existing_tag = self.tag_collection.find_one({"name": normalized_name})
            
            if existing_tag:
                return str(existing_tag['_id'])
            
            # Create new tag
            tag_id = str(uuid.uuid4())
            tag_schema = TagSchema(
                _id=tag_id,
                name=normalized_name
            )
            
            self.tag_collection.insert_one(tag_schema.to_dict())
            logger.info(f"Created new tag: {normalized_name}")
            
            return tag_id
            
        except Exception as e:
            logger.error(f"Error in get_or_create_tag: {e}")
            return None

    def associate_tags_with_task(self, task_id: str, tag_names: List[str]) -> bool:
        """
        Associate tags with a task
        """
        try:
            for tag_name in tag_names:
                tag_id = self.get_or_create_tag(tag_name)
                if tag_id:
                    # Create task-tag association
                    task_tag_id = str(uuid.uuid4())
                    task_tag_schema = TaskTagSchema(
                        _id=task_tag_id,
                        task_id=task_id,
                        tag_id=tag_id
                    )
                    
                    self.task_tag_collection.insert_one(task_tag_schema.to_dict())
                    logger.info(f"Associated tag '{tag_name}' with task '{task_id}'")
            
            return True
            
        except Exception as e:
            logger.error(f"Error associating tags with task: {e}")
            return False

    def get_task_tags(self, task_id: str) -> List[str]:
        """
        Get all tags for a specific task
        """
        try:
            # Get task-tag associations
            task_tags = list(self.task_tag_collection.find({"task_id": task_id}))
            
            if not task_tags:
                return []
            
            # Get tag IDs
            tag_ids = [task_tag['tag_id'] for task_tag in task_tags]
            
            # Get tag names
            tags = list(self.tag_collection.find({"_id": {"$in": tag_ids}}))
            
            return [tag['name'] for tag in tags]
            
        except Exception as e:
            logger.error(f"Error getting task tags: {e}")
            return []

    def get_tasks_by_tag(self, tag_name: str) -> List[str]:
        """
        Get all task IDs that have a specific tag
        """
        try:
            # Normalize tag name
            normalized_name = tag_name.lower()
            
            # Find the tag
            tag = self.tag_collection.find_one({"name": normalized_name})
            if not tag:
                return []
            
            # Get task-tag associations for this tag
            task_tags = list(self.task_tag_collection.find({"tag_id": tag['_id']}))
            
            # Extract task IDs
            task_ids = [task_tag['task_id'] for task_tag in task_tags]
            
            return task_ids
            
        except Exception as e:
            logger.error(f"Error getting tasks by tag: {e}")
            return []

    def get_all_tags(self) -> List[dict]:
        """
        Get all available tags
        """
        try:
            tags = list(self.tag_collection.find({}))
            
            # Convert ObjectId to string
            for tag in tags:
                if '_id' in tag:
                    tag['_id'] = str(tag['_id'])
                if 'created_at' in tag and tag['created_at']:
                    tag['created_at'] = tag['created_at'].isoformat()
            
            return tags
            
        except Exception as e:
            logger.error(f"Error getting all tags: {e}")
            return [] 