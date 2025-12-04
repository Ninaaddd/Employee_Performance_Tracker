"""
Streamlit UI for Employee Performance Tracking System

This is the main application file that creates a web-based interface
for the employee performance tracking system.

Run with: streamlit run streamlit_app.py
"""

from typing import Optional, List, Dict
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date
import pandas as pd
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Employee Performance Tracker",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Import your existing modules (adjust imports based on your structure)
# Assuming these modules exist from your project
try:
    from employee_manager import (
        add_employee,
        get_employee_by_id,
        list_all_employees,
        update_employee,
        delete_employee
    )
    from project_manager import (
        add_project,
        assign_employee_to_project,
        get_projects_for_employee,
        list_all_projects,
        get_employees_for_project
    )
    from performance_reviewer import (
        submit_performance_review,
        get_performance_reviews_for_employee
    )
    from reports import (
        generate_employee_project_report,
        generate_employee_performance_summary
    )
except ImportError:
    st.error("⚠️ Please ensure all manager modules are in the same directory")
    st.stop()


# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 0.3rem;
        margin: 1rem 0;
    }
    .error-message {
        padding: 1rem;
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        border-radius: 0.3rem;
        margin: 1rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'notification' not in st.session_state:
    st.session_state.notification = None
if 'notification_type' not in st.session_state:
    st.session_state.notification_type = None


def show_notification(message: str, type: str = "success"):
    """Display notification message"""
    st.session_state.notification = message
    st.session_state.notification_type = type


def display_notifications():
    """Display stored notifications"""
    if st.session_state.notification:
        if st.session_state.notification_type == "success":
            st.success(st.session_state.notification)
        elif st.session_state.notification_type == "error":
            st.error(st.session_state.notification)
        elif st.session_state.notification_type == "warning":
            st.warning(st.session_state.notification)
        elif st.session_state.notification_type == "info":
            st.info(st.session_state.notification)

        # Clear notification after display
        st.session_state.notification = None
        st.session_state.notification_type = None


def safe_convert_rating(rating):
    """
    Safely convert rating to float for display and calculations.

    Args:
        rating: Rating value (can be int, float, str, or None)

    Returns:
        float: Converted rating value between 0.0 and 5.0
    """
    try:
        if rating is None:
            return 0.0

        # If already a number
        if isinstance(rating, (int, float)):
            return float(rating)

        # If it's a string, clean and convert
        if isinstance(rating, str):
            # Remove whitespace
            rating = rating.strip()
            # Convert to float
            rating_float = float(rating)
            # Ensure it's in valid range
            return max(0.0, min(5.0, rating_float))

        return 0.0

    except (ValueError, TypeError) as e:
        print(f"Warning: Could not convert rating '{rating}': {e}")
        return 0.0


def safe_get_employee_id(value):
    """
    Safely convert employee_id to int.

    Args:
        value: Employee ID (can be int, str, or None)

    Returns:
        int: Employee ID or None if invalid
    """
    try:
        if value is None:
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            # Handle float strings like "3.0"
            return int(float(value.strip()))
        if isinstance(value, float):
            return int(value)
        return None
    except (ValueError, TypeError):
        return None


def safe_date_parse(date_value):
    """
    Safely parse date from various formats.

    Args:
        date_value: Can be str, date, datetime, or None

    Returns:
        date: Python date object
    """
    if date_value is None:
        return date.today()

    if isinstance(date_value, date) and not isinstance(date_value, datetime):
        return date_value

    if isinstance(date_value, datetime):
        return date_value.date()

    if isinstance(date_value, str):
        try:
            return datetime.strptime(date_value, '%Y-%m-%d').date()
        except ValueError:
            try:
                return datetime.strptime(date_value, '%m/%d/%Y').date()
            except ValueError:
                return date.today()

    return date.today()


def safe_datetime_parse(date_value):
    """
    Safely parse datetime from various formats.

    Args:
        date_value: Can be str, date, datetime, or None

    Returns:
        datetime: Python datetime object
    """
    if date_value is None:
        return datetime.now()

    if isinstance(date_value, datetime):
        return date_value

    if isinstance(date_value, date):
        return datetime.combine(date_value, datetime.min.time())

    if isinstance(date_value, str):
        try:
            return datetime.strptime(date_value, '%Y-%m-%d')
        except ValueError:
            try:
                return datetime.strptime(date_value, '%m/%d/%Y')
            except ValueError:
                return datetime.now()

    return datetime.now()


# ============================================================================
# DASHBOARD PAGE
# ============================================================================


def show_dashboard():
    """Display dashboard with key metrics and visualizations"""
    st.markdown('<p class="main-header">📊 Dashboard</p>',
                unsafe_allow_html=True)

    # Get data
    try:
        employees = list_all_employees()
        projects = list_all_projects()

        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="👥 Total Employees",
                value=len(employees) if employees else 0
            )

        with col2:
            st.metric(
                label="📁 Total Projects",
                value=len(projects) if projects else 0
            )

        with col3:
            active_projects = [p for p in projects if p.get(
                'status') == 'Active'] if projects else []
            st.metric(
                label="▶️ Active Projects",
                value=len(active_projects)
            )

        with col4:
            # Count total assignments
            assignment_count = 0
            if employees:
                for emp in employees:
                    emp_projects = get_projects_for_employee(
                        emp['employee_id'])
                    if emp_projects:
                        assignment_count += len(emp_projects)
            st.metric(
                label="🔗 Total Assignments",
                value=assignment_count
            )

        st.divider()

        # Visualizations
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("👥 Employees by Department")
            if employees:
                df = pd.DataFrame(employees)
                dept_counts = df['department'].value_counts().reset_index()
                dept_counts.columns = ['Department', 'Count']

                fig = px.pie(
                    dept_counts,
                    values='Count',
                    names='Department',
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No employee data available")

        with col2:
            st.subheader("📁 Projects by Status")
            if projects:
                df = pd.DataFrame(projects)
                status_counts = df['status'].value_counts().reset_index()
                status_counts.columns = ['Status', 'Count']

                colors = {
                    'Planning': '#FFA500',
                    'Active': '#28a745',
                    'Completed': '#17a2b8',
                    'On Hold': '#dc3545'
                }

                fig = px.bar(
                    status_counts,
                    x='Status',
                    y='Count',
                    color='Status',
                    color_discrete_map=colors
                )
                fig.update_layout(showlegend=False, height=350)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No project data available")

        # Recent Activity
        st.subheader("📋 Recent Employees")
        if employees:
            df = pd.DataFrame(employees)
            df_sorted = df.sort_values('hire_date', ascending=False).head(5)
            st.dataframe(
                df_sorted[['first_name', 'last_name',
                           'email', 'department', 'hire_date']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No employees found")

    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")


# ============================================================================
# EMPLOYEE MANAGEMENT PAGE
# ============================================================================
def show_employee_management():
    """Employee management interface"""
    st.markdown('<p class="main-header">👥 Employee Management</p>',
                unsafe_allow_html=True)

    tabs = st.tabs(["📋 View Employees", "➕ Add Employee",
                   "✏️ Edit Employee", "🔍 Search"])

    # Tab 1: View All Employees
    with tabs[0]:
        st.subheader("All Employees")

        try:
            employees = list_all_employees()

            if employees:
                df = pd.DataFrame(employees)

                # Add filters
                col1, col2 = st.columns(2)
                with col1:
                    dept_filter = st.multiselect(
                        "Filter by Department",
                        options=df['department'].unique(),
                        default=df['department'].unique()
                    )

                with col2:
                    sort_by = st.selectbox(
                        "Sort by",
                        ["first_name", "last_name", "hire_date", "department"]
                    )

                # Apply filters
                df_filtered = df[df['department'].isin(dept_filter)]
                df_filtered = df_filtered.sort_values(sort_by)

                # Display table
                st.dataframe(
                    df_filtered,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "employee_id": "ID",
                        "first_name": "First Name",
                        "last_name": "Last Name",
                        "email": "Email",
                        "hire_date": "Hire Date",
                        "department": "Department"
                    }
                )

                # Export option
                csv = df_filtered.to_csv(index=False)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name=f"employees_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No employees found. Add your first employee!")

        except Exception as e:
            st.error(f"Error loading employees: {str(e)}")

    # Tab 2: Add Employee
    with tabs[1]:
        st.subheader("Add New Employee")

        with st.form("add_employee_form"):
            col1, col2 = st.columns(2)

            with col1:
                first_name = st.text_input("First Name *", max_chars=50)
                last_name = st.text_input("Last Name *", max_chars=50)
                email = st.text_input("Email *", max_chars=100)

            with col2:
                hire_date = st.date_input(
                    "Hire Date *",
                    value=date.today(),
                    max_value=date.today()
                )
                department = st.selectbox(
                    "Department *",
                    ["Engineering", "Sales", "Marketing",
                        "HR", "Finance", "Operations", "Other"]
                )

            submitted = st.form_submit_button(
                "➕ Add Employee", use_container_width=True)

            if submitted:
                if not all([first_name, last_name, email, department]):
                    st.error("Please fill in all required fields")
                else:
                    try:
                        emp_id = add_employee(
                            first_name.strip(),
                            last_name.strip(),
                            email.strip().lower(),
                            hire_date.strftime('%Y-%m-%d'),
                            department
                        )

                        if emp_id:
                            st.success(
                                f"✅ Employee added successfully! ID: {emp_id}")
                            st.balloons()
                        else:
                            st.error(
                                "Failed to add employee. Email might already exist.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    # Tab 3: Edit Employee
    with tabs[2]:
        st.subheader("Edit Employee")

        try:
            employees = list_all_employees()

            if employees:
                # Select employee
                employee_options = {
                    f"{emp['first_name']} {emp['last_name']} ({emp['email']})": emp['employee_id']
                    for emp in employees
                }

                selected = st.selectbox(
                    "Select Employee", list(employee_options.keys()))

                if selected:
                    emp_id = employee_options[selected]
                    employee = get_employee_by_id(emp_id)

                    if employee:
                        with st.form("edit_employee_form"):
                            col1, col2 = st.columns(2)

                            with col1:
                                new_first = st.text_input(
                                    "First Name", value=employee['first_name'])
                                new_last = st.text_input(
                                    "Last Name", value=employee['last_name'])
                                new_email = st.text_input(
                                    "Email", value=employee['email'])

                            with col2:
                                # Use safe date parsing helper
                                hire_date_value = safe_date_parse(
                                    employee['hire_date'])

                            new_hire_date = st.date_input(
                                "Hire Date",
                                value=hire_date_value
                            )
                            new_dept = st.selectbox(
                                "Department",
                                ["Engineering", "Sales", "Marketing",
                                 "HR", "Finance", "Operations", "Other"],
                                index=["Engineering", "Sales", "Marketing", "HR", "Finance", "Operations", "Other"].index(
                                    employee['department']) if employee['department'] in ["Engineering", "Sales", "Marketing", "HR", "Finance", "Operations", "Other"] else 0
                            )

                            col_btn1, col_btn2 = st.columns(2)

                            with col_btn1:
                                update_btn = st.form_submit_button(
                                    "💾 Update Employee", use_container_width=True)

                            with col_btn2:
                                delete_btn = st.form_submit_button(
                                    "🗑️ Delete Employee", use_container_width=True, type="secondary")

                            if update_btn:
                                try:
                                    success = update_employee(
                                        emp_id,
                                        new_first,
                                        new_last,
                                        new_email,
                                        new_hire_date.strftime('%Y-%m-%d'),
                                        new_dept
                                    )
                                    if success:
                                        st.success(
                                            "✅ Employee updated successfully!")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Error updating: {str(e)}")

                            if delete_btn:
                                try:
                                    success = delete_employee(emp_id)
                                    if success:
                                        st.success(
                                            "✅ Employee deleted successfully!")
                                        st.rerun()
                                    else:
                                        st.error(
                                            "Cannot delete: Employee has assignments")
                                except Exception as e:
                                    st.error(f"Error deleting: {str(e)}")
            else:
                st.info("No employees available to edit")

        except Exception as e:
            st.error(f"Error: {str(e)}")

    # Tab 4: Search
    with tabs[3]:
        st.subheader("Search Employees")

        search_term = st.text_input("🔍 Search by name, email, or department")

        if search_term:
            try:
                employees = list_all_employees()

                if employees:
                    df = pd.DataFrame(employees)

                    # Filter
                    mask = (
                        df['first_name'].str.contains(search_term, case=False, na=False) |
                        df['last_name'].str.contains(search_term, case=False, na=False) |
                        df['email'].str.contains(search_term, case=False, na=False) |
                        df['department'].str.contains(
                            search_term, case=False, na=False)
                    )

                    results = df[mask]

                    if not results.empty:
                        st.success(f"Found {len(results)} result(s)")
                        st.dataframe(
                            results, use_container_width=True, hide_index=True)
                    else:
                        st.warning("No results found")
            except Exception as e:
                st.error(f"Search error: {str(e)}")


# ============================================================================
# PROJECT MANAGEMENT PAGE
# ============================================================================
def show_project_management():
    """Project management interface"""
    st.markdown('<p class="main-header">📁 Project Management</p>',
                unsafe_allow_html=True)

    tabs = st.tabs(["📋 View Projects", "➕ Add Project",
                   "🔗 Assign Employees", "👥 Project Teams"])

    # Tab 1: View Projects
    with tabs[0]:
        st.subheader("All Projects")

        try:
            projects = list_all_projects()

            if projects:
                df = pd.DataFrame(projects)

                # Filters
                col1, col2 = st.columns(2)
                with col1:
                    status_filter = st.multiselect(
                        "Filter by Status",
                        options=df['status'].unique(),
                        default=df['status'].unique()
                    )

                with col2:
                    sort_by = st.selectbox(
                        "Sort by",
                        ["project_name", "start_date", "status"]
                    )

                df_filtered = df[df['status'].isin(
                    status_filter)].sort_values(sort_by)

                st.dataframe(
                    df_filtered,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "project_id": "ID",
                        "project_name": "Project Name",
                        "start_date": "Start Date",
                        "end_date": "End Date",
                        "status": "Status"
                    }
                )
            else:
                st.info("No projects found. Create your first project!")

        except Exception as e:
            st.error(f"Error loading projects: {str(e)}")

    # Tab 2: Add Project
    with tabs[1]:
        st.subheader("Create New Project")

        with st.form("add_project_form"):
            project_name = st.text_input("Project Name *", max_chars=100)

            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date *", value=date.today())
            with col2:
                end_date = st.date_input("End Date (Optional)", value=None)

            status = st.selectbox(
                "Status",
                ["Planning", "Active", "On Hold", "Completed"]
            )

            submitted = st.form_submit_button(
                "➕ Create Project", use_container_width=True)

            if submitted:
                if not project_name:
                    st.error("Project name is required")
                else:
                    try:
                        end_date_str = end_date.strftime(
                            '%Y-%m-%d') if end_date else None

                        proj_id = add_project(
                            project_name.strip(),
                            start_date.strftime('%Y-%m-%d'),
                            end_date_str,
                            status
                        )

                        if proj_id:
                            st.success(
                                f"✅ Project created successfully! ID: {proj_id}")
                            st.balloons()
                        else:
                            st.error("Failed to create project")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    # Tab 3: Assign Employees
    with tabs[2]:
        st.subheader("Assign Employee to Project")

        try:
            employees = list_all_employees()
            projects = list_all_projects()

            if employees and projects:
                with st.form("assign_form"):
                    col1, col2 = st.columns(2)

                    with col1:
                        emp_options = {
                            f"{e['first_name']} {e['last_name']}": e['employee_id']
                            for e in employees
                        }
                        selected_emp = st.selectbox(
                            "Select Employee *", list(emp_options.keys()))

                    with col2:
                        proj_options = {
                            p['project_name']: p['project_id']
                            for p in projects
                        }
                        selected_proj = st.selectbox(
                            "Select Project *", list(proj_options.keys()))

                    role = st.text_input(
                        "Role/Position *", placeholder="e.g., Lead Developer, Designer")

                    submitted = st.form_submit_button(
                        "🔗 Assign", use_container_width=True)

                    if submitted:
                        if not role:
                            st.error("Role is required")
                        else:
                            try:
                                success = assign_employee_to_project(
                                    emp_options[selected_emp],
                                    proj_options[selected_proj],
                                    role.strip()
                                )

                                if success:
                                    st.success(
                                        "✅ Employee assigned successfully!")
                                else:
                                    st.error(
                                        "Assignment failed. May already exist.")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
            else:
                st.warning("Please create employees and projects first")

        except Exception as e:
            st.error(f"Error: {str(e)}")

    # Tab 4: Project Teams
    with tabs[3]:
        st.subheader("View Project Teams")

        try:
            projects = list_all_projects()

            if projects:
                proj_options = {p['project_name']: p['project_id']
                                for p in projects}
                selected = st.selectbox(
                    "Select Project", list(proj_options.keys()))

                if selected:
                    proj_id = proj_options[selected]
                    team = get_employees_for_project(proj_id)

                    if team:
                        st.success(f"Team Size: {len(team)}")

                        df = pd.DataFrame(team)
                        st.dataframe(df, use_container_width=True,
                                     hide_index=True)
                    else:
                        st.info("No employees assigned to this project yet")
            else:
                st.info("No projects available")

        except Exception as e:
            st.error(f"Error: {str(e)}")


# ============================================================================
# PERFORMANCE REVIEW PAGE
# ============================================================================
def show_performance_reviews():
    """Performance review interface"""
    st.markdown('<p class="main-header">⭐ Performance Reviews</p>',
                unsafe_allow_html=True)

    tabs = st.tabs(["➕ Submit Review", "📊 View Reviews", "📈 Analytics"])

    # Tab 1: Submit Review
    with tabs[0]:
        st.subheader("Submit Performance Review")

        try:
            employees = list_all_employees()

            if employees:
                with st.form("review_form"):
                    emp_options = {
                        f"{e['first_name']} {e['last_name']} - {e['department']}": e['employee_id']
                        for e in employees
                    }
                    selected_emp = st.selectbox(
                        "Select Employee *", list(emp_options.keys()))

                    col1, col2 = st.columns(2)
                    with col1:
                        review_date = st.date_input(
                            "Review Date *", value=date.today())
                        reviewer_name = st.text_input("Reviewer Name *")

                    with col2:
                        overall_rating = st.slider(
                            "Overall Rating *", 1.0, 5.0, 3.0, 0.5)

                    st.markdown("**Strengths**")
                    strengths = st.text_area(
                        "Enter strengths (one per line)",
                        height=100,
                        placeholder="Leadership\nTechnical Skills\nTeamwork"
                    )

                    st.markdown("**Areas for Improvement**")
                    improvements = st.text_area(
                        "Enter areas for improvement (one per line)",
                        height=100,
                        placeholder="Time Management\nDocumentation"
                    )

                    comments = st.text_area(
                        "Additional Comments",
                        height=100,
                        placeholder="Overall performance feedback..."
                    )

                    goals = st.text_area(
                        "Goals for Next Period",
                        height=100,
                        placeholder="Lead new project\nMentor junior developers"
                    )

                    submitted = st.form_submit_button(
                        "💾 Submit Review", use_container_width=True)

                    if submitted:
                        if not all([selected_emp, reviewer_name]):
                            st.error("Please fill required fields")
                        else:
                            try:
                                emp_id = emp_options[selected_emp]

                                # Process lists
                                strengths_list = [
                                    s.strip() for s in strengths.split('\n') if s.strip()]
                                improvements_list = [
                                    i.strip() for i in improvements.split('\n') if i.strip()]
                                goals_list = [g.strip()
                                              for g in goals.split('\n') if g.strip()]

                                review_id = submit_performance_review(
                                    employee_id=emp_id,
                                    review_date=review_date.strftime(
                                        '%Y-%m-%d'),
                                    reviewer_name=reviewer_name.strip(),
                                    overall_rating=overall_rating,
                                    strengths=strengths_list,
                                    areas_for_improvement=improvements_list,
                                    comments=comments.strip(),
                                    goals_for_next_period=goals_list
                                )

                                if review_id:
                                    st.success(
                                        "✅ Review submitted successfully!")
                                    st.balloons()
                                else:
                                    st.error("Failed to submit review")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
            else:
                st.warning("No employees available. Add employees first.")

        except Exception as e:
            st.error(f"Error: {str(e)}")

    # Tab 2: View Reviews
    with tabs[1]:
        st.subheader("View Employee Reviews")

        try:
            employees = list_all_employees()

            if employees:
                emp_options = {
                    f"{e['first_name']} {e['last_name']}": e['employee_id']
                    for e in employees
                }
                selected = st.selectbox(
                    "Select Employee", list(emp_options.keys()))

                if selected:
                    emp_id = emp_options[selected]
                    reviews = get_performance_reviews_for_employee(emp_id)

                    if reviews:
                        st.success(f"Total Reviews: {len(reviews)}")

                        for i, review in enumerate(reviews, 1):
                            rating = safe_convert_rating(
                                review.get('overall_rating'))
                            rating_stars = "⭐" * int(rating)
                            with st.expander(f"Review {i} - {review.get('review_date','N/A')} {rating_stars} ({rating:.1f})"):
                                col1, col2 = st.columns(2)

                                with col1:
                                    st.markdown(
                                        f"**Reviewer:** {review.get('reviewer_name', 'Unknown')}")
                                    st.markdown(
                                        f"**Date:** {review.get('review_date', 'N/A')}")
                                    st.markdown(
                                        f"**Rating:** {rating:.1f}/5.0 {rating_stars}")

                                with col2:
                                    if review.get('strengths'):
                                        st.markdown("**Strengths:**")
                                        for strength in review['strengths']:
                                            st.markdown(f"- {strength}")

                                if review.get('areas_for_improvement'):
                                    st.markdown("**Areas for Improvement:**")
                                    for area in review['areas_for_improvement']:
                                        st.markdown(f"- {area}")

                                if review.get('comments'):
                                    st.markdown("**Comments:**")
                                    st.markdown(review['comments'])

                                if review.get('goals_for_next_period'):
                                    st.markdown("**Goals:**")
                                    for goal in review['goals_for_next_period']:
                                        st.markdown(f"- {goal}")
                    else:
                        st.info("No reviews found for this employee")
            else:
                st.info("No employees available")

        except Exception as e:
            st.error(f"Error: {str(e)}")

    # Tab 3: Analytics
    with tabs[2]:
        st.subheader("Performance Analytics")

        try:
            employees = list_all_employees()

            if employees:
                # Collect all ratings
                def safe_float_conversion(value, default=0.0):
                    '''Safely convert any value to float.'''
                    try:
                        if value is None:
                            return default
                        if isinstance(value, (int, float)):
                            return float(value)
                        # Handle string conversion
                        return float(str(value).strip())
                    except (ValueError, TypeError):
                        return default

                    def safe_int_conversion(value, default=0):
                        """
                        Safely convert any value to int.
                        Handles int, float, string representations, and None.
                        """
                        try:
                            if value is None:
                                return default
                            if isinstance(value, int):
                                return value
                            if isinstance(value, float):
                                return int(value)
                            # Handle string conversion
                            cleaned = str(value).strip()
                            # Handle float strings like "3.0"
                            return int(float(cleaned))
                        except (ValueError, TypeError):
                            return default
                ratings_data = []

                for emp in employees:
                    reviews = get_performance_reviews_for_employee(
                        emp['employee_id'])
                    if reviews:
                        for review in reviews:
                            rating = safe_float_conversion(
                                review.get('overall_rating', 0))
                            ratings_data.append({
                                'Employee': f"{emp['first_name']} {emp['last_name']}",
                                'Department': emp['department'],
                                'Rating': rating,  # Now properly converted
                                'Date': review.get('review_date', '')
                            })

                if ratings_data:
                    df = pd.DataFrame(ratings_data)

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("**Average Rating by Department**")
                        avg_by_dept = df.groupby('Department')[
                            'Rating'].mean().reset_index()
                        fig = px.bar(
                            avg_by_dept,
                            x='Department',
                            y='Rating',
                            color='Rating',
                            color_continuous_scale='RdYlGn'
                        )
                        fig.update_layout(height=300)
                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        st.markdown("**Rating Distribution**")
                        fig = px.histogram(
                            df,
                            x='Rating',
                            nbins=20,
                            color_discrete_sequence=['#1f77b4']
                        )
                        fig.update_layout(height=300)
                        st.plotly_chart(fig, use_container_width=True)

                    # Top Performers
                    st.markdown("**Top Performers**")
                    top_performers = df.groupby('Employee')['Rating'].mean(
                    ).sort_values(ascending=False).head(5)

                    for idx, (name, rating) in enumerate(top_performers.items(), 1):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"{idx}. {name}")
                        with col2:
                            st.write(f"⭐ {rating:.2f}")
                else:
                    st.info("No performance reviews submitted yet")
            else:
                st.info("No employees available")

        except Exception as e:
            st.error(f"Error loading analytics: {str(e)}")


