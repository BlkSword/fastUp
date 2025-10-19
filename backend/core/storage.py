import os
import json
import uuid
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from models.schemas import TaskResponse, TaskStatus, FileUploadResponse

class TaskStorage:
    """Simple file-based storage for tasks"""
    
    def __init__(self, data_file: str = "tasks_data.json"):
        self.data_file = data_file
        self.ensure_data_file()
    
    def ensure_data_file(self):
        """Ensure the data file exists"""
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def load_tasks(self) -> Dict:
        """Load tasks from file"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def save_tasks(self, tasks: Dict):
        """Save tasks to file"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2, default=str)
    
    def create_task(self, name: str, description: Optional[str] = None) -> TaskResponse:
        """Create a new upload task"""
        task_id = str(uuid.uuid4())
        folder_path = os.path.join("uploads", task_id)
        os.makedirs(folder_path, exist_ok=True)
        
        task_data = {
            "id": task_id,
            "name": name,
            "description": description,
            "status": TaskStatus.ACTIVE.value,
            "folder_path": folder_path,
            "created_at": datetime.now().isoformat(),
            "uploaded_files_count": 0
        }
        
        tasks = self.load_tasks()
        tasks[task_id] = task_data
        self.save_tasks(tasks)
        
        return TaskResponse(**task_data)
    
    def get_actual_counts(self, folder_path: str) -> Tuple[int, int]:
        """Calculate actual file count and user count for a task folder"""
        actual_file_count = 0
        actual_users_count = 0
        
        if os.path.exists(folder_path):
            try:
                # Calculate number of users (subdirectories)
                actual_users_count = len(next(os.walk(folder_path))[1])
                
                # Calculate total number of files
                for root, dirs, files in os.walk(folder_path):
                    actual_file_count += len(files)
            except Exception:
                # If any error occurs during calculation, return zeros
                pass
                
        return actual_file_count, actual_users_count
    
    def get_all_tasks(self) -> List[TaskResponse]:
        """Get all tasks with updated counts"""
        tasks = self.load_tasks()
        result = []
        for task_data in tasks.values():
            task = TaskResponse(**task_data)
            # Update task with actual file count
            actual_file_count, _ = self.get_actual_counts(task.folder_path)
            task.uploaded_files_count = actual_file_count
            result.append(task)
        return result
    
    def get_task(self, task_id: str) -> Optional[TaskResponse]:
        """Get a task by ID with updated counts"""
        tasks = self.load_tasks()
        task_data = tasks.get(task_id)
        if task_data:
            task = TaskResponse(**task_data)
            # Update task with actual file count
            actual_file_count, _ = self.get_actual_counts(task.folder_path)
            task.uploaded_files_count = actual_file_count
            return task
        return None
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> Optional[TaskResponse]:
        """Update task status"""
        tasks = self.load_tasks()
        if task_id in tasks:
            tasks[task_id]["status"] = status.value
            self.save_tasks(tasks)
            return TaskResponse(**tasks[task_id])
        return None
    
    def increment_file_count(self, task_id: str):
        """Increment uploaded files count for a task"""
        tasks = self.load_tasks()
        if task_id in tasks:
            tasks[task_id]["uploaded_files_count"] = tasks[task_id].get("uploaded_files_count", 0) + 1
            self.save_tasks(tasks)
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        tasks = self.load_tasks()
        if task_id in tasks:
            del tasks[task_id]
            self.save_tasks(tasks)
            # Optionally remove the folder (be careful in production)
            # import shutil
            # shutil.rmtree(os.path.join("uploads", task_id), ignore_errors=True)
            return True
        return False

# Global storage instance
task_storage = TaskStorage()