# CYS404 Final Project Part 2

This is my Task 2 web application for the final project. The app uses the output from Part 1 to show a simple cybersecurity incident dashboard and predict incident resolution time.

The system has two parts. The backend is built with FastAPI and deployed on Render. The frontend is built with Streamlit and deployed on Streamlit Cloud.

The flow is simple. The user enters incident details in Streamlit, then Streamlit sends the input to the FastAPI backend. The backend loads the trained model and returns the predicted resolution time.

## Files In This Project

The backend folder contains the API and trained model.

```text
backend/main.py
backend/task2_rf_model.joblib
backend/requirements.txt
backend/render.yaml
```

`backend/main.py` is the FastAPI file. It receives the prediction input and returns the model prediction.

`backend/task2_rf_model.joblib` is the Random Forest model exported from Part 1.

`backend/requirements.txt` contains the Python libraries needed by Render.

`backend/render.yaml` stores the Render deployment settings.

The frontend folder contains the Streamlit page and the clustered dataset used for the dashboard.

```text
frontend/streamlit_app.py
frontend/clustered_cybersecurity_incidents.csv
frontend/requirements.txt
```

`frontend/streamlit_app.py` is the Streamlit dashboard and prediction form.

`frontend/clustered_cybersecurity_incidents.csv` is the clustered dataset exported from Part 1.

`frontend/requirements.txt` contains the Python libraries needed by Streamlit Cloud.

## Backend Deployment

The backend was deployed using Render.

Render settings used:

```text
Service Type: Web Service
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
```

Backend API link:

[https://cys404-final-report.onrender.com](https://cys404-final-report.onrender.com)

The main prediction endpoint used by the Streamlit app is:

```text
/predict
```

## Frontend Deployment

The frontend was deployed using Streamlit Cloud.

Streamlit Cloud settings used:

```text
Repository: wenkaiii/CYS404_Final_Report
Branch: main
Main file path: frontend/streamlit_app.py
```

Streamlit app link:

[https://cys404-task2.streamlit.app/](https://cys404-task2.streamlit.app/)

This is the main link for viewing and using the application.

## What The App Shows

The Overview page shows the incident dataset in a simple dashboard format. It includes risk profile distribution, attack type distribution, average financial loss by year, summary values, and a data preview table.

The Input page is used for prediction. The user fills in the incident information and clicks Predict. The app then displays the predicted incident resolution time in hours.

Prediction inputs used:

- country
- year
- attack type
- target industry
- financial loss
- number of affected users
- attack source
- security vulnerability type
- defense mechanism used

## Example API Input And Output

Example input:

```json
{
  "country": "USA",
  "year": 2024,
  "attack_type": "Ransomware",
  "target_industry": "Healthcare",
  "financial_loss_million": 50,
  "affected_users": 500000,
  "attack_source": "Nation-state",
  "vulnerability_type": "Zero-day",
  "defense_mechanism": "Firewall"
}
```

Example output:

```json
{
  "predicted_resolution_time_hours": 34.74,
  "period": "2021-2024"
}
```

## Render Free Version Note

The backend is deployed using the free version of Render. If nobody uses the API for some time, Render may make the backend inactive.

Because of this, the first prediction request may fail or take longer. If this happens, open the backend link first or wait around 1 minute, then try the prediction again.