# ============================================================================
# REPORTS PAGE
# ============================================================================
def show_reports():
    """Reports and analytics interface"""
    st.markdown('<p class="main-header">📊 Reports & Analytics</p>',
                unsafe_allow_html=True)

    tabs = st.tabs(["📋 Employee-Project Report",
                   "⭐ Performance Summary", "📈 Custom Reports"])

    # Tab 1: Employee-Project Report
    with tabs[0]:
        st.subheader("Employee-Project Assignment Report")

        try:
            report_data = generate_employee_project_report()

            if report_data:
                df = pd.DataFrame(report_data)

                # Filters
                col1, col2 = st.columns(2)
                with col1:
                    if 'department' in df.columns:
                        dept_filter = st.multiselect(
                            "Filter by Department",
                            options=df['department'].unique(),
                            default=df['department'].unique()
                        )
                        df = df[df['department'].isin(dept_filter)]

                with col2:
                    if 'project_name' in df.columns:
                        proj_filter = st.multiselect(
                            "Filter by Project",
                            options=df['project_name'].unique(),
                            default=df['project_name'].unique()
                        )
                        df = df[df['project_name'].isin(proj_filter)]

                # Display
                st.dataframe(df, use_container_width=True, hide_index=True)

                # Summary Stats
                st.divider()
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Total Assignments", len(df))

                with col2:
                    unique_employees = df['employee_name'].nunique(
                    ) if 'employee_name' in df.columns else 0
                    st.metric("Employees with Projects", unique_employees)

                with col3:
                    unique_projects = df['project_name'].nunique(
                    ) if 'project_name' in df.columns else 0
                    st.metric("Active Projects", unique_projects)

                # Visualization
                if 'employee_name' in df.columns and 'project_name' in df.columns:
                    st.subheader("Assignment Distribution")
                    assignments_per_emp = df.groupby(
                        'employee_name').size().reset_index(name='count')
                    fig = px.bar(
                        assignments_per_emp.nlargest(10, 'count'),
                        x='employee_name',
                        y='count',
                        title="Top 10 Employees by Project Count"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # Export
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Report as CSV",
                    data=csv,
                    file_name=f"employee_project_report_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No assignment data available")

        except Exception as e:
            st.error(f"Error generating report: {str(e)}")

    # Tab 2: Performance Summary
    with tabs[1]:
        st.subheader("Employee Performance Summary")

        try:
            employees = list_all_employees()

            if employees:
                emp_options = {
                    f"{e['first_name']} {e['last_name']} - {e['department']}": e['employee_id']
                    for e in employees
                }
                selected = st.selectbox(
                    "Select Employee", list(emp_options.keys()))

                if selected:
                    emp_id = emp_options[selected]

                    # Get employee info
                    employee = get_employee_by_id(emp_id)

                    if employee:
                        # Display employee card
                        st.markdown("### Employee Information")
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.markdown(
                                f"**Name:** {employee['first_name']} {employee['last_name']}")
                            st.markdown(f"**Email:** {employee['email']}")

                        with col2:
                            st.markdown(
                                f"**Department:** {employee['department']}")
                            st.markdown(
                                f"**Hire Date:** {employee['hire_date']}")

                        with col3:
                            # Calculate tenure using safe datetime parsing
                            hire_date_obj = safe_datetime_parse(
                                employee['hire_date'])
                            tenure_days = (datetime.now() - hire_date_obj).days
                            tenure_years = tenure_days / 365.25
                            st.markdown(
                                f"**Tenure:** {tenure_years:.1f} years")

                        st.divider()

                        # Get performance reviews
                        reviews = get_performance_reviews_for_employee(emp_id)

                        if reviews:
                            # Calculate metrics
                            ratings = [r.get('overall_rating', 0)
                                       for r in reviews if r.get('overall_rating')]
                            avg_rating = sum(ratings) / \
                                len(ratings) if ratings else 0

                            # Display metrics
                            col1, col2, col3 = st.columns(3)

                            with col1:
                                st.metric("📊 Average Rating",
                                          f"{avg_rating:.2f} / 5.0")

                            with col2:
                                st.metric("📝 Total Reviews", len(reviews))

                            with col3:
                                latest_rating = reviews[0].get(
                                    'overall_rating', 0) if reviews else 0
                                delta = latest_rating - \
                                    avg_rating if len(reviews) > 1 else 0
                                st.metric(
                                    "⭐ Latest Rating", f"{latest_rating:.1f}", delta=f"{delta:+.1f}")

                            # Rating trend chart
                            if len(reviews) > 1:
                                st.subheader("Performance Trend")

                                trend_data = []
                                for review in sorted(reviews, key=lambda x: x.get('review_date', '')):
                                    trend_data.append({
                                        'Date': review.get('review_date', ''),
                                        'Rating': review.get('overall_rating', 0)
                                    })

                                df_trend = pd.DataFrame(trend_data)
                                fig = px.line(
                                    df_trend,
                                    x='Date',
                                    y='Rating',
                                    markers=True,
                                    title="Rating Over Time"
                                )
                                fig.update_layout(yaxis_range=[0, 5])
                                st.plotly_chart(fig, use_container_width=True)

                            # Strengths word cloud (simplified)
                            st.subheader("Top Strengths")
                            all_strengths = []
                            for review in reviews:
                                if review.get('strengths'):
                                    all_strengths.extend(review['strengths'])

                            if all_strengths:
                                from collections import Counter
                                strength_counts = Counter(all_strengths)

                                for strength, count in strength_counts.most_common(5):
                                    st.markdown(
                                        f"- **{strength}** (mentioned {count} time{'s' if count > 1 else ''})")

                            # Areas for improvement
                            st.subheader("Development Areas")
                            all_improvements = []
                            for review in reviews:
                                if review.get('areas_for_improvement'):
                                    all_improvements.extend(
                                        review['areas_for_improvement'])

                            if all_improvements:
                                from collections import Counter
                                improvement_counts = Counter(all_improvements)

                                for area, count in improvement_counts.most_common(3):
                                    st.markdown(
                                        f"- {area} (mentioned {count} time{'s' if count > 1 else ''})")

                            # Projects
                            st.subheader("Current Projects")
                            projects = get_projects_for_employee(emp_id)

                            if projects:
                                df_proj = pd.DataFrame(projects)
                                st.dataframe(
                                    df_proj, use_container_width=True, hide_index=True)
                            else:
                                st.info("No projects assigned")

                        else:
                            st.info(
                                "No performance reviews available for this employee")
            else:
                st.info("No employees available")

        except Exception as e:
            st.error(f"Error loading performance summary: {str(e)}")

    # Tab 3: Custom Reports
    with tabs[2]:
        st.subheader("Custom Report Builder")

        report_type = st.selectbox(
            "Select Report Type",
            [
                "Employees by Department",
                "Projects by Status",
                "Recent Hires (Last 6 Months)",
                "Performance Distribution",
                "Unassigned Employees",
                "Project Workload"
            ]
        )

        if st.button("Generate Report", type="primary"):
            try:
                if report_type == "Employees by Department":
                    employees = list_all_employees()
                    if employees:
                        df = pd.DataFrame(employees)
                        summary = df.groupby(
                            'department').size().reset_index(name='count')

                        st.dataframe(summary, use_container_width=True)

                        fig = px.pie(
                            summary, values='count', names='department', title="Employee Distribution")
                        st.plotly_chart(fig, use_container_width=True)

                elif report_type == "Projects by Status":
                    projects = list_all_projects()
                    if projects:
                        df = pd.DataFrame(projects)
                        summary = df.groupby(
                            'status').size().reset_index(name='count')

                        st.dataframe(summary, use_container_width=True)

                        fig = px.bar(summary, x='status', y='count',
                                     title="Projects by Status")
                        st.plotly_chart(fig, use_container_width=True)

                elif report_type == "Recent Hires (Last 6 Months)":
                    employees = list_all_employees()
                    if employees:
                        df = pd.DataFrame(employees)
                        df['hire_date'] = pd.to_datetime(df['hire_date'])
                        six_months_ago = datetime.now() - pd.Timedelta(days=180)
                        recent = df[df['hire_date'] >= six_months_ago]

                        st.success(f"Found {len(recent)} recent hires")
                        st.dataframe(
                            recent, use_container_width=True, hide_index=True)

                elif report_type == "Performance Distribution":
                    employees = list_all_employees()
                    ratings_data = []

                    for emp in employees:
                        reviews = get_performance_reviews_for_employee(
                            emp['employee_id'])
                        if reviews:
                            for review in reviews:
                                ratings_data.append({
                                    'Rating': review.get('overall_rating', 0)
                                })

                    if ratings_data:
                        df = pd.DataFrame(ratings_data)

                        fig = px.histogram(
                            df,
                            x='Rating',
                            nbins=10,
                            title="Performance Rating Distribution"
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Average Rating",
                                      f"{df['Rating'].mean():.2f}")
                        with col2:
                            st.metric("Median Rating",
                                      f"{df['Rating'].median():.2f}")
                        with col3:
                            st.metric("Total Reviews", len(df))

                elif report_type == "Unassigned Employees":
                    employees = list_all_employees()
                    unassigned = []

                    for emp in employees:
                        projects = get_projects_for_employee(
                            emp['employee_id'])
                        if not projects or len(projects) == 0:
                            unassigned.append(emp)

                    if unassigned:
                        st.warning(
                            f"Found {len(unassigned)} unassigned employees")
                        df = pd.DataFrame(unassigned)
                        st.dataframe(df, use_container_width=True,
                                     hide_index=True)
                    else:
                        st.success("All employees are assigned to projects!")

                elif report_type == "Project Workload":
                    projects = list_all_projects()
                    workload_data = []

                    for proj in projects:
                        team = get_employees_for_project(proj['project_id'])
                        workload_data.append({
                            'Project': proj['project_name'],
                            'Status': proj['status'],
                            'Team Size': len(team) if team else 0
                        })

                    if workload_data:
                        df = pd.DataFrame(workload_data)
                        st.dataframe(df, use_container_width=True,
                                     hide_index=True)

                        fig = px.bar(
                            df,
                            x='Project',
                            y='Team Size',
                            color='Status',
                            title="Project Workload by Team Size"
                        )
                        st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"Error generating report: {str(e)}")


