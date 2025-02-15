# Social Media Fatigue Dashboard AI

Social Media Fatigue Dashboard AI leverages machine learning to predict digital fatigue from social media usage. This project integrates a Flask REST API, an ML model trained with scikit-learn, a cloud PostgreSQL database on Render, and interactive visualizations built in Power BI.

---

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Data and Model](#data-and-model)
- [API and Flask Application](#api-and-flask-application)
- [Database Setup (Local & Cloud)](#database-setup-local--cloud)
- [Power BI Dashboard](#power-bi-dashboard)
- [Dynamic Data Refresh (M Query)](#dynamic-data-refresh-m-query)
- [Postman Guide](#postman-guide)
- [Render Deployment Instructions](#render-deployment-instructions)
- [DAX Measures & Calculated Columns](#dax-measures--calculated-columns)
- [Visual Assets](#visual-assets)
- [How to Use](#how-to-use)
- [Links & Contact](#links--contact)

---

## Overview

Social Media Fatigue Dashboard AI is an end-to-end solution that uses AI to predict digital fatigue based on user metrics such as screen time, social media time, and platform usage. The system includes:
- A Flask REST API (with and without local DB logging)
- A machine learning model (trained using scikit-learn)
- Cloud-based database logging (PostgreSQL on Render)
- An interactive Power BI dashboard for real-time visual insights

---

## Project Structure

```
social-media-fatigue-dashboard-ai/
├── app.py                  # Flask API without local DB logging (for Render deployment)
├── appPrev.py              # Flask API with local database connection code (for local testing)
├── config.py               # Database configuration (for PostgreSQL on Render or MySQL locally)
├── db.py                   # Database connection and initialization functions
├── data_export.py          # Script to export prediction logs to CSV for Power BI
├── fatigue_model.pkl       # Trained machine learning model
├── fatigue_prediction_model.pkl
├── fatigue_prediction_modellf.pkl
├── SMMLipynb               # Jupyter Notebook for model training and analysis
├── social_media_data.csv   # Sample dataset
├── dashboard.pbix          # Power BI report file
├── templates/
│   └── index.html          # HTML frontend for the API
├── visual/                 # Visual assets\n│   ├── pic1.png        # Power BI Overview screenshot\n│   ├── pic2.png        # Usage Analysis screenshot\n│   ├── pic3.png        # Fatigue Insights screenshot\n│   ├── pic4.png        # Deep Dive screenshot\n│   ├── pic5.png        # Summary screenshot\n│   ├── database.png    # Database view (pgAdmin/WorkBench)\n│   └── video.mp4       # Demo video\n└── render.yaml           # Render deployment configuration
```

---

## Data and Model

- **Data Source:** `social_media_data.csv`  
  Columns include Age, SocialMediaTime, ScreenTime, PrimaryPlatform, etc.
- **Feature Engineering:**  
  - *TotalEntertainmentTime* = VideoTime + MusicTime + GamingTime  
  - *ScreenTimePerNotification* = ScreenTime / (Notifications + 1)
- **Model Training:**  
  Multiple algorithms (Linear Regression, Decision Tree, Random Forest, Gradient Boosting) were compared without tuning. The best model is saved as `fatigue_model.pkl`.

---

## API and Flask Application

The API is built with Flask and supports two configurations:
- **app.py:** For Render deployment (no local DB logging)
- **appPrev.py:** For local testing with database logging

**API Endpoint:** `/predict`  
**Expected JSON Input:**
```json
{
    "Age": 62,
    "SocialMediaTime": 2.35,
    "ScreenTime": 8.33,
    "PrimaryPlatform": "TikTok"
}
```
**Expected JSON Output:**
```json
{
    "Fatigue Category": "Average",
    "Predicted Fatigue Level": 5.01,
    "Recommendations": [
        "🔅 Reduce daily screen time by 2 hours",
        "Activate screen time management in app settings"
    ]
}
```

---

## Database Setup (Local & Cloud)

### Local MySQL Setup (for testing)
- **config.py (local):**
  ```python
  DB_CONFIG = {
      'host': 'localhost',
      'user': 'root',
      'password': '1978',
      'database': 'social',
      'port': 3310,
      'auth_plugin': 'mysql_native_password'
  }
  ```
- **Initialize Table:**
  Run the following SQL in MySQL Workbench:
  ```sql
  CREATE DATABASE IF NOT EXISTS social;
  USE social;
  CREATE TABLE IF NOT EXISTS predictions (
      id INT AUTO_INCREMENT PRIMARY KEY,
      age INT,
      social_media_time FLOAT,
      screen_time FLOAT,
      platform VARCHAR(50),
      prediction FLOAT,
      category VARCHAR(20),
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
  ```

### Cloud PostgreSQL on Render (Recommended)
- **Render Connection Details:**  
  - Host: `dpg-cunkaeggph6c73eujvqg-a`
  - Port: `5432`
  - Database: `social_4stp`
  - User: `root`
  - Password: *provided by Render*
- **config.py (cloud):**
  ```python
  DB_CONFIG = {
      'host': 'dpg-cunkaeggph6c73eujvqg-a',
      'port': 5432,
      'user': 'root',
      'password': 'dmTVQlqg7dgX7HvvIFGPA3tkoClUv1ZW',
      'database': 'social_4stp'
  }
  ```
- **Initialize Database:**  
  Use `initialize_database()` in `db.py` to create the `predictions` table on Render.

---

## Power BI Dashboard

The Power BI dashboard (dashboard.pbix) includes multiple pages:

1. **Overview Dashboard:**  
   KPI Cards for Total Social Media Time, Average Screen Time, Predicted Fatigue Level, Fatigue Category; Line Chart (Fatigue Level vs. Age); Bar Chart (Platform Usage); Pie Chart (Fatigue Distribution).

2. **Detailed Social Media Usage:**  
   Visual breakdown of usage by platform, age group, and content type.

3. **Fatigue Insights:**  
   Trend analysis, scatter plots, and detailed fatigue predictions.

4. **Deep Dive into Platforms:**  
   Interactive filtering using platform icons (clicking on an icon filters visuals for that platform).

5. **Summary & Recommendations:**  
   An executive summary of key findings and actionable recommendations.

### **Dynamic Data Refresh (M Query)**
```m
let
    timeStamp = Number.ToText(Number.From(DateTime.LocalNow())),
    url = "https://social-media-fatigue-dashboard-ai.onrender.com/predict?t=" & timeStamp,
    requestBody = [
        Age = paramAge,
        SocialMediaTime = paramSocialMediaTime,
        ScreenTime = paramScreenTime,
        PrimaryPlatform = paramPlatform
    ],
    bodyBinary = Json.FromValue(requestBody),
    Source = Web.Contents(url, [
        Content = bodyBinary,
        Headers = [#"Content-Type" = "application/json", Accept = "application/json"],
        Timeout = #duration(0, 0, 30, 0)
    ]),
    jsonResponse = Json.Document(Source),
    resultTable = Table.FromRecords({jsonResponse})
in
    resultTable
```
*Create parameters (`paramAge`, `paramSocialMediaTime`, `paramScreenTime`, `paramPlatform`) via Manage Parameters in Power BI.*

### **DAX Measures & Calculated Columns**

**Total Social Media Time:**
```DAX
Total_Social_Media_Time = SUM(social_media_data[SocialMediaTime])
```
**Average Screen Time:**
```DAX
Avg_Screen_Time = AVERAGE(social_media_data[ScreenTime])
```
**Fatigue Category Count:**
```DAX
Fatigue_Category_Count = COUNT(social_media_data[fatigue_category])
```
**Predicted Fatigue Level Average:**
```DAX
Predicted_Fatigue_Level_Avg = AVERAGE(social_media_data[predicted_fatigue_level])
```
**Users With High Fatigue:**
```DAX
Users_With_High_Fatigue = COUNTROWS(FILTER(social_media_data, social_media_data[fatigue_category] = "High"))
```
**Percentage of High Fatigue Users:**
```DAX
Percentage_High_Fatigue = DIVIDE([Users_With_High_Fatigue], COUNTROWS(social_media_data), 0)
```

*Add additional measures as required for your analysis.*

---

## Visual Assets

### **Power BI Dashboard Screenshots (in `visual/` folder)**
- **pic1.png:** Overview Dashboard  
- **pic2.png:** Detailed Social Media Usage  
- **pic3.png:** Fatigue Insights  
- **pic4.png:** Deep Dive into Platforms  
- **pic5.png:** Summary & Recommendations  

### **Database Screenshot**
- **database.png:** Screenshot of the `predictions` table in MySQL Workbench/pgAdmin.

### **HTML Frontend Screenshot**
- **html.png:** Screenshot of the index.html frontend.

### **Demo Video**
- **video.mp4:** A demonstration video of the dashboard and API.

---

## How to Use

1. **Run the Flask API Locally:**  
   ```bash
   python app.py
   ```
2. **Test API via Postman:**  
   Use the `/predict` endpoint with a JSON body (e.g., as shown above) to receive predictions.
3. **Export Data:**  
   Run `python data_export.py` to export the predictions table to `powerbi_data.csv` (if needed).
4. **Open the Power BI Report:**  
   Open `dashboard.pbix` and refresh data using either the CSV export or the dynamic M Query.
5. **Interact with the Dashboard:**  
   Use interactive filters, slicers, and navigation buttons (with icons) to explore data by platform and demographic.

---

## Render Deployment Instructions

1. **Push Code to GitHub:**  
   ```bash
   git init
   git add .
   git commit -m "Initial commit for SocialMedia-Fatigue-Insights project"
   git remote add origin https://github.com/yourusername/social-media-fatigue-dashboard-ai.git
   git push -u origin main
   ```
2. **Deploy on Render:**  
   - Log in to Render and create a new Web Service.  
   - Connect your GitHub repo and select branch `main`.  
   - **Start Command:**  
     ```
     gunicorn --timeout 120 -w 4 -b 0.0.0.0:$PORT app:app
     ```
   - Set environment variables as needed.
3. **Access Your Service:**  
   The public URL (e.g., `https://social-media-fatigue-dashboard-ai.onrender.com`) is provided once deployment is complete.
4. **Database Access:**  
   - Use PGHero or pgAdmin with the Render PostgreSQL connection details provided in your Render dashboard.

---

## Power BI Dashboard Link

For online access, publish your Power BI report to Power BI Service and share the link. For example:  
[View Power BI Dashboard](https://app.powerbi.com/view?r=YOUR_REPORT_LINK)

---

## Postman Guide

- **Endpoint:**  
  `https://social-media-fatigue-dashboard-ai.onrender.com/predict`
- **Method:** POST  
- **Headers:** `Content-Type: application/json`  
- **Sample Request Body:**
  ```json
  {
      "Age": 62,
      "SocialMediaTime": 2.35,
      "ScreenTime": 8.33,
      "PrimaryPlatform": "TikTok"
  }
  ```
- **Expected Response:**
  ```json
  {
      "Fatigue Category": "Average",
      "Predicted Fatigue Level": 5.01,
      "Recommendations": [
          "🔅 Reduce daily screen time by 2 hours",
          "Activate screen time management in app settings"
      ]
  }
  ```

---

## Contact & Links

- **LinkedIn:** [sonikirtan02](https://www.linkedin.com/in/sonikirtan02/)
- **Render Service URL:** [https://social-media-fatigue-dashboard-ai.onrender.com](https://social-media-fatigue-dashboard-ai.onrender.com)
- **Power BI Dashboard:** [View Power BI Dashboard](https://app.powerbi.com/view?r=YOUR_REPORT_LINK)

---

This README provides a comprehensive overview of the project, including details on database setup, API usage, Power BI dashboard, and deployment on Render. Customize the placeholders as needed and ensure your visual assets and links are correctly referenced. 

Feel free to adjust further to meet your project requirements!
```

---

This README.md file includes:
- A clear project title.
- Table of contents.
- Detailed sections covering project structure, data/model, API, database setup, Power BI dashboard (with dynamic M query and DAX measures), visual asset links (with placeholders for images and video), instructions for using Postman, Render deployment steps, and contact details.
- A Power BI dashboard link placeholder.
- It does not include hackathon info, and includes only one LinkedIn link as requested.

