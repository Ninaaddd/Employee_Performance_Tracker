import sys
from employee_manager import add_employee, get_employee_by_id
from project_manager import add_project, assign_employee_to_project, get_projects_for_employee
from performance_reviewer import submit_performance_review, get_performance_reviews_for_employee
from reports import generate_employee_project_report, generate_employee_performance_summary
from db_connections import get_sqlite_connection, get_mongo_db_collection, get_sql_connection


def get_conn():
    conn = get_sql_connection()
    conn1 = get_sqlite_connection()
    if conn is None:
        return None
    else:
        return conn


def get_mongodb_reviews():
    reviews_collection = get_mongo_db_collection()
    if reviews_collection is None:
        return None
    else:
        return reviews_collection


def get_review_input(employee_id):
    print("\n--- Review Details ---")

    review_date = input("Review Date (YYYY-MM-DD, e.g., 2025-10-01): ")
    reviewer_name = input("Reviewer Name: ")
    overall_rating = input("Overall Rating (1.0 to 5.0): ")

    strengths_str = input("Strengths (comma-separated list): ")
    areas_str = input("Areas for Improvement (comma-separated list): ")
    goals_str = input("Goals for Next Period (comma-separated list): ")
    comments = input("General Comments: ")

    strengths = [s.strip() for s in strengths_str.split(',') if s.strip()]
    areas_for_improvement = [a.strip()
                             for a in areas_str.split(',') if a.strip()]
    goals_for_next_period = [g.strip()
                             for g in goals_str.split(',') if g.strip()]

    flexible_data = {}
    print("\n--- Optional/Flexible Fields (Enter blank to skip) ---")
    while True:
        key = input(
            "Enter custom field name (or press Enter to finish): ").strip()
        if not key:
            break
        value = input(f"Enter value for '{key}': ").strip()
        flexible_data[key] = value

    review_data = {
        "employee_id": employee_id,
        "review_date": review_date,
        "reviewer_name": reviewer_name,
        "overall_rating": overall_rating,
        "strengths": strengths,
        "areas_for_improvement": areas_for_improvement,
        "comments": comments,
        "goals_for_next_period": goals_for_next_period,
    }
    review_data.update(flexible_data)

    return review_data


def handle_add_employee():
    conn = get_conn()
    print("\n--- Add New Employee ---")
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    email = input("Email: ")
    hire_date = input("Date of Hiring (YYYY-MM-DD): ")
    department = input("Department: ")

    rowid = add_employee(conn, first_name, last_name,
                         email, hire_date, department)
    if rowid is not None:
        print(f"\nEmployee Added successfully. Employee ID: {rowid}")
    else:
        print("\nEmployee addition failed.")


def handle_add_project():
    conn = get_conn()
    print("\n--- Add New Project ---")
    project_name = input("Project Name: ")
    start_date = input("Start Date (YYYY-MM-DD): ")
    end_date = input("End Date (YYYY-MM-DD): ")
    status = input("Status (Planning, Development, Completion): ")

    rowid = add_project(conn, project_name, start_date,
                        end_date if end_date else None, status)
    if rowid is not None:
        print(f"\nProject Added successfully. Project ID: {rowid}")
    else:
        print("\nProject addition failed.")


def handle_assign_project():
    conn = get_conn()
    print("\n--- Assign Employee to Project ---")
    employee_id = int(input("Enter Employee ID: "))
    project_id = input("Enter Project ID: ")
    role = input("Enter the role for the project: ")

    if get_employee_by_id(conn, employee_id) is None:
        print(f"\nError: Employee with ID {employee_id} not found.")
        return

    if assign_employee_to_project(conn, employee_id, project_id, role):
        print(f"\nEmployee {employee_id} assigned to project {project_id}.")
    else:
        print("\nAssignment failed (Check IDs or foreign key constraints).")


