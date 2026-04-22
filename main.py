import os
import time
import requests
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Power Outage Monitoring Dashboard", layout="wide")

# --- COLOR THEME & CUSTOM CSS ---
COLOR_PRIMARY_BLUE = "#004085"
COLOR_KPI_TITLE_GOLD = "#FFC107"
COLOR_KPI_VALUE_WHITE = "#FFFFFF"
COLOR_TEXT_DARK = "#112E4C"

st.markdown(f"""
    <style>
        .block-container {{
            padding-top: 1rem;
            padding-bottom: 1rem;
        }}
        /* Headers styling */
        h1, h2, h3, h4, h5, h6 {{
            color: {COLOR_TEXT_DARK};
            border-bottom: 2px solid {COLOR_PRIMARY_BLUE};
            padding-bottom: 5px;
            margin-bottom: 15px;
        }}
        /* Custom blue dividers */
        hr {{
            border: 0;
            border-top: 2px solid {COLOR_PRIMARY_BLUE};
            margin: 1rem 0;
        }}
        /* KPI Card Styles matching your image */
        .kpi-card {{
            background-color: {COLOR_PRIMARY_BLUE};
            border-radius: 5px;
            padding: 1.5rem 1rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 100%;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        }}
        .kpi-title {{
            color: {COLOR_KPI_TITLE_GOLD};
            font-weight: bold;
            font-size: 0.9rem;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
        }}
        .kpi-value {{
            color: {COLOR_KPI_VALUE_WHITE};
            font-weight: bold;
            font-size: 2.5rem;
            margin-bottom: 0;
            line-height: 1.2;
        }}
        .kpi-subtext {{
            color: {COLOR_KPI_VALUE_WHITE};
            font-size: 0.85rem;
            margin-top: 0.8rem;
            padding-top: 0.5rem;
            border-top: 1px solid rgba(255, 255, 255, 0.2);
        }}
        /* White background for tables */
        .stDataFrame {{
            background-color: white;
        }}
    </style>
""", unsafe_allow_html=True)

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
        return True
    else:
        st.error(f"❌ Failed to trigger scraper. GitHub responded: {response.text}")
        return False

# --- 1. FILE CHECKING LOGIC ---
today_str = datetime.now(IST).strftime("%Y-%m-%d")
file_today = f"{today_str}_Outages_Today.csv"
file_5day = f"{today_str}_Outages_Last_5_Days.csv"

if not os.path.exists(file_today) or not os.path.exists(file_5day):
    lock_file = "scraper_lock.txt"
    should_trigger = True
    
    if os.path.exists(lock_file):
        if time.time() - os.path.getmtime(lock_file) < 300: 
            should_trigger = False
            
    if should_trigger:
        success = trigger_scraper()
        if success:
            with open(lock_file, "w") as f:
                f.write(str(time.time()))
            st.warning(f"⚠️ Data for {today_str} is missing. Automatically fetching fresh data from PSPCL...")
            st.info("⏳ Please wait ~2 minutes and refresh this page.")
        else:
            st.error("🚨 Could not fetch data due to GitHub API error. Fix the token to continue.")
    else:
        st.info("⏳ The scraper is currently running in the background. Please wait a moment and refresh.")
        
    st.stop()

# --- 2. DATA LOADING LOGIC ---
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

st.title("⚡ Power Outage Monitoring Dashboard")

# --- TOP HALF: SPLIT VIEW ---
col_left, col_right = st.columns(2, gap="large")

# ==========================================
# LEFT PAGE: TODAY'S OUTAGES
# ==========================================
with col_left:
    st.header(f"📅 Today's Outages ({datetime.now(IST).strftime('%d %b %Y')})")
    
    today_planned = df_today[df_today['Type of Outage'] == 'Planned Outage']
    today_unplanned = df_today[df_today['Type of Outage'] == 'Unplanned Outage']
    
    # Styled KPIs with Active/Closed Subtext
    st.subheader("Outage Summary")
    kpi1, kpi2 = st.columns(2)
    
    with kpi1:
        active_p = len(today_planned[today_planned['Status_Calc'] == 'Active'])
        closed_p = len(today_planned[today_planned['Status_Calc'] == 'Closed'])
        st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-title">Total Planned Outages</div>
                <div class="kpi-value">{len(today_planned)}</div>
                <div class="kpi-subtext">🔴 Active: {active_p} &nbsp;|&nbsp; 🟢 Closed: {closed_p}</div>
            </div>
        ''', unsafe_allow_html=True)
        
    with kpi2:
        active_u = len(today_unplanned[today_unplanned['Status_Calc'] == 'Active'])
        closed_u = len(today_unplanned[today_unplanned['Status_Calc'] == 'Closed'])
        st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-title">Total Unplanned Outages</div>
                <div class="kpi-value">{len(today_unplanned)}</div>
                <div class="kpi-subtext">🔴 Active: {active_u} &nbsp;|&nbsp; 🟢 Closed: {closed_u}</div>
            </div>
        ''', unsafe_allow_html=True)

    st.divider()

    # Zone-wise Table
    st.subheader("Zone-wise Distribution (Today)")
    if not df_today.empty:
        zone_today = df_today.groupby(['Zone', 'Type of Outage']).size().unstack(fill_value=0).reset_index()
        if 'Planned Outage' not in zone_today: zone_today['Planned Outage'] = 0
        if 'Unplanned Outage' not in zone_today: zone_today['Unplanned Outage'] = 0
        zone_today['Total'] = zone_today['Planned Outage'] + zone_today['Unplanned Outage']
        
        st.dataframe(zone_today, use_container_width=True, hide_index=True)
    else:
        st.info("No data available for today.")


