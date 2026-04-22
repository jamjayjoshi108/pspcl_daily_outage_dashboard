import os
import time
import requests
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone

# --- IST TIMEZONE SETUP ---
IST = timezone(timedelta(hours=5, minutes=30))

# --- GITHUB TRIGGER LOGIC ---
def trigger_scraper():
    repo_owner = "jamjayjoshi108"
    repo_name = "pspcl_daily_outage_dashboard" 
    
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/daily_scrape.yml/dispatches"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {st.secrets['GITHUB_TOKEN']}"
    }
    response = requests.post(url, headers=headers, json={"ref": "main"})
    
    if response.status_code == 204:
        st.toast("✅ Scraper triggered successfully in the cloud!")
    else:
        st.error(f"❌ Failed to trigger scraper. GitHub responded: {response.text}")

# --- 1. FILE CHECKING LOGIC (OUTSIDE CACHE) ---
today_str = datetime.now(IST).strftime("%Y-%m-%d")
file_today = f"{today_str}_Outages_Today.csv"
file_5day = f"{today_str}_Outages_Last_5_Days.csv"

if not os.path.exists(file_today) or not os.path.exists(file_5day):
    lock_file = "scraper_lock.txt"
    should_trigger = True
    
    if os.path.exists(lock_file):
        # If the lock file is less than 5 minutes old, don't trigger again
        if time.time() - os.path.getmtime(lock_file) < 300: 
            should_trigger = False
            
    if should_trigger:
        trigger_scraper()
        with open(lock_file, "w") as f:
            f.write(str(time.time()))
        st.warning(f"⚠️ Data for {today_str} is missing. Automatically fetching fresh data from PSPCL...")
        st.info("⏳ Please wait ~2 minutes and refresh this page.")
    else:
        st.info("⏳ The scraper is currently running in the background. Please wait a moment and refresh.")
        
    st.stop() # Halts the dashboard so it doesn't crash trying to load missing data

# --- 2. DATA LOADING LOGIC (ONLY RUNS IF FILES EXIST) ---
@st.cache_data(ttl="10m")
def load_data(f_today, f_5day):
    df_today = pd.read_csv(f_today)
    df_5day = pd.read_csv(f_5day)
    
    df_today['Type of Outage'] = df_today['Type of Outage'].replace('Power Off By PC', 'Planned Outage')
    df_5day['Type of Outage'] = df_5day['Type of Outage'].replace('Power Off By PC', 'Planned Outage')
    
    time_cols = ['Schedule Created At', 'Start Time', 'End Time', 'Last Updated At']
    for df in [df_today, df_5day]:
        for col in time_cols:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        df['Status_Calc'] = df['End Time'].apply(lambda x: 'Active' if pd.isna(x) else 'Closed')
        
        def assign_bucket(mins):
            if pd.isna(mins) or mins < 0: return "Active/Unknown"
            hrs = mins / 60
            if hrs <= 2: return "Up to 2 Hrs"
            elif hrs <= 4: return "2-4 Hrs"
            elif hrs <= 8: return "4-8 Hrs"
            else: return "Above 8 Hrs"
            
        df['Duration Bucket'] = df['Diff in mins'].apply(assign_bucket)
        
    return df_today, df_5day

df_today, df_5day = load_data(file_today, file_5day)

# Colors based on your uploaded image legend
COLOR_PLANNED = "#ea4335" 
COLOR_UNPLANNED = "#45a29e"

st.title("⚡ Power Outage Monitoring Dashboard")

# --- MAIN LAYOUT (Matches Notebook Left/Right Pages) ---
col_left, col_right = st.columns(2, gap="large")

