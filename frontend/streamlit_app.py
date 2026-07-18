from pathlib import Path
import pandas as pd
import requests
import streamlit as st


st.set_page_config(
    page_title="Cybersecurity Threat Dashboard",
    layout="wide"
)

API_URL = "https://cys404-final-report.onrender.com"

@st.cache_data
def load_data():
    data_path = Path(__file__).parent / "clustered_cybersecurity_incidents.csv"
    return pd.read_csv(data_path)

df = load_data()

st.title("Cybersecurity Threat Dashboard")
st.caption("Cybersecurity incident dashboard and resolution time prediction app.")

st.sidebar.header("Select Data")

selected_profiles = st.sidebar.multiselect(
    "Risk Profile",
    sorted(df["risk_profile_name"].dropna().unique()),
    default=sorted(df["risk_profile_name"].dropna().unique())
)

selected_attacks = st.sidebar.multiselect(
    "Attack Type",
    sorted(df["Attack_Type"].dropna().unique()),
    default=sorted(df["Attack_Type"].dropna().unique())
)

year_min = int(df["Year"].min())
year_max = int(df["Year"].max())

selected_years = st.sidebar.slider(
    "Year Range",
    year_min,
    year_max,
    (year_min, year_max)
)

filtered_df = df[
    df["risk_profile_name"].isin(selected_profiles)
    & df["Attack_Type"].isin(selected_attacks)
    & df["Year"].between(selected_years[0], selected_years[1])
]

if filtered_df.empty:
    st.warning("No data found for the selected filters.")
    st.stop()

overview_tab, input_tab = st.tabs(["Overview", "Input"])

with overview_tab:
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    metric_col1.metric("Incidents", f"{len(filtered_df):,}")
    metric_col2.metric(
        "Average Loss",
        f"${filtered_df['Financial_Loss_in_Million_$'].mean():.2f}M"
    )
    metric_col3.metric(
        "Average Users",
        f"{filtered_df['Number_of_Affected_Users'].mean():,.0f}"
    )
    metric_col4.metric(
        "Average Resolution",
        f"{filtered_df['Incident_Resolution_Time_in_Hours'].mean():.2f}h"
    )

    st.subheader("Risk Profile Overview")

    profile_summary = (
        filtered_df.groupby("risk_profile_name")
        .agg(
            incidents=("risk_profile_name", "count"),
            avg_loss_million=("Financial_Loss_in_Million_$", "mean"),
            avg_affected_users=("Number_of_Affected_Users", "mean"),
            avg_resolution_hours=("Incident_Resolution_Time_in_Hours", "mean"),
            avg_loss_per_user=("loss_per_user", "mean")
        )
        .reset_index()
        .sort_values("incidents", ascending=False)
    )

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.bar_chart(filtered_df["risk_profile_name"].value_counts())

    with chart_col2:
        st.dataframe(
            profile_summary.style.format({
                "avg_loss_million": "{:.2f}",
                "avg_affected_users": "{:,.0f}",
                "avg_resolution_hours": "{:.2f}",
                "avg_loss_per_user": "{:.2f}"
            }),
            use_container_width=True,
            height=260
        )

    st.subheader("Incident Patterns")

    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:
        attack_counts = filtered_df["Attack_Type"].value_counts()
        st.bar_chart(attack_counts)

    with chart_col4:
        loss_by_year = filtered_df.groupby("Year")["Financial_Loss_in_Million_$"].mean()
        st.line_chart(loss_by_year)

    st.subheader("Data Preview")

    display_columns = [
        "Country",
        "Year",
        "Attack_Type",
        "Target_Industry",
        "Financial_Loss_in_Million_$",
        "Number_of_Affected_Users",
        "Incident_Resolution_Time_in_Hours",
        "risk_profile_name"
    ]

    st.dataframe(
        filtered_df[display_columns].sort_values(
            ["Year", "Financial_Loss_in_Million_$"],
            ascending=[False, False]
        ),
        use_container_width=True,
        height=360
    )

with input_tab:
    st.subheader("Predict Incident Resolution Time")

    with st.form("prediction_form"):
        input_col1, input_col2 = st.columns(2)

        with input_col1:
            country = st.selectbox("Country", sorted(df["Country"].dropna().unique()))
            year = st.slider(
                "Incident Year",
                int(df["Year"].min()),
                int(df["Year"].max()),
                2024
            )
            attack_type = st.selectbox(
                "Attack Type",
                sorted(df["Attack_Type"].dropna().unique())
            )
            target_industry = st.selectbox(
                "Target Industry",
                sorted(df["Target_Industry"].dropna().unique())
            )

        with input_col2:
            financial_loss = st.number_input(
                "Financial Loss in Million $",
                min_value=0.01,
                value=50.0,
                step=1.0
            )
            affected_users = st.number_input(
                "Number of Affected Users",
                min_value=1,
                value=500000,
                step=1000
            )
            attack_source = st.selectbox(
                "Attack Source",
                sorted(df["Attack_Source"].dropna().unique())
            )
            vulnerability_type = st.selectbox(
                "Security Vulnerability Type",
                sorted(df["Security_Vulnerability_Type"].dropna().unique())
            )
            defense_mechanism = st.selectbox(
                "Defense Mechanism Used",
                sorted(df["Defense_Mechanism_Used"].dropna().unique())
            )

        submitted = st.form_submit_button("Predict")

    if submitted:
        payload = {
            "country": country,
            "year": year,
            "attack_type": attack_type,
            "target_industry": target_industry,
            "financial_loss_million": financial_loss,
            "affected_users": affected_users,
            "attack_source": attack_source,
            "vulnerability_type": vulnerability_type,
            "defense_mechanism": defense_mechanism,
        }

        try:
            response = requests.post(
                f"{API_URL}/predict",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            st.success(
                f"Predicted Resolution Time: "
                f"{result['predicted_resolution_time_hours']} hours"
            )
        except Exception as error:
            st.error(
                "Prediction request failed. The Render backend may still be starting. "
                "Wait about 1 minute and try again."
            )
            st.write(error)
