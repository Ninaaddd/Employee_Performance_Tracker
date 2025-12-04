from db_connections import get_sqlite_connection, get_sql_connection


def add_employee(first_name, last_name, email, hire_date, department):
    """Add a new employee to the database."""
    conn = None
    try:
        conn = get_sql_connection()
        conn1 = get_sqlite_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO Employees (first_name, last_name, email, hire_date, department) 
            VALUES (%s, %s, %s, %s, %s)
            RETURNING employee_id
            """, (first_name, last_name, email, hire_date, department))
        result = cursor.fetchone()
        conn.commit()
        return result[0] if result else None

    except Exception as e:
        print(f"Error adding employee: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()


def get_employee_by_id(employee_id):
    """Retrieve a single employee by ID."""
    conn = None
    try:
        conn = get_sql_connection()
        conn1 = get_sqlite_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM Employees WHERE employee_id=%s", (employee_id,))
        row = cursor.fetchone()

        if row:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))
        return None

    except Exception as e:
        print(f"Error getting employee: {e}")
        return None
    finally:
        if conn:
            conn.close()


def list_all_employees():
    """Retrieve all employees from the database."""
    conn = None
    try:
        conn = get_sql_connection()
        conn1 = get_sqlite_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM Employees ORDER BY last_name, first_name")

        columns = [description[0] for description in cursor.description]
        employees = []

        for row in cursor.fetchall():
            employees.append(dict(zip(columns, row)))

        return employees

    except Exception as e:
        print(f"Error listing employees: {e}")
        return []
    finally:
        if conn:
            conn.close()


def update_employee(employee_id, first_name, last_name, email, hire_date, department):
    """Update an existing employee's information."""
    conn = None
    try:
        conn = get_sql_connection()
        conn1 = get_sqlite_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE Employees 
            SET first_name=%s, last_name=%s, email=%s, hire_date=%s, department=%s
            WHERE employee_id=%s
        """, (first_name, last_name, email, hire_date, department, employee_id))

        conn.commit()
        return cursor.rowcount > 0

    except Exception as e:
        print(f"Error updating employee: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def delete_employee(employee_id):
    """Delete an employee if they have no project assignments."""
    conn = None
    try:
        conn = get_sql_connection()
        conn1 = get_sqlite_connection()
        cursor = conn.cursor()

        # Check for project assignments
        cursor.execute("""
            SELECT COUNT(*) FROM EmployeeProjects 
            WHERE employee_id=%s
        """, (employee_id,))

        if cursor.fetchone()[0] > 0:
            print("Cannot delete: Employee has project assignments")
            return False

        # Safe to delete
        cursor.execute(
            "DELETE FROM Employees WHERE employee_id=%s", (employee_id,))
        conn.commit()

        return cursor.rowcount > 0

    except Exception as e:
        print(f"Error deleting employee: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()
    """
    Delete an employee if they have no project assignments.
    
    Args:
        employee_id (int): ID of employee to delete
    
    Returns:
        bool: True if deleted, False if employee has assignments or error
    """
    try:
        from db_connections import get_sql_connection

        conn = get_sql_connection()
        cursor = conn.cursor()

        # Check for project assignments
        cursor.execute("""
            SELECT COUNT(*) FROM EmployeeProjects 
            WHERE employee_id=%s
        """, (employee_id,))

        assignment_count = cursor.fetchone()[0]

        if assignment_count > 0:
            print(
                f"Cannot delete: Employee has {assignment_count} project assignment(s)")
            return False

        # Safe to delete
        cursor.execute(
            "DELETE FROM Employees WHERE employee_id=%s", (employee_id,))
        conn.commit()

        return cursor.rowcount > 0

    except Exception as e:
        print(f"Error deleting employee: {e}")
        return False
    finally:
        if conn:
            conn.close()
