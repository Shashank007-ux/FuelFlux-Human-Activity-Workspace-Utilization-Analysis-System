import streamlit as st
import pandas as pd

st.title("FuelFlux Workspace Utilization Dashboard")

df = pd.read_csv("output/logs/activity_log.csv")

st.subheader("Raw Activity Log")
st.dataframe(df)

st.subheader("Activity Distribution")
activity_counts = df["Activity"].value_counts()
st.bar_chart(activity_counts)

st.subheader("Per-Person Summary")
summary = df.groupby(["Person_ID", "Activity"]).size().unstack(fill_value=0)
st.dataframe(summary)