import sqlite3
from collections import Counter
from db_connections import get_sqlite_connection
from employee_manager import get_employee_by_id
from performance_reviewer import get_performance_reviews_for_employee

def generate_employee_project_report():
    """Generate comprehensive employee-project assignment report."""
    conn = None
    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                e.employee_id,
                e.first_name || ' ' || e.last_name as employee_name,
                e.department,
                p.project_id,
                p.project_name,
                p.status as project_status,
                ep.role,
                ep.assignment_date
            FROM Employees e
            INNER JOIN EmployeeProjects ep ON e.employee_id = ep.employee_id
            INNER JOIN Projects p ON ep.project_id = p.project_id
            ORDER BY e.last_name, e.first_name, p.project_name
        """)
        
        columns = [description[0] for description in cursor.description]
        report_data = []
        
        for row in cursor.fetchall():
            report_data.append(dict(zip(columns, row)))
        
        return report_data
        
    except Exception as e:
        print(f"Error generating report: {e}")
        return []
    finally:
        if conn:
            conn.close()


def generate_employee_performance_summary(employee_id):
    """Generate performance summary for a specific employee."""
    from performance_reviewer import get_performance_reviews_for_employee
    
    # Get employee details
    conn = None
    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM Employees WHERE employee_id=?", (employee_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        columns = [description[0] for description in cursor.description]
        employee = dict(zip(columns, row))
        
        # Get reviews from MongoDB
        reviews = get_performance_reviews_for_employee(employee_id)
        
        # Calculate average rating
        if reviews:
            ratings = [r.get('overall_rating', 0) for r in reviews if r.get('overall_rating')]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
        else:
            avg_rating = 0
        
        return {
            'employee': employee,
            'reviews': reviews,
            'average_rating': avg_rating,
            'review_count': len(reviews)
        }
        
    except Exception as e:
        print(f"Error generating summary: {e}")
        return None
    finally:
        if conn:
            conn.close()
