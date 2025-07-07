from log import logger
from pymongo.collection import Collection
from .mongo_template import MongoTemplate
from typing import List, Dict, Any, Optional

def addnewTask(collection: Collection, request_body) -> bool:
    """
        It helps to log the task into the database collection 
        Args:
            collection (Collection): Collection in which data needs to be inserted
            request_body (dict): Dictionary needs to be inserted
        Response:
            str: denotes the uuid insered
    """
    try: 
        logger.info(f"Inserting the task into the collection")
        query = request_body

        new_user_created = MongoTemplate.add_new_task(collection, query)
        if not new_user_created:
            logger.error(f"Error while inserting the task into the collection")
            return False
        
        return True

    except Exception as e:
        logger.error(f"Got an unexpected error with {e}")
        return False


def getTasks(collection: Collection, filters: Optional[Dict[str, Any]] = None, ordering: Optional[str] = None, task_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
        It helps to retrieve tasks from the database collection with optional filtering and ordering
        Args:
            collection (Collection): Collection from which data needs to be retrieved
            filters (dict): Optional filters to apply
            ordering (str): Optional ordering parameter (e.g., "-priority", "created_at")
            task_ids (list): Optional list of specific task IDs to filter by
        Response:
            List[Dict]: List of task documents
    """
    try:
        logger.info(f"Retrieving tasks from collection with filters: {filters}, ordering: {ordering}, task_ids: {task_ids}")
        
        # Build query
        query = {}
        if filters:
            if filters.get('priority'):
                query['priority'] = filters['priority']
            if filters.get('status'):
                query['status'] = filters['status']
            if filters.get('completed') is not None:
                query['completed'] = filters['completed']
        
        # Add task_ids filter if provided
        if task_ids:
            query['_id'] = {'$in': task_ids}
        
        # Build sort
        sort = []
        if ordering:
            if ordering.startswith('-'):
                sort.append((ordering[1:], -1))  # Descending
            else:
                sort.append((ordering, 1))  # Ascending
        
        # If no sort specified, default to created_at descending
        if not sort:
            sort = [('created_at', -1)]
        
        # Execute query
        cursor = collection.find(query).sort(sort)
        tasks = list(cursor)
        
        logger.info(f"Retrieved {len(tasks)} tasks from collection")
        return tasks
        
    except Exception as e:
        logger.error(f"Got an unexpected error while retrieving tasks: {e}")
        return []
