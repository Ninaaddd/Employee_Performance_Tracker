import sqlite3
import os
from pymongo import MongoClient
import psycopg2
import threading
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

# ============================================================================
# CONFIGURATION - STREAMLIT CLOUD COMPATIBLE
# ============================================================================


def get_postgres_url():
    """
    Get PostgreSQL connection URL.
    Tries Streamlit secrets first, then environment variables.
    """
    # Try Streamlit secrets
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'DATABASE_URL' in st.secrets:
            return st.secrets['DATABASE_URL']
    except Exception:
        pass

    # Try environment variable
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        return db_url

    raise ValueError(
        "PostgreSQL URL not configured. Please set DATABASE_URL in:\n"
        "1. Streamlit Cloud: Settings → Secrets\n"
        "2. Locally: .env file\n"
        "Format: postgresql://user:password@host:port/database"
    )


def get_db_path():
    """
    Get database path that works both locally and on Streamlit Cloud.

    Returns:
        str: Path to SQLite database file
    """
    # Try to get from Streamlit secrets first (for cloud deployment)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'DB_PATH' in st.secrets:
            return st.secrets['DB_PATH']
    except Exception:
        pass

    # Try environment variable
    db_path = os.getenv('DB_PATH')
    if db_path:
        return db_path

    # Default to current directory (works for Streamlit Cloud)
    return 'company_db.db'


def get_mongo_uri():
    """
    Get MongoDB URI that works both locally and on Streamlit Cloud.

    Returns:
        str: MongoDB connection URI
    """
    # Try to get from Streamlit secrets first (for cloud deployment)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'MONGO_URI' in st.secrets:
            return st.secrets['MONGO_URI']
    except Exception:
        pass

    # Try environment variable
    mongo_uri = os.environ.get('MONGO_URI')
    if mongo_uri:
        return mongo_uri

    # Default (will fail but provides clear error)
    raise ValueError(
        "MongoDB URI not configured. Please set MONGO_URI in:\n"
        "1. Streamlit Cloud: Settings → Secrets\n"
        "2. Locally: .env file"
    )


def get_mongo_db_name():
    """
    Get MongoDB database name.

    Returns:
        str: Database name
    """
    # Try to get from Streamlit secrets first
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'MONGO_DB' in st.secrets:
            return st.secrets['MONGO_DB']
    except Exception:
        pass

    # Try environment variable
    db_name = os.getenv('MONGO_DB')
    if db_name:
        return db_name

    # Default
    return 'performance_reviews_db'


# Set configuration
DATABASE_URL = get_postgres_url()
DB_PATH = get_db_path()
MONGO_URI = get_mongo_uri()
MONGO_DB_NAME = get_mongo_db_name()

print(f"Database configuration loaded:")
print(f" PostgreSQL URL configured")
print(f"  SQLite Path: {DB_PATH}")
print(f"  MongoDB Database: {MONGO_DB_NAME}")


# ============================================================================
# SQL DATABASE FUNCTIONS
# ============================================================================

def get_sql_connection():
    """
    Get a NEW PostgreSQL connection for each request.
    This is simpler and works better with Streamlit's execution model.

    Returns:
        psycopg2.connection: Database connection
    """
    try:
        conn = psycopg2.connect(
            DATABASE_URL,
            connect_timeout=10,
            # options='-c statement_timeout=30000'  # 30 second timeout
        )
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        raise


def get_sqlite_connection():
    """
    Get a new SQLite database connection.

    Returns:
        sqlite3.Connection: Database connection object

    Raises:
        Exception: If connection fails
    """
    try:
        # Ensure directory exists
        db_file = Path(DB_PATH)
        db_file.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        conn.row_factory = sqlite3.Row  # Enable column access by name

        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")

        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode = WAL")

        return conn

    except Exception as e:
        print(f"Error connecting to SQLite: {e}")
        raise


