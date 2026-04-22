import os
import time
import requests
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Power Outage Monitoring Dashboard", layout="wide")

# --- GLOBAL TABLE HEADER STYLING ---
HEADER_STYLES = [
    {
        'selector': 'th',
        'props': [
            ('background-color', '#004085 !important'),
            ('color', '#FFC107 !important'),
            ('font-weight', 'bold !important'),
            ('text-align', 'center !important')
        ]
    },
    {
        'selector': 'th div',
        'props': [
            ('color', '#FFC107 !important'),
            ('font-weight', 'bold !important')
        ]
    }
]

# --- COLOR THEME & ENTERPRISE CSS ---
st.markdown("""
    <style>
        /* Base Container */
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 1.5rem;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        /* Force all standard paragraph, caption, and markdown text to Dark Black */
        p, span, div, caption, .stMarkdown {
            color: #000000 !important;
        }

        /* UNIFIED HEADERS */
        h1, h2, h3, h4, h5, h6, div.block-container h1 {
            color: #004085 !important;
            font-weight: 700 !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        div.block-container h1 {
            text-align: center;
            border-bottom: 3px solid #004085 !important;
            padding-bottom: 10px;
            margin-bottom: 30px !important;
            font-size: 2.2rem !important;
        }
        
        h2 {
            font-size: 1.3rem !important;
            border-bottom: 2px solid #004085 !important;
            padding-bottom: 5px;
            margin-bottom: 10px !important;
        }
        
        h3 {
            font-size: 1.05rem !important;
            margin-bottom: 12px !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* Crisp Dividers */
        hr {
            border: 0;
            border-top: 1px solid #004085;
            margin: 1.5rem 0;
            opacity: 0.3;
        }

        /* EXECUTIVE KPI CARDS */
        .kpi-card {
            background: linear-gradient(135deg, #004481 0%, #0066cc 100%);
            border-radius: 6px;
            padding: 1.2rem 1.2rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 100%;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
            transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
            border: 1px solid #003366;
        }

        .kpi-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 16px rgba(0, 68, 129, 0.2);
        }

        .kpi-card .kpi-title, .kpi-title {
            color: #FFC107 !important;
            font-weight: 600;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.4rem;
        }

        .kpi-card .kpi-value, .kpi-value {
            color: #FFFFFF !important;
            font-weight: 700;
            font-size: 2.6rem;
            margin-bottom: 0;
            line-height: 1.1;
        }

        .kpi-card .kpi-subtext, .kpi-subtext {
            color: #F8F9FA !important;
            font-size: 0.85rem;
            margin-top: 1rem;
            padding-top: 0.6rem;
            border-top: 1px solid rgba(255, 255, 255, 0.2);
            display: flex;
            justify-content: flex-start;
            gap: 15px;
        }

        .status-badge {
            background-color: rgba(0, 0, 0, 0.25);
            padding: 3px 8px;
            border-radius: 4px;
            font-weight: 500;
            color: #FFFFFF !important;
        }

        /* TABLE BORDERS */
        [data-testid="stDataFrame"] > div {
            border: 2px solid #004085 !important;
            border-radius: 6px;
            overflow: hidden;
        }
    </style>
""", unsafe_allow_html=True)

# --- IST TIMEZONE SETUP ---
IST = timezone(timedelta(hours=5, minutes=30))

# --- GITHUB TRIGGER LOGIC ---
def trigger_scraper():
    repo_owner = "jamjayjoshi108"
    repo_name = "pspcl_daily_outage_dashboard" 
    
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/263899469/dispatches"
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

# --- 1. FILE DEFINITIONS & CHECKING LOGIC ---
now_ist = datetime.now(IST)

# PORTAL DELAY FIX: The PSPCL portal updates after 7 AM. 
# If the current time is before 8:00 AM IST, we safely treat "Today" as yesterday.
if now_ist.hour < 8:
    now_ist -= timedelta(days=1)

today_str = now_ist.strftime("%Y-%m-%d")

try:
    ly_date = now_ist.replace(year=now_ist.year - 1)
except ValueError:
    ly_date = now_ist.replace(year=now_ist.year - 1, day=28)
ly_str = ly_date.strftime("%Y-%m-%d")

file_today = f"{today_str}_Outages_Today.csv"
file_5day = f"{today_str}_Outages_Last_5_Days.csv"
file_today_ly = f"{ly_str}_Outages_Today_Last_Year.csv"
file_5day_ly = f"{ly_str}_Outages_Last_5_Days_Last_Year.csv"

files_missing = not (
    os.path.exists(file_today) and 
    os.path.exists(file_5day) and 
    os.path.exists(file_today_ly) and 
    os.path.exists(file_5day_ly)
)

if files_missing:
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
            st.warning(f"⚠️ Data for {today_str} or YoY dates is missing. Automatically fetching fresh data from PSPCL...")
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
            
        df['Status_Calc'] = df['Status'].apply(
            lambda x: 'Active' if str(x).strip().title() == 'Open' else 'Closed'
        )
        
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
df_today_ly, df_5day_ly = load_data(file_today_ly, file_5day_ly)

# --- HELPER FUNCTIONS FOR TABLES ---
def create_bucket_pivot(df, bucket_order):
    if df.empty:
        return pd.DataFrame(columns=bucket_order + ['Total'])
    pivot = pd.crosstab(df['Circle'], df['Duration Bucket'])
    pivot = pivot.reindex(columns=[c for c in bucket_order if c in pivot.columns], fill_value=0)
    pivot['Total'] = pivot.sum(axis=1)
    return pivot

def generate_yoy_dist(df_curr, df_ly, group_col):
    if df_curr.empty:
        c_grp = pd.DataFrame(columns=[group_col, 'Planned Outage', 'Unplanned Outage'])
    else:
        c_grp = df_curr.groupby([group_col, 'Type of Outage']).size().unstack(fill_value=0).reset_index()
        
    if df_ly.empty:
        l_grp = pd.DataFrame(columns=[group_col, 'Planned Outage', 'Unplanned Outage'])
    else:
        l_grp = df_ly.groupby([group_col, 'Type of Outage']).size().unstack(fill_value=0).reset_index()

    for col in ['Planned Outage', 'Unplanned Outage']:
        if col not in c_grp.columns: c_grp[col] = 0
        if col not in l_grp.columns: l_grp[col] = 0

    c_grp['2026 Total'] = c_grp['Planned Outage'] + c_grp['Unplanned Outage']
    l_grp['2025 Total'] = l_grp['Planned Outage'] + l_grp['Unplanned Outage']
    
    c_grp = c_grp.rename(columns={'Planned Outage': '2026 Planned', 'Unplanned Outage': '2026 Unplanned'})
    l_grp = l_grp.rename(columns={'Planned Outage': '2025 Planned', 'Unplanned Outage': '2025 Unplanned'})
    
    merged = pd.merge(c_grp, l_grp, on=group_col, how='outer').fillna(0)
    
    for col in ['2026 Planned', '2026 Unplanned', '2026 Total', '2025 Planned', '2025 Unplanned', '2025 Total']:
        merged[col] = merged[col].astype(int)
        
    merged['YoY Delta (Total)'] = merged['2026 Total'] - merged['2025 Total']
    return merged[[group_col, '2026 Planned', '2025 Planned', '2026 Unplanned', '2025 Unplanned', '2026 Total', '2025 Total', 'YoY Delta (Total)']]

def highlight_delta(val):
    if isinstance(val, int):
        if val > 0: return 'color: #D32F2F; font-weight: bold;'
        elif val < 0: return 'color: #388E3C; font-weight: bold;'
    return ''

def generate_yoy_kpi_html(title, current_val, delta_val):
    if delta_val > 0:
        delta_str, delta_color = f"⬆ +{delta_val}", "#FF8A80"
    elif delta_val < 0:
        delta_str, delta_color = f"⬇ {delta_val}", "#69F0AE"
    else:
        delta_str, delta_color = "➖ 0", "#FFFFFF"
        
    return f'''
        <div class="kpi-card">
            <div>
                <div class="kpi-title">{title}</div>
                <div class="kpi-value">{current_val}</div>
            </div>
            <div class="kpi-subtext">
                <span class="status-badge" style="color: {delta_color} !important; font-weight: bold;">
                    {delta_str} vs Last Year
                </span>
            </div>
        </div>
    '''

# --- NOTORIOUS FEEDERS CALCULATION ---
df_5day['Outage Date'] = df_5day['Start Time'].dt.date
feeder_days = df_5day.groupby(['Circle', 'Feeder'])['Outage Date'].nunique().reset_index(name='Days with Outages')
notorious = feeder_days[feeder_days['Days with Outages'] >= 3]

feeder_stats = df_5day.groupby(['Circle', 'Feeder']).agg(
    Total_Events=('Start Time', 'size'),
    Avg_Mins=('Diff in mins', 'mean'),
    Total_Mins=('Diff in mins', 'sum')
).reset_index()

feeder_stats.rename(columns={'Total_Events': 'Total Outage Outage Events'}, inplace=True)
feeder_stats['Total Duration (Hours)'] = (feeder_stats['Total_Mins'] / 60).round(2)
feeder_stats['Average Duration (Hours)'] = (feeder_stats['Avg_Mins'] / 60).round(2)
feeder_stats = feeder_stats.drop(columns=['Avg_Mins', 'Total_Mins'])

notorious = notorious.merge(feeder_stats, on=['Circle', 'Feeder'])
notorious = notorious.sort_values(by=['Circle', 'Days with Outages', 'Total Outage Outage Events'], ascending=[True, False, False])
top_5_notorious = notorious.groupby('Circle').head(5)

notorious_set = set(zip(top_5_notorious['Circle'], top_5_notorious['Feeder']))


# --- MAIN DASHBOARD RENDER ---
st.title("⚡ Power Outage Monitoring Dashboard")

# --- TAB SYSTEM INTEGRATION ---
tab1, tab2 = st.tabs(["📊 Dashboard", "📈 YoY Comparison"])

