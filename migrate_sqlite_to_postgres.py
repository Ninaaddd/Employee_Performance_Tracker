"""
migrate_sqlite_to_postgres.py

Migrate data from SQLite (company.db) to PostgreSQL (Neon/Supabase).
FIXED: Handles date format conversion and empty string dates.

Usage:
    1. Set up your PostgreSQL database (Neon recommended)
    2. Add DATABASE_URL to .env file
    3. Run: python migrate_sqlite_to_postgres.py
"""

import sqlite3
import psycopg2
from psycopg2.extras import execute_batch
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


def print_header(text):
    """Print formatted header."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def convert_date_format(date_str):
    """
    Convert date from various formats to PostgreSQL format (YYYY-MM-DD).
    Handles: MM/DD/YYYY, DD-MM-YYYY, YYYY-MM-DD, empty strings

    Args:
        date_str: Date string in any format

    Returns:
        str: Date in YYYY-MM-DD format or None
    """
    if not date_str or date_str.strip() == '':
        return None

    date_str = date_str.strip()

    # Already in correct format
    if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
        return date_str

    # Try common formats
    formats = [
        '%m/%d/%Y',  # 06/10/2025
        '%d/%m/%Y',  # 10/06/2025
        '%Y/%m/%d',  # 2025/06/10
        '%m-%d-%Y',  # 06-10-2025
        '%d-%m-%Y',  # 10-06-2025
        '%Y-%m-%d',  # 2025-06-10
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue

    print(f"  ⚠️  Warning: Could not parse date '{date_str}', using NULL")
    return None


def export_from_sqlite(sqlite_path='company_db.db'):
    """Export all data from SQLite database."""
    print_header("STEP 1: Exporting Data from SQLite")

    if not os.path.exists(sqlite_path):
        print(f"✗ SQLite database not found: {sqlite_path}")
        return None

    try:
        conn = sqlite3.connect(sqlite_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        data = {}

        # Export Employees
        print("Exporting employees...")
        cursor.execute("SELECT * FROM Employees ORDER BY employee_id")
        data['employees'] = []
        for row in cursor.fetchall():
            emp = dict(row)
            # Convert hire_date
            emp['hire_date'] = convert_date_format(emp.get('hire_date', ''))
            data['employees'].append(emp)
        print(f"  ✓ Exported {len(data['employees'])} employees")

        # Export Projects
        print("Exporting projects...")
        cursor.execute("SELECT * FROM Projects ORDER BY project_id")
        data['projects'] = []
        for row in cursor.fetchall():
            proj = dict(row)
            # Convert dates
            proj['start_date'] = convert_date_format(
                proj.get('start_date', ''))
            proj['end_date'] = convert_date_format(proj.get('end_date', ''))
            # Skip if start_date is None
            if proj['start_date'] is None:
                print(
                    f"  ⚠️  Skipping project '{proj.get('project_name')}' - invalid start date")
                continue
            data['projects'].append(proj)
        print(f"  ✓ Exported {len(data['projects'])} projects")

        # Export EmployeeProjects
        print("Exporting employee-project assignments...")
        cursor.execute("SELECT * FROM EmployeeProjects ORDER BY assignment_id")
        data['employee_projects'] = []
        for row in cursor.fetchall():
            assign = dict(row)
            # Convert assignment_date
            assign['assignment_date'] = convert_date_format(
                assign.get('assignment_date', ''))
            if assign['assignment_date'] is None:
                assign['assignment_date'] = datetime.now().strftime('%Y-%m-%d')
            data['employee_projects'].append(assign)
        print(f"  ✓ Exported {len(data['employee_projects'])} assignments")

        conn.close()

        # Save backup
        backup_file = f'migration_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        import json
        with open(backup_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"\n✓ Backup saved to: {backup_file}")

        return data

    except Exception as e:
        print(f"✗ Error exporting from SQLite: {e}")
        import traceback
        traceback.print_exc()
        return None


def import_to_postgres(data, database_url):
    """Import data into PostgreSQL database."""
    print_header("STEP 2: Importing Data to PostgreSQL")

    if not data:
        print("✗ No data to import")
        return False

    conn = None
    try:
        # Connect to PostgreSQL
        print("Connecting to PostgreSQL...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        print("  ✓ Connected")

        # Create tables first
        print("\nCreating tables...")

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

        conn.commit()
        print("  ✓ Tables created")

        # Check if tables have data
        cursor.execute("SELECT COUNT(*) FROM Employees")
        emp_count = cursor.fetchone()[0]

        if emp_count > 0:
            response = input(
                f"\n⚠️  PostgreSQL already has {emp_count} employees. Clear and re-import? (yes/no): ")
            if response.lower() != 'yes':
                print("Migration cancelled")
                return False

            # Clear existing data
            print("\nClearing existing data...")
            cursor.execute("TRUNCATE TABLE EmployeeProjects CASCADE")
            cursor.execute("TRUNCATE TABLE Projects RESTART IDENTITY CASCADE")
            cursor.execute("TRUNCATE TABLE Employees RESTART IDENTITY CASCADE")
            conn.commit()
            print("  ✓ Existing data cleared")

        # Import Employees
        print("\nImporting employees...")
        employee_count = 0
        if data['employees']:
            for emp in data['employees']:
                if emp['hire_date'] is None:
                    print(
                        f"  ⚠️  Skipping employee {emp.get('email')} - invalid hire date")
                    continue

                try:
                    cursor.execute("""
                        INSERT INTO Employees (first_name, last_name, email, hire_date, department)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (emp['first_name'], emp['last_name'], emp['email'],
                          emp['hire_date'], emp['department']))
                    employee_count += 1
                except Exception as e:
                    print(
                        f"  ⚠️  Could not import employee {emp.get('email')}: {e}")

            conn.commit()
            print(f"  ✓ Imported {employee_count} employees")

        # Import Projects
        print("Importing projects...")
        project_count = 0
        if data['projects']:
            for proj in data['projects']:
                try:
                    cursor.execute("""
                        INSERT INTO Projects (project_name, start_date, end_date, status)
                        VALUES (%s, %s, %s, %s)
                    """, (proj['project_name'], proj['start_date'],
                          proj['end_date'], proj.get('status', 'Planning')))
                    project_count += 1
                except Exception as e:
                    print(
                        f"  ⚠️  Could not import project {proj.get('project_name')}: {e}")

            conn.commit()
            print(f"  ✓ Imported {project_count} projects")

        # Import EmployeeProjects
        print("Importing employee-project assignments...")
        assignment_count = 0
        if data['employee_projects']:
            for assign in data['employee_projects']:
                try:
                    cursor.execute("""
                        INSERT INTO EmployeeProjects (employee_id, project_id, role, assignment_date)
                        VALUES (%s, %s, %s, %s)
                    """, (assign['employee_id'], assign['project_id'],
                          assign['role'], assign['assignment_date']))
                    assignment_count += 1
                except Exception as e:
                    print(f"  ⚠️  Could not import assignment: {e}")

            conn.commit()
            print(f"  ✓ Imported {assignment_count} assignments")

        # Verify import
        print("\nVerifying import...")
        cursor.execute("SELECT COUNT(*) FROM Employees")
        final_emp_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Projects")
        final_proj_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM EmployeeProjects")
        final_assign_count = cursor.fetchone()[0]

        print(f"  ✓ PostgreSQL now has:")
        print(f"    - {final_emp_count} employees")
        print(f"    - {final_proj_count} projects")
        print(f"    - {final_assign_count} assignments")

        cursor.close()
        return True

    except Exception as e:
        print(f"\n✗ Error importing to PostgreSQL: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
        return False

    finally:
        if conn:
            conn.close()


def main():
    """Run the migration."""
    print("\n" + "="*70)
    print("  SQLite → PostgreSQL Migration Tool (FIXED VERSION)")
    print("="*70)

    # Check for DATABASE_URL
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("\n✗ DATABASE_URL not found in environment variables")
        print("\nPlease add to .env file:")
        print("DATABASE_URL=postgresql://user:password@host:port/database")
        return

    print(f"\n✓ PostgreSQL URL configured")
    print(
        f"  Host: {database_url.split('@')[1].split('/')[0] if '@' in database_url else 'unknown'}")

    # Ask for confirmation
    print("\n⚠️  This will migrate data from SQLite to PostgreSQL")
    print("    - Dates will be converted to YYYY-MM-DD format")
    print("    - Invalid/empty dates will be skipped")
    response = input("Continue? (yes/no): ")

    if response.lower() != 'yes':
        print("Migration cancelled")
        return

    # Export from SQLite
    data = export_from_sqlite('company_db.db')

    if not data:
        print("\n✗ Migration failed: Could not export data")
        return

    # Import to PostgreSQL
    success = import_to_postgres(data, database_url)

    if success:
        print_header("✅ MIGRATION COMPLETE!")
        print("\nNext steps:")
        print("1. Test your application: streamlit run streamlit_app.py")
        print("2. Update Streamlit Cloud secrets with DATABASE_URL")
        print("3. Deploy your application")
    else:
        print_header("✗ MIGRATION FAILED")
        print("\nPlease check the errors above and try again.")


if __name__ == "__main__":
    main()
