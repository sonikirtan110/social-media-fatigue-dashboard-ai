
# Social Media Fatigue Dashboard AI


## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Data and Model](#data-and-model)
- [API and Flask Application](#api-and-flask-application)
- [Database Setup (Local & Cloud)](#database-setup)
- [Power BI Dashboard](#power-bi-dashboard)
- [Dynamic Data Refresh (M Query)](#dynamic-data-refresh)
- [Postman Guide](#postman-guide)
- [Render Deployment Instructions](#render-deployment-instructions)
- [DAX Measures & Calculated Columns](#dax-measures--calculated-columns)
- [Visual Assets](#visual-assets)
- [How to Use](#how-to-use)
- [Contact & Links](#contact--links)

---

## Overview

**Social Media Fatigue Dashboard AI** leverages machine learning to predict user fatigue based on social media metrics such as screen time, social media time, and platform usage. The system is built using:
- **Python & Flask**: For creating a REST API that serves predictions.
- **scikit-learn**: To train ML models (Linear Regression, Decision Tree, Random Forest, Gradient Boosting) on historical data.
- **MySQL / PostgreSQL**: For logging prediction history (used locally).
- **Power BI**: For interactive visualization and dynamic reporting.
- **Render**: For cloud deployment of the API.

The project integrates dynamic API outputs (fatigue prediction) with Power BI visuals and uses interactive icons for platform-based filtering.

---

## Project Structure

```
social-media-fatigue-dashboard-ai/
├── app.py                  # Flask API without local DB logging (for Render deployment)
├── appPrev.py              # Flask API with local database connection code
├── config.py               # Database configuration (for PostgreSQL/MySQL)
├── data_export.py          # Script to export DB predictions to CSV for Power BI
├── db.py                   # Database connection and initialization functions
├── fatigue_model.pkl       # Trained machine learning model
├── fatigue_prediction_model.pkl
├── fatigue_prediction_modellf.pkl
├── SMMLipynb               # Jupyter Notebook for model training and analysis
├── social_media_data.csv   # Sample dataset
├── dashboard.pbix          # Power BI report file
├── templates/
│   └── index.html          # HTML frontend
├── visual/                 # Contains visual assets:\n│   ├── pic1.png\n│   ├── pic2.png\n│   ├── pic3.png\n│   ├── pic4.png\n│   ├── pic5.png\n│   └── video.mp4\n└── render.yaml         # Render deployment configuration
```

---

## Data and Model

- **Data Source:** `social_media_data.csv` (includes columns such as Age, SocialMediaTime, ScreenTime, PrimaryPlatform, etc.)
- **Feature Engineering:**  
  - *TotalEntertainmentTime* = VideoTime + MusicTime + GamingTime  
  - *ScreenTimePerNotification* = ScreenTime / (Notifications + 1)
- **Model Training:**  
  We compared several algorithms (Linear Regression, Decision Tree, Random Forest, Gradient Boosting) without hyperparameter tuning. The best model is saved as `fatigue_model.pkl`.

---

## API and Flask Application

Our Flask API is defined in `app.py` (for Render deployment) and `appPrev.py` (for local database connection). The API endpoint `/predict` expects a JSON input such as:
```json
{
    "Age": 62,
    "SocialMediaTime": 2.35,
    "ScreenTime": 8.33,
    "PrimaryPlatform": "TikTok"
}

```
and returns:
```json
{
    "Recommendations": [
        "🔅 Reduce daily screen time by 2 hours",
        "Activate screen time management in app settings"
    ],
    "fatigue_category": "Average",
    "predicted_fatigue_level": 5.01
}
```
The API logs predictions to the database and generates recommendations via the `FatigueAdvisor` class.

---

## Database Setup

### **Local MySQL/PostgreSQL (for Testing)**
- **Local Configuration (config.py):**
  ```python
  DB_CONFIG = {
      'host': 'localhost',
      'user': 'root',
      'password': '1978',
      'database': 'social',
      'port': 3310,  # Adjusted for local MySQL
      'auth_plugin': 'mysql_native_password'
  }
  ```
- **Cloud PostgreSQL on Render:**
  Update `config.py` as:
  ```python
  DB_CONFIG = {
      'host': 'dpg-cunkaeggph6c73eujvqg-a',   # Render internal hostname
      'port': 5432,
      'user': 'root',
      'password': 'dmTVQlqg7dgX7HvvIFGPA3tkoClUv1ZW',
      'database': 'social_4stp'
  }
  ```
- **Database Initialization:**  
  Run `initialize_database()` from `db.py` to create the `predictions` table.
  
- **Accessing the Database:**  
  Use pgAdmin or similar tools. In pgAdmin, create a new server connection with the external hostname (e.g., `dpg-cunkaeggph6c73eujvqg-a.render.com`), port `5432`, username `root`, and your password.

---

## Power BI Dashboard

### **Dashboard Overview**
The Power BI dashboard (dashboard.pbix) is split into multiple pages:
1. **Overview Dashboard:**  
   - KPI Cards for Total Social Media Time, Average Screen Time, Predicted Fatigue Level, and Fatigue Category.  
   - A Line Chart for Fatigue Level vs. Age, Bar Chart for Platform Usage, and a Pie Chart for Fatigue Distribution.
2. **Detailed Social Media Usage:**  
   - Visualizations showing usage by platform, age group, and more.
3. **Fatigue Insights:**  
   - Trend analysis, scatter plots, and detailed fatigue predictions.
4. **Deep Dive into Platforms:**  
   - Interactive platform filtering using clickable icons (e.g., Facebook, Instagram, TikTok).
5. **Summary & Recommendations:**  
   - An executive summary slide with key findings and recommendations.

### **Interactive Elements**
- **Navigation Menu:**  
  A top/bottom menu with icons (stored in the `visual/` folder as pic1.png, pic2.png, etc.) allows filtering by platform.
- **Dynamic M Query:**  
  The dashboard includes a dynamic M query (provided in the repo) that refreshes prediction data from the API.

### **DAX Measures (All DAX included in this document)**
- **Total_Social_Media_Time:**  
  ```DAX
  Total_Social_Media_Time = SUM(social_media_data[SocialMediaTime])
  ```
- **Avg_Screen_Time:**  
  ```DAX
  Avg_Screen_Time = AVERAGE(social_media_data[ScreenTime])
  ```
- **Fatigue_Category_Count:**  
  ```DAX
  Fatigue_Category_Count = COUNT(social_media_data[fatigue_category])
  ```
- **Predicted_Fatigue_Level_Avg:**  
  ```DAX
  Predicted_Fatigue_Level_Avg = AVERAGE(social_media_data[predicted_fatigue_level])
  ```
- **Additional DAX Measures** for other pages are available in the project documentation.

---

## Dynamic Data Refresh (M Query)

Below is the M Query used to dynamically fetch API data:

```m
let
    url = "https://social-media-fatigue-dashboard-ai.onrender.com/predict",
    timeStamp = Number.ToText(Number.From(DateTime.LocalNow())),
    fullUrl = url & "?t=" & timeStamp,
    Source = Web.Contents(fullUrl, [
        Headers = [
            #"Content-Type" = "application/json",
            Accept = "application/json"
        ],
        Timeout = #duration(0, 0, 30, 0)
    ]),
    jsonResponse = Json.Document(Source),
    resultTable = Table.FromRecords({jsonResponse})
in
    resultTable
```

*This query is used in Power BI to ensure the API is called freshly each time.*

---

## Render Deployment Instructions

1. **Push Code to GitHub:**  
   - Initialize your repository and push all files.
   - Recommended repo name: **social-media-fatigue-dashboard-ai** for search optimization.
2. **Deploy on Render:**
   - Go to Render Dashboard and click **New → Web Service**.
   - Connect your GitHub repository and select the branch.
   - **Start Command:**  
     ```bash
     gunicorn --timeout 120 -w 4 -b 0.0.0.0:$PORT app:app
     ```
   - Configure environment variables (if needed) for DB credentials.
3. **Test API Endpoint:**  
   - Use Postman to send a POST request to `https://social-media-fatigue-dashboard-ai.onrender.com/predict` with your sample JSON input.
4. **Set Up Database Monitoring with PGHero:**  
   - Render provides PGHero for PostgreSQL. Click the PGHero link in your Render database dashboard to monitor queries, space, and performance.

---

## Postman Guide

1. **Test Your API:**  
   - Set the method to POST.
   - Use the URL:  
     ```
     https://social-media-fatigue-dashboard-ai.onrender.com/predict
     ```
   - Use the following JSON body:
     ```json
     {
        "Age": 62,
        "SocialMediaTime": 2.35,
        "ScreenTime": 8.33,
        "PrimaryPlatform": "TikTok"
     }  
     ```
3. **Expected Response:**
   ```json
   {
    "Recommendations": [
        "🔅 Reduce daily screen time by 2 hours",
        "Activate screen time management in app settings"
    ],
    "fatigue_category": "Average",
    "predicted_fatigue_level": 5.01
}
   ```
3. **Troubleshooting:**  
   - If the response is not as expected, check your logs on Render.

---

## Visual Assets

Place the following assets in the `visual/` folder:
- **visual/pic1.png** – Power BI overview screenshot
- **pic2.png** – Platform-wise analysis visual
- **pic3.png** – Fatigue insights visual
- **pic4.png** – Deep dive into platforms (with interactive icons)
- **pic5.png** – Database view showing predictions (from pgAdmin or phpMyAdmin)
- **video.mp4** – A short demo video explaining the dashboard and API

---

## How to Use

1. **Run the API Locally for Testing:**  
   ```bash
   python app.py
   ```
2. **Export Data to CSV:**  
   Run `python data_export.py` to export predictions from the database.
3. **Open the Power BI Report (dashboard.pbix):**  
   - Connect to the exported CSV or use the dynamic M query to pull real-time API data.
4. **Interact with the Dashboard:**  
   - Use the navigation menu and interactive icons to filter by platform.
   - View KPIs, trend charts, and detailed analyses.

---

## Contact & Links

- **LinkedIn:** [https://www.linkedin.com/in/sonikirtan02/](https://www.linkedin.com/in/sonikirtan02/)
- **Project URL on Render:** [https://social-media-fatigue-dashboard-ai.onrender.com](https://social-media-fatigue-dashboard-ai.onrender.com)

---



---

Feel free to adjust the content as necessary for your presentation. This README is structured to guide users, developers, and mentors through every component of your project—from data ingestion to dashboard visualization and deployment on Render.
