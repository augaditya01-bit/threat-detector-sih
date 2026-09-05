"""
STEP 4: Live visualization dashboard.

Reads alerts.jsonl (written by 3_stream_and_detect.py) and displays
it as a live-updating webpage: a table of recent alerts, a count per
threat type, and a timeline chart.

Run this file FOURTH, using the special command:
    streamlit run 4_dashboard.py

Do NOT run it with plain "python3 4_dashboard.py" -- Streamlit apps
need to be launched through the streamlit command so it can serve
the webpage correctly.

For the live effect, run 3_stream_and_detect.py in one terminal
window WHILE this dashboard is open in another -- you'll watch
alerts appear on screen as they're generated, simulating a real
Security Operations Center (SOC) screen.
"""

import json
import time
import pandas as pd
import streamlit as st

ALERTS_FILE = "alerts.jsonl"
REFRESH_SECONDS = 1

st.set_page_config(page_title="Cyber Threat Detection Dashboard", layout="wide")
st.title("🛡️ AI-Based Cyber Threat Detection — Live Dashboard")
st.caption("Unidirectional traffic monitoring | Read-only ingest simulation")

def load_alerts():
    rows = []
    try:
        with open(ALERTS_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    except FileNotFoundError:
        pass
    return pd.DataFrame(rows)

placeholder = st.empty()

while True:
    df = load_alerts()

    with placeholder.container():
        if df.empty:
            st.info("No alerts yet. Run `python3 3_stream_and_detect.py` in another terminal to start generating traffic and alerts.")
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Alerts", len(df))
            col2.metric("Threat Types Seen", df["threat_class"].nunique())
            col3.metric("Avg Confidence", f"{df['confidence'].mean():.2f}")

            st.subheader("Alerts Over Time by Threat Type")
            counts_over_time = df.groupby("threat_class").size()
            st.bar_chart(counts_over_time)

            st.subheader("Recent Alerts (most recent first)")
            display_df = df.sort_values("flow_id", ascending=False).head(25)
            st.dataframe(
                display_df[["timestamp", "flow_id", "threat_class", "confidence"]],
                width="stretch",
            )

            st.subheader("Inspect Evidence for a Specific Alert")
            selected_flow = st.selectbox("Choose a flow_id to inspect:", display_df["flow_id"].tolist())
            selected_row = df[df["flow_id"] == selected_flow].iloc[0]
            st.json(selected_row["evidence"])

    time.sleep(REFRESH_SECONDS)
    st.rerun()