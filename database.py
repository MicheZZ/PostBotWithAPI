import sqlite3
import asyncio
import threading
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path: str = "blog.db"):
        self.db_path = db_path
        self._lock = threading.Lock()

    @contextmanager
    def get_connection(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()

    def create_tables(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    def add_post(self, title: str, content: str) -> int:
        with self._lock:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO posts (title, content) VALUES (?, ?)",
                    (title, content)
                )
                conn.commit()
                return cursor.lastrowid

    def get_all_posts(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM posts ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_post_by_id(self, post_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_post(self, post_id: int, title: str, content: str) -> bool:
        with self._lock:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE posts SET title = ?, content = ? WHERE id = ?",
                    (title, content, post_id)
                )
                conn.commit()
                return cursor.rowcount > 0

    def delete_post(self, post_id: int) -> bool:
        with self._lock:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
                conn.commit()
                return cursor.rowcount > 0

    def check_connection(self) -> bool:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return True
        except Exception:
            return False
