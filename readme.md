# Steps to run this service

1. Clone this servie into your system.
2. Install python and create a .venv (virtual environment) directory into your system.
3. Install all the dependencies into the .venv folder
    - source .venv/bin/activate
    - pip install -r requirements.txt

4. Get the GPT LLm model details and GPT API Key and put in llms/GPT.py
    -> _url_cycle = cycle(["LLM_MODEL_DETAIL"])
    -> _api_key_cycle = cycle(["LLM_MODEL_API_KEY"])
    ** Not sharing few things because of sensitive information.

5. Create a cluster inside a db, Create a db, Create a empty collection.
    ** Preferred names you can find in the constants file
6. To run and check the functioning of this application you can refer below items.


# Resollect Task Management API

A comprehensive task management system with AI-powered features including priority classification, tag generation, and sub-task breakdown capabilities.

## 🚀 Features

### Core Task Management
- ✅ **CRUD Operations** - Create, Read, Update, Delete tasks
- ✅ **Priority Classification** - AI-powered task priority assignment
- ✅ **Status Tracking** - Pending, In Progress, Completed states
- ✅ **Deadline Management** - Task scheduling and deadline tracking

### AI-Powered Features
- 🤖 **Smart Priority Detection** - Automatic priority classification using GPT
- 🏷️ **Intelligent Tag Generation** - AI-generated relevant tags for tasks
- 📋 **Sub-task Breakdown** - Automatic decomposition of complex tasks into actionable sub-tasks

### Advanced Filtering & Organization
- 🔍 **Multi-criteria Filtering** - Filter by priority, status, completion, and tags
- 📊 **Flexible Sorting** - Sort by any field (ascending/descending)
- 🏷️ **Tag-based Organization** - Group and filter tasks by tags
- 🔗 **Hierarchical Structure** - Parent-child relationships between tasks

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- MongoDB database
- GPT API access (for AI features)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd resollect_assignment
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure AI Integration**
   - Edit `llms/GPT.py`
   - Add your GPT model details and API key:
   ```python
   _url_cycle = cycle(["YOUR_LLM_MODEL_URL"])
   _api_key_cycle = cycle(["YOUR_API_KEY"])
   ```

5. **Set up MongoDB**
   - Create a MongoDB cluster
   - Create database: `brs-db`
   - Collections will be created automatically

6. **Run the application**
   ```bash
   python app.py
   ```

## 📁 Project Structure

```
resollect_assignment/
├── app.py                          # Main Flask application
├── config.py                       # Configuration settings
├── constants.py                    # Application constants
├── log.py                          # Logging configuration
├── requirements.txt                # Python dependencies
├── readme.md                       # This file
│
├── config_mapping/                 # Data models and schemas
│   ├── __init__.py
│   └── mapping.py                  # Task, Tag, and Response schemas
│
├── controller/                     # API controllers (modular structure)
│   ├── __init__.py
│   ├── main_controller.py          # Main controller registration
│   ├── task_controller.py          # Legacy compatibility
│   ├── task_list_controller.py     # Task listing and creation
│   ├── task_detail_controller.py   # Individual task operations
│   ├── task_complete_controller.py # Task completion
│   ├── tag_controller.py           # Tag operations
│   ├── subtask_controller.py       # Sub-task generation
│   └── controller_helper.py        # Shared controller utilities
│
├── services/                       # Business logic services
│   ├── __init__.py
│   ├── tag_service.py              # Tag management and AI generation
│   └── subtask_service.py          # Sub-task generation and relationships
│
├── mongodb/                        # Database operations
│   ├── __init__.py
│   ├── mongo_template.py           # MongoDB connection and utilities
│   └── mongo_operations.py         # Database CRUD operations
│
└── llms/                          # AI/LLM integration
    ├── __init__.py
    └── GPT.py                      # GPT model integration
```

## 🎯 API Endpoints

### Task Management

#### Create Task with AI Features
```bash
POST /resollect/tasks/task
Content-Type: application/json

{
  "title": "Complete project report",
  "inputStr": "Need to finish the quarterly report by Friday",
  "deadline": "2024-12-31T23:59:59"
}

# Response includes AI-generated priority and tags
{
  "successCode": 200,
  "successResponse": "Task is successfully submitted with id: {id} and tags: ['Work', 'Urgent']"
}
```

#### List Tasks with Advanced Filtering
```bash
# Basic filtering
GET /resollect/tasks/task?priority=Critical&ordering=-created_at

# Tag-based filtering
GET /resollect/tasks/task?tag=work

# Combined filters
GET /resollect/tasks/task?tag=urgent&priority=High&status=Pending

# Sort by deadline
GET /resollect/tasks/task?ordering=-deadline
```