with tab2:
    st.header("📈 Year-over-Year Comparison")
    st.markdown("Comparing current outage volumes to the exact same timeframe from last year.")
    
    curr_today_p = len(df_today[df_today['Type of Outage'] == 'Planned Outage'])
    curr_today_u = len(df_today[df_today['Type of Outage'] == 'Unplanned Outage'])
    curr_5day_p = len(df_5day[df_5day['Type of Outage'] == 'Planned Outage'])
    curr_5day_u = len(df_5day[df_5day['Type of Outage'] == 'Unplanned Outage'])
    
    ly_today_p = len(df_today_ly[df_today_ly['Type of Outage'] == 'Planned Outage'])
    ly_today_u = len(df_today_ly[df_today_ly['Type of Outage'] == 'Unplanned Outage'])
    ly_5day_p = len(df_5day_ly[df_5day_ly['Type of Outage'] == 'Planned Outage'])
    ly_5day_u = len(df_5day_ly[df_5day_ly['Type of Outage'] == 'Unplanned Outage'])
    
    st.subheader(f"Executive Summary vs. Same Day Last Year ({ly_date.strftime('%d %b %Y')})")
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1: st.markdown(generate_yoy_kpi_html("Planned (Today)", curr_today_p, int(curr_today_p - ly_today_p)), unsafe_allow_html=True)
    with kpi_col2: st.markdown(generate_yoy_kpi_html("Unplanned (Today)", curr_today_u, int(curr_today_u - ly_today_u)), unsafe_allow_html=True)
    with kpi_col3: st.markdown(generate_yoy_kpi_html("Planned (5 Days)", curr_5day_p, int(curr_5day_p - ly_5day_p)), unsafe_allow_html=True)
    with kpi_col4: st.markdown(generate_yoy_kpi_html("Unplanned (5 Days)", curr_5day_u, int(curr_5day_u - ly_5day_u)), unsafe_allow_html=True)
    
    st.divider()

    st.subheader("Zone-wise Distribution YoY (Today)")
    yoy_zone_today = generate_yoy_dist(df_today, df_today_ly, 'Zone')
    st.dataframe(yoy_zone_today.style.map(highlight_delta, subset=['YoY Delta (Total)']).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)

    st.subheader("Circle-wise Distribution YoY (Today)")
    yoy_circle_today = generate_yoy_dist(df_today, df_today_ly, 'Circle')
    st.dataframe(yoy_circle_today.style.map(highlight_delta, subset=['YoY Delta (Total)']).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
    
    st.divider()

    st.subheader("Zone-wise Distribution YoY (5 Days)")
    yoy_zone_5day = generate_yoy_dist(df_5day, df_5day_ly, 'Zone')
    st.dataframe(yoy_zone_5day.style.map(highlight_delta, subset=['YoY Delta (Total)']).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)

    st.subheader("Circle-wise Distribution YoY (5 Days)")
    yoy_circle_5day = generate_yoy_dist(df_5day, df_5day_ly, 'Circle')
    st.dataframe(yoy_circle_5day.style.map(highlight_delta, subset=['YoY Delta (Total)']).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
    
    st.divider()

    st.subheader("🚨 Current Top Notorious Feeders vs. Last Year")
    st.markdown("Displays the current top notorious feeders and shows their historical performance exactly a year ago.")
    
    if not df_5day_ly.empty:
        df_5day_ly['Outage Date'] = df_5day_ly['Start Time'].dt.date
        f_days_ly = df_5day_ly.groupby(['Circle', 'Feeder'])['Outage Date'].nunique().reset_index(name='2025 Days with Outages')
        f_stats_ly = df_5day_ly.groupby(['Circle', 'Feeder']).agg(
            LY_Events=('Start Time', 'size'),
            LY_Mins=('Diff in mins', 'sum')
        ).reset_index()
        f_stats_ly['2025 Duration (Hrs)'] = (f_stats_ly['LY_Mins'] / 60).round(2)
        ly_noto = pd.merge(f_days_ly, f_stats_ly[['Circle', 'Feeder', 'LY_Events', '2025 Duration (Hrs)']], on=['Circle', 'Feeder'])
        
        noto_yoy = pd.merge(
            top_5_notorious[['Circle', 'Feeder', 'Days with Outages', 'Total Outage Outage Events', 'Total Duration (Hours)']], 
            ly_noto, on=['Circle', 'Feeder'], how='left'
        ).fillna(0)
        
        noto_yoy = noto_yoy.rename(columns={
            'Days with Outages': '2026 Days with Outages',
            'Total Outage Outage Events': '2026 Outage Events',
            'Total Duration (Hours)': '2026 Duration (Hrs)',
            'LY_Events': '2025 Outage Events'
        })
        
        noto_yoy['2025 Days with Outages'] = noto_yoy['2025 Days with Outages'].astype(int)
        noto_yoy['2025 Outage Events'] = noto_yoy['2025 Outage Events'].astype(int)
        
        st.dataframe(noto_yoy.style.format({
            '2026 Duration (Hrs)': '{:.2f}', 
            '2025 Duration (Hrs)': '{:.2f}'
        }).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
    else:
        st.info("No Notorious Feeder data available to map against Last Year.")

    st.divider()

    st.subheader("4. Comprehensive Circle-wise Breakdown YoY (Last 5 Days)")
    bucket_order = ["Up to 2 Hrs", "2-4 Hrs", "4-8 Hrs", "Above 8 Hrs", "Active/Unknown"]
    
    curr_5d_p = create_bucket_pivot(df_5day[df_5day['Type of Outage'] == 'Planned Outage'], bucket_order)
    curr_5d_u = create_bucket_pivot(df_5day[df_5day['Type of Outage'] == 'Unplanned Outage'], bucket_order)
    ly_5d_p = create_bucket_pivot(df_5day_ly[df_5day_ly['Type of Outage'] == 'Planned Outage'], bucket_order)
    ly_5d_u = create_bucket_pivot(df_5day_ly[df_5day_ly['Type of Outage'] == 'Unplanned Outage'], bucket_order)
    
    comp_p = pd.concat([curr_5d_p, ly_5d_p], axis=1, keys=['Current 5 Days (Planned)', 'Last Year 5 Days (Planned)']).fillna(0).astype(int)
    comp_u = pd.concat([curr_5d_u, ly_5d_u], axis=1, keys=['Current 5 Days (Unplanned)', 'Last Year 5 Days (Unplanned)']).fillna(0).astype(int)
    
    st.markdown("**Planned Outages Summary:**")
    st.dataframe(comp_p.style.set_table_styles(HEADER_STYLES), width="stretch")
    
    st.markdown("**Unplanned Outages Summary:**")
    st.dataframe(comp_u.style.set_table_styles(HEADER_STYLES), width="stretch")


with tab1:
    # --- TOP HALF: SPLIT VIEW ---
    col_left, col_right = st.columns(2, gap="large")

    # ==========================================
    # LEFT PAGE: TODAY'S OUTAGES
    # ==========================================
    with col_left:
        st.header(f"📅 Today's Outages ({now_ist.strftime('%d %b %Y')})")
        
        today_planned = df_today[df_today['Type of Outage'] == 'Planned Outage']
        today_unplanned = df_today[df_today['Type of Outage'] == 'Unplanned Outage']
        
        st.subheader("Outage Summary")
        kpi1, kpi2 = st.columns(2)
        
        with kpi1:
            active_p = len(today_planned[today_planned['Status_Calc'] == 'Active'])
            closed_p = len(today_planned[today_planned['Status_Calc'] == 'Closed'])
            st.markdown(f'''
                <div class="kpi-card">
                    <div>
                        <div class="kpi-title">Total Planned Outages</div>
                        <div class="kpi-value">{len(today_planned)}</div>
                    </div>
                    <div class="kpi-subtext">
                        <span class="status-badge">🔴 Active: {active_p}</span> 
                        <span class="status-badge">🟢 Closed: {closed_p}</span>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
            
        with kpi2:
            active_u = len(today_unplanned[today_unplanned['Status_Calc'] == 'Active'])
            closed_u = len(today_unplanned[today_unplanned['Status_Calc'] == 'Closed'])
            st.markdown(f'''
                <div class="kpi-card">
                    <div>
                        <div class="kpi-title">Total Unplanned Outages</div>
                        <div class="kpi-value">{len(today_unplanned)}</div>
                    </div>
                    <div class="kpi-subtext">
                        <span class="status-badge">🔴 Active: {active_u}</span> 
                        <span class="status-badge">🟢 Closed: {closed_u}</span>
                    </div>
                </div>
            ''', unsafe_allow_html=True)

        st.divider()

        st.subheader("Zone-wise Distribution (Today)")
        if not df_today.empty:
            zone_today = df_today.groupby(['Zone', 'Type of Outage']).size().unstack(fill_value=0).reset_index()
            if 'Planned Outage' not in zone_today: zone_today['Planned Outage'] = 0
            if 'Unplanned Outage' not in zone_today: zone_today['Unplanned Outage'] = 0
            zone_today['Total'] = zone_today['Planned Outage'] + zone_today['Unplanned Outage']
            
            st.dataframe(zone_today.style.set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
        else:
            st.info("No data available for today.")


    # ==========================================
    # RIGHT PAGE: LAST 5 DAYS
    # ==========================================
    with col_right:
        st.header("⏳ Last 5 Days Trends")
        
        fiveday_planned = df_5day[df_5day['Type of Outage'] == 'Planned Outage']
        fiveday_unplanned = df_5day[df_5day['Type of Outage'] == 'Unplanned Outage']
        
        st.subheader("Outage Summary (5 Days)")
        kpi3, kpi4 = st.columns(2)
        
        with kpi3:
            st.markdown(f'''
                <div class="kpi-card">
                    <div>
                        <div class="kpi-title">Total Planned Outages</div>
                        <div class="kpi-value">{len(fiveday_planned)}</div>
                    </div>
                    <div class="kpi-subtext" style="visibility: hidden;">Spacer</div> 
                </div>
            ''', unsafe_allow_html=True)
            
        with kpi4:
            st.markdown(f'''
                <div class="kpi-card">
                    <div>
                        <div class="kpi-title">Total Unplanned Outages</div>
                        <div class="kpi-value">{len(fiveday_unplanned)}</div>
                    </div>
                    <div class="kpi-subtext" style="visibility: hidden;">Spacer</div>
                </div>
            ''', unsafe_allow_html=True)

        st.divider()

        st.subheader("Zone-wise Distribution (5 Days)")
        if not df_5day.empty:
            zone_5day = df_5day.groupby(['Zone', 'Type of Outage']).size().unstack(fill_value=0).reset_index()
            if 'Planned Outage' not in zone_5day: zone_5day['Planned Outage'] = 0
            if 'Unplanned Outage' not in zone_5day: zone_5day['Unplanned Outage'] = 0
            zone_5day['Total'] = zone_5day['Planned Outage'] + zone_5day['Unplanned Outage']
            
            st.dataframe(zone_5day.style.set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
        else:
            st.info("No data available for the last 5 days.")


    # ==========================================
    # MIDDLE SECTION: NOTORIOUS FEEDERS
    # ==========================================
    st.divider()
    st.header("🚨 Notorious Feeders (3+ Days of Outages in Last 5 Days)")
    st.caption("Top 5 worst-performing feeders per circle based on continuous outage days.")

    noto_col1, noto_col2 = st.columns(2)

    with noto_col1:
        circle_options = ["All Circles"] + sorted(top_5_notorious['Circle'].unique().tolist())
        selected_notorious_circle = st.selectbox("Filter by Circle:", options=circle_options, index=0)

    with noto_col2:
        outage_type_options = ["All Types", "Planned Outage", "Unplanned Outage"]
        selected_notorious_type = st.selectbox("Filter by Outage Type:", options=outage_type_options, index=0)

    # Dynamic filter specifically for displaying this table
    df_dyn = df_5day.copy()
    if selected_notorious_type != "All Types":
        df_dyn = df_dyn[df_dyn['Type of Outage'] == selected_notorious_type]

    if not df_dyn.empty:
        dyn_days = df_dyn.groupby(['Circle', 'Feeder'])['Outage Date'].nunique().reset_index(name='Days with Outages')
        dyn_noto = dyn_days[dyn_days['Days with Outages'] >= 3]

        if not dyn_noto.empty:
            dyn_stats = df_dyn.groupby(['Circle', 'Feeder']).agg(
                Total_Events=('Start Time', 'size'),
                Avg_Mins=('Diff in mins', 'mean'),
                Total_Mins=('Diff in mins', 'sum')
            ).reset_index()

            dyn_stats.rename(columns={'Total_Events': 'Total Outage Outage Events'}, inplace=True)
            dyn_stats['Total Duration (Hours)'] = (dyn_stats['Total_Mins'] / 60).round(2)
            dyn_stats['Average Duration (Hours)'] = (dyn_stats['Avg_Mins'] / 60).round(2)
            dyn_stats = dyn_stats.drop(columns=['Avg_Mins', 'Total_Mins'])

            dyn_noto = dyn_noto.merge(dyn_stats, on=['Circle', 'Feeder'])
            dyn_noto = dyn_noto.sort_values(by=['Circle', 'Days with Outages', 'Total Outage Outage Events'], ascending=[True, False, False])
            dyn_top5 = dyn_noto.groupby('Circle').head(5)

            if selected_notorious_circle != "All Circles":
                filtered_notorious = dyn_top5[dyn_top5['Circle'] == selected_notorious_circle]
            else:
                filtered_notorious = dyn_top5

            if not filtered_notorious.empty:
                styled_notorious = filtered_notorious.style.format({
                    'Average Duration (Hours)': '{:.2f}',
                    'Total Duration (Hours)': '{:.2f}'
                }).set_table_styles(HEADER_STYLES)
                st.dataframe(styled_notorious, width="stretch", hide_index=True)
            else:
                st.info(f"No notorious feeders found for {selected_notorious_circle} matching the criteria.")
        else:
            st.info(f"No notorious feeders identified for {selected_notorious_type}.")
    else:
        st.info("No data available for the selected outage type.")


    # ==========================================
    # BOTTOM HALF: FULL-WIDTH COMBINED SECTION
    # ==========================================
    st.divider()
    st.header("Comprehensive Circle-wise Breakdown")
    bucket_order = ["Up to 2 Hrs", "2-4 Hrs", "4-8 Hrs", "Above 8 Hrs", "Active/Unknown"]

    curr_5d_p_tab1 = create_bucket_pivot(df_5day[df_5day['Type of Outage'] == 'Planned Outage'], bucket_order)
    curr_5d_u_tab1 = create_bucket_pivot(df_5day[df_5day['Type of Outage'] == 'Unplanned Outage'], bucket_order)

    combined_circle = pd.concat([curr_5d_p_tab1, curr_5d_u_tab1], axis=1, keys=['LAST 5 DAYS (Planned Outages)', 'LAST 5 DAYS (Unplanned Outages)']).fillna(0).astype(int)

    st.markdown(" **Click on any row inside the table below** to view the specific Feeder drill-down details.")

    if not combined_circle.empty:
        styled_combined = combined_circle.style.set_table_styles(HEADER_STYLES)
        
        selection_event = st.dataframe(
            styled_combined, 
            width="stretch",
            on_select="rerun",
            selection_mode="single-row" 
        )

        if len(selection_event.selection.rows) > 0:
            selected_index = selection_event.selection.rows[0]
            selected_circle = combined_circle.index[selected_index]
            
            st.subheader(f"Feeder Details for: {selected_circle}")
            
            # --- DRILL-DOWN DATE FILTER ---
            circle_dates_raw = df_5day[df_5day['Circle'] == selected_circle]['Outage Date'].dropna().unique()
            circle_dates = sorted(list(circle_dates_raw))

            selected_dates = st.multiselect(
                "Filter 5-Days View by Date:",
                options=circle_dates,
                default=circle_dates,
                format_func=lambda x: x.strftime('%d %b %Y')
            )
            
            def highlight_notorious(row):
                if (selected_circle, row['Feeder']) in notorious_set:
                    return ['background-color: rgba(220, 53, 69, 0.15); color: #850000; font-weight: bold'] * len(row)
                return [''] * len(row)

            today_left, today_right = st.columns(2)
            
            with today_left:
                st.markdown(f"**🔴 TODAY: Planned Outages**")
                feeder_list_tp = today_planned[today_planned['Circle'] == selected_circle][['Feeder', 'Diff in mins', 'Status_Calc', 'Duration Bucket']]
                feeder_list_tp = feeder_list_tp.rename(columns={'Status_Calc': 'Status'})
                styled_tp = feeder_list_tp.style.apply(highlight_notorious, axis=1).set_table_styles(HEADER_STYLES)
                st.dataframe(styled_tp, width="stretch", hide_index=True)
                
            with today_right:
                st.markdown(f"**🔴 TODAY: Unplanned Outages**")
                feeder_list_tu = today_unplanned[today_unplanned['Circle'] == selected_circle][['Feeder', 'Diff in mins', 'Status_Calc', 'Duration Bucket']]
                feeder_list_tu = feeder_list_tu.rename(columns={'Status_Calc': 'Status'})
                styled_tu = feeder_list_tu.style.apply(highlight_notorious, axis=1).set_table_styles(HEADER_STYLES)
                st.dataframe(styled_tu, width="stretch", hide_index=True)
                
            st.write("") 
            
            fiveday_left, fiveday_right = st.columns(2)
            
            with fiveday_left:
                st.markdown(f"**🟢 5-DAYS: Planned Outages**")
                feeder_list_fp = fiveday_planned[fiveday_planned['Circle'] == selected_circle].copy()
                
                if not feeder_list_fp.empty:
                    feeder_list_fp = feeder_list_fp[feeder_list_fp['Outage Date'].isin(selected_dates)]
                    
                if not feeder_list_fp.empty:
                    feeder_list_fp['Diff in Hours'] = (feeder_list_fp['Diff in mins'] / 60).round(2)
                    feeder_list_fp = feeder_list_fp[['Outage Date', 'Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket']]
                    styled_fp = feeder_list_fp.style.apply(highlight_notorious, axis=1).format({'Diff in Hours': '{:.2f}'}).set_table_styles(HEADER_STYLES)
                    st.dataframe(styled_fp, width="stretch", hide_index=True)
                else:
                    empty_df = pd.DataFrame(columns=['Outage Date', 'Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket'])
                    st.dataframe(empty_df.style.set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
                
            with fiveday_right:
                st.markdown(f"**🟢 5-DAYS: Unplanned Outages**")
                feeder_list_fu = fiveday_unplanned[fiveday_unplanned['Circle'] == selected_circle].copy()
                
                if not feeder_list_fu.empty:
                    feeder_list_fu = feeder_list_fu[feeder_list_fu['Outage Date'].isin(selected_dates)]
                    
                if not feeder_list_fu.empty:
                    feeder_list_fu['Diff in Hours'] = (feeder_list_fu['Diff in mins'] / 60).round(2)
                    feeder_list_fu = feeder_list_fu[['Outage Date', 'Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket']]
                    styled_fu = feeder_list_fu.style.apply(highlight_notorious, axis=1).format({'Diff in Hours': '{:.2f}'}).set_table_styles(HEADER_STYLES)
                    st.dataframe(styled_fu, width="stretch", hide_index=True)
                else:
                    empty_df = pd.DataFrame(columns=['Outage Date', 'Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket'])
                    st.dataframe(empty_df.style.set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
    else:
        st.info("No circle data available.")
        

#  =======================================================================================================================================
#  =======================================================================================================================================
#V3
#  =======================================================================================================================================
#  =======================================================================================================================================
# import os
# import time
# import requests
# import streamlit as st
# import pandas as pd
# from datetime import datetime, timedelta, timezone

# # --- PAGE CONFIGURATION ---
# st.set_page_config(page_title="Power Outage Monitoring Dashboard", layout="wide")

# # --- GLOBAL TABLE HEADER STYLING ---
# # This applies the Blue background (#004085) and Gold text (#FFC107) to all table headers
# HEADER_STYLES = [
#     {
#         'selector': 'th',
#         'props': [
#             ('background-color', '#004085 !important'),
#             ('color', '#FFC107 !important'),
#             ('font-weight', 'bold !important'),
#             ('text-align', 'center !important')
#         ]
#     },
#     {
#         'selector': 'th div', # Targets the text inside the header div for specific Streamlit/Pandas versions
#         'props': [
#             ('color', '#FFC107 !important'),
#             ('font-weight', 'bold !important')
#         ]
#     }
# ]

# # --- COLOR THEME & ENTERPRISE CSS ---
# st.markdown("""
#     <style>
#         /* Base Container */
#         .block-container {
#             padding-top: 1.5rem;
#             padding-bottom: 1.5rem;
#             font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
#         }

#         /* Force all standard paragraph, caption, and markdown text to Dark Black */
#         p, span, div, caption, .stMarkdown {
#             color: #000000 !important;
#         }

#         /* UNIFIED HEADERS: ALL USE IDENTICAL PROFESSIONAL BLUE */
#         h1, h2, h3, h4, h5, h6, div.block-container h1 {
#             color: #004085 !important;
#             font-weight: 700 !important;
#             font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
#         }

#         div.block-container h1 {
#             text-align: center;
#             border-bottom: 3px solid #004085 !important;
#             padding-bottom: 10px;
#             margin-bottom: 30px !important;
#             font-size: 2.2rem !important;
#         }
        
#         h2 {
#             font-size: 1.3rem !important;
#             border-bottom: 2px solid #004085 !important;
#             padding-bottom: 5px;
#             margin-bottom: 10px !important;
#         }
        
#         h3 {
#             font-size: 1.05rem !important;
#             margin-bottom: 12px !important;
#             text-transform: uppercase;
#             letter-spacing: 0.5px;
#         }

#         /* Crisp Dividers */
#         hr {
#             border: 0;
#             border-top: 1px solid #004085;
#             margin: 1.5rem 0;
#             opacity: 0.3;
#         }

#         /* EXECUTIVE KPI CARDS */
#         .kpi-card {
#             background: linear-gradient(135deg, #004481 0%, #0066cc 100%);
#             border-radius: 6px;
#             padding: 1.2rem 1.2rem;
#             display: flex;
#             flex-direction: column;
#             justify-content: space-between;
#             height: 100%;
#             box-shadow: 0 2px 4px rgba(0,0,0,0.08);
#             transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
#             border: 1px solid #003366;
#         }

#         .kpi-card:hover {
#             transform: translateY(-4px);
#             box-shadow: 0 8px 16px rgba(0, 68, 129, 0.2);
#         }

#         .kpi-card .kpi-title, .kpi-title {
#             color: #FFC107 !important;
#             font-weight: 600;
#             font-size: 0.85rem;
#             text-transform: uppercase;
#             letter-spacing: 0.5px;
#             margin-bottom: 0.4rem;
#         }

#         .kpi-card .kpi-value, .kpi-value {
#             color: #FFFFFF !important;
#             font-weight: 700;
#             font-size: 2.6rem;
#             margin-bottom: 0;
#             line-height: 1.1;
#         }

#         .kpi-card .kpi-subtext, .kpi-subtext {
#             color: #F8F9FA !important;
#             font-size: 0.85rem;
#             margin-top: 1rem;
#             padding-top: 0.6rem;
#             border-top: 1px solid rgba(255, 255, 255, 0.2);
#             display: flex;
#             justify-content: flex-start;
#             gap: 15px;
#         }

#         .status-badge {
#             background-color: rgba(0, 0, 0, 0.25);
#             padding: 3px 8px;
#             border-radius: 4px;
#             font-weight: 500;
#             color: #FFFFFF !important;
#         }

#         /* TABLE BORDERS: ENFORCING PROFESSIONAL BLUE */
#         [data-testid="stDataFrame"] > div {
#             border: 2px solid #004085 !important;
#             border-radius: 6px;
#             overflow: hidden;
#         }
#     </style>
# """, unsafe_allow_html=True)

# # --- IST TIMEZONE SETUP ---
# IST = timezone(timedelta(hours=5, minutes=30))

# # --- GITHUB TRIGGER LOGIC ---
# def trigger_scraper():
#     repo_owner = "jamjayjoshi108"
#     repo_name = "pspcl_daily_outage_dashboard" 
    
#     url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/daily_scrape.yml/dispatches"
#     headers = {
#         "Accept": "application/vnd.github.v3+json",
#         "Authorization": f"token {st.secrets['GITHUB_TOKEN']}"
#     }
#     response = requests.post(url, headers=headers, json={"ref": "main"})
    
#     if response.status_code == 204:
#         st.toast("✅ Scraper triggered successfully in the cloud!")
#         return True
#     else:
#         st.error(f"❌ Failed to trigger scraper. GitHub responded: {response.text}")
#         return False

# # --- 1. FILE CHECKING LOGIC ---
# today_str = datetime.now(IST).strftime("%Y-%m-%d")
# file_today = f"{today_str}_Outages_Today.csv"
# file_5day = f"{today_str}_Outages_Last_5_Days.csv"

# if not os.path.exists(file_today) or not os.path.exists(file_5day):
#     lock_file = "scraper_lock.txt"
#     should_trigger = True
    
#     if os.path.exists(lock_file):
#         if time.time() - os.path.getmtime(lock_file) < 300: 
#             should_trigger = False
            
#     if should_trigger:
#         success = trigger_scraper()
#         if success:
#             with open(lock_file, "w") as f:
#                 f.write(str(time.time()))
#             st.warning(f"⚠️ Data for {today_str} is missing. Automatically fetching fresh data from PSPCL...")
#             st.info("⏳ Please wait ~2 minutes and refresh this page.")
#         else:
#             st.error("🚨 Could not fetch data due to GitHub API error. Fix the token to continue.")
#     else:
#         st.info("⏳ The scraper is currently running in the background. Please wait a moment and refresh.")
        
#     st.stop()

# # --- 2. DATA LOADING LOGIC ---
# @st.cache_data(ttl="10m")
# def load_data(f_today, f_5day):
#     df_today = pd.read_csv(f_today)
#     df_5day = pd.read_csv(f_5day)
    
#     df_today['Type of Outage'] = df_today['Type of Outage'].replace('Power Off By PC', 'Planned Outage')
#     df_5day['Type of Outage'] = df_5day['Type of Outage'].replace('Power Off By PC', 'Planned Outage')
    
#     time_cols = ['Schedule Created At', 'Start Time', 'End Time', 'Last Updated At']
#     for df in [df_today, df_5day]:
#         for col in time_cols:
#             df[col] = pd.to_datetime(df[col], errors='coerce')
            
#         df['Status_Calc'] = df['Status'].apply(
#             lambda x: 'Active' if str(x).strip().title() == 'Open' else 'Closed'
#         )
        
#         def assign_bucket(mins):
#             if pd.isna(mins) or mins < 0: return "Active/Unknown"
#             hrs = mins / 60
#             if hrs <= 2: return "Up to 2 Hrs"
#             elif hrs <= 4: return "2-4 Hrs"
#             elif hrs <= 8: return "4-8 Hrs"
#             else: return "Above 8 Hrs"
            
#         df['Duration Bucket'] = df['Diff in mins'].apply(assign_bucket)
        
#     return df_today, df_5day

# df_today, df_5day = load_data(file_today, file_5day)

# # --- NOTORIOUS FEEDERS CALCULATION (GLOBAL BASELINE FOR HIGHLIGHTING) ---
# df_5day['Outage Date'] = df_5day['Start Time'].dt.date
# feeder_days = df_5day.groupby(['Circle', 'Feeder'])['Outage Date'].nunique().reset_index(name='Days with Outages')
# notorious = feeder_days[feeder_days['Days with Outages'] >= 3]

# feeder_stats = df_5day.groupby(['Circle', 'Feeder']).agg(
#     Total_Events=('Start Time', 'size'),
#     Avg_Mins=('Diff in mins', 'mean'),
#     Total_Mins=('Diff in mins', 'sum')
# ).reset_index()

# feeder_stats.rename(columns={'Total_Events': 'Total Outage Outage Events'}, inplace=True)
# feeder_stats['Total Duration (Hours)'] = (feeder_stats['Total_Mins'] / 60).round(2)
# feeder_stats['Average Duration (Hours)'] = (feeder_stats['Avg_Mins'] / 60).round(2)
# feeder_stats = feeder_stats.drop(columns=['Avg_Mins', 'Total_Mins'])

# notorious = notorious.merge(feeder_stats, on=['Circle', 'Feeder'])
# notorious = notorious.sort_values(by=['Circle', 'Days with Outages', 'Total Outage Outage Events'], ascending=[True, False, False])
# top_5_notorious = notorious.groupby('Circle').head(5)

# notorious_set = set(zip(top_5_notorious['Circle'], top_5_notorious['Feeder']))


# # --- MAIN DASHBOARD RENDER ---
# st.title("⚡ Power Outage Monitoring Dashboard")

# # --- TOP HALF: SPLIT VIEW ---
# col_left, col_right = st.columns(2, gap="large")

# # ==========================================
# # LEFT PAGE: TODAY'S OUTAGES
# # ==========================================
# with col_left:
#     st.header(f"📅 Today's Outages ({datetime.now(IST).strftime('%d %b %Y')})")
    
#     today_planned = df_today[df_today['Type of Outage'] == 'Planned Outage']
#     today_unplanned = df_today[df_today['Type of Outage'] == 'Unplanned Outage']
    
#     st.subheader("Outage Summary")
#     kpi1, kpi2 = st.columns(2)
    
#     with kpi1:
#         active_p = len(today_planned[today_planned['Status_Calc'] == 'Active'])
#         closed_p = len(today_planned[today_planned['Status_Calc'] == 'Closed'])
#         st.markdown(f'''
#             <div class="kpi-card">
#                 <div>
#                     <div class="kpi-title">Total Planned Outages</div>
#                     <div class="kpi-value">{len(today_planned)}</div>
#                 </div>
#                 <div class="kpi-subtext">
#                     <span class="status-badge">🔴 Active: {active_p}</span> 
#                     <span class="status-badge">🟢 Closed: {closed_p}</span>
#                 </div>
#             </div>
#         ''', unsafe_allow_html=True)
        
#     with kpi2:
#         active_u = len(today_unplanned[today_unplanned['Status_Calc'] == 'Active'])
#         closed_u = len(today_unplanned[today_unplanned['Status_Calc'] == 'Closed'])
#         st.markdown(f'''
#             <div class="kpi-card">
#                 <div>
#                     <div class="kpi-title">Total Unplanned Outages</div>
#                     <div class="kpi-value">{len(today_unplanned)}</div>
#                 </div>
#                 <div class="kpi-subtext">
#                     <span class="status-badge">🔴 Active: {active_u}</span> 
#                     <span class="status-badge">🟢 Closed: {closed_u}</span>
#                 </div>
#             </div>
#         ''', unsafe_allow_html=True)

#     st.divider()

#     st.subheader("Zone-wise Distribution (Today)")
#     if not df_today.empty:
#         zone_today = df_today.groupby(['Zone', 'Type of Outage']).size().unstack(fill_value=0).reset_index()
#         if 'Planned Outage' not in zone_today: zone_today['Planned Outage'] = 0
#         if 'Unplanned Outage' not in zone_today: zone_today['Unplanned Outage'] = 0
#         zone_today['Total'] = zone_today['Planned Outage'] + zone_today['Unplanned Outage']
        
#         st.dataframe(zone_today.style.set_table_styles(HEADER_STYLES), use_container_width=True, hide_index=True)
#     else:
#         st.info("No data available for today.")


# # ==========================================
# # RIGHT PAGE: LAST 5 DAYS
# # ==========================================
# with col_right:
#     st.header("⏳ Last 5 Days Trends")
    
#     fiveday_planned = df_5day[df_5day['Type of Outage'] == 'Planned Outage']
#     fiveday_unplanned = df_5day[df_5day['Type of Outage'] == 'Unplanned Outage']
    
#     st.subheader("Outage Summary (5 Days)")
#     kpi3, kpi4 = st.columns(2)
    
#     with kpi3:
#         st.markdown(f'''
#             <div class="kpi-card">
#                 <div>
#                     <div class="kpi-title">Total Planned Outages</div>
#                     <div class="kpi-value">{len(fiveday_planned)}</div>
#                 </div>
#                 <div class="kpi-subtext" style="visibility: hidden;">Spacer</div> 
#             </div>
#         ''', unsafe_allow_html=True)
        
#     with kpi4:
#         st.markdown(f'''
#             <div class="kpi-card">
#                 <div>
#                     <div class="kpi-title">Total Unplanned Outages</div>
#                     <div class="kpi-value">{len(fiveday_unplanned)}</div>
#                 </div>
#                 <div class="kpi-subtext" style="visibility: hidden;">Spacer</div>
#             </div>
#         ''', unsafe_allow_html=True)

#     st.divider()

#     st.subheader("Zone-wise Distribution (5 Days)")
#     if not df_5day.empty:
#         zone_5day = df_5day.groupby(['Zone', 'Type of Outage']).size().unstack(fill_value=0).reset_index()
#         if 'Planned Outage' not in zone_5day: zone_5day['Planned Outage'] = 0
#         if 'Unplanned Outage' not in zone_5day: zone_5day['Unplanned Outage'] = 0
#         zone_5day['Total'] = zone_5day['Planned Outage'] + zone_5day['Unplanned Outage']
        
#         st.dataframe(zone_5day.style.set_table_styles(HEADER_STYLES), use_container_width=True, hide_index=True)
#     else:
#         st.info("No data available for the last 5 days.")


# # ==========================================
# # MIDDLE SECTION: NOTORIOUS FEEDERS
# # ==========================================
# st.divider()
# st.header("🚨 Notorious Feeders (3+ Days of Outages in Last 5 Days)")
# st.caption("Top 5 worst-performing feeders per circle based on continuous outage days.")

# noto_col1, noto_col2 = st.columns(2)

# with noto_col1:
#     circle_options = ["All Circles"] + sorted(top_5_notorious['Circle'].unique().tolist())
#     selected_notorious_circle = st.selectbox("Filter by Circle:", options=circle_options, index=0)

# with noto_col2:
#     outage_type_options = ["All Types", "Planned Outage", "Unplanned Outage"]
#     selected_notorious_type = st.selectbox("Filter by Outage Type:", options=outage_type_options, index=0)

# # Dynamic filter specifically for displaying this table
# df_dyn = df_5day.copy()
# if selected_notorious_type != "All Types":
#     df_dyn = df_dyn[df_dyn['Type of Outage'] == selected_notorious_type]

# if not df_dyn.empty:
#     dyn_days = df_dyn.groupby(['Circle', 'Feeder'])['Outage Date'].nunique().reset_index(name='Days with Outages')
#     dyn_noto = dyn_days[dyn_days['Days with Outages'] >= 3]

#     if not dyn_noto.empty:
#         dyn_stats = df_dyn.groupby(['Circle', 'Feeder']).agg(
#             Total_Events=('Start Time', 'size'),
#             Avg_Mins=('Diff in mins', 'mean'),
#             Total_Mins=('Diff in mins', 'sum')
#         ).reset_index()

#         dyn_stats.rename(columns={'Total_Events': 'Total Outage Outage Events'}, inplace=True)
#         dyn_stats['Total Duration (Hours)'] = (dyn_stats['Total_Mins'] / 60).round(2)
#         dyn_stats['Average Duration (Hours)'] = (dyn_stats['Avg_Mins'] / 60).round(2)
#         dyn_stats = dyn_stats.drop(columns=['Avg_Mins', 'Total_Mins'])

#         dyn_noto = dyn_noto.merge(dyn_stats, on=['Circle', 'Feeder'])
#         dyn_noto = dyn_noto.sort_values(by=['Circle', 'Days with Outages', 'Total Outage Outage Events'], ascending=[True, False, False])
#         dyn_top5 = dyn_noto.groupby('Circle').head(5)

#         if selected_notorious_circle != "All Circles":
#             filtered_notorious = dyn_top5[dyn_top5['Circle'] == selected_notorious_circle]
#         else:
#             filtered_notorious = dyn_top5

#         if not filtered_notorious.empty:
#             styled_notorious = filtered_notorious.style.format({
#                 'Average Duration (Hours)': '{:.2f}',
#                 'Total Duration (Hours)': '{:.2f}'
#             }).set_table_styles(HEADER_STYLES)
#             st.dataframe(styled_notorious, use_container_width=True, hide_index=True)
#         else:
#             st.info(f"No notorious feeders found for {selected_notorious_circle} matching the criteria.")
#     else:
#         st.info(f"No notorious feeders identified for {selected_notorious_type}.")
# else:
#     st.info("No data available for the selected outage type.")


# # ==========================================
# # BOTTOM HALF: FULL-WIDTH COMBINED SECTION
# # ==========================================
# st.divider()
# st.header("Comprehensive Circle-wise Breakdown")
# bucket_order = ["Up to 2 Hrs", "2-4 Hrs", "4-8 Hrs", "Above 8 Hrs", "Active/Unknown"]

# if not today_planned.empty:
#     p_pivot = pd.crosstab(today_planned['Circle'], today_planned['Duration Bucket'])
#     p_pivot = p_pivot.reindex(columns=[c for c in bucket_order if c in p_pivot.columns], fill_value=0)
#     p_pivot['Total'] = p_pivot.sum(axis=1)
# else:
#     p_pivot = pd.DataFrame(columns=bucket_order + ['Total'])

# if not fiveday_unplanned.empty:
#     u_pivot = pd.crosstab(fiveday_unplanned['Circle'], fiveday_unplanned['Duration Bucket'])
#     u_pivot = u_pivot.reindex(columns=[c for c in bucket_order if c in u_pivot.columns], fill_value=0)
#     u_pivot['Total'] = u_pivot.sum(axis=1)
# else:
#     u_pivot = pd.DataFrame(columns=bucket_order + ['Total'])

# combined_circle = pd.concat([p_pivot, u_pivot], axis=1, keys=['TODAY (Planned Outages)', 'LAST 5 DAYS (Unplanned Outages)']).fillna(0).astype(int)

# st.markdown(" **Click on any row inside the table below** to view the specific Feeder drill-down details.")

# if not combined_circle.empty:
#     styled_combined = combined_circle.style.set_table_styles(HEADER_STYLES)
    
#     selection_event = st.dataframe(
#         styled_combined, 
#         use_container_width=True,
#         on_select="rerun",
#         selection_mode="single-row" 
#     )

#     if len(selection_event.selection.rows) > 0:
#         selected_index = selection_event.selection.rows[0]
#         selected_circle = combined_circle.index[selected_index]
        
#         st.subheader(f"Feeder Details for: {selected_circle}")
        
#         # --- DRILL-DOWN DATE FILTER ---
#         circle_dates_raw = df_5day[df_5day['Circle'] == selected_circle]['Outage Date'].dropna().unique()
#         circle_dates = sorted(list(circle_dates_raw))

#         selected_dates = st.multiselect(
#             "Filter 5-Days View by Date:",
#             options=circle_dates,
#             default=circle_dates,
#             format_func=lambda x: x.strftime('%d %b %Y')
#         )
        
#         def highlight_notorious(row):
#             if (selected_circle, row['Feeder']) in notorious_set:
#                 return ['background-color: rgba(220, 53, 69, 0.15); color: #850000; font-weight: bold'] * len(row)
#             return [''] * len(row)

#         today_left, today_right = st.columns(2)
        
#         with today_left:
#             st.markdown(f"**🔴 TODAY: Planned Outages**")
#             feeder_list_tp = today_planned[today_planned['Circle'] == selected_circle][['Feeder', 'Diff in mins', 'Status_Calc', 'Duration Bucket']]
#             feeder_list_tp = feeder_list_tp.rename(columns={'Status_Calc': 'Status'})
#             styled_tp = feeder_list_tp.style.apply(highlight_notorious, axis=1).set_table_styles(HEADER_STYLES)
#             st.dataframe(styled_tp, use_container_width=True, hide_index=True)
            
#         with today_right:
#             st.markdown(f"**🔴 TODAY: Unplanned Outages**")
#             feeder_list_tu = today_unplanned[today_unplanned['Circle'] == selected_circle][['Feeder', 'Diff in mins', 'Status_Calc', 'Duration Bucket']]
#             feeder_list_tu = feeder_list_tu.rename(columns={'Status_Calc': 'Status'})
#             styled_tu = feeder_list_tu.style.apply(highlight_notorious, axis=1).set_table_styles(HEADER_STYLES)
#             st.dataframe(styled_tu, use_container_width=True, hide_index=True)
            
#         st.write("") 
        
#         fiveday_left, fiveday_right = st.columns(2)
        
#         with fiveday_left:
#             st.markdown(f"**🟢 5-DAYS: Planned Outages**")
#             feeder_list_fp = fiveday_planned[fiveday_planned['Circle'] == selected_circle].copy()
            
#             if not feeder_list_fp.empty:
#                 feeder_list_fp = feeder_list_fp[feeder_list_fp['Outage Date'].isin(selected_dates)]
                
#             if not feeder_list_fp.empty:
#                 feeder_list_fp['Diff in Hours'] = (feeder_list_fp['Diff in mins'] / 60).round(2)
#                 # EXPLICITLY ADDING OUTAGE DATE COLUMN HERE
#                 feeder_list_fp = feeder_list_fp[['Outage Date', 'Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket']]
#                 styled_fp = feeder_list_fp.style.apply(highlight_notorious, axis=1).format({'Diff in Hours': '{:.2f}'}).set_table_styles(HEADER_STYLES)
#                 st.dataframe(styled_fp, use_container_width=True, hide_index=True)
#             else:
#                 empty_df = pd.DataFrame(columns=['Outage Date', 'Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket'])
#                 st.dataframe(empty_df.style.set_table_styles(HEADER_STYLES), use_container_width=True, hide_index=True)
            
#         with fiveday_right:
#             st.markdown(f"**🟢 5-DAYS: Unplanned Outages**")
#             feeder_list_fu = fiveday_unplanned[fiveday_unplanned['Circle'] == selected_circle].copy()
            
#             if not feeder_list_fu.empty:
#                 feeder_list_fu = feeder_list_fu[feeder_list_fu['Outage Date'].isin(selected_dates)]
                
#             if not feeder_list_fu.empty:
#                 feeder_list_fu['Diff in Hours'] = (feeder_list_fu['Diff in mins'] / 60).round(2)
#                 # EXPLICITLY ADDING OUTAGE DATE COLUMN HERE
#                 feeder_list_fu = feeder_list_fu[['Outage Date', 'Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket']]
#                 styled_fu = feeder_list_fu.style.apply(highlight_notorious, axis=1).format({'Diff in Hours': '{:.2f}'}).set_table_styles(HEADER_STYLES)
#                 st.dataframe(styled_fu, use_container_width=True, hide_index=True)
#             else:
#                 empty_df = pd.DataFrame(columns=['Outage Date', 'Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket'])
#                 st.dataframe(empty_df.style.set_table_styles(HEADER_STYLES), use_container_width=True, hide_index=True)
# else:
#     st.info("No circle data available.")


#  =======================================================================================================================================
#  =======================================================================================================================================
#V2
#  =======================================================================================================================================
#  =======================================================================================================================================

# import os
# import time
# import requests
# import streamlit as st
# import pandas as pd
# from datetime import datetime, timedelta, timezone

# # --- PAGE CONFIGURATION ---
# st.set_page_config(page_title="Power Outage Monitoring Dashboard", layout="wide")

# # --- GLOBAL TABLE HEADER STYLING ---
# # This applies the Blue background (#004085) and Gold text (#FFC107) to all table headers
# HEADER_STYLES = [
#     {
#         'selector': 'th',
#         'props': [
#             ('background-color', '#004085 !important'),
#             ('color', '#FFC107 !important'),
#             ('font-weight', 'bold !important'),
#             ('text-align', 'center !important')
#         ]
#     },
#     {
#         'selector': 'th div', # Targets the text inside the header div for specific Streamlit/Pandas versions
#         'props': [
#             ('color', '#FFC107 !important'),
#             ('font-weight', 'bold !important')
#         ]
#     }
# ]

# # --- COLOR THEME & ENTERPRISE CSS ---
# st.markdown("""
#     <style>
#         /* Base Container */
#         .block-container {
#             padding-top: 1.5rem;
#             padding-bottom: 1.5rem;
#             font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
#         }

#         /* Force all standard paragraph, caption, and markdown text to Dark Black */
#         p, span, div, caption, .stMarkdown {
#             color: #000000 !important;
#         }

#         /* UNIFIED HEADERS: ALL USE IDENTICAL PROFESSIONAL BLUE */
#         h1, h2, h3, h4, h5, h6, div.block-container h1 {
#             color: #004085 !important;
#             font-weight: 700 !important;
#             font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
#         }

#         div.block-container h1 {
#             text-align: center;
#             border-bottom: 3px solid #004085 !important;
#             padding-bottom: 10px;
#             margin-bottom: 30px !important;
#             font-size: 2.2rem !important;
#         }
        
#         h2 {
#             font-size: 1.3rem !important;
#             border-bottom: 2px solid #004085 !important;
#             padding-bottom: 5px;
#             margin-bottom: 10px !important;
#         }
        
#         h3 {
#             font-size: 1.05rem !important;
#             margin-bottom: 12px !important;
#             text-transform: uppercase;
#             letter-spacing: 0.5px;
#         }

#         /* Crisp Dividers */
#         hr {
#             border: 0;
#             border-top: 1px solid #004085;
#             margin: 1.5rem 0;
#             opacity: 0.3;
#         }

#         /* EXECUTIVE KPI CARDS */
#         .kpi-card {
#             background: linear-gradient(135deg, #004481 0%, #0066cc 100%);
#             border-radius: 6px;
#             padding: 1.2rem 1.2rem;
#             display: flex;
#             flex-direction: column;
#             justify-content: space-between;
#             height: 100%;
#             box-shadow: 0 2px 4px rgba(0,0,0,0.08);
#             transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
#             border: 1px solid #003366;
#         }

#         .kpi-card:hover {
#             transform: translateY(-4px);
#             box-shadow: 0 8px 16px rgba(0, 68, 129, 0.2);
#         }

#         .kpi-card .kpi-title, .kpi-title {
#             color: #FFC107 !important;
#             font-weight: 600;
#             font-size: 0.85rem;
#             text-transform: uppercase;
#             letter-spacing: 0.5px;
#             margin-bottom: 0.4rem;
#         }

#         .kpi-card .kpi-value, .kpi-value {
#             color: #FFFFFF !important;
#             font-weight: 700;
#             font-size: 2.6rem;
#             margin-bottom: 0;
#             line-height: 1.1;
#         }

#         .kpi-card .kpi-subtext, .kpi-subtext {
#             color: #F8F9FA !important;
#             font-size: 0.85rem;
#             margin-top: 1rem;
#             padding-top: 0.6rem;
#             border-top: 1px solid rgba(255, 255, 255, 0.2);
#             display: flex;
#             justify-content: flex-start;
#             gap: 15px;
#         }

#         .status-badge {
#             background-color: rgba(0, 0, 0, 0.25);
#             padding: 3px 8px;
#             border-radius: 4px;
#             font-weight: 500;
#             color: #FFFFFF !important;
#         }

#         /* TABLE BORDERS: ENFORCING PROFESSIONAL BLUE */
#         [data-testid="stDataFrame"] > div {
#             border: 2px solid #004085 !important;
#             border-radius: 6px;
#             overflow: hidden;
#         }
#     </style>
# """, unsafe_allow_html=True)

# # --- IST TIMEZONE SETUP ---
# IST = timezone(timedelta(hours=5, minutes=30))

# # --- GITHUB TRIGGER LOGIC ---
# def trigger_scraper():
#     repo_owner = "jamjayjoshi108"
#     repo_name = "pspcl_daily_outage_dashboard" 
    
#     url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/daily_scrape.yml/dispatches"
#     headers = {
#         "Accept": "application/vnd.github.v3+json",
#         "Authorization": f"token {st.secrets['GITHUB_TOKEN']}"
#     }
#     response = requests.post(url, headers=headers, json={"ref": "main"})
    
#     if response.status_code == 204:
#         st.toast("✅ Scraper triggered successfully in the cloud!")
#         return True
#     else:
#         st.error(f"❌ Failed to trigger scraper. GitHub responded: {response.text}")
#         return False

# # --- 1. FILE CHECKING LOGIC ---
# today_str = datetime.now(IST).strftime("%Y-%m-%d")
# file_today = f"{today_str}_Outages_Today.csv"
# file_5day = f"{today_str}_Outages_Last_5_Days.csv"

# if not os.path.exists(file_today) or not os.path.exists(file_5day):
#     lock_file = "scraper_lock.txt"
#     should_trigger = True
    
#     if os.path.exists(lock_file):
#         if time.time() - os.path.getmtime(lock_file) < 300: 
#             should_trigger = False
            
#     if should_trigger:
#         success = trigger_scraper()
#         if success:
#             with open(lock_file, "w") as f:
#                 f.write(str(time.time()))
#             st.warning(f"⚠️ Data for {today_str} is missing. Automatically fetching fresh data from PSPCL...")
#             st.info("⏳ Please wait ~2 minutes and refresh this page.")
#         else:
#             st.error("🚨 Could not fetch data due to GitHub API error. Fix the token to continue.")
#     else:
#         st.info("⏳ The scraper is currently running in the background. Please wait a moment and refresh.")
        
#     st.stop()

# # --- 2. DATA LOADING LOGIC ---
# @st.cache_data(ttl="10m")
# def load_data(f_today, f_5day):
#     df_today = pd.read_csv(f_today)
#     df_5day = pd.read_csv(f_5day)
    
#     df_today['Type of Outage'] = df_today['Type of Outage'].replace('Power Off By PC', 'Planned Outage')
#     df_5day['Type of Outage'] = df_5day['Type of Outage'].replace('Power Off By PC', 'Planned Outage')
    
#     time_cols = ['Schedule Created At', 'Start Time', 'End Time', 'Last Updated At']
#     for df in [df_today, df_5day]:
#         for col in time_cols:
#             df[col] = pd.to_datetime(df[col], errors='coerce')
            
#         df['Status_Calc'] = df['Status'].apply(
#             lambda x: 'Active' if str(x).strip().title() == 'Open' else 'Closed'
#         )
        
#         def assign_bucket(mins):
#             if pd.isna(mins) or mins < 0: return "Active/Unknown"
#             hrs = mins / 60
#             if hrs <= 2: return "Up to 2 Hrs"
#             elif hrs <= 4: return "2-4 Hrs"
#             elif hrs <= 8: return "4-8 Hrs"
#             else: return "Above 8 Hrs"
            
#         df['Duration Bucket'] = df['Diff in mins'].apply(assign_bucket)
        
#     return df_today, df_5day

# df_today, df_5day = load_data(file_today, file_5day)

# # --- NOTORIOUS FEEDERS CALCULATION ---
# df_5day['Outage Date'] = df_5day['Start Time'].dt.date
# feeder_days = df_5day.groupby(['Circle', 'Feeder'])['Outage Date'].nunique().reset_index(name='Days with Outages')
# notorious = feeder_days[feeder_days['Days with Outages'] >= 3]

# feeder_stats = df_5day.groupby(['Circle', 'Feeder']).agg(
#     Total_Events=('Start Time', 'size'),
#     Avg_Mins=('Diff in mins', 'mean')
# ).reset_index()

# feeder_stats.rename(columns={'Total_Events': 'Total Outage Outage Events'}, inplace=True)
# feeder_stats['Average Duration (Hours)'] = (feeder_stats['Avg_Mins'] / 60).round(2)
# feeder_stats = feeder_stats.drop(columns=['Avg_Mins'])

# notorious = notorious.merge(feeder_stats, on=['Circle', 'Feeder'])
# notorious = notorious.sort_values(by=['Circle', 'Days with Outages', 'Total Outage Outage Events'], ascending=[True, False, False])
# top_5_notorious = notorious.groupby('Circle').head(5)

# notorious_set = set(zip(top_5_notorious['Circle'], top_5_notorious['Feeder']))


# # --- MAIN DASHBOARD RENDER ---
# st.title("⚡ Power Outage Monitoring Dashboard")

# # --- TOP HALF: SPLIT VIEW ---
# col_left, col_right = st.columns(2, gap="large")

# # ==========================================
# # LEFT PAGE: TODAY'S OUTAGES
# # ==========================================
# with col_left:
#     st.header(f"📅 Today's Outages ({datetime.now(IST).strftime('%d %b %Y')})")
    
#     today_planned = df_today[df_today['Type of Outage'] == 'Planned Outage']
#     today_unplanned = df_today[df_today['Type of Outage'] == 'Unplanned Outage']
    
#     st.subheader("Outage Summary")
#     kpi1, kpi2 = st.columns(2)
    
#     with kpi1:
#         active_p = len(today_planned[today_planned['Status_Calc'] == 'Active'])
#         closed_p = len(today_planned[today_planned['Status_Calc'] == 'Closed'])
#         st.markdown(f'''
#             <div class="kpi-card">
#                 <div>
#                     <div class="kpi-title">Total Planned Outages</div>
#                     <div class="kpi-value">{len(today_planned)}</div>
#                 </div>
#                 <div class="kpi-subtext">
#                     <span class="status-badge">🔴 Active: {active_p}</span> 
#                     <span class="status-badge">🟢 Closed: {closed_p}</span>
#                 </div>
#             </div>
#         ''', unsafe_allow_html=True)
        
#     with kpi2:
#         active_u = len(today_unplanned[today_unplanned['Status_Calc'] == 'Active'])
#         closed_u = len(today_unplanned[today_unplanned['Status_Calc'] == 'Closed'])
#         st.markdown(f'''
#             <div class="kpi-card">
#                 <div>
#                     <div class="kpi-title">Total Unplanned Outages</div>
#                     <div class="kpi-value">{len(today_unplanned)}</div>
#                 </div>
#                 <div class="kpi-subtext">
#                     <span class="status-badge">🔴 Active: {active_u}</span> 
#                     <span class="status-badge">🟢 Closed: {closed_u}</span>
#                 </div>
#             </div>
#         ''', unsafe_allow_html=True)

#     st.divider()

#     st.subheader("Zone-wise Distribution (Today)")
#     if not df_today.empty:
#         zone_today = df_today.groupby(['Zone', 'Type of Outage']).size().unstack(fill_value=0).reset_index()
#         if 'Planned Outage' not in zone_today: zone_today['Planned Outage'] = 0
#         if 'Unplanned Outage' not in zone_today: zone_today['Unplanned Outage'] = 0
#         zone_today['Total'] = zone_today['Planned Outage'] + zone_today['Unplanned Outage']
        
#         # Apply header styling
#         st.dataframe(zone_today.style.set_table_styles(HEADER_STYLES), use_container_width=True, hide_index=True)
#     else:
#         st.info("No data available for today.")


# # ==========================================
# # RIGHT PAGE: LAST 5 DAYS
# # ==========================================
# with col_right:
#     st.header("⏳ Last 5 Days Trends")
    
#     fiveday_planned = df_5day[df_5day['Type of Outage'] == 'Planned Outage']
#     fiveday_unplanned = df_5day[df_5day['Type of Outage'] == 'Unplanned Outage']
    
#     st.subheader("Outage Summary (5 Days)")
#     kpi3, kpi4 = st.columns(2)
    
#     with kpi3:
#         st.markdown(f'''
#             <div class="kpi-card">
#                 <div>
#                     <div class="kpi-title">Total Planned Outages</div>
#                     <div class="kpi-value">{len(fiveday_planned)}</div>
#                 </div>
#                 <div class="kpi-subtext" style="visibility: hidden;">Spacer</div> 
#             </div>
#         ''', unsafe_allow_html=True)
        
#     with kpi4:
#         st.markdown(f'''
#             <div class="kpi-card">
#                 <div>
#                     <div class="kpi-title">Total Unplanned Outages</div>
#                     <div class="kpi-value">{len(fiveday_unplanned)}</div>
#                 </div>
#                 <div class="kpi-subtext" style="visibility: hidden;">Spacer</div>
#             </div>
#         ''', unsafe_allow_html=True)

#     st.divider()

#     st.subheader("Zone-wise Distribution (5 Days)")
#     if not df_5day.empty:
#         zone_5day = df_5day.groupby(['Zone', 'Type of Outage']).size().unstack(fill_value=0).reset_index()
#         if 'Planned Outage' not in zone_5day: zone_5day['Planned Outage'] = 0
#         if 'Unplanned Outage' not in zone_5day: zone_5day['Unplanned Outage'] = 0
#         zone_5day['Total'] = zone_5day['Planned Outage'] + zone_5day['Unplanned Outage']
        
#         # Apply header styling
#         st.dataframe(zone_5day.style.set_table_styles(HEADER_STYLES), use_container_width=True, hide_index=True)
#     else:
#         st.info("No data available for the last 5 days.")


# # ==========================================
# # MIDDLE SECTION: NOTORIOUS FEEDERS
# # ==========================================
# st.divider()
# st.header("🚨 Notorious Feeders (3+ Days of Outages in Last 5 Days)")
# st.caption("Top 5 worst-performing feeders per circle based on continuous outage days.")

# if not top_5_notorious.empty:
#     circle_options = ["All Circles"] + sorted(top_5_notorious['Circle'].unique().tolist())
#     selected_notorious_circle = st.selectbox("Filter by Circle:", options=circle_options, index=0)
    
#     if selected_notorious_circle == "All Circles":
#         filtered_notorious = top_5_notorious
#     else:
#         filtered_notorious = top_5_notorious[top_5_notorious['Circle'] == selected_notorious_circle]
        
#     # Apply format AND header styling
#     styled_notorious = filtered_notorious.style.format({'Average Duration (Hours)': '{:.2f}'}).set_table_styles(HEADER_STYLES)
#     st.dataframe(styled_notorious, use_container_width=True, hide_index=True)
# else:
#     st.info("Excellent! No notorious feeders identified matching this criteria.")


# # ==========================================
# # BOTTOM HALF: FULL-WIDTH COMBINED SECTION
# # ==========================================
# st.divider()
# st.header("Comprehensive Circle-wise Breakdown")
# bucket_order = ["Up to 2 Hrs", "2-4 Hrs", "4-8 Hrs", "Above 8 Hrs", "Active/Unknown"]

# if not today_planned.empty:
#     p_pivot = pd.crosstab(today_planned['Circle'], today_planned['Duration Bucket'])
#     p_pivot = p_pivot.reindex(columns=[c for c in bucket_order if c in p_pivot.columns], fill_value=0)
#     p_pivot['Total'] = p_pivot.sum(axis=1)
# else:
#     p_pivot = pd.DataFrame(columns=bucket_order + ['Total'])

# if not fiveday_unplanned.empty:
#     u_pivot = pd.crosstab(fiveday_unplanned['Circle'], fiveday_unplanned['Duration Bucket'])
#     u_pivot = u_pivot.reindex(columns=[c for c in bucket_order if c in u_pivot.columns], fill_value=0)
#     u_pivot['Total'] = u_pivot.sum(axis=1)
# else:
#     u_pivot = pd.DataFrame(columns=bucket_order + ['Total'])

# combined_circle = pd.concat([p_pivot, u_pivot], axis=1, keys=['TODAY (Planned Outages)', 'LAST 5 DAYS (Unplanned Outages)']).fillna(0).astype(int)

# st.markdown(" **Click on any row inside the table below** to view the specific Feeder drill-down details.")

# if not combined_circle.empty:
#     # Apply header styling to the main interactive dataframe
#     styled_combined = combined_circle.style.set_table_styles(HEADER_STYLES)
    
#     selection_event = st.dataframe(
#         styled_combined, 
#         use_container_width=True,
#         on_select="rerun",
#         selection_mode="single-row" 
#     )

#     if len(selection_event.selection.rows) > 0:
#         selected_index = selection_event.selection.rows[0]
#         selected_circle = combined_circle.index[selected_index]
        
#         st.subheader(f"Feeder Details for: {selected_circle}")
        
#         def highlight_notorious(row):
#             if (selected_circle, row['Feeder']) in notorious_set:
#                 return ['background-color: rgba(220, 53, 69, 0.15); color: #850000; font-weight: bold'] * len(row)
#             return [''] * len(row)

#         today_left, today_right = st.columns(2)
        
#         with today_left:
#             st.markdown(f"**🔴 TODAY: Planned Outages**")
#             feeder_list_tp = today_planned[today_planned['Circle'] == selected_circle][['Feeder', 'Diff in mins', 'Status_Calc', 'Duration Bucket']]
#             feeder_list_tp = feeder_list_tp.rename(columns={'Status_Calc': 'Status'})
#             styled_tp = feeder_list_tp.style.apply(highlight_notorious, axis=1).set_table_styles(HEADER_STYLES)
#             st.dataframe(styled_tp, use_container_width=True, hide_index=True)
            
#         with today_right:
#             st.markdown(f"**🔴 TODAY: Unplanned Outages**")
#             feeder_list_tu = today_unplanned[today_unplanned['Circle'] == selected_circle][['Feeder', 'Diff in mins', 'Status_Calc', 'Duration Bucket']]
#             feeder_list_tu = feeder_list_tu.rename(columns={'Status_Calc': 'Status'})
#             styled_tu = feeder_list_tu.style.apply(highlight_notorious, axis=1).set_table_styles(HEADER_STYLES)
#             st.dataframe(styled_tu, use_container_width=True, hide_index=True)
            
#         st.write("") 
        
#         fiveday_left, fiveday_right = st.columns(2)
        
#         with fiveday_left:
#             st.markdown(f"**🟢 5-DAYS: Planned Outages**")
#             feeder_list_fp = fiveday_planned[fiveday_planned['Circle'] == selected_circle].copy()
#             if not feeder_list_fp.empty:
#                 feeder_list_fp['Diff in Hours'] = (feeder_list_fp['Diff in mins'] / 60).round(2)
#                 feeder_list_fp = feeder_list_fp[['Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket']]
#                 styled_fp = feeder_list_fp.style.apply(highlight_notorious, axis=1).format({'Diff in Hours': '{:.2f}'}).set_table_styles(HEADER_STYLES)
#                 st.dataframe(styled_fp, use_container_width=True, hide_index=True)
#             else:
#                 empty_df = pd.DataFrame(columns=['Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket'])
#                 st.dataframe(empty_df.style.set_table_styles(HEADER_STYLES), use_container_width=True, hide_index=True)
            
#         with fiveday_right:
#             st.markdown(f"**🟢 5-DAYS: Unplanned Outages**")
#             feeder_list_fu = fiveday_unplanned[fiveday_unplanned['Circle'] == selected_circle].copy()
#             if not feeder_list_fu.empty:
#                 feeder_list_fu['Diff in Hours'] = (feeder_list_fu['Diff in mins'] / 60).round(2)
#                 feeder_list_fu = feeder_list_fu[['Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket']]
#                 styled_fu = feeder_list_fu.style.apply(highlight_notorious, axis=1).format({'Diff in Hours': '{:.2f}'}).set_table_styles(HEADER_STYLES)
#                 st.dataframe(styled_fu, use_container_width=True, hide_index=True)
#             else:
#                 empty_df = pd.DataFrame(columns=['Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket'])
#                 st.dataframe(empty_df.style.set_table_styles(HEADER_STYLES), use_container_width=True, hide_index=True)
# else:
#     st.info("No circle data available.")
#  =======================================================================================================================================
#  =======================================================================================================================================
#V1
#  =======================================================================================================================================
#  =======================================================================================================================================

# import os
# import time
# import requests
# import streamlit as st
# import pandas as pd
# from datetime import datetime, timedelta, timezone

# # --- PAGE CONFIGURATION ---
# st.set_page_config(page_title="Power Outage Monitoring Dashboard", layout="wide")

# # --- COLOR THEME & ENTERPRISE CSS ---
# st.markdown("""
#     <style>
#         /* Base Container */
#         .block-container {
#             padding-top: 1.5rem;
#             padding-bottom: 1.5rem;
#             font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
#         }

#         /* Professional Header Styling */
#         h1 {
#             color: #004085 !important;
#             font-weight: 700 !important;
#             text-align: center;
#             border-bottom: 3px solid #004085;
#             padding-bottom: 10px;
#             margin-bottom: 30px !important;
#             font-size: 2.2rem !important;
#         }
        
#         /* Shrunk Section Headers */
#         h2 {
#             font-size: 1.3rem !important;
#             color: #112E4C !important;
#             font-weight: 600 !important;
#             margin-bottom: 10px !important;
#             border-bottom: 2px solid #E2E8F0;
#             padding-bottom: 5px;
#         }
        
#         /* Shrunk Subheaders */
#         h3 {
#             font-size: 1.05rem !important;
#             color: #4A5568 !important;
#             font-weight: 600 !important;
#             margin-bottom: 12px !important;
#             text-transform: uppercase;
#             letter-spacing: 0.5px;
#         }

#         /* Crisp Dividers */
#         hr {
#             border: 0;
#             border-top: 1px solid #CBD5E0;
#             margin: 1.5rem 0;
#         }

#         /* Executive KPI Cards with Hover Pop */
#         .kpi-card {
#             background: linear-gradient(135deg, #004481 0%, #0066cc 100%);
#             border-radius: 6px;
#             padding: 1.2rem 1.2rem;
#             display: flex;
#             flex-direction: column;
#             justify-content: space-between;
#             height: 100%;
#             box-shadow: 0 2px 4px rgba(0,0,0,0.08);
#             transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
#             border: 1px solid #003366;
#         }

#         .kpi-card:hover {
#             transform: translateY(-4px);
#             box-shadow: 0 8px 16px rgba(0, 68, 129, 0.2);
#         }

#         .kpi-title {
#             color: #FFC107;
#             font-weight: 600;
#             font-size: 0.85rem;
#             text-transform: uppercase;
#             letter-spacing: 0.5px;
#             margin-bottom: 0.4rem;
#         }

#         .kpi-value {
#             color: #FFFFFF;
#             font-weight: 700;
#             font-size: 2.6rem;
#             margin-bottom: 0;
#             line-height: 1.1;
#         }

#         .kpi-subtext {
#             color: #F8F9FA;
#             font-size: 0.85rem;
#             margin-top: 1rem;
#             padding-top: 0.6rem;
#             border-top: 1px solid rgba(255, 255, 255, 0.2);
#             display: flex;
#             justify-content: flex-start;
#             gap: 15px;
#         }

#         /* Clear, High-Contrast Status Badges */
#         .status-badge {
#             background-color: rgba(0, 0, 0, 0.25);
#             padding: 3px 8px;
#             border-radius: 4px;
#             font-weight: 500;
#         }

#         /* Solid Table Borders to replace Light Grey */
#         [data-testid="stDataFrame"] > div {
#             border: 1px solid #004085 !important;
#             border-radius: 4px;
#         }
#     </style>
# """, unsafe_allow_html=True)

# # --- IST TIMEZONE SETUP ---
# IST = timezone(timedelta(hours=5, minutes=30))

# # --- GITHUB TRIGGER LOGIC ---
# def trigger_scraper():
#     repo_owner = "jamjayjoshi108"
#     repo_name = "pspcl_daily_outage_dashboard" 
    
#     url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/daily_scrape.yml/dispatches"
#     headers = {
#         "Accept": "application/vnd.github.v3+json",
#         "Authorization": f"token {st.secrets['GITHUB_TOKEN']}"
#     }
#     response = requests.post(url, headers=headers, json={"ref": "main"})
    
#     if response.status_code == 204:
#         st.toast("✅ Scraper triggered successfully in the cloud!")
#         return True
#     else:
#         st.error(f"❌ Failed to trigger scraper. GitHub responded: {response.text}")
#         return False

# # --- 1. FILE CHECKING LOGIC ---
# today_str = datetime.now(IST).strftime("%Y-%m-%d")
# file_today = f"{today_str}_Outages_Today.csv"
# file_5day = f"{today_str}_Outages_Last_5_Days.csv"

# if not os.path.exists(file_today) or not os.path.exists(file_5day):
#     lock_file = "scraper_lock.txt"
#     should_trigger = True
    
#     if os.path.exists(lock_file):
#         if time.time() - os.path.getmtime(lock_file) < 300: 
#             should_trigger = False
            
#     if should_trigger:
#         success = trigger_scraper()
#         if success:
#             with open(lock_file, "w") as f:
#                 f.write(str(time.time()))
#             st.warning(f"⚠️ Data for {today_str} is missing. Automatically fetching fresh data from PSPCL...")
#             st.info("⏳ Please wait ~2 minutes and refresh this page.")
#         else:
#             st.error("🚨 Could not fetch data due to GitHub API error. Fix the token to continue.")
#     else:
#         st.info("⏳ The scraper is currently running in the background. Please wait a moment and refresh.")
        
#     st.stop()

# # --- 2. DATA LOADING LOGIC ---
# @st.cache_data(ttl="10m")
# def load_data(f_today, f_5day):
#     df_today = pd.read_csv(f_today)
#     df_5day = pd.read_csv(f_5day)
    
#     df_today['Type of Outage'] = df_today['Type of Outage'].replace('Power Off By PC', 'Planned Outage')
#     df_5day['Type of Outage'] = df_5day['Type of Outage'].replace('Power Off By PC', 'Planned Outage')
    
#     time_cols = ['Schedule Created At', 'Start Time', 'End Time', 'Last Updated At']
#     for df in [df_today, df_5day]:
#         for col in time_cols:
#             df[col] = pd.to_datetime(df[col], errors='coerce')
            
#         # NEW LOGIC: Use the actual 'Status' column
#         # Maps 'Open' to 'Active'. 'Closed' and 'Cancelled' will both become 'Closed'.
#         df['Status_Calc'] = df['Status'].apply(
#             lambda x: 'Active' if str(x).strip().title() == 'Open' else 'Closed'
#         )
        
#         def assign_bucket(mins):
#             if pd.isna(mins) or mins < 0: return "Active/Unknown"
#             hrs = mins / 60
#             if hrs <= 2: return "Up to 2 Hrs"
#             elif hrs <= 4: return "2-4 Hrs"
#             elif hrs <= 8: return "4-8 Hrs"
#             else: return "Above 8 Hrs"
            
#         df['Duration Bucket'] = df['Diff in mins'].apply(assign_bucket)
        
#     return df_today, df_5day

# df_today, df_5day = load_data(file_today, file_5day)

# st.title("⚡ Power Outage Monitoring Dashboard")

# # --- TOP HALF: SPLIT VIEW ---
# col_left, col_right = st.columns(2, gap="large")

# # ==========================================
# # LEFT PAGE: TODAY'S OUTAGES
# # ==========================================
# with col_left:
#     st.header(f"📅 Today's Outages ({datetime.now(IST).strftime('%d %b %Y')})")
    
#     today_planned = df_today[df_today['Type of Outage'] == 'Planned Outage']
#     today_unplanned = df_today[df_today['Type of Outage'] == 'Unplanned Outage']
    
#     st.subheader("Outage Summary")
#     kpi1, kpi2 = st.columns(2)
    
#     with kpi1:
#         active_p = len(today_planned[today_planned['Status_Calc'] == 'Active'])
#         closed_p = len(today_planned[today_planned['Status_Calc'] == 'Closed'])
#         st.markdown(f'''
#             <div class="kpi-card">
#                 <div>
#                     <div class="kpi-title">Total Planned Outages</div>
#                     <div class="kpi-value">{len(today_planned)}</div>
#                 </div>
#                 <div class="kpi-subtext">
#                     <span class="status-badge">🔴 Active: {active_p}</span> 
#                     <span class="status-badge">🟢 Closed: {closed_p}</span>
#                 </div>
#             </div>
#         ''', unsafe_allow_html=True)
        
#     with kpi2:
#         active_u = len(today_unplanned[today_unplanned['Status_Calc'] == 'Active'])
#         closed_u = len(today_unplanned[today_unplanned['Status_Calc'] == 'Closed'])
#         st.markdown(f'''
#             <div class="kpi-card">
#                 <div>
#                     <div class="kpi-title">Total Unplanned Outages</div>
#                     <div class="kpi-value">{len(today_unplanned)}</div>
#                 </div>
#                 <div class="kpi-subtext">
#                     <span class="status-badge">🔴 Active: {active_u}</span> 
#                     <span class="status-badge">🟢 Closed: {closed_u}</span>
#                 </div>
#             </div>
#         ''', unsafe_allow_html=True)

#     st.divider()

#     # Zone-wise Table
#     st.subheader("Zone-wise Distribution (Today)")
#     if not df_today.empty:
#         zone_today = df_today.groupby(['Zone', 'Type of Outage']).size().unstack(fill_value=0).reset_index()
#         if 'Planned Outage' not in zone_today: zone_today['Planned Outage'] = 0
#         if 'Unplanned Outage' not in zone_today: zone_today['Unplanned Outage'] = 0
#         zone_today['Total'] = zone_today['Planned Outage'] + zone_today['Unplanned Outage']
        
#         st.dataframe(zone_today, use_container_width=True, hide_index=True)
#     else:
#         st.info("No data available for today.")


# # ==========================================
# # RIGHT PAGE: LAST 5 DAYS
# # ==========================================
# with col_right:
#     st.header("⏳ Last 5 Days Trends")
    
#     fiveday_planned = df_5day[df_5day['Type of Outage'] == 'Planned Outage']
#     fiveday_unplanned = df_5day[df_5day['Type of Outage'] == 'Unplanned Outage']
    
#     st.subheader("Outage Summary (5 Days)")
#     kpi3, kpi4 = st.columns(2)
    
#     # NOTE: The hidden kpi-subtext below ensures height alignment with the left column
#     with kpi3:
#         st.markdown(f'''
#             <div class="kpi-card">
#                 <div>
#                     <div class="kpi-title">Total Planned Outages</div>
#                     <div class="kpi-value">{len(fiveday_planned)}</div>
#                 </div>
#                 <div class="kpi-subtext" style="visibility: hidden;">Spacer</div> 
#             </div>
#         ''', unsafe_allow_html=True)
        
#     with kpi4:
#         st.markdown(f'''
#             <div class="kpi-card">
#                 <div>
#                     <div class="kpi-title">Total Unplanned Outages</div>
#                     <div class="kpi-value">{len(fiveday_unplanned)}</div>
#                 </div>
#                 <div class="kpi-subtext" style="visibility: hidden;">Spacer</div>
#             </div>
#         ''', unsafe_allow_html=True)

#     st.divider()

#     # Zone-wise Table
#     st.subheader("Zone-wise Distribution (5 Days)")
#     if not df_5day.empty:
#         zone_5day = df_5day.groupby(['Zone', 'Type of Outage']).size().unstack(fill_value=0).reset_index()
#         if 'Planned Outage' not in zone_5day: zone_5day['Planned Outage'] = 0
#         if 'Unplanned Outage' not in zone_5day: zone_5day['Unplanned Outage'] = 0
#         zone_5day['Total'] = zone_5day['Planned Outage'] + zone_5day['Unplanned Outage']
        
#         st.dataframe(zone_5day, use_container_width=True, hide_index=True)
#     else:
#         st.info("No data available for the last 5 days.")


# # ==========================================
# # BOTTOM HALF: FULL-WIDTH COMBINED SECTION
# # ==========================================
# st.divider()
# st.header("Comprehensive Circle-wise Breakdown")
# bucket_order = ["Up to 2 Hrs", "2-4 Hrs", "4-8 Hrs", "Above 8 Hrs", "Active/Unknown"]

# # 1. Prepare Today Planned Pivot
# if not today_planned.empty:
#     p_pivot = pd.crosstab(today_planned['Circle'], today_planned['Duration Bucket'])
#     p_pivot = p_pivot.reindex(columns=[c for c in bucket_order if c in p_pivot.columns], fill_value=0)
#     p_pivot['Total'] = p_pivot.sum(axis=1)
# else:
#     p_pivot = pd.DataFrame(columns=bucket_order + ['Total'])

# # 2. Prepare 5-Day Unplanned Pivot
# if not fiveday_unplanned.empty:
#     u_pivot = pd.crosstab(fiveday_unplanned['Circle'], fiveday_unplanned['Duration Bucket'])
#     u_pivot = u_pivot.reindex(columns=[c for c in bucket_order if c in u_pivot.columns], fill_value=0)
#     u_pivot['Total'] = u_pivot.sum(axis=1)
# else:
#     u_pivot = pd.DataFrame(columns=bucket_order + ['Total'])

# # 3. Combine both into a single full-width MultiIndex Table
# combined_circle = pd.concat([p_pivot, u_pivot], axis=1, keys=['TODAY (Planned Outages)', 'LAST 5 DAYS (Unplanned Outages)']).fillna(0).astype(int)

# st.markdown("👆 **Click on any row inside the table below** to view the specific Feeder drill-down details.")

# # The table is now interactive. When you click a row, it triggers an event.
# if not combined_circle.empty:
#     selection_event = st.dataframe(
#         combined_circle, 
#         use_container_width=True,
#         on_select="rerun",
#         selection_mode="single-row" 
#     )

#     # 4. Unified Feeder Drill-Down Triggered by Table Click
#     if len(selection_event.selection.rows) > 0:
#         selected_index = selection_event.selection.rows[0]
#         selected_circle = combined_circle.index[selected_index]
        
#         st.subheader(f"Feeder Details for: {selected_circle}")
        
#         # --- ROW 1: TODAY ---
#         today_left, today_right = st.columns(2)
        
#         with today_left:
#             st.markdown(f"**🔴 TODAY: Planned Outages**")
#             feeder_list_tp = today_planned[today_planned['Circle'] == selected_circle][['Feeder', 'Diff in mins', 'Status_Calc', 'Duration Bucket']]
#             feeder_list_tp = feeder_list_tp.rename(columns={'Status_Calc': 'Status'})
#             st.dataframe(feeder_list_tp, use_container_width=True, hide_index=True)
            
#         with today_right:
#             st.markdown(f"**🔴 TODAY: Unplanned Outages**")
#             feeder_list_tu = today_unplanned[today_unplanned['Circle'] == selected_circle][['Feeder', 'Diff in mins', 'Status_Calc', 'Duration Bucket']]
#             feeder_list_tu = feeder_list_tu.rename(columns={'Status_Calc': 'Status'})
#             st.dataframe(feeder_list_tu, use_container_width=True, hide_index=True)
            
#         st.write("") 
        
#         # --- ROW 2: 5-DAYS ---
#         fiveday_left, fiveday_right = st.columns(2)
        
#         with fiveday_left:
#             st.markdown(f"**🟢 5-DAYS: Planned Outages**")
#             feeder_list_fp = fiveday_planned[fiveday_planned['Circle'] == selected_circle].copy()
#             if not feeder_list_fp.empty:
#                 feeder_list_fp['Diff in Hours'] = (feeder_list_fp['Diff in mins'] / 60).round(2)
#                 feeder_list_fp = feeder_list_fp[['Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket']]
#             else:
#                 feeder_list_fp = pd.DataFrame(columns=['Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket'])
#             st.dataframe(feeder_list_fp, use_container_width=True, hide_index=True)
            
#         with fiveday_right:
#             st.markdown(f"**🟢 5-DAYS: Unplanned Outages**")
#             feeder_list_fu = fiveday_unplanned[fiveday_unplanned['Circle'] == selected_circle].copy()
#             if not feeder_list_fu.empty:
#                 feeder_list_fu['Diff in Hours'] = (feeder_list_fu['Diff in mins'] / 60).round(2)
#                 feeder_list_fu = feeder_list_fu[['Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket']]
#             else:
#                 feeder_list_fu = pd.DataFrame(columns=['Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket'])
#             st.dataframe(feeder_list_fu, use_container_width=True, hide_index=True)
# else:
#     st.info("No circle data available.")
