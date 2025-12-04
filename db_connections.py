import sqlite3
from pymongo import MongoClient
import os
from pathlib import Path

# ============================================================================
# CONFIGURATION - STREAMLIT CLOUD COMPATIBLE
# ============================================================================


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
    return 'company.db'


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
    mongo_uri = os.getenv('MONGO_URI')
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
DB_PATH = get_db_path()
MONGO_URI = get_mongo_uri()
MONGO_DB_NAME = get_mongo_db_name()

print(f"Database configuration loaded:")
print(f"  SQLite Path: {DB_PATH}")
print(f"  MongoDB Database: {MONGO_DB_NAME}")


# ============================================================================
# SQL DATABASE FUNCTIONS
# ============================================================================

def get_sql_connection():
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
    Initialize SQL database with required tables.
    Creates tables only if they don't exist.
    """
    conn = None
    try:
        conn = get_sql_connection()
        cursor = conn.cursor()

        # Create Employees table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Employees (
                employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                hire_date DATE NOT NULL,
                department TEXT NOT NULL
            )
        ''')

        # Create Projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Projects (
                project_id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE,
                status TEXT DEFAULT 'Planning'
            )
        ''')

        # Create EmployeeProjects junction table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS EmployeeProjects (
                assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                project_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                assignment_date DATE NOT NULL,
                FOREIGN KEY (employee_id) REFERENCES Employees(employee_id),
                FOREIGN KEY (project_id) REFERENCES Projects(project_id),
                UNIQUE(employee_id, project_id)
            )
        ''')

        conn.commit()
        print("✓ SQLite database initialized successfully")

        # Check if tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"  Tables created: {[table[0] for table in tables]}")

    except Exception as e:
        print(f"Error initializing SQLite database: {e}")
        if conn:
            conn.rollback()
        raise

    finally:
        if conn:
            conn.close()


# ============================================================================
# MONGODB FUNCTIONS
# ============================================================================

def get_mongo_collection():
    """
    Get MongoDB collection for performance reviews.

    Returns:
        pymongo.collection.Collection: MongoDB collection object

    Raises:
        Exception: If connection fails
    """
    try:
        # Create MongoDB client with timeout
        client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000
        )

        # Test connection
        client.admin.command('ping')
        print("✓ MongoDB connection successful")

        # Get database and collection
        db = client[MONGO_DB_NAME]
        collection = db['reviews']

        # Create indexes for better performance
        try:
            collection.create_index("employee_id")
            # Descending for recent first
            collection.create_index([("review_date", -1)])
        except Exception as e:
            print(f"Warning: Could not create indexes: {e}")

        return collection

    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        print(f"URI (masked): {MONGO_URI[:20]}...{MONGO_URI[-10:]}")
        raise


def test_mongo_connection():
    """
    Test MongoDB connection and return status.

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        collection = get_mongo_collection()
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
        print(f"✗ SQLite initialization failed: {e}")
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