# ==========================================
# RIGHT PAGE: LAST 5 DAYS
# ==========================================
with col_right:
    st.header("⏳ Last 5 Days Trends")
    
    fiveday_planned = df_5day[df_5day['Type of Outage'] == 'Planned Outage']
    fiveday_unplanned = df_5day[df_5day['Type of Outage'] == 'Unplanned Outage']
    
    # Styled KPIs WITHOUT Active/Closed Subtext
    st.subheader("Outage Summary (5 Days)")
    kpi3, kpi4 = st.columns(2)
    
    with kpi3:
        st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-title">Total Planned Outages</div>
                <div class="kpi-value">{len(fiveday_planned)}</div>
            </div>
        ''', unsafe_allow_html=True)
        
    with kpi4:
        st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-title">Total Unplanned Outages</div>
                <div class="kpi-value">{len(fiveday_unplanned)}</div>
            </div>
        ''', unsafe_allow_html=True)

    st.divider()

    # Zone-wise Table
    st.subheader("Zone-wise Distribution (5 Days)")
    if not df_5day.empty:
        zone_5day = df_5day.groupby(['Zone', 'Type of Outage']).size().unstack(fill_value=0).reset_index()
        if 'Planned Outage' not in zone_5day: zone_5day['Planned Outage'] = 0
        if 'Unplanned Outage' not in zone_5day: zone_5day['Unplanned Outage'] = 0
        zone_5day['Total'] = zone_5day['Planned Outage'] + zone_5day['Unplanned Outage']
        
        st.dataframe(zone_5day, use_container_width=True, hide_index=True)
    else:
        st.info("No data available for the last 5 days.")


# ==========================================
# BOTTOM HALF: FULL-WIDTH COMBINED SECTION
# ==========================================
st.divider()
st.header("Comprehensive Circle-wise Breakdown")
bucket_order = ["Up to 2 Hrs", "2-4 Hrs", "4-8 Hrs", "Above 8 Hrs", "Active/Unknown"]

# 1. Prepare Today Planned Pivot
if not today_planned.empty:
    p_pivot = pd.crosstab(today_planned['Circle'], today_planned['Duration Bucket'])
    p_pivot = p_pivot.reindex(columns=[c for c in bucket_order if c in p_pivot.columns], fill_value=0)
    p_pivot['Total'] = p_pivot.sum(axis=1)
else:
    p_pivot = pd.DataFrame(columns=bucket_order + ['Total'])

# 2. Prepare 5-Day Unplanned Pivot
if not fiveday_unplanned.empty:
    u_pivot = pd.crosstab(fiveday_unplanned['Circle'], fiveday_unplanned['Duration Bucket'])
    u_pivot = u_pivot.reindex(columns=[c for c in bucket_order if c in u_pivot.columns], fill_value=0)
    u_pivot['Total'] = u_pivot.sum(axis=1)
else:
    u_pivot = pd.DataFrame(columns=bucket_order + ['Total'])

# 3. Combine both into a single full-width MultiIndex Table
combined_circle = pd.concat([p_pivot, u_pivot], axis=1, keys=['TODAY (Planned Outages)', 'LAST 5 DAYS (Unplanned Outages)']).fillna(0).astype(int)

st.markdown("👆 **Click on any row inside the table below** to view the specific Feeder drill-down details.")

# The table is now interactive. When you click a row, it triggers an event.
if not combined_circle.empty:
    selection_event = st.dataframe(
        combined_circle, 
        use_container_width=True,
        on_select="rerun",
        selection_mode="single-row"  # Changed from single_row to single-row
    )

    # 4. Unified Feeder Drill-Down Triggered by Table Click
    if len(selection_event.selection.rows) > 0:
        # Get the selected row index, then map it back to the circle name
        selected_index = selection_event.selection.rows[0]
        selected_circle = combined_circle.index[selected_index]
        
        st.subheader(f"Feeder Details for: {selected_circle}")
        drill_left, drill_right = st.columns(2)
        
        with drill_left:
            st.markdown(f"**🔴 TODAY: Planned Feeders**")
            feeder_list_p = today_planned[today_planned['Circle'] == selected_circle][['Feeder', 'Diff in mins', 'Status_Calc', 'Duration Bucket']]
            # Rename for display
            feeder_list_p = feeder_list_p.rename(columns={'Status_Calc': 'Status'})
            st.dataframe(feeder_list_p, use_container_width=True, hide_index=True)
            
        with drill_right:
            st.markdown(f"**🟢 5-DAYS: Unplanned Feeders**")
            feeder_list_u = fiveday_unplanned[fiveday_unplanned['Circle'] == selected_circle].copy()
            # Calculate Hours and format columns
            feeder_list_u['Diff in Hours'] = (feeder_list_u['Diff in mins'] / 60).round(2)
            feeder_list_u = feeder_list_u[['Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket']]
            st.dataframe(feeder_list_u, use_container_width=True, hide_index=True)
else:
    st.info("No circle data available.")