#### Task Operations
```bash
# Get single task (includes tags and sub-tasks)
GET /resollect/tasks/{task_id}

# Update task
PUT /resollect/tasks/{task_id}
Content-Type: application/json
{
  "title": "Updated title",
  "status": "In Progress"
}

# Delete task
DELETE /resollect/tasks/{task_id}

# Mark task as completed
POST /resollect/tasks/{task_id}/complete
```

### AI Sub-task Generation

#### Generate Sub-tasks for Complex Tasks
```bash
POST /resollect/tasks/{task_id}/generate-subtasks

# Example: Break down "Plan team trip to mountains"
# Returns 5 actionable sub-tasks:
[
  "Research mountain destinations",
  "Check team availability", 
  "Book accommodations",
  "Plan transportation",
  "Create itinerary"
]
```

#### Sub-task Management
```bash
# Get all sub-tasks for a parent task
GET /resollect/tasks/{task_id}/subtasks

# Get parent task for a sub-task
GET /resollect/tasks/subtask/{subtask_id}/parent
```

### Tag Management

#### List All Available Tags
```bash
GET /resollect/tags/
```

#### Tag-based Task Filtering
```bash
# Filter tasks by tag
GET /resollect/tasks/task?tag=work

# Multiple tag combinations
GET /resollect/tasks/task?tag=urgent&priority=High
```

### Debug & Development

#### Debug Endpoints
```bash
# List all task IDs
GET /resollect/tasks/debug/ids
```

## 🤖 AI Integration

### Priority Classification
- **Prompt**: Analyzes task title and description to classify priority
- **Output**: Low, Medium, High, or Critical
- **Use Case**: Automatic priority assignment for new tasks

### Tag Generation
- **Prompt**: Generates relevant tags from predefined list
- **Available Tags**: Work, Personal, Health, Finance, Learning, Urgent, Shopping
- **Output**: Up to 3 relevant tags per task

### Sub-task Breakdown
- **Prompt**: Project manager-style task decomposition
- **Output**: JSON array of actionable sub-task titles
- **Features**: Automatic deadline calculation, tag generation for sub-tasks

## 🏗️ Architecture

### Modular Controller Design
- **Separation of Concerns**: Each controller handles specific functionality
- **Maintainability**: Easy to find and modify features
- **Testability**: Individual controllers can be tested in isolation
- **Scalability**: Easy to add new features without cluttering code

### Database Design
- **MongoDB**: NoSQL database for flexible schema
- **Collections**: 
  - `task_handler` - Main tasks
  - `tags` - Tag entities
  - `task_tags` - Many-to-many relationships
- **Relationships**: Self-referencing for parent-child task structure

### Service Layer
- **TagService**: Handles tag operations and AI generation
- **SubTaskService**: Manages sub-task creation and relationships
- **MongoTemplate**: Database connection and utilities

## 🔧 Configuration

### Environment Variables
```bash
# MongoDB
MONGO_CONNECT_URL="mongodb+srv://username:password@cluster.mongodb.net/"

# Database
MONGO_DB_NAME="brs-db"
TASK_HANDLER_COLLECTION="task_handler"
TAG_COLLECTION="tags"
TASK_TAG_COLLECTION="task_tags"
```

### AI Prompts (Customizable)
```python
# Priority classification
INPUT_TASK_PRIORITY_FINALIZER = "Analyze the following task and classify its priority..."

# Tag generation  
TASK_TAG_GENERATION_PROMPT = "Based on the following task, generate up to 3 relevant tags..."

# Sub-task generation
SUBTASK_GENERATION_PROMPT = "You are a project manager. Break down the following task..."
```

## 🧪 Testing

### API Testing Examples

#### Create and Manage Tasks
```bash
# 1. Create a task
curl -X POST http://localhost:5001/resollect/tasks/task \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Task", "inputStr": "Test description", "deadline": "2024-12-31T23:59:59"}'

# 2. Get the task ID from response and generate sub-tasks
curl -X POST http://localhost:5001/resollect/tasks/{task_id}/generate-subtasks

# 3. View the task with sub-tasks
curl http://localhost:5001/resollect/tasks/{task_id}

# 4. Filter by tags
curl http://localhost:5001/resollect/tasks/task?tag=work
```

## 🚀 Deployment

### Production Setup
1. **Environment Variables**: Set production MongoDB and GPT credentials
2. **Logging**: Configure production logging levels
3. **Security**: Implement authentication and rate limiting
4. **Monitoring**: Add health checks and metrics

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5001
CMD ["python", "app.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the API documentation
- Review the controller README for detailed endpoint information
- Open an issue for bugs or feature requests

---

**Built with ❤️ using Flask, MongoDB, and GPT AI**