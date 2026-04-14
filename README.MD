# 🩺 HealthLens AI V1

HealthLens AI V1 is an AI-powered Healthcare Analytics Dashboard that enables users to explore healthcare cost data using natural language queries.

It combines data processing, visualization, and intelligent insights into a single interactive dashboard.

---

## 🚀 Features

### 🧠 AI-Powered Querying
- Supports natural language queries like:
  - "Compare medical and pharmacy cost"
  - "Medical cost trend"
  - "Top 5 costly members"

### 📊 Interactive Dashboard
- KPI Cards (Total Cost, Avg Cost, ED Visits, IP Visits)
- Dynamic charts (auto-adjust based on query)
- Data table with formatted values

### 🎛️ Filters
- Line of Business (LOB)
- Gender

### 💡 Smart Suggestions
- Predefined working queries for guided exploration

### 📈 Intelligent Visualization
- Auto-detects:
  - X-axis
  - Y-axis
  - Chart title
- Handles time-series and categorical data

### 📥 Export Options
- Download results as:
  - Excel (.xlsx)
  - PDF report

---

## 🏗️ Project Structure
HealthLens AI V1/
│
├── app.py # Main UI (Gradio dashboard)
├── engine.py # Query processing logic
├── data_loader.py # Data ingestion & preprocessing
├── data.csv # Sample healthcare dataset
├── requirements.txt # Dependencies
└── README.md


## ⚙️ Tech Stack

- Python
- Pandas
- Plotly
- Gradio
- ReportLab (PDF export)
- OpenPyXL (Excel export)