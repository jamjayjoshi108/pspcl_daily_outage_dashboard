import os
import time
import requests
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Power Outage Monitoring Dashboard", layout="wide")

# --- GLOBAL TABLE HEADER STYLING ---
# This applies the Blue background (#004085) and Gold text (#FFC107) to all table headers
HEADER_STYLES = [{
    'selector': 'th',
    'props': [('background-color', '#004085'), ('color', '#FFC107'), ('font-weight', 'bold')]
}]

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

        /* UNIFIED HEADERS: ALL USE IDENTICAL PROFESSIONAL BLUE */
        h1, h2, h3, h4, h5, h6 {
            color: #004085 !important;
            font-weight: 700 !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        h1 {
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

        /* EXECUTIVE KPI CARDS (Protecting inside text colors) */
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

        /* TABLE BORDERS: ENFORCING PROFESSIONAL BLUE */
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

# --- NOTORIOUS FEEDERS CALCULATION ---
df_5day['Outage Date'] = df_5day['Start Time'].dt.date
feeder_days = df_5day.groupby(['Circle', 'Feeder'])['Outage Date'].nunique().reset_index(name='Days with Outages')
notorious = feeder_days[feeder_days['Days with Outages'] >= 3]

feeder_stats = df_5day.groupby(['Circle', 'Feeder']).agg(
    Total_Events=('Start Time', 'size'),
    Avg_Mins=('Diff in mins', 'mean')
).reset_index()

feeder_stats.rename(columns={'Total_Events': 'Total Outage Events'}, inplace=True)
feeder_stats['Average Duration (Hours)'] = (feeder_stats['Avg_Mins'] / 60).round(2)
feeder_stats = feeder_stats.drop(columns=['Avg_Mins'])

notorious = notorious.merge(feeder_stats, on=['Circle', 'Feeder'])
notorious = notorious.sort_values(by=['Circle', 'Days with Outages', 'Total Outage Events'], ascending=[True, False, False])
top_5_notorious = notorious.groupby('Circle').head(5)

notorious_set = set(zip(top_5_notorious['Circle'], top_5_notorious['Feeder']))


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
        
        # Apply header styling
        st.dataframe(zone_today.style.set_table_styles(HEADER_STYLES), use_container_width=True, hide_index=True)
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
        
        # Apply header styling
        st.dataframe(zone_5day.style.set_table_styles(HEADER_STYLES), use_container_width=True, hide_index=True)
    else:
        st.info("No data available for the last 5 days.")


# ==========================================
# MIDDLE SECTION: NOTORIOUS FEEDERS
# ==========================================
st.divider()
st.header("🚨 Notorious Feeders (3+ Days of Outages in Last 5 Days)")
st.caption("Top 5 worst-performing feeders per circle based on continuous outage days.")

if not top_5_notorious.empty:
    circle_options = ["All Circles"] + sorted(top_5_notorious['Circle'].unique().tolist())
    selected_notorious_circle = st.selectbox("Filter by Circle:", options=circle_options, index=0)
    
    if selected_notorious_circle == "All Circles":
        filtered_notorious = top_5_notorious
    else:
        filtered_notorious = top_5_notorious[top_5_notorious['Circle'] == selected_notorious_circle]
        
    # Apply format AND header styling
    styled_notorious = filtered_notorious.style.format({'Average Duration (Hours)': '{:.2f}'}).set_table_styles(HEADER_STYLES)
    st.dataframe(styled_notorious, use_container_width=True, hide_index=True)
else:
    st.info("Excellent! No notorious feeders identified matching this criteria.")


# ==========================================
# BOTTOM HALF: FULL-WIDTH COMBINED SECTION
# ==========================================
st.divider()
st.header("Comprehensive Circle-wise Breakdown")
bucket_order = ["Up to 2 Hrs", "2-4 Hrs", "4-8 Hrs", "Above 8 Hrs", "Active/Unknown"]

if not today_planned.empty:
    p_pivot = pd.crosstab(today_planned['Circle'], today_planned['Duration Bucket'])
    p_pivot = p_pivot.reindex(columns=[c for c in bucket_order if c in p_pivot.columns], fill_value=0)
    p_pivot['Total'] = p_pivot.sum(axis=1)
else:
    p_pivot = pd.DataFrame(columns=bucket_order + ['Total'])

if not fiveday_unplanned.empty:
    u_pivot = pd.crosstab(fiveday_unplanned['Circle'], fiveday_unplanned['Duration Bucket'])
    u_pivot = u_pivot.reindex(columns=[c for c in bucket_order if c in u_pivot.columns], fill_value=0)
    u_pivot['Total'] = u_pivot.sum(axis=1)
else:
    u_pivot = pd.DataFrame(columns=bucket_order + ['Total'])

combined_circle = pd.concat([p_pivot, u_pivot], axis=1, keys=['TODAY (Planned Outages)', 'LAST 5 DAYS (Unplanned Outages)']).fillna(0).astype(int)

st.markdown("👆 **Click on any row inside the table below** to view the specific Feeder drill-down details.")

if not combined_circle.empty:
    # Apply header styling to the main interactive dataframe
    styled_combined = combined_circle.style.set_table_styles(HEADER_STYLES)
    
    selection_event = st.dataframe(
        styled_combined, 
        use_container_width=True,
        on_select="rerun",
        selection_mode="single-row" 
    )

    if len(selection_event.selection.rows) > 0:
        selected_index = selection_event.selection.rows[0]
        selected_circle = combined_circle.index[selected_index]
        
        st.subheader(f"Feeder Details for: {selected_circle}")
        
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
            st.dataframe(styled_tp, use_container_width=True, hide_index=True)
            
        with today_right:
            st.markdown(f"**🔴 TODAY: Unplanned Outages**")
            feeder_list_tu = today_unplanned[today_unplanned['Circle'] == selected_circle][['Feeder', 'Diff in mins', 'Status_Calc', 'Duration Bucket']]
            feeder_list_tu = feeder_list_tu.rename(columns={'Status_Calc': 'Status'})
            styled_tu = feeder_list_tu.style.apply(highlight_notorious, axis=1).set_table_styles(HEADER_STYLES)
            st.dataframe(styled_tu, use_container_width=True, hide_index=True)
            
        st.write("") 
        
        fiveday_left, fiveday_right = st.columns(2)
        
        with fiveday_left:
            st.markdown(f"**🟢 5-DAYS: Planned Outages**")
            feeder_list_fp = fiveday_planned[fiveday_planned['Circle'] == selected_circle].copy()
            if not feeder_list_fp.empty:
                feeder_list_fp['Diff in Hours'] = (feeder_list_fp['Diff in mins'] / 60).round(2)
                feeder_list_fp = feeder_list_fp[['Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket']]
                styled_fp = feeder_list_fp.style.apply(highlight_notorious, axis=1).format({'Diff in Hours': '{:.2f}'}).set_table_styles(HEADER_STYLES)
                st.dataframe(styled_fp, use_container_width=True, hide_index=True)
            else:
                empty_df = pd.DataFrame(columns=['Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket'])
                st.dataframe(empty_df.style.set_table_styles(HEADER_STYLES), use_container_width=True, hide_index=True)
            
        with fiveday_right:
            st.markdown(f"**🟢 5-DAYS: Unplanned Outages**")
            feeder_list_fu = fiveday_unplanned[fiveday_unplanned['Circle'] == selected_circle].copy()
            if not feeder_list_fu.empty:
                feeder_list_fu['Diff in Hours'] = (feeder_list_fu['Diff in mins'] / 60).round(2)
                feeder_list_fu = feeder_list_fu[['Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket']]
                styled_fu = feeder_list_fu.style.apply(highlight_notorious, axis=1).format({'Diff in Hours': '{:.2f}'}).set_table_styles(HEADER_STYLES)
                st.dataframe(styled_fu, use_container_width=True, hide_index=True)
            else:
                empty_df = pd.DataFrame(columns=['Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket'])
                st.dataframe(empty_df.style.set_table_styles(HEADER_STYLES), use_container_width=True, hide_index=True)
else:
    st.info("No circle data available.")

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
