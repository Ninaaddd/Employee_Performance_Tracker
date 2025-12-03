from db_connections import get_sqlite_connection

def add_project(project_name, start_date, end_date=None, status='Planning'):
    """Add a new project to the database."""
    conn = None
    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO Projects (project_name, start_date, end_date, status)
            VALUES (?, ?, ?, ?)
        """, (project_name, start_date, end_date, status))
        
        conn.commit()
        return cursor.lastrowid
        
    except Exception as e:
        print(f"Error adding project: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()


def list_all_projects():
    """Retrieve all projects from the database."""
    conn = None
    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM Projects ORDER BY project_name")
        
        columns = [description[0] for description in cursor.description]
        projects = []
        
        for row in cursor.fetchall():
            projects.append(dict(zip(columns, row)))
        
        return projects
        
    except Exception as e:
        print(f"Error listing projects: {e}")
        return []
    finally:
        if conn:
            conn.close()


def get_project_by_id(project_id):
    """Get a specific project by ID."""
    conn = None
    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM Projects WHERE project_id=?", (project_id,))
        row = cursor.fetchone()
        
        if row:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))
        return None
        
    except Exception as e:
        print(f"Error getting project: {e}")
        return None
    finally:
        if conn:
            conn.close()


def assign_employee_to_project(employee_id, project_id, role):
    """Assign an employee to a project with a specific role."""
    conn = None
    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        
        # Check if assignment already exists
        cursor.execute("""
            SELECT COUNT(*) FROM EmployeeProjects 
            WHERE employee_id=? AND project_id=?
        """, (employee_id, project_id))
        
        if cursor.fetchone()[0] > 0:
            print("Employee already assigned to this project")
            return False
        
        # Create assignment
        cursor.execute("""
            INSERT INTO EmployeeProjects (employee_id, project_id, role, assignment_date)
            VALUES (?, ?, ?, date('now'))
        """, (employee_id, project_id, role))
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Error assigning employee: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def get_projects_for_employee(employee_id):
    """Get all projects assigned to a specific employee."""
    conn = None
    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                p.project_id,
                p.project_name,
                p.start_date,
                p.end_date,
                p.status,
                ep.role,
                ep.assignment_date
            FROM Projects p
            INNER JOIN EmployeeProjects ep ON p.project_id = ep.project_id
            WHERE ep.employee_id = ?
            ORDER BY p.project_name
        """, (employee_id,))
        
        columns = [description[0] for description in cursor.description]
        projects = []
        
        for row in cursor.fetchall():
            projects.append(dict(zip(columns, row)))
        
        return projects
        
    except Exception as e:
        print(f"Error getting projects for employee: {e}")
        return []
    finally:
        if conn:
            conn.close()


def get_employees_for_project(project_id):
    """Get all employees assigned to a specific project."""
    conn = None
    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                e.employee_id,
                e.first_name,
                e.last_name,
                e.email,
                e.department,
                ep.role,
                ep.assignment_date
            FROM Employees e
            INNER JOIN EmployeeProjects ep ON e.employee_id = ep.employee_id
            WHERE ep.project_id = ?
            ORDER BY e.last_name, e.first_name
        """, (project_id,))
        
        columns = [description[0] for description in cursor.description]
        employees = []
        
        for row in cursor.fetchall():
            employees.append(dict(zip(columns, row)))
        
        return employees
        
    except Exception as e:
        print(f"Error getting employees for project: {e}")
        return []
    finally:
        if conn:
            conn.close()