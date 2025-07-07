# How to run this service

1. Clone this service into your system
2. Create a .venv file to install the environment dependencies.
3. Run command "pip install -r requirements.txt" and wait for some time to get all the dependencies installed.
4. Put GPT LLM model details and GPT Api Key in llms/GPT.py

   - As both are sensitive data, I'm not sharing them with anyone.


# Controller Structure

This directory contains the task management API controllers organized into separate files for better maintainability and separation of concerns.

## File Structure

### Core Controllers

1. **`task_list_controller.py`**
   - Handles task listing and creation with AI-powered tag generation
   - Endpoints:
     - `GET /resollect/tasks/task` - List tasks with filtering, sorting, and tag filtering
     - `POST /resollect/tasks/task` - Create new task with AI-generated tags
     - `GET /resollect/tasks/debug/ids` - Debug endpoint to list all task IDs

2. **`task_detail_controller.py`**
   - Handles individual task operations
   - Endpoints:
     - `GET /resollect/tasks/{id}` - Get single task by ID (includes tags)
     - `PUT /resollect/tasks/{id}` - Update task by ID
     - `DELETE /resollect/tasks/{id}` - Delete task by ID

3. **`task_complete_controller.py`**
   - Handles task completion operations
   - Endpoints:
     - `POST /resollect/tasks/{id}/complete` - Mark task as completed

4. **`tag_controller.py`**
   - Handles tag operations
   - Endpoints:
     - `GET /resollect/tags/` - List all available tags

5. **`subtask_controller.py`**
   - Handles AI-powered sub-task generation and parent-child relationships
   - Endpoints:
     - `POST /resollect/tasks/{id}/generate-subtasks` - Generate AI-powered sub-tasks
     - `GET /resollect/tasks/{id}/subtasks` - Get all sub-tasks for a parent task
     - `GET /resollect/tasks/subtask/{id}/parent` - Get parent task for a sub-task

### Registration and Compatibility

4. **`main_controller.py`**
   - Main controller registration file
   - Registers all namespaces with Flask app
   - Use this for new applications

5. **`task_controller.py`**
   - Legacy import file for backward compatibility
   - Imports all controllers from separate files
   - Maintains existing import structure

## Usage

### For New Applications

```python
from flask import Flask
from controller.main_controller import register_controllers

app = Flask(__name__)
api = register_controllers(app)
```

### For Existing Applications (Backward Compatibility)

```python
from controller.task_controller import api
# All existing imports will continue to work
```

## API Endpoints

### Task List Operations
- `GET /resollect/tasks/task?priority=Critical&ordering=-created_at`
- `GET /resollect/tasks/task?tag=work` - Filter by tag
- `GET /resollect/tasks/task?tag=urgent&priority=High` - Filter by tag and priority
- `POST /resollect/tasks/task` (with JSON body) - Creates task with AI-generated tags

### Task Detail Operations
- `GET /resollect/tasks/{task_id}` - Returns task with associated tags
- `PUT /resollect/tasks/{task_id}` (with JSON body)
- `DELETE /resollect/tasks/{task_id}`

### Task Completion
- `POST /resollect/tasks/{task_id}/complete`

### Tag Operations
- `GET /resollect/tags/` - List all available tags

### Sub-task Operations
- `POST /resollect/tasks/{task_id}/generate-subtasks` - Generate AI-powered sub-tasks
- `GET /resollect/tasks/{task_id}/subtasks` - Get all sub-tasks for a parent task
- `GET /resollect/tasks/subtask/{subtask_id}/parent` - Get parent task for a sub-task

### Debug
- `GET /resollect/tasks/debug/ids`

## Benefits of This Structure

1. **Separation of Concerns**: Each file handles specific functionality
2. **Maintainability**: Easier to find and modify specific features
3. **Testability**: Can test individual controllers in isolation
4. **Scalability**: Easy to add new controllers without cluttering existing code
5. **Backward Compatibility**: Existing code continues to work unchanged

## Adding New Controllers

To add a new controller:

1. Create a new file (e.g., `task_analytics_controller.py`)
2. Define your namespace and resources
3. Import and register in `main_controller.py`
4. Add import to `task_controller.py` for backward compatibility 