def initialize_sql_database():
    """
    Initialize PostgreSQL database with required tables.
    Creates tables only if they don't exist.
    """
    conn = None
    try:
        conn = get_sql_connection()  # postgres connection
        conn1 = get_sqlite_connection()  # sqlite connection
        cursor = conn.cursor()

        # Create Employees table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Employees (
                employee_id SERIAL PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                hire_date DATE NOT NULL,
                department VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create Projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Projects (
                project_id SERIAL PRIMARY KEY,
                project_name VARCHAR(200) NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE,
                status VARCHAR(50) DEFAULT 'Planning',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create EmployeeProjects junction table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS EmployeeProjects (
                assignment_id SERIAL PRIMARY KEY,
                employee_id INTEGER NOT NULL,
                project_id INTEGER NOT NULL,
                role VARCHAR(100) NOT NULL,
                assignment_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES Employees(employee_id) ON DELETE CASCADE,
                FOREIGN KEY (project_id) REFERENCES Projects(project_id) ON DELETE CASCADE,
                UNIQUE(employee_id, project_id)
            )
        ''')

        # Create indexes for better performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_employees_email 
            ON Employees(email)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_employees_department 
            ON Employees(department)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_employee_projects_employee 
            ON EmployeeProjects(employee_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_employee_projects_project 
            ON EmployeeProjects(project_id)
        ''')

        conn.commit()
        print("✓ PostgreSQL database initialized successfully")

        # Check tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        print(f"  Tables: {[t[0] for t in tables]}")

    except Exception as e:
        print(f"✗ Error initializing PostgreSQL database: {e}")
        if conn:
            conn.rollback()
        raise

    finally:
        if conn:
            cursor.close()


# ============================================================================
# MONGODB FUNCTIONS
# ============================================================================
_mongo_client = None
_mongo_lock = threading.Lock()


def get_mongo_db_collection():
    """Get MongoDB collection (singleton client)."""
    global _mongo_client

    with _mongo_lock:
        if _mongo_client is None:
            try:
                _mongo_client = MongoClient(
                    MONGO_URI,
                    serverSelectionTimeoutMS=10000,
                    connectTimeoutMS=10000,
                    socketTimeoutMS=10000
                )
                # Test connection
                _mongo_client.admin.command('ping')
                print("✓ MongoDB connection successful")
            except Exception as e:
                print(f"✗ MongoDB connection failed: {e}")
                raise

        db = _mongo_client[MONGO_DB_NAME]
        collection = db['reviews']

        # Create indexes
        try:
            collection.create_index("employee_id")
            collection.create_index([("review_date", -1)])
        except:
            pass

        return collection


def test_mongo_connection():
    """
    Test MongoDB connection and return status.

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        collection = get_mongo_db_collection()
        # Try a simple operation
        collection.count_documents({})
        return True, "MongoDB connection successful"
    except Exception as e:
        return False, f"MongoDB connection failed: {str(e)}"


# ============================================================================
# INITIALIZATION
# ============================================================================

def initialize_databases():
    """
    Initialize both SQL and NoSQL databases.
    Called on application startup.
    """
    print("\n" + "="*60)
    print("INITIALIZING DATABASES")
    print("="*60)

    # Initialize SQLite
    try:
        initialize_sql_database()
    except Exception as e:
        print(f"✗ PostgreSQL initialization failed: {e}")
        raise

    # Test MongoDB connection
    try:
        success, message = test_mongo_connection()
        if success:
            print(f"✓ {message}")
        else:
            print(f"✗ {message}")
            print("  Note: App will work but reviews won't be saved")
    except Exception as e:
        print(f"✗ MongoDB test failed: {e}")
        print("  Note: App will work but reviews won't be saved")

    print("="*60)
    print("DATABASE INITIALIZATION COMPLETE")
    print("="*60 + "\n")


# ============================================================================
# AUTO-INITIALIZE ON IMPORT
# ============================================================================

# Initialize databases when module is imported
try:
    initialize_databases()
except Exception as e:
    print(f"Warning: Database initialization had issues: {e}")
    print("Some features may not work correctly")
