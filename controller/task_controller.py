# Legacy import file - maintains backward compatibility
# For new implementations, use the separate controller files:
# - task_list_controller.py
# - task_detail_controller.py  
# - task_complete_controller.py
# - tag_controller.py
# - subtask_controller.py
# - main_controller.py

from .task_list_controller import *
from .task_detail_controller import *
from .task_complete_controller import *
from .tag_controller import *
from .subtask_controller import * 