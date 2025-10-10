# 🌍 Air Quality Index (AQI) Forecasting Pipeline

An **end-to-end, serverless machine learning pipeline** that automatically collects, processes, and stores real-time **Air Quality Index (AQI)** and weather data for major cities in **Pakistan** — built using Python, GitHub Actions, and public APIs.

---

## 🧠 Project Overview

This project predicts the **Air Quality Index (AQI)** for the next 3 days using real-time and historical weather & pollution data.

It integrates:
- **Automated data collection**
- **Feature engineering**
- **Model training**
- **Serverless CI/CD**
- **Web-based visualization (Streamlit dashboard planned)**

---

## ⚙️ Tech Stack

| Component | Technology |
|------------|-------------|
| Language | Python |
| ML Libraries | scikit-learn, TensorFlow |
| Feature Store | Hopsworks / Vertex AI |
| Pipeline Orchestration | GitHub Actions (Serverless) |
| APIs | OpenWeather, AQICN, OpenAQ |
| Visualization | Streamlit / Flask |
| Explainability | SHAP |
| Version Control | Git & GitHub |

---

## 🚀 Features

### 🧩 **1. Feature Pipeline Development**
- Fetches raw weather and pollutant data from **OpenWeather** and **AQICN**
- Extracts derived and time-based features (hour, day, AQI change rate)
- Stores processed data in structured CSVs for ML model training

### 🧠 **2. Historical Data Backfill**
- Runs pipelines for past dates to create training datasets
- Aggregates multi-source data into a unified dataset

### ⚙️ **3. Automated CI/CD Pipeline**
- **GitHub Actions** runs this project every hour automatically  
- Fetches latest data using `fetch_api.py`
- Updates the `/data` directory and pushes results to the repo
- Fully **serverless** — no manual execution required

### 📈 **4. Model Training (Upcoming)**
- Trains regression/deep learning models (Random Forest, LSTM)
- Evaluates with RMSE, MAE, and R² metrics
- Automatically retrains daily using updated data

### 💻 **5. Web Dashboard (Upcoming)**
- Real-time AQI prediction dashboard built in **Streamlit**
- Visualizes:
  - Current AQI by city
  - 3-day forecast trends
  - Feature importance via **SHAP**

---

## 🧾 Data Sources

| API | Purpose | Example Endpoint |
|------|----------|------------------|
| **OpenWeather Air Pollution API** | Historical, Current, and Forecasted pollutants | `https://api.openweathermap.org/data/2.5/air_pollution` |
| **AQICN API** | City-level AQI and pollutant forecasts | `https://api.waqi.info/feed/{city}/?token=YOUR_TOKEN` |
| **OpenAQ (optional)** | Global historical air quality data | `https://api.openaq.org/v3/measurements` |

---

---

## ⚡ Automation Pipeline

The **GitHub Actions workflow** (`.github/workflows/aqi_pipeline.yml`) automates this process:

1. ⏰ Triggers hourly or manually
2. 🧱 Spins up a clean Ubuntu VM
3. 🐍 Installs Python 3.12 and dependencies
4. 🔑 Injects API keys from GitHub Secrets
5. ☁ Runs `fetch_api.py` to collect new data
6. 💾 Saves updated CSVs into `/data/`
7. 📤 Commits and pushes new data back to GitHub

---

## 🔑 GitHub Secrets Setup

Go to your repository →  
**Settings → Secrets and variables → Actions → New repository secret**

Add:

| Secret Name | Description |
|--------------|--------------|
| `OPENWEATHER_KEY` | OpenWeather API Key |
| `AQICN_TOKEN` | AQICN API Token |
| `OPENAQ_KEY` | (Optional) OpenAQ API Key |

---

## 🧪 Running Locally

1. Clone the repository:
   ```bash
   git clone https://github.com/Javeria-Motiwala/AQI_Project.git
   cd AQI_Project