def handle_submit_review():
    conn = get_conn()
    reviews = get_mongodb_reviews()
    print("\n--- Submit Performance Review ---")
    employee_id = int(input("Enter Employee ID for review: "))

    if get_employee_by_id(conn, employee_id) is None:
        print(
            f"\nError: Employee with ID {employee_id} not found in the system.")
        return

    review_data = get_review_input(employee_id)

    if review_data:
        submit_args = {
            "employee_id": review_data.pop("employee_id"),
            "review_date": review_data.pop("review_date"),
            "reviewer_name": review_data.pop("reviewer_name"),
            "overall_rating": review_data.pop("overall_rating"),
            "strengths": review_data.pop("strengths"),
            "areas_for_improvement": review_data.pop("areas_for_improvement"),
            "comments": review_data.pop("comments"),
            "goals_for_next_period": review_data.pop("goals_for_next_period"),
        }

        inserted_id = submit_performance_review(
            reviews,
            **submit_args,
            **review_data
        )
        if inserted_id:
            print(f"\nReview submitted successfully. Mongo ID: {inserted_id}")
        else:
            print("\nReview submission failed.")


def handle_view_projects():
    conn = get_conn()
    print("\n--- View Employee Projects ---")
    employee_id = int(input("Enter Employee ID: "))

    if get_employee_by_id(conn, employee_id) is None:
        print(f"\nError: Employee with ID {employee_id} not found.")
        return

    result = get_project_for_employees(conn, employee_id)
    if result:
        print(f"\nProjects for Employee {employee_id}:")
        for project in result:
            print(
                f"  - {project['project_name']} (Role: {project['role']}, Status: {project['status']})")
    else:
        print(
            f"\nEmployee {employee_id} is not currently assigned to any projects.")


def handle_view_performance():
    conn = get_conn()
    reviews = get_mongodb_reviews()
    print("\n--- View Employee Performance Reviews ---")
    employee_id = int(input("Enter Employee ID: "))

    if get_employee_by_id(conn, employee_id) is None:
        print(f"\nError: Employee with ID {employee_id} not found.")
        return

    emp_performance = get_performance_reviews_for_employee(
        reviews, employee_id)
    if emp_performance:
        print(f"\nPerformance Reviews for Employee {employee_id}:")
        for review in emp_performance:
            print("-" * 40)
            print(f"Review Date: {review.get('review_date', 'N/A')}")
            print(f"Reviewer: {review.get('reviewer_name', 'N/A')}")
            print(f"Rating: {review.get('overall_rating', 'N/A')}")
            print(f"Strengths: {', '.join(review.get('strengths', []))}")
    else:
        print(f"\nNo performance reviews found for Employee {employee_id}.")


def handle_reports():
    conn = get_conn()
    reviews = get_mongodb_reviews()
    print("\n--- Generate Reports ---")
    print("\n[Project Report]")
    generate_employee_project_report(conn)

    print("\n[Performance Summary]")
    employee_id = int(
        input("Enter Employee ID for performance summary (e.g., 1): "))
    if get_employee_by_id(conn, employee_id) is None:
        print(
            f"\nError: Employee with ID {employee_id} not found for report generation.")
    else:
        generate_employee_performance_summary(conn, reviews, employee_id)


def display_menu():
    print("\n" + "=" * 40)
    print("  Employee Performance Tracker Menu")
    print("=" * 40)
    print("1. Add Employee")
    print("2. Add Project")
    print("3. Assign Employee to Project")
    print("4. Submit Performance Review")
    print("5. View Employee Projects")
    print("6. View Employee Performance (Raw Reviews)")
    print("7. Generate Summary Reports")
    print("8. Exit")
    print("-" * 40)


def main():
    menu_actions = {
        1: handle_add_employee,
        2: handle_add_project,
        3: handle_assign_project,
        4: handle_submit_review,
        5: handle_view_projects,
        6: handle_view_performance,
        7: handle_reports,
    }

    while True:
        try:
            display_menu()
            choice = int(input("Enter your choice (1-8): "))

            if choice is None:
                continue
            elif choice < 1 or choice > 8:
                print("Enter a number from 1 to 8!")
                continue
            elif choice == 8:
                print("Exiting application. Goodbye!")
                sys.exit(0)

            action = menu_actions.get(choice)
            if action:
                action()
            else:
                print("Invalid choice. Please enter a number between 1 and 8.")

        except KeyboardInterrupt:
            print("\nExiting application. Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")


if __name__ == '__main__':
    main()
