import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Power Outage Operations Dashboard", layout="wide", initial_sidebar_state="expanded")

# --- DATA LOADING & CLEANING ---
from datetime import datetime

@st.cache_data
def load_data():
    # Automatically get today's date in YYYY-MM-DD format
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # Dynamically load the files matching today's date
    df_today = pd.read_csv(f"{today_str}_Outages_Today.csv")
    df_5day = pd.read_csv(f"{today_str}_Outages_Last_5_Days.csv")
    
    # Map outage types
    df_today['Type of Outage'] = df_today['Type of Outage'].replace('Power Off By PC', 'Planned Outage')
    df_5day['Type of Outage'] = df_5day['Type of Outage'].replace('Power Off By PC', 'Planned Outage')
    
    # Convert time columns
    time_cols = ['Schedule Created At', 'Start Time', 'End Time', 'Last Updated At']
    for col in time_cols:
        df_today[col] = pd.to_datetime(df_today[col], errors='coerce')
        df_5day[col] = pd.to_datetime(df_5day[col], errors='coerce')
        
    return df_today, df_5day

df_today, df_5day = load_data()

# --- GLOBAL NAVIGATION (SIDEBAR) ---
st.sidebar.header("Global Filters")

# 1. State/Zone Level
zones = df_today['Zone'].dropna().unique()
selected_zone = st.sidebar.selectbox("Select Zone", options=["All Zones"] + list(zones))

# 2. Circle Level
if selected_zone != "All Zones":
    df_today = df_today[df_today['Zone'] == selected_zone]
    df_5day = df_5day[df_5day['Zone'] == selected_zone]

circles = df_today['Circle'].dropna().unique()
selected_circle = st.sidebar.selectbox("Select Circle", options=["All Circles"] + list(circles))

if selected_circle != "All Circles":
    df_today = df_today[df_today['Circle'] == selected_circle]
    df_5day = df_5day[df_5day['Circle'] == selected_circle]

# --- MAIN DASHBOARD LAYOUT ---
st.title("⚡ Power Outage Monitoring Dashboard")
col_today, col_5day = st.columns(2)

# ==========================================
# PART 1: TODAY'S SNAPSHOT (LEFT COLUMN)
# ==========================================
with col_today:
    st.header("🔴 Today's Snapshot")
    
    # KPIs
    active_outages = df_today[df_today['End Time'].isnull()].shape[0]
    total_duration = df_today['Diff in mins'].sum()
    st.metric(label="Active Outages", value=active_outages, delta="Requires Attention", delta_color="inverse")
    
    # 2-Step Drill Down Logic (Division -> S/D -> Feeder)
    st.subheader("Outage Drill-Down")
    
    # Step 1: Select Division
    divisions = df_today['Division'].dropna().unique()
    selected_div = st.selectbox("Step 1: Select Division", options=divisions)
    df_div = df_today[df_today['Division'] == selected_div]
    
    # Step 2: Select S/D
    sub_divisions = df_div['S/D'].dropna().unique()
    selected_sd = st.selectbox("Step 2: Select Sub-Division (S/D)", options=sub_divisions)
    df_sd = df_div[df_div['S/D'] == selected_sd]
    
    # Final Level: Feeder View Chart
    if not df_sd.empty:
        fig_feeder = px.bar(
            df_sd, 
            x='Feeder', 
            y='Diff in mins', 
            color='Type of Outage',
            title=f"Feeder Status for {selected_sd}",
            color_discrete_map={"Unplanned Outage": "red", "Planned Outage": "blue"}
        )
        st.plotly_chart(fig_feeder, use_container_width=True)
    else:
        st.info("No outages recorded for this Sub-Division today.")

    # Top 10 Notorious Feeders (Today)
    st.subheader("Top 10 Notorious Feeders Today")
    top_10_today = df_today.groupby(['Feeder', 'Type of Outage'])['Diff in mins'].sum().reset_index()
    top_10_today = top_10_today.sort_values(by='Diff in mins', ascending=False).head(10)
    st.dataframe(top_10_today, use_container_width=True, hide_index=True)


# ==========================================
# PART 2: 5-DAY RETROSPECTIVE (RIGHT COLUMN)
# ==========================================
with col_5day:
    st.header("🔵 5-Day Retrospective")
    
    # Trend Chart
    st.subheader("5-Day Trend (Duration by Type)")
    df_5day['Date Only'] = df_5day['Start Time'].dt.date
    trend_data = df_5day.groupby(['Date Only', 'Type of Outage'])['Diff in mins'].sum().reset_index()
    
    fig_trend = px.bar(
        trend_data, 
        x='Date Only', 
        y='Diff in mins', 
        color='Type of Outage',
        barmode='group',
        color_discrete_map={"Unplanned Outage": "red", "Planned Outage": "blue"}
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    # The 5-Consecutive-Day Notorious Logic
    st.subheader("⚠️ Critical Alert: 5-Day Consecutive Repeaters")
    
    if not df_5day.empty:
        daily_feeder = df_5day.groupby(['Date Only', 'Circle', 'Division', 'Feeder'])['Diff in mins'].sum().reset_index()
        daily_feeder['Daily Rank'] = daily_feeder.groupby(['Date Only', 'Circle'])['Diff in mins'].rank(method='dense', ascending=False)
        top_daily = daily_feeder[daily_feeder['Daily Rank'] <= 10]
        consecutive_counts = top_daily.groupby(['Circle', 'Division', 'Feeder']).size().reset_index(name='Days in Top 10')
        critical_repeaters = consecutive_counts[consecutive_counts['Days in Top 10'] == 5]
        
        if not critical_repeaters.empty:
            st.error("The following feeders have been in the Top 10 highest outage durations for 5 consecutive days.")
            st.dataframe(critical_repeaters, use_container_width=True, hide_index=True)
        else:
            st.success("No feeders have hit the notorious list for 5 consecutive days.")
    else:
        st.info("Insufficient 5-day data available.")
