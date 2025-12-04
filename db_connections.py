import sqlite3
import os
from pymongo import MongoClient
from pymongo.collection import Collection
from dotenv import load_dotenv

load_dotenv()

SQL_DB_NAME = os.getenv("DB_PATH")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DATABASE = os.getenv("MONGO_DB")
MONGO_COLLECTTION = os.getenv("MONGO_DB_COLLECTION")


def get_sqlite_connection():
    try:
        conn = sqlite3.connect(SQL_DB_NAME)  # creates or connection
        conn.execute("PRAGMA foreign_keys=ON;")
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"SQLite connection error: {e}")
        return None


def create_and_set_database():
    conn = get_sqlite_connection()
    if conn is None:
        print("Failed to establish SQLite connection. Cannot set up schema.")
        return
    try:
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Employees(
                employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT,
                email TEXT NOT NULL UNIQUE,
                hire_date TEXT NOT NULL,
                department TEXT NOT NULL
        )             
    ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Projects(
                project_id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT,
                status TEXT NOT NULL DEFAULT 'Planning',
                CHECK(status IN ('Planning','Development','Completion'))
        )
    ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS EmployeeProjects(
                assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                project_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                assignment_date TEXT NOT NULL,
                FOREIGN KEY(employee_id) REFERENCES Employees(employee_id) ON DELETE CASCADE,
                FOREIGN KEY(project_id) REFERENCES Projects(project_id) ON DELETE CASCADE
        )
    ''')
        conn.commit()

        print(
            f"SQLite database '{SQL_DB_NAME}' and tables verified/created successfully")
    except sqlite3.Error as e:
        print(f"SQLite schema creation error: {e}")

    finally:
        conn.close()


def get_mongo_db_collection():
    try:
        client = MongoClient(MONGO_URI)

        client.admin.command('ping')

        db = client[MONGO_DATABASE]
        reviews_collection = db[MONGO_COLLECTTION]

        # print(f"MongoDB connection to '{MONGO_DATABASE}.{MONGO_COLLECTTION}' is successfull")

        reviews_collection.create_index("employee_id")
        return reviews_collection
    except Exception as e:
        print(f"MongoDB connection error. Check your MONGO_URI and network connection.")
        print(f"Error details: {e}")
        return None


if __name__ == '__main__':
    create_and_set_database()

    mongo_col = get_mongo_db_collection()
    if mongo_col is not None:
        print(f"Ready to interact with MongoDB collection: {mongo_col.name}")
