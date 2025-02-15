# SocialMedia-Fatigue-Insights

SocialMedia-Fatigue-Insights is an AI-driven interactive dashboard that analyzes social media usage and predicts digital fatigue. The project integrates a machine learning model, a Flask REST API, and Power BI for visualization. Data is stored locally in MySQL (viewable via MySQL Workbench), while the API is deployed on Render. This repository includes the code for the REST API, ML model, and instructions for deploying and connecting data sources.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [File Structure](#file-structure)
- [Installation & Setup](#installation--setup)
  - [Local Database Setup](#local-database-setup)
  - [Deploying on Render](#deploying-on-render)
- [API Usage](#api-usage)
  - [Postman Guide](#postman-guide)
- [Power BI Dashboard](#power-bi-dashboard)
  - [Dynamic M Query](#dynamic-m-query)
  - [DAX Measures](#dax-measures)
- [Visuals](#visuals)
  - [Power BI Images](#power-bi-images)
  - [Database Screenshot](#database-screenshot)
  - [HTML Frontend Screenshot](#html-frontend-screenshot)
  - [Demo Video](#demo-video)
- [Presentation Guide](#presentation-guide)
- [Links](#links)

---

## Overview

**SocialMedia-Fatigue-Insights** leverages machine learning to predict digital fatigue based on social media usage. The solution is composed of:
- A **Flask REST API** that accepts JSON input (e.g., Age, SocialMediaTime, ScreenTime, PrimaryPlatform) and returns a predicted fatigue level and category.
- A machine learning model (trained using scikit-learn) that is saved as a `.pkl` file.
- A local **MySQL database** for logging predictions (viewable in MySQL Workbench).
- A **Power BI dashboard** that visualizes key metrics, trends, and insights.

---

## Features

- **Real-Time Predictions:** Input data via Postman triggers fatigue predictions.
- **Database Logging:** All predictions are stored in a local MySQL database.
- **Interactive Dashboard:** Power BI dashboard with multiple pages including Overview, Usage Analysis, Fatigue Trends, and Summary.
- **Dynamic Filtering:** Interactive icons allow filtering by platform (e.g., TikTok, Instagram, YouTube, Facebook).
- **AI-Powered Recommendations:** The system provides recommendations based on predicted fatigue levels.

---

## File Structure

```
SocialMedia-Fatigue-Insights/
├── app.py                # Flask API (without database code for public API usage)
├── appPrev.py            # Flask API with local database connection code (for development)
├── config.py             # Database configuration (for PostgreSQL or MySQL as required)
├── db.py                 # Database connection and initialization functions
├── data_export.py        # Exports prediction logs to CSV for Power BI
├── fatigue_model.pkl     # Trained ML model file
├── fatigue_prediction_model.pkl  # Alternate ML model file (if provided)
├── SMMLipynb             # Jupyter Notebook for ML experiments
├── social_media_data.csv # Sample dataset
├── dashboard.pbix        # Power BI report file
├── visual/               # Contains visual assets:\n│   ├── pic.png\n│   ├── pic2.png\n│   ├── pic3.png\n│   ├── pic4.png\n│   ├── pic5.png\n│   ├── database.png\n│   └── video.mp4\n└── templates/\n    └── index.html    # HTML frontend for the API
```

---

## Installation & Setup

### Local Database Setup

1. **Install MySQL Server** on your local machine and open MySQL Workbench.
2. **Create the Database:**
   - Open MySQL Workbench and run the following SQL commands:
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
3. **Update `config.py`:**
   ```python
   # config.py
   DB_CONFIG = {
       'host': 'localhost',
       'user': 'root',
       'password': '1978',
       'database': 'social',
       'port': 3310,  # Ensure your MySQL Workbench is configured on this port
       'auth_plugin': 'mysql_native_password'
   }
   ```

### Deploying on Render

1. **Push Your Code to GitHub:**
   - Initialize Git, commit your files, and push to your repository (e.g., `SocialMedia-Fatigue-Insights`).
   
2. **Create a New Web Service on Render:**
   - Log in to [Render](https://dashboard.render.com/).
   - Click **New → Web Service** and connect your GitHub repo.
   - Set the **Start Command** (e.g., using Gunicorn):
     ```
     gunicorn --timeout 120 -w 4 -b 0.0.0.0:$PORT app:app
     ```
   - Set environment variables if necessary.
   - Click **Create Web Service**.

3. **Set Up a Scheduled Cron Job (Optional):**
   - If you want to export data automatically, create a Cron Job on Render to run:
     ```
     python data_export.py
     ```
   - Schedule it as needed.

---

## API Usage

### Postman Guide

- **Endpoint:**  
  `https://<your-render-service>.onrender.com/predict`

- **Sample JSON Input:**
  ```json
  {
      "Age": 52,
      "SocialMediaTime": 12.35,
      "ScreenTime": 20.33,
      "PrimaryPlatform": "Instagram"
  }
  ```
- **Expected JSON Output:**
  ```json
  {
      "Fatigue Category": "Average",
      "Predicted Fatigue Level": 5.17,
      "Recommendations": [
          "Enable reminder breaks every 45 minutes of viewing"
      ]
  }
  ```
- **Usage:**
  - Use Postman to test the POST endpoint.
  - Ensure the request header is set to `Content-Type: application/json`.

---

## Power BI Dashboard

### Dynamic M Query (For Real-Time Data)

Use the following M query to call your API dynamically:

```m
let
    timeStamp = Number.ToText(Number.From(DateTime.LocalNow())),
    url = "https://<your-render-service>.onrender.com/predict?t=" & timeStamp,
    requestBody = [
        Age = paramAge,
        SocialMediaTime = paramSocialMediaTime,
        ScreenTime = paramScreenTime,
        PrimaryPlatform = paramPlatform
    ],
    bodyBinary = Json.FromValue(requestBody),
    Source = Web.Contents(url, [
        Content = bodyBinary,
        Headers = [
            #"Content-Type" = "application/json",
            #"Accept" = "application/json"
        ],
        Timeout = #duration(0,0,30,0)
    ]),
    jsonResponse = Json.Document(Source),
    resultTable = Table.FromRecords({jsonResponse})
in
    resultTable
```

*Note:* Create parameters (`paramAge`, `paramSocialMediaTime`, `paramScreenTime`, `paramPlatform`) in Power BI via **Manage Parameters**.

### DAX Measures for Dashboard (Copy these into your Word file)

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
- **Users_With_High_Fatigue:**
  ```DAX
  Users_With_High_Fatigue = COUNTROWS(FILTER(social_media_data, social_media_data[fatigue_category] = "High"))
  ```
- **Percentage_High_Fatigue:**
  ```DAX
  Percentage_High_Fatigue = DIVIDE([Users_With_High_Fatigue], COUNTROWS(social_media_data), 0)
  ```

---

## Visuals (Screenshot & Video Sections)

### Power BI Images
Place your images (located in the `visual/` folder) in the README as follows:
- **pic.png:** Overview dashboard screenshot
- **pic2.png:** Usage analysis page screenshot
- **pic3.png:** Fatigue insights page screenshot
- **pic4.png:** Deep dive page screenshot
- **pic5.png:** Summary page screenshot

### Database Image
- **database.png:** Screenshot from MySQL Workbench showing the `predictions` table.

### HTML Frontend Image
- **html.png:** Screenshot of your index.html frontend.

### Demo Video
- **video.mp4:** Embedded demo video (if possible, link locally or host it; if not, provide a link).

You can display these images in the README by using Markdown image syntax:
```markdown
## Visuals

### Power BI Dashboard Screenshots
![Overview](visual/pic.png)
![Usage Analysis](visual/pic2.png)
![Fatigue Insights](visual/pic3.png)
![Deep Dive](visual/pic4.png)
![Summary](visual/pic5.png)

### Database Screenshot
![Database Predictions](visual/database.png)

### HTML Frontend
![HTML Frontend](visual/html.png)

### Demo Video
[Demo Video](visual/video.mp4)
```

---

## Render Setup Guide

### How to Deploy on Render:
1. **Push your project to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit for SocialMedia-Fatigue-Insights project"
   git remote add origin https://github.com/yourusername/SocialMedia-Fatigue-Insights.git
   git push -u origin main
   ```
2. **Log in to Render** and create a **New Web Service**:
   - Connect your GitHub repository.
   - Set the branch to `main`.
   - In the **Start Command**, use:
     ```
     gunicorn --timeout 120 -w 4 -b 0.0.0.0:$PORT app:app
     ```
3. **Set Environment Variables** (if needed) via the Render Dashboard.
4. **Deploy your service**. Once deployed, Render will provide a public URL (e.g., `https://fatigue-prediction-api.onrender.com`).
5. **Access PGHero** (if enabled) through the Render database dashboard to monitor your PostgreSQL database.

### Connecting to Your Database Locally with pgAdmin:
1. Open pgAdmin on your laptop.
2. Create a new server connection:
   - **Name:** Social Media Fatigue DB
   - **Host name/address:** Use the external hostname provided by Render, e.g., `dpg-cunkaeggph6c73eujvqg-a.render.com`
   - **Port:** `5432`
   - **Maintenance database:** `social_4stp`
   - **Username:** `root`
   - **Password:** (Use your Render database password)
   - **SSL Mode:** Set to `require` if needed.
3. Save and connect. You should now see your database and tables (e.g., `predictions`).

---

## Additional Files

- **social_media_data.csv:** Sample dataset.
- **ML Files:** Jupyter Notebook (SMMLipynb) and model files (`fatigue_model.pkl`, etc.).
- **appPrev.py:** A variant of your API for local testing with database connection.
- **dashboard.pbix:** Your Power BI report file.
- **data_export.py:** Exports prediction logs to CSV for Power BI.

---

## Repository Name Suggestion for SEO

**Recommended Repo Name:** `SocialMedia-Fatigue-Insights`  
This name is descriptive, keyword-rich, and optimized for search.

---

## Links

- **LinkedIn:** [Your LinkedIn Profile](https://www.linkedin.com/in/yourusername)
- **Render Setup Guide:** (See above steps)
- **Postman API Testing Guide:**  
  - Use the `/predict` endpoint with a JSON body:
    ```json
    {
        "Age": 52,
        "SocialMediaTime": 12.35,
        "ScreenTime": 20.33,
        "PrimaryPlatform": "Instagram"
    }
    ```
  - Verify response contains keys: `"Fatigue Category"`, `"Predicted Fatigue Level"`, and `"Recommendations"`.

---

## **Conclusion**

This project, **SocialMedia-Fatigue-Insights**, integrates an ML-based REST API with a local MySQL or PostgreSQL database and a dynamic Power BI dashboard. It enables real-time prediction logging, interactive visualizations, and actionable insights on digital fatigue. Follow the steps above to deploy the project on Render, connect your database with pgAdmin, and view dynamic predictions in Power BI.

You can copy this README.md into your repository and adjust the placeholders (e.g., your LinkedIn URL, image filenames, Render host details) as necessary.
