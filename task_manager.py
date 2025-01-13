import sqlite3
from datetime import datetime
from enum import Enum

class Priority(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class TaskManager:
    def __init__(self, db_path="productivity.db"):
        self.db_path = db_path
        self._create_table()
    
    def _create_table(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    status TEXT DEFAULT 'Incomplete',
                    deadline DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def add_task(self, name: str, priority: Priority, deadline: str = None, 
                 category: str = None, tags: list = None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO tasks 
                   (name, priority, deadline, category, tags) 
                   VALUES (?, ?, ?, ?, ?)""",
                (name, priority.value, deadline, category, ','.join(tags or []))
            )
            conn.commit()
            return cursor.lastrowid

    def update_task(self, task_id: int, **kwargs):
        allowed_fields = {'name', 'priority', 'status', 'deadline'}
        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not update_fields:
            return False

        query = "UPDATE tasks SET " + ", ".join(f"{k} = ?" for k in update_fields)
        query += " WHERE id = ?"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (*update_fields.values(), task_id))
            conn.commit()
            return cursor.rowcount > 0

    def delete_task(self, task_id: int):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_all_tasks(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, priority, status, deadline FROM tasks ORDER BY created_at DESC"
            )
            return cursor.fetchall()

    def toggle_task_status(self, task_id: int):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE tasks 
                   SET status = CASE 
                       WHEN status = 'Complete' THEN 'Incomplete' 
                       ELSE 'Complete' 
                   END 
                   WHERE id = ?""",
                (task_id,)
            )
            conn.commit()
            return cursor.rowcount > 0

    def get_progress_stats(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN status = 'Complete' THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN status = 'Incomplete' THEN 1 ELSE 0 END) as pending
                FROM tasks
            """)
            return cursor.fetchone()

    def get_tasks_by_priority(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT priority, 
                       COUNT(*) as total,
                       SUM(CASE WHEN status = 'Complete' THEN 1 ELSE 0 END) as completed
                FROM tasks 
                GROUP BY priority
            """)
            return cursor.fetchall()

    def get_tasks_due_soon(self, days=7):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM tasks 
                WHERE deadline <= date('now', '+? days') 
                AND status = 'Incomplete'
                ORDER BY deadline ASC
            """, (days,))
            return cursor.fetchall() 