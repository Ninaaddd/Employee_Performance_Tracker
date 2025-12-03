# 🚀 Quick Start Guide

Get your Employee Performance Tracking System up and running in 5 minutes!

## ⚡ Super Quick Start (TL;DR)

```bash
# Clone, install, configure, run
git clone https://github.com/yourusername/employee-performance-tracker.git
cd employee-performance-tracker
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your MongoDB credentials
python db_connections.py
streamlit run streamlit_app.py
```

Done! The app opens at `http://localhost:8501`

---

## 📋 Step-by-Step Setup

### Step 1: Prerequisites Check (2 minutes)

```bash
# Check Python version (need 3.9+)
python --version

# Check pip
pip --version

# Check git
git --version
```

**Don't have Python 3.9+?** Download from [python.org](https://www.python.org/downloads/)

### Step 2: Get the Code (1 minute)

```bash
# Option A: Clone from GitHub
git clone https://github.com/Ninaaddd/employee-performance-tracker.git
cd employee-performance-tracker

# Option B: Download ZIP
# Go to GitHub → Click "Code" → "Download ZIP"
# Extract and navigate to folder
```

### Step 3: Setup Virtual Environment (1 minute)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
.\venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

# You should see (venv) in your terminal prompt
```

### Step 4: Install Dependencies (2 minutes)

```bash
# Install all required packages
pip install -r requirements.txt

# This installs:
# - streamlit (web framework)
# - pandas (data handling)
# - plotly (charts)
# - pymongo (MongoDB)
# - and more...
```

### Step 5: Configure MongoDB (5 minutes)

#### Option A: MongoDB Atlas (Cloud - Recommended)

1. **Sign Up**: Go to [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)

2. **Create Free Cluster**:
   - Click "Build a Database"
   - Choose "Free" tier (M0)
   - Select a cloud provider and region
   - Click "Create"

3. **Create Database User**:
   - Go to "Database Access"
   - Click "Add New Database User"
   - Username: `admin`
   - Password: Generate or create a strong password
   - Click "Add User"

4. **Whitelist Your IP**:
   - Go to "Network Access"
   - Click "Add IP Address"
   - Click "Add Current IP Address" (or use `0.0.0.0/0` for testing)
   - Click "Confirm"

5. **Get Connection String**:
   - Go to "Database" → Click "Connect"
   - Choose "Connect your application"
   - Copy the connection string
   - It looks like: `mongodb+srv://admin:<password>@cluster0.xxxxx.mongodb.net/`

6. **Update .env File**:
   ```bash
   # Copy the template
   cp .env.example .env
   
   # Edit .env (use nano, vim, or any text editor)
   nano .env
   
   # Update MONGO_URI with your connection string
   # Replace <password> with your actual password
   MONGO_URI=mongodb+srv://admin:yourpassword@cluster0.xxxxx.mongodb.net/
   ```

#### Option B: Local MongoDB

```bash
# Install MongoDB locally
# macOS:
brew install mongodb-community

# Ubuntu:
sudo apt install mongodb

# Windows: Download from mongodb.com

# Update .env
MONGO_URI=mongodb://localhost:27017/
```

### Step 6: Initialize Database (30 seconds)

```bash
# Create SQLite database and tables
python db_connections.py

# You should see:
# "Database initialized successfully"
```

### Step 7: Run the App (10 seconds)

```bash
# Start Streamlit
streamlit run streamlit_app.py

# Browser will automatically open to http://localhost:8501
```

---

## 🎉 First Use

### Add Your First Employee

1. Click **👥 Employees** in sidebar
2. Go to **Add New** tab
3. Fill in:
   - First Name: John
   - Last Name: Doe
   - Email: john.doe@company.com
   - Hire Date: Select today
   - Department: Engineering
4. Click **➕ Add Employee**
5. Success! 🎊

### Create Your First Project

1. Click **📁 Projects** in sidebar
2. Go to **Add Project** tab
3. Fill in:
   - Project Name: Website Redesign
   - Start Date: Select date
   - Status: Active
4. Click **➕ Create Project**

### Make Your First Assignment

1. Stay in **📁 Projects**
2. Go to **Assign Employees** tab
3. Select Employee: John Doe
4. Select Project: Website Redesign
5. Role: Lead Developer
6. Click **🔗 Assign**

### Submit Your First Review

1. Click **⭐ Performance** in sidebar
2. Go to **Submit Review** tab
3. Select Employee: John Doe
4. Fill in review details
5. Set Rating: 4.5 stars
6. Click **💾 Submit Review**

---

## 🆘 Troubleshooting

### Issue: Can't access MongoDB

```bash
# Check your connection
python -c "from pymongo import MongoClient; client = MongoClient('your_uri'); print(client.server_info())"

# If this fails:
# 1. Check internet connection
# 2. Verify connection string in .env
# 3. Check MongoDB Atlas IP whitelist
# 4. Verify username/password
```

### Issue: Port already in use

```bash
# Kill existing Streamlit process
# Windows:
taskkill /F /IM python.exe /FI "WINDOWTITLE eq streamlit*"

# macOS/Linux:
pkill -f streamlit

# Or use different port:
streamlit run streamlit_app.py --server.port 8502
```

### Issue: Module not found

```bash
# Make sure virtual environment is activated
# You should see (venv) in terminal

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: Database locked

```bash
# Make sure no other app is using company.db
# Close any DB browser tools
# Restart the application
```

---

## 💡 Pro Tips

1. **Add Sample Data**: Run this for demo data
   ```python
   python -c "from helper_functions import create_sample_data; create_sample_data()"
   ```

2. **Auto-refresh**: Streamlit auto-refreshes when you edit code

3. **Clear Cache**: Press `C` in the browser if data seems stuck

4. **Keyboard Shortcuts**: Press `?` in browser to see all shortcuts

5. **Export Data**: Use download buttons to save CSV files

6. **Backup Often**: Go to Settings → Maintenance → Backup Database

---

## 📚 Next Steps

- ✅ **Read Full README**: See [README.md](README.md) for detailed docs
- ✅ **Explore Features**: Try all menu options
- ✅ **Customize**: Edit `.streamlit/config.toml` for themes
- ✅ **Deploy**: Follow deployment guide for production
- ✅ **Contribute**: Submit issues or PRs on GitHub

---

## 🎯 Common Use Cases

### Daily Operations
1. Check Dashboard for overview
2. Add new employees as hired
3. Create projects as approved
4. Assign team members
5. Track project status

### Monthly Reviews
1. Go to Performance section
2. Submit reviews for team
3. View Analytics tab
4. Identify top performers
5. Export reports

### Quarterly Reporting
1. Go to Reports section
2. Generate Employee-Project report
3. Download CSV
4. Create presentations
5. Share with management


---

**Happy Tracking! 🚀**

*Questions? Open an issue on GitHub or email us!*