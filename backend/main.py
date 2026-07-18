from pathlib import Path
import math

from fastapi import FastAPI
import joblib
import pandas as pd
from pydantic import BaseModel, Field


app = FastAPI()

MODEL_PATH = Path(__file__).parent / "task2_rf_model.joblib"
model_package = joblib.load(MODEL_PATH)
model = model_package["model"]

LOSS_MEDIAN = 49.73
USERS_MEDIAN = 493675.0


class IncidentInput(BaseModel):
    country: str
    year: int
    attack_type: str
    target_industry: str
    financial_loss_million: float = Field(gt=0)
    affected_users: int = Field(ge=1)
    attack_source: str
    vulnerability_type: str
    defense_mechanism: str


def get_period(year):
    if year <= 2017:
        return "2015-2017"
    if year <= 2020:
        return "2018-2020"
    return "2021-2024"


def make_input_row(data):
    loss_per_user = 0.0
    if data.affected_users > 0:
        loss_per_user = data.financial_loss_million * 1000000 / data.affected_users

    return {
        "Year": data.year,
        "Financial_Loss_in_Million_$": data.financial_loss_million,
        "Number_of_Affected_Users": data.affected_users,
        "loss_per_user": loss_per_user,
        "log_affected_users": math.log1p(data.affected_users),
        "log_financial_loss": math.log1p(data.financial_loss_million),
        "high_loss_flag": 1 if data.financial_loss_million >= LOSS_MEDIAN else 0,
        "high_user_impact_flag": 1 if data.affected_users >= USERS_MEDIAN else 0,
        "Country": data.country,
        "Attack_Type": data.attack_type,
        "Target_Industry": data.target_industry,
        "Attack_Source": data.attack_source,
        "Security_Vulnerability_Type": data.vulnerability_type,
        "Defense_Mechanism_Used": data.defense_mechanism,
        "period": get_period(data.year),
    }


@app.get("/")
def home():
    return {"message": "Cybersecurity incident resolution time API"}


@app.post("/predict")
def predict(data: IncidentInput):
    input_df = pd.DataFrame([make_input_row(data)])
    prediction = float(model.predict(input_df)[0])
    prediction = max(0.0, prediction)

    return {
        "predicted_resolution_time_hours": round(prediction, 2),
        "period": get_period(data.year)
    }