# ==========================================
# LEFT PAGE: TODAY'S OUTAGES
# ==========================================
with col_left:
    st.header(f"📅 Today's Outages ({datetime.now().strftime('%d %b %Y')})")
    
    # Top KPI Boxes
    st.subheader("Outage Summary")
    kpi1, kpi2 = st.columns(2)
    
    today_planned = df_today[df_today['Type of Outage'] == 'Planned Outage']
    today_unplanned = df_today[df_today['Type of Outage'] == 'Unplanned Outage']
    
    with kpi1:
        st.metric("Total Planned Outages", len(today_planned))
        st.caption(f"🔴 Active: {len(today_planned[today_planned['Status_Calc'] == 'Active'])} | 🟢 Closed: {len(today_planned[today_planned['Status_Calc'] == 'Closed'])}")
        
    with kpi2:
        st.metric("Total Unplanned Outages", len(today_unplanned))
        st.caption(f"🔴 Active: {len(today_unplanned[today_unplanned['Status_Calc'] == 'Active'])} | 🟢 Closed: {len(today_unplanned[today_unplanned['Status_Calc'] == 'Closed'])}")

    st.divider()

    # Middle Boxes: Zone-wise Charts
    st.subheader("Zone-wise Distribution")
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        fig_zone_p = px.histogram(today_planned, x="Zone", title="Zone-wise Planned", color_discrete_sequence=[COLOR_PLANNED])
        fig_zone_p.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=250)
        st.plotly_chart(fig_zone_p, use_container_width=True)
        
    with chart_col2:
        fig_zone_u = px.histogram(today_unplanned, x="Zone", title="Zone-wise Unplanned", color_discrete_sequence=[COLOR_UNPLANNED])
        fig_zone_u.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=250)
        st.plotly_chart(fig_zone_u, use_container_width=True)

    st.divider()

    # Bottom Table: Circle-wise Planned Breakdown
    st.subheader("Circle-wise Planned Breakdown")
    bucket_order = ["Up to 2 Hrs", "2-4 Hrs", "4-8 Hrs", "Above 8 Hrs", "Active/Unknown"]
    
    if not today_planned.empty:
        # Create Pivot Table
        planned_pivot = pd.crosstab(today_planned['Circle'], today_planned['Duration Bucket'])
        # Reorder columns to match notebook logically
        planned_pivot = planned_pivot.reindex(columns=[c for c in bucket_order if c in planned_pivot.columns], fill_value=0)
        planned_pivot['Total Planned Outages'] = planned_pivot.sum(axis=1)
        st.dataframe(planned_pivot, use_container_width=True)
        
        # Feeder Drill-Down
        st.markdown("**Click a Circle to view Feeder Details:**")
        selected_circle = st.selectbox("Select Circle:", options=planned_pivot.index, key="circle_select")
        feeder_list = today_planned[today_planned['Circle'] == selected_circle][['Feeder', 'Diff in mins', 'Status_Calc', 'Duration Bucket']]
        st.dataframe(feeder_list, use_container_width=True, hide_index=True)
    else:
        st.info("No Planned Outages recorded today.")


# ==========================================
# RIGHT PAGE: LAST 5 DAYS
# ==========================================
with col_right:
    st.header("⏳ Last 5 Days Trends")
    
    # Top KPI Boxes
    st.subheader("Outage Summary (5 Days)")
    kpi3, kpi4 = st.columns(2)
    
    fiveday_planned = df_5day[df_5day['Type of Outage'] == 'Planned Outage']
    fiveday_unplanned = df_5day[df_5day['Type of Outage'] == 'Unplanned Outage']
    
    with kpi3:
        st.metric("Total Planned Outages", len(fiveday_planned))
        
    with kpi4:
        st.metric("Total Unplanned Outages", len(fiveday_unplanned))

    st.divider()

    # Middle Boxes: Zone-wise Charts
    st.subheader("Zone-wise Distribution")
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        fig_5_zone_p = px.histogram(fiveday_planned, x="Zone", title="Zone-wise Planned", color_discrete_sequence=[COLOR_PLANNED])
        fig_5_zone_p.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=250)
        st.plotly_chart(fig_5_zone_p, use_container_width=True)
        
    with chart_col4:
        fig_5_zone_u = px.histogram(fiveday_unplanned, x="Zone", title="Zone-wise Unplanned", color_discrete_sequence=[COLOR_UNPLANNED])
        fig_5_zone_u.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=250)
        st.plotly_chart(fig_5_zone_u, use_container_width=True)

    st.divider()

    # Bottom Table: Circle-wise Unplanned Breakdown
    st.subheader("Circle-wise Unplanned Breakdown")
    
    if not fiveday_unplanned.empty:
        unplanned_pivot = pd.crosstab(fiveday_unplanned['Circle'], fiveday_unplanned['Duration Bucket'])
        unplanned_pivot = unplanned_pivot.reindex(columns=[c for c in bucket_order if c in unplanned_pivot.columns], fill_value=0)
        unplanned_pivot['Total Unplanned Outages'] = unplanned_pivot.sum(axis=1)
        st.dataframe(unplanned_pivot, use_container_width=True)
        
        # Feeder Drill-Down for Unplanned
        st.markdown("**Click a Circle to view Unplanned Feeder Details:**")
        selected_unplanned_circle = st.selectbox("Select Circle:", options=unplanned_pivot.index, key="circle_select_unplanned")
        feeder_list_u = fiveday_unplanned[fiveday_unplanned['Circle'] == selected_unplanned_circle][['Start Time', 'Feeder', 'Diff in mins', 'Duration Bucket']]
        st.dataframe(feeder_list_u, use_container_width=True, hide_index=True)
    else:
        st.info("No Unplanned Outages recorded in the last 5 days.")
