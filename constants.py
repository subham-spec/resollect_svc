MONGO_CONNECT_URL = "mongodb+srv://subhamsharmalnps123:sTt0StUxAQbA7qPr@brs.l1rwa.mongodb.net/"
MONGO_DB_NAME = "brs-db"
TASK_HANDLER_COLLECTION = "task_handler"
TAG_COLLECTION = "tags"
TASK_TAG_COLLECTION = "task_tags"


INPUT_TASK_PRIORITY_FINALIZER = "Analyze the following task and classify its priority as 'Low', 'Medium', 'High', or 'Critical'. Task Title: {title}, Description: {description}. Return only the priority level, for the above mentioned task."
INPUT_TASK_SYSTEM_TEMPLATE = "You are an expert in the task priority analyzer and you always give 100% accurate results for the given task, after analysing it."

TASK_TAG_GENERATION_PROMPT = "Based on the following task, generate up to 3 relevant one-word tags from the following list: [Work, Personal, Health, Finance, Learning, Urgent, Shopping]. Return them as a JSON array of strings. Task: {title} - {description}"
TASK_TAG_SYSTEM_TEMPLATE = "You are an expert in task categorization. Return only a valid JSON array of strings containing the most relevant tags from the provided list."

SUBTASK_GENERATION_PROMPT = "You are a project manager. Break down the following task into a list of smaller, actionable sub-tasks. Return the result as a JSON array of simple task titles. Each sub-task should be specific, measurable, and achievable. Task: '{title} - {description}'"
SUBTASK_SYSTEM_TEMPLATE = "You are an expert project manager. Return only a valid JSON array of strings containing actionable sub-task titles. Each sub-task should be clear and specific."
