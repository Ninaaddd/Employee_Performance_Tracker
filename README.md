# 👥 Employee Performance Tracking System

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.29.0-red)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)

**A comprehensive employee management system with hybrid database architecture**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Project Structure](#-project-structure)
- [Database Schema](#-database-schema)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)
- [Contact](#-contact)

---

## 🌟 Overview

The **Employee Performance Tracking System** is a modern web-based application designed to streamline HR operations and employee management. It combines the power of SQL (SQLite) for structured data with NoSQL (MongoDB) for flexible document storage, providing a robust solution for managing employees, projects, and performance reviews.

### 🎯 Purpose

- **Employee Management**: Centralized employee database with complete CRUD operations
- **Project Tracking**: Manage projects and assign team members with specific roles
- **Performance Reviews**: Comprehensive review system with ratings and feedback
- **Analytics & Reporting**: Visual insights into team performance and project allocation
- **Data Export**: Export data for further analysis or record-keeping

### 🏆 Key Highlights

- ✅ **Hybrid Database Architecture** - SQL for relational data, NoSQL for flexible documents
- ✅ **Modern Web UI** - Built with Streamlit for intuitive user experience
- ✅ **Interactive Visualizations** - Plotly charts for data insights
- ✅ **Real-time Updates** - Immediate feedback on all operations
- ✅ **Comprehensive Testing** - 80%+ code coverage with pytest
- ✅ **Production Ready** - Deployment-ready with Docker support

---

## ✨ Features

### 📊 Dashboard

- **Real-time Metrics**: Overview of employees, projects, and assignments
- **Visual Analytics**: Department distribution, project status charts
- **Recent Activity**: Latest employee additions and updates
- **Quick Stats**: Key performance indicators at a glance

### 👥 Employee Management

- **CRUD Operations**: Create, Read, Update, Delete employees
- **Advanced Search**: Find employees by name, email, or department
- **Filtering**: Multi-criteria filtering and sorting
- **Data Export**: Download employee data as CSV
- **Validation**: Email uniqueness and data integrity checks

### 📁 Project Management

- **Project Lifecycle**: Track projects from planning to completion
- **Team Assignment**: Assign employees to projects with roles
- **Status Tracking**: Monitor project status (Planning, Active, On Hold, Completed)
- **Team View**: See all members assigned to each project
- **Timeline Management**: Start and end date tracking

### ⭐ Performance Reviews

- **Comprehensive Reviews**: Rating system (1-5 stars) with detailed feedback
- **Multiple Categories**: Strengths, areas for improvement, goals
- **Review History**: Complete review timeline per employee
- **Analytics Dashboard**: Performance trends and distributions
- **Top Performers**: Identify and recognize high achievers

### 📈 Reports & Analytics

- **Employee-Project Report**: Detailed assignment overview
- **Performance Summary**: Individual employee performance analysis
- **Custom Reports**: Pre-built templates for various insights
- **Data Visualization**: Interactive charts and graphs
- **Export Functionality**: Download reports for external use

### ⚙️ Settings & Maintenance

- **Database Info**: Connection status and statistics
- **Backup System**: One-click database backup
- **Data Export**: JSON export for complete data portability
- **System Information**: Version and configuration details

---

## 🏗️ Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│                   (Streamlit Web UI)                        │
├─────────────────────────────────────────────────────────────┤
│                  Business Logic Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Employee   │  │   Project    │  │ Performance  │     │
│  │   Manager    │  │   Manager    │  │   Reviewer   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
├─────────────────────────────────────────────────────────────┤
│                  Data Access Layer                          │
│                 (db_connections.py)                         │
├─────────────────────────────────────────────────────────────┤
│                   Data Storage Layer                        │
│         ┌──────────────┐         ┌──────────────┐          │
│         │   SQLite     │         │   MongoDB    │          │
│         │  (Employees, │         │   (Reviews)  │          │
│         │   Projects)  │         │              │          │
│         └──────────────┘         └──────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

#### Frontend

- **Streamlit 1.29.0** - Web application framework
- **Plotly 5.18.0** - Interactive data visualization
- **Pandas 2.1.4** - Data manipulation and analysis

#### Backend

- **Python 3.9+** - Core programming language
- **SQLite** - Relational database for structured data
- **MongoDB Atlas** - NoSQL database for flexible documents

#### Testing & Quality

- **Pytest 7.4.3** - Unit testing framework
- **Pytest-cov 4.1.0** - Code coverage measurement
- **Mongomock 4.1.2** - MongoDB mocking for tests

#### Development Tools

- **python-dotenv** - Environment variable management
- **VS Code** - Recommended IDE

---

## 🔧 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9 or higher**

  ```bash
  python --version  # Should show 3.9+
  ```

- **pip** (Python package manager)

  ```bash
  pip --version
  ```

- **Git** (for version control)

  ```bash
  git --version
  ```

- **MongoDB Atlas Account** (free tier available)

  - Sign up at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
  - Or install MongoDB locally

- **50 MB free disk space**

---

## 🚀 Installation

### Option 1: Quick Start (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/employee-performance-tracker.git
cd employee-performance-tracker

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Copy environment template
cp .env.example .env

# 6. Edit .env with your MongoDB credentials
# (Use your favorite text editor)

# 7. Initialize database
python db_connections.py

# 8. Run the application
streamlit run streamlit_app.py
```

### Option 2: Manual Installation

```bash
# Install core dependencies
pip install streamlit==1.29.0
pip install pandas==2.1.4
pip install plotly==5.18.0
pip install pymongo==4.6.0
pip install python-dotenv==1.0.0

# Install testing dependencies (optional)
pip install pytest==7.4.3
pip install pytest-cov==4.1.0
pip install mongomock==4.1.2
```

### Option 3: Docker Installation

```bash
# Build the Docker image
docker build -t employee-tracker .

# Run the container
docker run -p 8501:8501 --env-file .env employee-tracker

# Or use Docker Compose
docker-compose up -d
```

---

## ⚙️ Configuration

### 1. Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration
DB_PATH=./company.db

# MongoDB Configuration
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGO_DB=performance_reviews_db

# Application Settings (Optional)
APP_TITLE=Employee Performance Tracker
DEBUG_MODE=False
```

### 2. MongoDB Atlas Setup

1. **Create Account**: Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. **Create Cluster**: Choose the free tier (M0)
3. **Create Database User**:
   - Username: `admin`
   - Password: Choose a strong password
4. **Whitelist IP**:
   - Add your current IP
   - Or use `0.0.0.0/0` for testing (not recommended for production)
5. **Get Connection String**:
   - Click "Connect" → "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your password
   - Add to `.env` file

### 3. Streamlit Configuration (Optional)

Create `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
port = 8501
headless = false
```

---

## 📁 Project Structure

```
employee-performance-tracker/
│
├── 📄 streamlit_app.py              # Main Streamlit application
├── 📄 db_connections.py             # Database connection management
├── 📄 employee_manager.py           # Employee CRUD operations
├── 📄 project_manager.py            # Project management functions
├── 📄 performance_reviewer.py       # Performance review functions
├── 📄 reports.py                    # Reporting and analytics
│
├── 📁 tests/                        # Test suite
│   ├── test_employee_manager.py
│   ├── test_project_manager.py
│   ├── test_performance_reviewer.py
│   └── conftest.py
│
├── 📁 .streamlit/                   # Streamlit configuration
│   ├── config.toml
│   └── secrets.toml (gitignored)
│
├── 📄 requirements.txt              # Python dependencies
├── 📄 .env                          # Environment variables (gitignored)
├── 📄 .env.example                  # Environment template
├── 📄 .gitignore                    # Git ignore rules
├── 📄 README.md                     # This file
├── 📄 LICENSE                       # MIT License
├── 📄 Dockerfile                    # Docker configuration
├── 📄 docker-compose.yml            # Docker Compose setup
│
│
├── 📁 backups/                      # Database backups (gitignored)
└── 📁 exports/                      # Data exports (gitignored)
```

---

## 🗄️ Database Schema

### SQL Database (SQLite)

#### Employees Table

```sql
CREATE TABLE Employees (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    hire_date DATE NOT NULL,
    department TEXT NOT NULL
);
```

#### Projects Table

```sql
CREATE TABLE Projects (
    project_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    status TEXT DEFAULT 'Planning'
);
```

#### EmployeeProjects Table (Junction)

```sql
CREATE TABLE EmployeeProjects (
    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    assignment_date DATE NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES Employees(employee_id),
    FOREIGN KEY (project_id) REFERENCES Projects(project_id),
    UNIQUE(employee_id, project_id)
);
```

### NoSQL Database (MongoDB)

#### Reviews Collection

```javascript
{
  "_id": ObjectId("..."),
  "employee_id": 1,
  "review_date": "2025-01-15",
  "reviewer_name": "John Manager",
  "overall_rating": 4.5,
  "strengths": ["Leadership", "Technical Skills"],
  "areas_for_improvement": ["Time Management"],
  "comments": "Excellent performance this quarter.",
  "goals_for_next_period": ["Lead new project", "Mentor juniors"]
}
```

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_employee_manager.py

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x
```

### Test Coverage

Current coverage: **84%**

```bash
# Generate coverage report
pytest --cov=. --cov-report term-missing

# View HTML report
pytest --cov=. --cov-report=html
# Then open htmlcov/index.html
```

### Writing Tests

```python
# tests/test_example.py
import pytest
from employee_manager import add_employee

def test_add_employee_success(test_db):
    """Test successful employee addition."""
    emp_id = add_employee("John", "Doe", "john@test.com", "2024-01-01", "IT")
    assert emp_id is not None
    assert emp_id > 0

def test_add_employee_duplicate_email(test_db):
    """Test duplicate email handling."""
    add_employee("John", "Doe", "john@test.com", "2024-01-01", "IT")

    with pytest.raises(Exception):
        add_employee("Jane", "Smith", "john@test.com", "2024-01-02", "HR")
```

---

## 🚢 Deployment

### Streamlit Community Cloud (Free)

1. **Push to GitHub**:

   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Deploy**:

   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your repository
   - Main file: `streamlit_app.py`
   - Click "Deploy"

3. **Add Secrets**:
   - In Streamlit Cloud dashboard
   - Go to "Settings" → "Secrets"
   - Add:
   ```toml
   MONGO_URI = "mongodb+srv://..."
   MONGO_DB = "performance_reviews_db"
   ```

### Heroku

```bash
# Create Procfile
echo "web: sh setup.sh && streamlit run streamlit_app.py" > Procfile

# Create setup.sh
cat > setup.sh << 'EOF'
mkdir -p ~/.streamlit/
echo "\
[general]\n\
email = \"your-email@domain.com\"\n\
" > ~/.streamlit/credentials.toml
echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml
EOF

# Deploy
heroku create your-app-name
git push heroku main
heroku config:set MONGO_URI="mongodb+srv://..."
```

### Docker

```bash
# Build
docker build -t employee-tracker:latest .

# Run
docker run -d \
  -p 8501:8501 \
  -e MONGO_URI="mongodb+srv://..." \
  -e MONGO_DB="performance_reviews_db" \
  --name employee-tracker \
  employee-tracker:latest

# Or use Docker Compose
docker-compose up -d
```

---

## 🔍 Troubleshooting

### Common Issues

#### Issue: "Module not found" error

```bash
# Solution: Ensure all dependencies are installed
pip install -r requirements.txt

# If still failing, try reinstalling
pip install --force-reinstall -r requirements.txt
```

#### Issue: "MongoDB connection timeout"

```python
# Solution 1: Check connection string
# Make sure MONGO_URI in .env is correct

# Solution 2: Whitelist IP in MongoDB Atlas
# Go to Network Access → Add IP Address

# Solution 3: Test connection
from pymongo import MongoClient
client = MongoClient("your_connection_string", serverSelectionTimeoutMS=5000)
client.server_info()  # Should not raise exception
```

#### Issue: "Database is locked" (SQLite)

```python
# Solution: Increase timeout
conn = sqlite3.connect("company.db", timeout=30.0)

# Or enable WAL mode
conn.execute("PRAGMA journal_mode=WAL")
```

#### Issue: "Port 8501 already in use"

```bash
# Solution 1: Kill existing process
# On Windows:
taskkill /F /IM streamlit.exe

# On macOS/Linux:
kill -9 $(lsof -ti:8501)

# Solution 2: Use different port
streamlit run streamlit_app.py --server.port 8502
```

#### Issue: "Invalid literal for int() with base 10"

```python
# Solution: Use type conversion utilities
from type_conversion_utils import safe_convert_rating

# Instead of:
rating = int(review['overall_rating'])

# Use:
rating = safe_convert_rating(review['overall_rating'])
```

### Getting Help

1. **Check Documentation**: Review this README and inline code comments
2. **Search Issues**: Look for similar issues in the GitHub repository
3. **Create Issue**: If problem persists, create a detailed issue report
4. **Contact Support**: Reach out via email (see Contact section)

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

⭐ Star this repo if you find it helpful!

</div>

---

_Last Updated: December 2025_
