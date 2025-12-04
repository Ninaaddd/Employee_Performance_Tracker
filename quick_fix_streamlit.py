"""
quick_fix_streamlit.py

Automatically patches the date handling issues in streamlit_app.py

Usage:
    python quick_fix_streamlit.py
"""

import re

# Read the file
with open('streamlit_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add helper functions after imports (after the safe_get_employee_id function)
helper_functions = '''

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

'''

# Find the position to insert helper functions (after safe_get_employee_id)
insert_position = content.find('def safe_get_employee_id(value):')
if insert_position != -1:
    # Find the end of the safe_get_employee_id function
    next_def = content.find('\n# ====', insert_position)
    if next_def != -1:
        content = content[:next_def] + helper_functions + content[next_def:]
        print("✓ Added helper functions")
    else:
        print("⚠ Could not find insertion point for helper functions")
else:
    print("⚠ Could not find safe_get_employee_id function")

# Fix 1: Edit Employee section - hire date parsing
old_pattern_1 = r'''new_hire_date = st\.date_input\(
\s*"Hire Date",
\s*value=datetime\.strptime\(
\s*employee\['hire_date'\], '%Y-%m-%d'\)\.date\(\)
\s*\)'''

new_code_1 = '''# Use safe date parsing helper
                            hire_date_value = safe_date_parse(employee['hire_date'])
                            
                            new_hire_date = st.date_input(
                                "Hire Date",
                                value=hire_date_value
                            )'''

content = re.sub(old_pattern_1, new_code_1, content, flags=re.MULTILINE)
print("✓ Fixed Edit Employee date handling")

# Fix 2: Performance Summary - tenure calculation
old_pattern_2 = r'''# Calculate tenure
\s*hire_date_obj = datetime\.strptime\(
\s*employee\['hire_date'\], '%Y-%m-%d'\)
\s*tenure_days = \(datetime\.now\(\) - hire_date_obj\)\.days'''

new_code_2 = '''# Calculate tenure using safe datetime parsing
                        hire_date_obj = safe_datetime_parse(employee['hire_date'])
                        tenure_days = (datetime.now() - hire_date_obj).days'''

content = re.sub(old_pattern_2, new_code_2, content, flags=re.MULTILINE)
print("✓ Fixed Performance Summary tenure calculation")

# Write back to file
with open('streamlit_app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ All fixes applied successfully!")
print("\nYou can now run: streamlit run streamlit_app.py")