# ============================================================================
# SETTINGS PAGE
# ============================================================================
def show_settings():
    """Settings and configuration page"""
    st.markdown('<p class="main-header">⚙️ Settings</p>',
                unsafe_allow_html=True)

    tabs = st.tabs(["📊 Database Info", "🔧 Maintenance", "📖 About"])

    # Tab 1: Database Info
    with tabs[0]:
        st.subheader("Database Information")

        try:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### SQL Database (Postgres -- neon.tech)")
                employees = list_all_employees()
                projects = list_all_projects()

                st.metric("Total Employees", len(
                    employees) if employees else 0)
                st.metric("Total Projects", len(projects) if projects else 0)

                # Calculate total assignments
                assignment_count = 0
                if employees:
                    for emp in employees:
                        emp_projects = get_projects_for_employee(
                            emp['employee_id'])
                        if emp_projects:
                            assignment_count += len(emp_projects)

                st.metric("Total Assignments", assignment_count)

            with col2:
                st.markdown("### NoSQL Database (MongoDB)")

                # Count total reviews
                total_reviews = 0
                if employees:
                    for emp in employees:
                        reviews = get_performance_reviews_for_employee(
                            emp['employee_id'])
                        if reviews:
                            total_reviews += len(reviews)

                st.metric("Total Reviews", total_reviews)

                # Connection status
                try:
                    # Try to get a review to test connection
                    if employees:
                        test_reviews = get_performance_reviews_for_employee(
                            employees[0]['employee_id'])
                        st.success("✅ MongoDB Connected")
                except:
                    st.error("❌ MongoDB Connection Failed")

        except Exception as e:
            st.error(f"Error loading database info: {str(e)}")

    # Tab 2: Maintenance
    with tabs[1]:
        st.subheader("Database Maintenance")

        st.warning("⚠️ Use these operations carefully!")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Backup")
            if st.button("📥 Backup Database", use_container_width=True):
                try:
                    import shutil
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    shutil.copy2(
                        "company.db", f"company_backup_{timestamp}.db")
                    st.success(
                        f"✅ Backup created: company_backup_{timestamp}.db")
                except Exception as e:
                    st.error(f"Backup failed: {str(e)}")

        with col2:
            st.markdown("### Export")
            if st.button("📤 Export All Data", use_container_width=True):
                try:
                    employees = list_all_employees()
                    projects = list_all_projects()

                    # Create a combined export
                    export_data = {
                        'employees': employees,
                        'projects': projects,
                        'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }

                    import json
                    json_str = json.dumps(export_data, indent=2)

                    st.download_button(
                        label="Download JSON",
                        data=json_str,
                        file_name=f"database_export_{datetime.now().strftime('%Y%m%d')}.json",
                        mime="application/json"
                    )
                except Exception as e:
                    st.error(f"Export failed: {str(e)}")

        st.divider()

        # Danger Zone
        st.markdown("### ⚠️ Danger Zone")

        with st.expander("Clear Sample Data"):
            st.error(
                "This will delete all sample/test data. This action cannot be undone!")

            confirm = st.text_input("Type 'DELETE' to confirm")

            if st.button("🗑️ Delete Sample Data", type="secondary"):
                if confirm == "DELETE":
                    st.warning(
                        "This feature would delete sample data (implement with care)")
                    # Implement actual deletion logic here
                else:
                    st.error("Please type 'DELETE' to confirm")

    # Tab 3: About
    with tabs[2]:
        st.subheader("About This Application")

        st.markdown("""
        ### Employee Performance Tracking System
        
        **Version:** 2.0.0 (Streamlit Edition)
        
        **Description:**
        A comprehensive employee management system that tracks employee information, 
        project assignments, and performance reviews using a hybrid database architecture.
        
        **Technologies:**
        - **Frontend:** Streamlit
        - **Backend:** Python 3.9+
        - **SQL Database:** Postgres (neon.tech)
        - **NoSQL Database:** MongoDB Atlas
        - **Visualization:** Plotly
        - **Testing:** Pytest
        
        **Features:**
        - ✅ Employee Management (CRUD operations)
        - ✅ Project Management
        - ✅ Employee-Project Assignments
        - ✅ Performance Reviews
        - ✅ Analytics & Reporting
        - ✅ Data Visualization
        - ✅ Export Functionality
        
        **Author:** Your Name
        
        **License:** MIT License
        
        **Documentation:** See README.md for detailed setup and usage instructions.
        
        ---
        
        ### System Requirements
        - Python 3.9 or higher
        - 50 MB free disk space
        - Internet connection (for MongoDB Atlas)
        
        ### Support
        For issues or questions, please contact: ninadkulkarni3615@gmail.com
        """)

        st.divider()

        # System info
        import sys
        st.markdown("### System Information")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**Python Version:** {sys.version.split()[0]}")
            st.markdown(f"**Streamlit Version:** {st.__version__}")

        with col2:
            st.markdown(f"**Platform:** {sys.platform}")


# ============================================================================
# MAIN APPLICATION
# ============================================================================
def main():
    """Main application entry point"""

    # Sidebar navigation
    st.sidebar.title("🏢 Navigation")

    page = st.sidebar.radio(
        "Go to",
        [
            "📊 Dashboard",
            "👥 Employees",
            "📁 Projects",
            "⭐ Performance",
            "📊 Reports",
            "⚙️ Settings"
        ]
    )

    st.sidebar.divider()

    # Quick stats in sidebar
    try:
        employees = list_all_employees()
        projects = list_all_projects()

        st.sidebar.markdown("### Quick Stats")
        st.sidebar.metric("Employees", len(employees) if employees else 0)
        st.sidebar.metric("Projects", len(projects) if projects else 0)

    except:
        pass

    st.sidebar.divider()
    st.sidebar.markdown("""
    ### Quick Actions
    - Add new employee
    - Create project
    - Submit review
    """)

    # Display notifications
    display_notifications()

    # Route to appropriate page
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "👥 Employees":
        show_employee_management()
    elif page == "📁 Projects":
        show_project_management()
    elif page == "⭐ Performance":
        show_performance_reviews()
    elif page == "📊 Reports":
        show_reports()
    elif page == "⚙️ Settings":
        show_settings()

    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        Employee Performance Tracking System v2.0 | 
        Built with Streamlit | 
        © 2025
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
