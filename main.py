import os
import time
import requests
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
import pytz

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
        .block-container { padding-top: 1.5rem


# # # # #  =======================================================================================================================================
# # # # #  =======================================================================================================================================
# # # # #V9 ----- working V8 code + API attempt --- removed scrapping in this version
# # # # #  =======================================================================================================================================
# # # # #  =======================================================================================================================================

# import os
# import time
# import requests
# import streamlit as st
# import pandas as pd
# from datetime import datetime, timedelta, timezone

# # --- PAGE CONFIGURATION ---
# st.set_page_config(page_title="Power Outage Monitoring Dashboard", layout="wide")

# # --- GLOBAL TABLE HEADER STYLING ---
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
#         'selector': 'th div',
#         'props': [
#             ('color', '#FFC107 !important'),
#             ('font-weight', 'bold !important')
#         ]
#     }
# ]

# # --- COLOR THEME & ENTERPRISE CSS ---
# st.markdown("""
#     <style>
#         .block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
#         p, span, div, caption, .stMarkdown { color: #000000 !important; }
#         h1, h2, h3, h4, h5, h6, div.block-container h1 { color: #004085 !important; font-weight: 700 !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
#         div.block-container h1 { text-align: center; border-bottom: 3px solid #004085 !important; padding-bottom: 10px; margin-bottom: 30px !important; font-size: 2.2rem !important; }
#         h2 { font-size: 1.3rem !important; border-bottom: 2px solid #004085 !important; padding-bottom: 5px; margin-bottom: 10px !important; }
#         h3 { font-size: 1.05rem !important; margin-bottom: 12px !important; text-transform: uppercase; letter-spacing: 0.5px; }
#         hr { border: 0; border-top: 1px solid #004085; margin: 1.5rem 0; opacity: 0.3; }
        
#         .kpi-card { background: linear-gradient(135deg, #004481 0%, #0066cc 100%); border-radius: 6px; padding: 1.2rem 1.2rem; display: flex; flex-direction: column; justify-content: space-between; height: 100%; box-shadow: 0 2px 4px rgba(0,0,0,0.08); transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out; border: 1px solid #003366; }
#         .kpi-card:hover { transform: translateY(-4px); box-shadow: 0 8px 16px rgba(0, 68, 129, 0.2); }
#         .kpi-card .kpi-title, .kpi-title { color: #FFC107 !important; font-weight: 600; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.4rem; }
#         .kpi-card .kpi-value, .kpi-value { color: #FFFFFF !important; font-weight: 700; font-size: 2.6rem; margin-bottom: 0; line-height: 1.1; }
#         .kpi-card .kpi-subtext, .kpi-subtext { color: #F8F9FA !important; font-size: 0.85rem; margin-top: 1rem; padding-top: 0.6rem; border-top: 1px solid rgba(255, 255, 255, 0.2); display: flex; justify-content: flex-start; gap: 15px; }
        
#         .status-badge { background-color: rgba(0, 0, 0, 0.25); padding: 3px 8px; border-radius: 4px; font-weight: 500; color: #FFFFFF !important; }
#         [data-testid="stDataFrame"] > div { border: 2px solid #004085 !important; border-radius: 6px; overflow: hidden; }
        
#         .loading-text-box { background-color: #F8F9FA; border-left: 4px solid #004085; padding: 10px 15px; border-radius: 4px; font-family: monospace; font-size: 0.95rem; margin-bottom: 10px; }
#     </style>
# """, unsafe_allow_html=True)

# # --- IST TIMEZONE SETUP ---
# IST = timezone(timedelta(hours=5, minutes=30))
# now_ist = datetime.now(IST)

# # --- 1. DATA NORMALIZATION LOGIC ---
# def normalize_api_data(raw_data, is_ptw=False, default_type="Unplanned Outage"):
#     """Translates exact API JSON keys to the dataframe columns expected by the UI."""
#     if not raw_data:
#         return pd.DataFrame()
        
#     df = pd.DataFrame(raw_data)
    
#     rename_map = {
#         'outage_id': 'ID', 'outage_status': 'Status', 'created_time': 'Schedule Created At',
#         'start_time': 'Start Time', 'end_time': 'End Time', 'last_updated': 'Last Updated At',
#         'duration_minutes': 'Diff in mins', 'zone_name': 'Zone', 'circle_name': 'Circle',
#         'division_name': 'Division', 'feeder_name': 'Feeder', 'outage_type': 'Type of Outage',
#         'ptw_id': 'ID', 'current_status': 'Status', 'feeders': 'Feeder'
#     }
    
#     df.rename(columns=lambda x: rename_map.get(str(x).lower().strip(), x), inplace=True)
    
#     if 'Feeder' in df.columns:
#         if df['Feeder'].apply(lambda x: isinstance(x, list)).any():
#             df = df.explode('Feeder')
#         df['Feeder'] = df['Feeder'].astype(str).str.strip()
        
#     if 'Type of Outage' not in df.columns and not is_ptw:
#         df['Type of Outage'] = default_type
        
#     for req_col in ['Zone', 'Circle', 'Feeder', 'ID']:
#         if req_col not in df.columns:
#             df[req_col] = "Unknown"
            
#     if 'Start Time' in df.columns and 'End Time' in df.columns:
#         df['Start Time'] = pd.to_datetime(df['Start Time'], errors='coerce')
#         df['End Time'] = pd.to_datetime(df['End Time'], errors='coerce')
#         if 'Diff in mins' not in df.columns:
#             df['Diff in mins'] = (df['End Time'] - df['Start Time']).dt.total_seconds() / 60.0
            
#     return clean_outage_data(df)


# # --- 2. DATA CLEANING LOGIC ---
# def clean_outage_data(df):
#     """Standardizes dates, buckets, and removes cancelled outages."""
#     if df.empty: return df
    
#     if 'Status' in df.columns:
#         df = df[~df['Status'].astype(str).str.contains('Cancel', na=False, case=False)]
#         df['Status_Calc'] = df['Status'].apply(lambda x: 'Active' if str(x).strip().title() == 'Open' else 'Closed')
#     else:
#         df['Status_Calc'] = 'Closed'
        
#     time_cols = ['Schedule Created At', 'Start Time', 'End Time', 'Last Updated At']
#     for col in time_cols:
#         if col in df.columns:
#             df[col] = pd.to_datetime(df[col], errors='coerce')
            
#     if 'Diff in mins' in df.columns:
#         df['Diff in mins'] = pd.to_numeric(df['Diff in mins'], errors='coerce').fillna(0)
#         def assign_bucket(mins):
#             if pd.isna(mins) or mins < 0: return "Active/Unknown"
#             hrs = mins / 60
#             if hrs <= 2: return "Up to 2 Hrs"
#             elif hrs <= 4: return "2-4 Hrs"
#             elif hrs <= 8: return "4-8 Hrs"
#             else: return "Above 8 Hrs"
#         df['Duration Bucket'] = df['Diff in mins'].apply(assign_bucket)
        
#     if 'Start Time' in df.columns:
#         df['Outage Date'] = df['Start Time'].dt.date
        
#     return df


# # --- 3. DYNAMIC API FETCHING LOGIC (NO @st.cache_data HERE) ---
# def fetch_api_with_ui(progress_bar, status_text, endpoint, api_name, start_date, end_date, default_type, is_ptw):
#     """Fetches data from API in strict 30-day buckets, updating the provided Streamlit UI placeholders."""
#     base_url = "https://distribution.pspcl.in"
#     url = f"{base_url}/returns/module.php?to={endpoint}"
#     api_key = "pdc@12345"
    
#     all_data = []
#     current_start = start_date
#     total_days = (end_date - start_date).days + 1
    
#     if total_days <= 0:
#         progress_bar.progress(1.0)
#         status_text.success(f"✅ **{api_name}**: Date range is zero or negative. Loaded 0 records.")
#         return pd.DataFrame()

#     start_time = time.time()
    
#     while current_start <= end_date:
#         current_end = min(current_start + timedelta(days=29), end_date)
        
#         days_processed = (current_start - start_date).days
#         pct_complete = min(days_processed / total_days, 0.99)
#         elapsed = time.time() - start_time
        
#         progress_bar.progress(pct_complete)
#         status_text.markdown(f"""
#             <div class="loading-text-box">
#                 <b>📡 API Target:</b> {api_name}<br/>
#                 <b>⏳ Fetching Bucket:</b> {current_start.strftime('%d %b %Y')} to {current_end.strftime('%d %b %Y')}<br/>
#                 <b>📊 Progress:</b> {int(pct_complete * 100)}% Complete<br/>
#                 <b>⏱️ Time Elapsed:</b> {elapsed:.1f} seconds
#             </div>
#         """, unsafe_allow_html=True)
        
#         payload = {
#             "fromdate": current_start.strftime("%Y-%m-%d"),
#             "todate": current_end.strftime("%Y-%m-%d"),
#             "apikey": api_key
#         }
        
#         try:
#             response = requests.post(url, json=payload, timeout=30)
#             if response.status_code == 200:
#                 data = response.json()
#                 if isinstance(data, list):
#                     all_data.extend(data)
#         except Exception as e:
#             st.error(f"API Error fetching {current_start.strftime('%Y-%m-%d')}: {e}")
            
#         current_start = current_end + timedelta(days=1)
        
#     final_time = time.time() - start_time
#     progress_bar.progress(1.0)
#     status_text.success(f"✅ **{api_name} Data Fetched Successfully!** (100% Complete) | **Total Time:** {final_time:.1f}s | **Total Records:** {len(all_data):,}")
    
#     return normalize_api_data(all_data, is_ptw=is_ptw, default_type=default_type)

# @st.cache_data(show_spinner=False)
# def load_historical_ly():
#     df_25 = pd.read_csv('Historical_2025.csv') if os.path.exists('Historical_2025.csv') else pd.DataFrame()
#     return clean_outage_data(df_25)


# # --- UI TITLE ---
# st.title("⚡ Power Outage Monitoring Dashboard")

# # --- MANUAL CACHE & REAL-TIME LOADING UI ---
# outage_api_start = datetime(2026, 1, 1).date()
# ptw_api_start = datetime(2025, 11, 1).date()
# api_end_date = now_ist.date()

# cache_ttl = 15 * 60 # 15 minutes in seconds

# # Check if data needs to be loaded (either first load, or 15 mins have passed)
# if "last_fetch_time" not in st.session_state or (time.time() - st.session_state.last_fetch_time) > cache_ttl:
#     with st.status("🔄 Initializing Dashboard Data...", expanded=True) as status:
#         st.markdown("### 🔌 Outages Data Tracker")
#         pb_outages = st.progress(0)
#         st_outages = st.empty()
#         df_master = fetch_api_with_ui(pb_outages, st_outages, "OutageAPI.getOutages", "Outages API", outage_api_start, api_end_date, "Unplanned Outage", False)
        
#         st.divider()
        
#         st.markdown("### 🛠️ PTW Requests Tracker")
#         pb_ptw = st.progress(0)
#         st_ptw = st.empty()
#         df_ptw = fetch_api_with_ui(pb_ptw, st_ptw, "OutageAPI.getPTWRequests", "PTW API", ptw_api_start, api_end_date, "Planned Outage", True)
        
#         st.divider()
        
#         st.markdown("### 🕰️ Historical Data Tracker")
#         st.info("Loading 2025 Historical Baseline (Local CSV)...")
#         df_hist_ly = load_historical_ly()
#         st.success("✅ 2025 Historical Data Loaded Successfully!")
        
#         status.update(label="✅ All Dashboard Data Synchronized and Ready!", state="complete", expanded=False)
        
#         # Save to custom session_state cache
#         st.session_state.df_master = df_master
#         st.session_state.df_ptw = df_ptw
#         st.session_state.df_hist_ly = df_hist_ly
#         st.session_state.last_fetch_time = time.time()
# else:
#     # Load instantly from session_state if data is still fresh
#     df_master = st.session_state.df_master
#     df_ptw = st.session_state.df_ptw
#     df_hist_ly = st.session_state.df_hist_ly

# # Duplicate master for YoY logic
# df_hist_curr = df_master.copy()


# # --- 4. DASHBOARD HELPER FUNCTIONS ---
# def render_date_selector(tab_key):
#     st.markdown("📅 **Select Time Period:**")
    
#     period = st.radio(
#         "Select Time Period",
#         options=["Today", "Current Month", "Last Month", "Last 3 Months", "Last 6 Months", "Custom"],
#         horizontal=True,
#         label_visibility="collapsed",
#         key=f"{tab_key}_radio"
#     )
    
#     today = now_ist.date()
    
#     if period == "Today":
#         calc_start, calc_end = today, today
#     elif period == "Current Month":
#         calc_start, calc_end = today.replace(day=1), today
#     elif period == "Last Month":
#         first_of_this_month = today.replace(day=1)
#         last_of_last_month = first_of_this_month - timedelta(days=1)
#         calc_start, calc_end = last_of_last_month.replace(day=1), last_of_last_month
#     elif period == "Last 3 Months":
#         calc_start, calc_end = today - timedelta(days=90), today
#     elif period == "Last 6 Months":
#         calc_start, calc_end = today - timedelta(days=180), today
#     else: 
#         calc_start = st.session_state.get(f"{tab_key}_custom_start", today)
#         calc_end = st.session_state.get(f"{tab_key}_custom_end", today)

#     col1, col2 = st.columns(2)
#     with col1:
#         start_date = st.date_input("From Date", value=calc_start, format="DD/MM/YYYY", disabled=(period != "Custom"))
#     with col2:
#         end_date = st.date_input("To Date", value=calc_end, format="DD/MM/YYYY", disabled=(period != "Custom"))
        
#     if period == "Custom":
#         st.session_state[f"{tab_key}_custom_start"] = start_date
#         st.session_state[f"{tab_key}_custom_end"] = end_date
        
#     return start_date, end_date

# def safe_ly_date(dt):
#     try: return dt.replace(year=dt.year - 1)
#     except ValueError: return dt.replace(year=dt.year - 1, day=28)

# def generate_yoy_dist_expanded(df_curr, df_ly, group_col):
#     def _agg(df, prefix):
#         if df.empty: return pd.DataFrame({group_col: []}).set_index(group_col)
#         df['Diff in mins'] = pd.to_numeric(df['Diff in mins'], errors='coerce').fillna(0)
#         g = df.groupby([group_col, 'Type of Outage']).agg(
#             Count=('Type of Outage', 'size'),
#             TotalHrs=('Diff in mins', lambda x: round(x.sum() / 60, 2)),
#             AvgHrs=('Diff in mins', lambda x: round(x.mean() / 60, 2))
#         ).unstack(fill_value=0)
#         g.columns = [f"{prefix} {outage} ({metric})" for metric, outage in g.columns]
#         return g

#     c_grp = _agg(df_curr, 'Curr')
#     l_grp = _agg(df_ly, 'LY')
#     merged = pd.merge(c_grp, l_grp, on=group_col, how='outer').fillna(0).reset_index()
    
#     expected_cols = []
#     for prefix in ['Curr', 'LY']:
#         for outage in ['Planned Outage', 'Unplanned Outage']:
#             for metric in ['Count', 'TotalHrs', 'AvgHrs']:
#                 col_name = f"{prefix} {outage} ({metric})"
#                 expected_cols.append(col_name)
#                 if col_name not in merged.columns: merged[col_name] = 0
                    
#     for col in expected_cols:
#         if '(Count)' in col: merged[col] = merged[col].astype(int)
#         else: merged[col] = merged[col].astype(float).round(2)
            
#     merged['Curr Total (Count)'] = merged['Curr Planned Outage (Count)'] + merged['Curr Unplanned Outage (Count)']
#     merged['LY Total (Count)'] = merged['LY Planned Outage (Count)'] + merged['LY Unplanned Outage (Count)']
#     merged['YoY Delta (Total)'] = merged['Curr Total (Count)'] - merged['LY Total (Count)']
    
#     cols_order = [group_col, 
#                   'Curr Planned Outage (Count)', 'Curr Planned Outage (TotalHrs)', 'Curr Planned Outage (AvgHrs)',
#                   'LY Planned Outage (Count)', 'LY Planned Outage (TotalHrs)', 'LY Planned Outage (AvgHrs)',
#                   'Curr Unplanned Outage (Count)', 'Curr Unplanned Outage (TotalHrs)', 'Curr Unplanned Outage (AvgHrs)',
#                   'LY Unplanned Outage (Count)', 'LY Unplanned Outage (TotalHrs)', 'LY Unplanned Outage (AvgHrs)',
#                   'Curr Total (Count)', 'LY Total (Count)', 'YoY Delta (Total)']
#     cols_order = [c for c in cols_order if c in merged.columns]
#     merged = merged[cols_order]

#     if not merged.empty:
#         gt_row = pd.Series(index=cols_order, dtype=object)
#         gt_row[group_col] = 'Grand Total'
#         for col in cols_order:
#             if col == group_col: continue
#             if '(Count)' in col or 'Delta' in col or '(TotalHrs)' in col:
#                 gt_row[col] = merged[col].sum()
        
#         for prefix in ['Curr', 'LY']:
#             for outage in ['Planned Outage', 'Unplanned Outage']:
#                 count_col = f"{prefix} {outage} (Count)"
#                 tot_col = f"{prefix} {outage} (TotalHrs)"
#                 avg_col = f"{prefix} {outage} (AvgHrs)"
#                 if count_col in cols_order and tot_col in cols_order and avg_col in cols_order:
#                     gt_row[avg_col] = round(gt_row[tot_col] / gt_row[count_col], 2) if gt_row[count_col] > 0 else 0
        
#         merged = pd.concat([merged, pd.DataFrame([gt_row])], ignore_index=True)

#     return merged

# def apply_pu_gradient(styler, df):
#     p_cols = [c for c in df.columns if 'Planned' in str(c) and pd.api.types.is_numeric_dtype(df[c])]
#     u_cols = [c for c in df.columns if 'Unplanned' in str(c) and pd.api.types.is_numeric_dtype(df[c])]
#     pc_cols = [c for c in df.columns if 'Power Off By PC' in str(c) and pd.api.types.is_numeric_dtype(df[c])]
    
#     if 'Grand Total' in df.index: row_idx = df.index.drop('Grand Total')
#     else:
#         try:
#             group_col = df.columns[0]
#             if not df.empty and df.iloc[-1][group_col] == 'Grand Total': row_idx = df.index[:-1]
#             else: row_idx = df.index
#         except: row_idx = df.index
            
#     if p_cols: styler = styler.background_gradient(subset=pd.IndexSlice[row_idx, p_cols], cmap='Blues', vmin=0)
#     if pc_cols: styler = styler.background_gradient(subset=pd.IndexSlice[row_idx, pc_cols], cmap='Purples', vmin=0)
#     if u_cols: styler = styler.background_gradient(subset=pd.IndexSlice[row_idx, u_cols], cmap='Reds', vmin=0)
#     return styler

# def highlight_delta(val):
#     if isinstance(val, (int, float)):
#         if val > 0: return 'color: #D32F2F; font-weight: bold;'
#         elif val < 0: return 'color: #388E3C; font-weight: bold;'
#     return ''

# def create_bucket_pivot(df, bucket_order):
#     if df.empty: return pd.DataFrame(columns=bucket_order + ['Total'])
#     pivot = pd.crosstab(df['Circle'], df['Duration Bucket'])
#     pivot = pivot.reindex(columns=[c for c in bucket_order if c in pivot.columns], fill_value=0)
#     pivot['Total'] = pivot.sum(axis=1)
#     return pivot


# # --- TABS RENDERING ---
# tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📈 YoY Comparison", "🛠️ PTW Frequency"])

# # ==========================================
# # TAB 1: DASHBOARD (Unified & Filtered)
# # ==========================================
# with tab1:
#     st.header("📊 Outage Dashboard")
#     start_d1, end_d1 = render_date_selector("tab1")
#     st.divider()

#     if not df_master.empty:
#         df_master['Outage Date'] = pd.to_datetime(df_master['Outage Date']).dt.date
#         mask_t1 = (df_master['Outage Date'] >= start_d1) & (df_master['Outage Date'] <= end_d1)
#         filtered_tab1 = df_master[mask_t1].copy()
#     else:
#         filtered_tab1 = pd.DataFrame()

#     if filtered_tab1.empty:
#         st.info("No outage data found for the selected time period.")
#     else:
#         planned_df = filtered_tab1[filtered_tab1['Type of Outage'] == 'Planned Outage']
#         pc_df = filtered_tab1[filtered_tab1['Type of Outage'] == 'Power Off By PC']
#         unplanned_df = filtered_tab1[filtered_tab1['Type of Outage'] == 'Unplanned Outage']

#         # --- 1. KPI WIDGETS ---
#         def get_counts(df_sub):
#             has_status = 'Status_Calc' in df_sub.columns
#             if 'ID' in df_sub.columns:
#                 tot = df_sub['ID'].nunique()
#                 act = df_sub[df_sub['Status_Calc'] == 'Active']['ID'].nunique() if has_status else 0
#                 clo = df_sub[df_sub['Status_Calc'] == 'Closed']['ID'].nunique() if has_status else tot
#             else:
#                 tot = len(df_sub)
#                 act = len(df_sub[df_sub['Status_Calc'] == 'Active']) if has_status else 0
#                 clo = len(df_sub[df_sub['Status_Calc'] == 'Closed']) if has_status else tot
#             return tot, act, clo

#         tot_p, act_p, clo_p = get_counts(planned_df)
#         tot_pc, act_pc, clo_pc = get_counts(pc_df)
#         tot_u, act_u, clo_u = get_counts(unplanned_df)

#         kpi1, kpi2, kpi3 = st.columns(3)
#         with kpi1:
#             st.markdown(f'<div class="kpi-card"><div><div class="kpi-title">Planned Outages</div><div class="kpi-value">{tot_p}</div></div><div class="kpi-subtext"><span class="status-badge">🔴 Active: {act_p}</span> <span class="status-badge">🟢 Closed: {clo_p}</span></div></div>', unsafe_allow_html=True)
#         with kpi2:
#             st.markdown(f'<div class="kpi-card"><div><div class="kpi-title">Power Off By PC</div><div class="kpi-value">{tot_pc}</div></div><div class="kpi-subtext"><span class="status-badge">🔴 Active: {act_pc}</span> <span class="status-badge">🟢 Closed: {clo_pc}</span></div></div>', unsafe_allow_html=True)
#         with kpi3:
#             st.markdown(f'<div class="kpi-card"><div><div class="kpi-title">Unplanned Outages</div><div class="kpi-value">{tot_u}</div></div><div class="kpi-subtext"><span class="status-badge">🔴 Active: {act_u}</span> <span class="status-badge">🟢 Closed: {clo_u}</span></div></div>', unsafe_allow_html=True)

#         st.divider()

#         # --- 2. ZONE-WISE DISTRIBUTION ---
#         st.subheader("📍 Zone-wise Distribution")
#         zone_df = filtered_tab1.groupby(['Zone', 'Type of Outage']).size().unstack(fill_value=0).reset_index()
#         for col in ['Planned Outage', 'Power Off By PC', 'Unplanned Outage']:
#             if col not in zone_df: zone_df[col] = 0
            
#         zone_df['Total'] = zone_df['Planned Outage'] + zone_df['Power Off By PC'] + zone_df['Unplanned Outage']
#         gt_row_zone = pd.Series(zone_df.sum(numeric_only=True), name='Grand Total')
#         gt_row_zone['Zone'] = 'Grand Total'
#         zone_df = pd.concat([zone_df, pd.DataFrame([gt_row_zone])], ignore_index=True)
        
#         st.dataframe(apply_pu_gradient(zone_df.style, zone_df).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)

#         st.divider()

#         # --- 3. NOTORIOUS FEEDERS ---
#         st.subheader("🚨 Notorious Feeders (3+ Days of Outages)")
#         st.caption("Top 5 worst-performing feeders per circle based on days with outages in the selected period.")

#         noto_col1, noto_col2 = st.columns(2)
#         all_circles = sorted(filtered_tab1['Circle'].dropna().unique().tolist())
#         with noto_col1: selected_notorious_circle = st.selectbox("Filter by Circle:", ["All Circles"] + all_circles, index=0, key="noto_circ")
#         with noto_col2: selected_notorious_type = st.selectbox("Filter by Outage Type:", ["All Types", "Planned Outage", "Power Off By PC", "Unplanned Outage"], index=0, key="noto_type")

#         dyn_noto_df = filtered_tab1.copy()
#         if selected_notorious_type != "All Types": dyn_noto_df = dyn_noto_df[dyn_noto_df['Type of Outage'] == selected_notorious_type]

#         if not dyn_noto_df.empty:
#             dyn_days = dyn_noto_df.groupby(['Circle', 'Feeder'])['Outage Date'].nunique().reset_index(name='Days with Outages')
#             dyn_noto = dyn_days[dyn_days['Days with Outages'] >= 3]

#             if not dyn_noto.empty:
#                 dyn_stats = dyn_noto_df.groupby(['Circle', 'Feeder']).agg(Total_Events=('Start Time', 'size'), Max_Mins=('Diff in mins', 'max'), Total_Mins=('Diff in mins', 'sum')).reset_index()
#                 dyn_stats.rename(columns={'Total_Events': 'Total Outage Events'}, inplace=True)
#                 dyn_stats['Total Duration (Hours)'] = (dyn_stats['Total_Mins'] / 60).round(2)
#                 dyn_stats['Max Duration (Hours)'] = (dyn_stats['Max_Mins'] / 60).round(2)
#                 dyn_stats = dyn_stats.drop(columns=['Max_Mins', 'Total_Mins'])

#                 dyn_noto = dyn_noto.merge(dyn_stats, on=['Circle', 'Feeder']).sort_values(by=['Circle', 'Days with Outages', 'Total Outage Events'], ascending=[True, False, False])
#                 dyn_top5 = dyn_noto.groupby('Circle').head(5)
                
#                 global_notorious_set = set(zip(dyn_top5['Circle'], dyn_top5['Feeder']))
                
#                 filtered_notorious = dyn_top5[dyn_top5['Circle'] == selected_notorious_circle] if selected_notorious_circle != "All Circles" else dyn_top5

#                 if not filtered_notorious.empty:
#                     st.dataframe(filtered_notorious.style.format({'Max Duration (Hours)': '{:.2f}', 'Total Duration (Hours)': '{:.2f}'}).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#                 else: st.info(f"No notorious feeders found for {selected_notorious_circle} matching the criteria.")
#             else: 
#                 global_notorious_set = set()
#                 st.info(f"No notorious feeders identified (no feeder had 3+ days of outages in this timeframe).")
#         else: 
#             global_notorious_set = set()
#             st.info("No data available for the selected outage type.")

#         st.divider()

#         # --- 4. COMPREHENSIVE CIRCLE-WISE BREAKDOWN & DRILLDOWN ---
#         st.subheader("🔌 Comprehensive Circle-wise Breakdown")
#         st.markdown(" **Click on any row inside the table below** to view the specific Feeder drill-down details.")

#         bucket_order = ["Up to 2 Hrs", "2-4 Hrs", "4-8 Hrs", "Above 8 Hrs", "Active/Unknown"]
#         p_piv = create_bucket_pivot(planned_df, bucket_order)
#         pc_piv = create_bucket_pivot(pc_df, bucket_order)
#         u_piv = create_bucket_pivot(unplanned_df, bucket_order)

#         circle_piv = pd.concat(
#             [p_piv, pc_piv, u_piv], 
#             axis=1, 
#             keys=['Planned Outages', 'Power Off By PC', 'Unplanned Outages']
#         ).fillna(0).astype(int)

#         if not circle_piv.empty:
#             circle_piv[('Overall Total', 'Total Events')] = circle_piv.loc[:, (slice(None), 'Total')].sum(axis=1)
#             circle_piv.loc['Grand Total'] = circle_piv.sum(numeric_only=True)

#             styled_circle = apply_pu_gradient(circle_piv.style, circle_piv).set_table_styles(HEADER_STYLES)
            
#             selection_circle = st.dataframe(styled_circle, width="stretch", on_select="rerun", selection_mode="single-row")

#             if len(selection_circle.selection.rows) > 0:
#                 selected_circle = circle_piv.index[selection_circle.selection.rows[0]]
                
#                 if selected_circle != 'Grand Total':
#                     st.markdown(f"#### 🔍 Feeder Details for: **{selected_circle}**")
#                     def highlight_noto(row): return ['background-color: rgba(220, 53, 69, 0.15); color: #850000; font-weight: bold'] * len(row) if (selected_circle, row['Feeder']) in global_notorious_set else [''] * len(row)

#                     c_left, c_mid, c_right = st.columns(3)
#                     cols_to_show = ['Outage Date', 'Feeder', 'Diff in mins', 'Status_Calc', 'Duration Bucket']
#                     format_dict = {'Diff in Hours': '{:.2f}'}
                    
#                     def prep_feeder_df(df_sub):
#                         if df_sub.empty: return pd.DataFrame(columns=['Outage Date', 'Feeder', 'Diff in Hours', 'Status', 'Duration Bucket'])
#                         res = df_sub[df_sub['Circle'] == selected_circle][cols_to_show].rename(columns={'Status_Calc': 'Status'}).copy()
#                         res['Diff in Hours'] = (res['Diff in mins'] / 60).round(2)
#                         return res.drop(columns=['Diff in mins'])

#                     with c_left:
#                         st.markdown(f"**🔵 Planned Outages**")
#                         st.dataframe(prep_feeder_df(planned_df).style.apply(highlight_noto, axis=1).format(format_dict).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#                     with c_mid:
#                         st.markdown(f"**🟣 Power Off By PC**")
#                         st.dataframe(prep_feeder_df(pc_df).style.apply(highlight_noto, axis=1).format(format_dict).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#                     with c_right:
#                         st.markdown(f"**🔴 Unplanned Outages**")
#                         st.dataframe(prep_feeder_df(unplanned_df).style.apply(highlight_noto, axis=1).format(format_dict).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)


# # ==========================================
# # TAB 2: DYNAMIC YOY DRILL-DOWN
# # ==========================================
# with tab2:
#     st.header("📈 Historical Year-over-Year Drilldown")
#     start_d2, end_d2 = render_date_selector("tab2")
#     st.divider()
    
#     if df_hist_curr.empty or df_hist_ly.empty:
#         st.error("Historical Master Data not found or API returned empty for current year.")
#     else:
#         ly_start_d2 = safe_ly_date(start_d2)
#         ly_end_d2 = safe_ly_date(end_d2)
        
#         df_hist_curr['Outage Date'] = pd.to_datetime(df_hist_curr['Outage Date']).dt.date
#         mask_curr = (df_hist_curr['Outage Date'] >= start_d2) & (df_hist_curr['Outage Date'] <= end_d2)
#         filtered_curr = df_hist_curr[mask_curr]
        
#         df_hist_ly['Outage Date'] = pd.to_datetime(df_hist_ly['Outage Date']).dt.date
#         mask_ly = (df_hist_ly['Outage Date'] >= ly_start_d2) & (df_hist_ly['Outage Date'] <= ly_end_d2)
#         filtered_ly = df_hist_ly[mask_ly]

#         st.markdown(f"### 📍 1. Zone-wise Distribution")
#         st.caption("Includes total counts, total hours, and average hours. Click any row to drill down.")
        
#         yoy_zone = generate_yoy_dist_expanded(filtered_curr, filtered_ly, 'Zone')
        
#         zone_selection = st.dataframe(
#             yoy_zone.style.map(highlight_delta, subset=['YoY Delta (Total)']).format(precision=2).set_table_styles(HEADER_STYLES), 
#             width="stretch", hide_index=True, on_select="rerun", selection_mode="single-row"
#         )

#         if len(zone_selection.selection.rows) > 0:
#             selected_zone = yoy_zone.iloc[zone_selection.selection.rows[0]]['Zone']
            
#             if selected_zone != 'Grand Total':
#                 st.markdown(f"### 🎯 2. Circle-wise Distribution for **{selected_zone}**")
#                 st.caption("Click any row to drill down into Feeder-wise data.")
                
#                 curr_zone_df = filtered_curr[filtered_curr['Zone'] == selected_zone]
#                 ly_zone_df = filtered_ly[filtered_ly['Zone'] == selected_zone]
                
#                 yoy_circle = generate_yoy_dist_expanded(curr_zone_df, ly_zone_df, 'Circle')
                
#                 circle_selection = st.dataframe(
#                     yoy_circle.style.map(highlight_delta, subset=['YoY Delta (Total)']).format(precision=2).set_table_styles(HEADER_STYLES), 
#                     width="stretch", hide_index=True, on_select="rerun", selection_mode="single-row"
#                 )

#                 if len(circle_selection.selection.rows) > 0:
#                     selected_circle = yoy_circle.iloc[circle_selection.selection.rows[0]]['Circle']
                    
#                     if selected_circle != 'Grand Total':
#                         st.markdown(f"### 🔌 3. Feeder-wise Distribution for **{selected_circle}**")
                        
#                         curr_circle_df = curr_zone_df[curr_zone_df['Circle'] == selected_circle]
#                         ly_circle_df = ly_zone_df[ly_zone_df['Circle'] == selected_circle]
                        
#                         yoy_feeder = generate_yoy_dist_expanded(curr_circle_df, ly_circle_df, 'Feeder')
#                         st.dataframe(yoy_feeder.style.map(highlight_delta, subset=['YoY Delta (Total)']).format(precision=2).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)


# # ==========================================
# # TAB 3: PTW FREQUENCY
# # ==========================================
# with tab3:
#     st.header("🛠️ PTW Frequency Tracker")
#     start_d3, end_d3 = render_date_selector("tab3")
#     st.divider()
    
#     st.markdown("Identifies specific feeders that had a Permit to Work (PTW) taken against them **two or more times** in separate requests over the selected timeframe.")

#     if df_ptw.empty:
#         st.info("No PTW data available in the current timeframe.")
#     else:
#         ptw_col = 'ID'
#         feeder_col = 'Feeder'
#         status_col = 'Status'
#         circle_col = 'Circle'
        
#         if 'Start Time' in df_ptw.columns:
#             df_ptw['Temp_Date'] = pd.to_datetime(df_ptw['Start Time'], errors='coerce').dt.date
#             mask_ptw = (df_ptw['Temp_Date'] >= start_d3) & (df_ptw['Temp_Date'] <= end_d3)
#             filtered_ptw = df_ptw[mask_ptw].copy()
#         else:
#             filtered_ptw = df_ptw.copy()
            
#         if filtered_ptw.empty:
#             st.warning("⚠️ No PTW data found for the selected time period.")
#         else:
#             if ptw_col not in filtered_ptw.columns or feeder_col not in filtered_ptw.columns:
#                 st.error("Required columns missing from PTW data after normalization.")
#             else:
#                 ptw_clean = filtered_ptw.copy()
                
#                 if status_col in ptw_clean.columns:
#                     ptw_clean = ptw_clean[~ptw_clean[status_col].astype(str).str.contains('Cancel', na=False, case=False)]

#                 ptw_clean = ptw_clean[ptw_clean[feeder_col] != '']

#                 group_cols = [feeder_col]
#                 if circle_col in ptw_clean.columns: 
#                     group_cols.insert(0, circle_col)
                    
#                 ptw_counts = ptw_clean.groupby(group_cols).agg(
#                     Unique_PTWs=(ptw_col, 'nunique'), 
#                     PTW_IDs=(ptw_col, lambda x: ', '.join(x.dropna().astype(str).unique()))
#                 ).reset_index()
                
#                 repeat_feeders = ptw_counts[ptw_counts['Unique_PTWs'] >= 2].sort_values(by='Unique_PTWs', ascending=False)
#                 repeat_feeders = repeat_feeders.rename(columns={'Unique_PTWs': 'PTW Request Count', 'PTW_IDs': 'Associated PTW Request Numbers'})

#                 if not repeat_feeders.empty:
#                     gt_dict = {c: '' for c in repeat_feeders.columns}
#                     gt_dict[repeat_feeders.columns[0]] = 'Grand Total'
#                     gt_dict['PTW Request Count'] = int(repeat_feeders['PTW Request Count'].sum())
#                     repeat_feeders = pd.concat([repeat_feeders, pd.DataFrame([gt_dict])], ignore_index=True)

#                 kpi1, kpi2 = st.columns(2)
#                 with kpi1: st.markdown(f'<div class="kpi-card"><div><div class="kpi-title">Total Active PTW Requests</div><div class="kpi-value">{filtered_ptw[ptw_col].nunique()}</div></div><div class="kpi-subtext"><span class="status-badge">Selected Timeframe</span></div></div>', unsafe_allow_html=True)
#                 with kpi2: st.markdown(f'<div class="kpi-card"><div><div class="kpi-title">Feeders with Multiple PTWs</div><div class="kpi-value">{len(repeat_feeders) - 1 if not repeat_feeders.empty else 0}</div></div><div class="kpi-subtext"><span class="status-badge" style="background-color: #D32F2F;">🔴 Needs Review</span></div></div>', unsafe_allow_html=True) 

#                 st.divider()
#                 st.subheader("⚠️ Repeat PTW Feeders Detail View")
#                 if not repeat_feeders.empty:
#                     st.dataframe(repeat_feeders.style.set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#                 else:
#                     st.success("No feeders had multiple PTWs requested against them in the selected timeframe! 🎉")
# # # #  =======================================================================================================================================
# # # #  =======================================================================================================================================
# # # #V8
# # # #  =======================================================================================================================================
# # # #  =======================================================================================================================================

# import os
# import time
# import requests
# import streamlit as st
# import pandas as pd
# from datetime import datetime, timedelta, timezone

# # --- PAGE CONFIGURATION ---
# st.set_page_config(page_title="Power Outage Monitoring Dashboard", layout="wide")

# # --- GLOBAL TABLE HEADER STYLING ---
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
#         'selector': 'th div',
#         'props': [
#             ('color', '#FFC107 !important'),
#             ('font-weight', 'bold !important')
#         ]
#     }
# ]

# # --- COLOR THEME & ENTERPRISE CSS ---
# st.markdown("""
#     <style>
#         .block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
#         p, span, div, caption, .stMarkdown { color: #000000 !important; }
#         h1, h2, h3, h4, h5, h6, div.block-container h1 { color: #004085 !important; font-weight: 700 !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
#         div.block-container h1 { text-align: center; border-bottom: 3px solid #004085 !important; padding-bottom: 10px; margin-bottom: 30px !important; font-size: 2.2rem !important; }
#         h2 { font-size: 1.3rem !important; border-bottom: 2px solid #004085 !important; padding-bottom: 5px; margin-bottom: 10px !important; }
#         h3 { font-size: 1.05rem !important; margin-bottom: 12px !important; text-transform: uppercase; letter-spacing: 0.5px; }
#         hr { border: 0; border-top: 1px solid #004085; margin: 1.5rem 0; opacity: 0.3; }
        
#         .kpi-card { background: linear-gradient(135deg, #004481 0%, #0066cc 100%); border-radius: 6px; padding: 1.2rem 1.2rem; display: flex; flex-direction: column; justify-content: space-between; height: 100%; box-shadow: 0 2px 4px rgba(0,0,0,0.08); transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out; border: 1px solid #003366; }
#         .kpi-card:hover { transform: translateY(-4px); box-shadow: 0 8px 16px rgba(0, 68, 129, 0.2); }
#         .kpi-card .kpi-title, .kpi-title { color: #FFC107 !important; font-weight: 600; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.4rem; }
#         .kpi-card .kpi-value, .kpi-value { color: #FFFFFF !important; font-weight: 700; font-size: 2.6rem; margin-bottom: 0; line-height: 1.1; }
#         .kpi-card .kpi-subtext, .kpi-subtext { color: #F8F9FA !important; font-size: 0.85rem; margin-top: 1rem; padding-top: 0.6rem; border-top: 1px solid rgba(255, 255, 255, 0.2); display: flex; justify-content: flex-start; gap: 15px; }
        
#         .status-badge { background-color: rgba(0, 0, 0, 0.25); padding: 3px 8px; border-radius: 4px; font-weight: 500; color: #FFFFFF !important; }
#         [data-testid="stDataFrame"] > div { border: 2px solid #004085 !important; border-radius: 6px; overflow: hidden; }
#     </style>
# """, unsafe_allow_html=True)

# # --- IST TIMEZONE SETUP ---
# IST = timezone(timedelta(hours=5, minutes=30))
# now_ist = datetime.now(IST)

# # --- GITHUB TRIGGER LOGIC ---
# def trigger_scraper():
#     repo_owner = "jamjayjoshi108"
#     repo_name = "pspcl_daily_outage_dashboard" 
#     url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/263899469/dispatches"
#     headers = {"Accept": "application/vnd.github.v3+json", "Authorization": f"token {st.secrets['GITHUB_TOKEN']}"}
#     response = requests.post(url, headers=headers, json={"ref": "main"})
    
#     if response.status_code == 204:
#         st.toast("✅ Scraper triggered successfully in the cloud!")
#         return True
#     else:
#         st.error(f"❌ Failed to trigger scraper. GitHub responded: {response.text}")
#         return False

# # --- 1. FILE DEFINITIONS & CHECKING LOGIC ---
# if now_ist.hour < 8: now_ist -= timedelta(days=1)
# today_str = now_ist.strftime("%Y-%m-%d")

# file_today = f"{today_str}_Outages_Today.csv"
# file_5day = f"{today_str}_Outages_Last_5_Days.csv"
# file_ptw = f"{today_str}_PTW_Last_7_Days.csv"

# files_missing = not (os.path.exists(file_today) and os.path.exists(file_5day) and os.path.exists(file_ptw))

# if files_missing:
#     lock_file = "scraper_lock.txt"
#     should_trigger = True
#     if os.path.exists(lock_file) and time.time() - os.path.getmtime(lock_file) < 300: 
#         should_trigger = False
            
#     if should_trigger:
#         if trigger_scraper():
#             with open(lock_file, "w") as f: f.write(str(time.time()))
#             st.warning(f"⚠️ Data for {today_str} is missing. Automatically fetching fresh data from PSPCL...")
#             st.info("⏳ Please wait ~2 minutes and refresh this page.")
#         else:
#             st.error("🚨 Could not fetch data due to GitHub API error. Fix the token to continue.")
#     else:
#         st.info("⏳ The scraper is currently running in the background. Please wait a moment and refresh.")
#     st.stop()


# # --- 2. DATA LOADING & CLEANING LOGIC ---
# def clean_outage_data(df):
#     """Standardizes dates, buckets, and removes cancelled outages across all files."""
#     if df.empty: return df
#     if 'Status' in df.columns:
#         df = df[~df['Status'].astype(str).str.contains('Cancel', na=False, case=False)]
#         df['Status_Calc'] = df['Status'].apply(lambda x: 'Active' if str(x).strip().title() == 'Open' else 'Closed')
        
#     time_cols = ['Schedule Created At', 'Start Time', 'End Time', 'Last Updated At']
#     for col in time_cols:
#         if col in df.columns:
#             df[col] = pd.to_datetime(df[col], errors='coerce')
            
#     if 'Diff in mins' in df.columns:
#         def assign_bucket(mins):
#             if pd.isna(mins) or mins < 0: return "Active/Unknown"
#             hrs = mins / 60
#             if hrs <= 2: return "Up to 2 Hrs"
#             elif hrs <= 4: return "2-4 Hrs"
#             elif hrs <= 8: return "4-8 Hrs"
#             else: return "Above 8 Hrs"
#         df['Duration Bucket'] = df['Diff in mins'].apply(assign_bucket)
        
#     if 'Start Time' in df.columns:
#         df['Outage Date'] = df['Start Time'].dt.date
        
#     return df

# @st.cache_data(ttl="10m")
# def load_live_data(f_today, f_5day, f_ptw):
#     df_t = pd.read_csv(f_today) if os.path.exists(f_today) else pd.DataFrame()
#     df_5 = pd.read_csv(f_5day) if os.path.exists(f_5day) else pd.DataFrame()
#     df_p = pd.read_csv(f_ptw) if os.path.exists(f_ptw) else pd.DataFrame()
#     return clean_outage_data(df_t), clean_outage_data(df_5), df_p

# @st.cache_data
# def load_historical_data():
#     df_26 = pd.read_csv('Historical_2026.csv') if os.path.exists('Historical_2026.csv') else pd.DataFrame()
#     df_25 = pd.read_csv('Historical_2025.csv') if os.path.exists('Historical_2025.csv') else pd.DataFrame()
#     return clean_outage_data(df_26), clean_outage_data(df_25)

# df_today, df_5day, df_ptw = load_live_data(file_today, file_5day, file_ptw)
# df_hist_curr, df_hist_ly = load_historical_data()

# # --- CREATE UNIFIED MASTER DATAFRAME ---
# dfs_to_combine = []
# for d in [df_hist_curr, df_5day, df_today]:
#     if not d.empty: dfs_to_combine.append(d)

# if dfs_to_combine:
#     df_master = pd.concat(dfs_to_combine, ignore_index=True)
    
#     # # 1. Identify the exact ID column name (usually 'ID' or 'Outage ID')
#     # id_col = next((c for c in df_master.columns if str(c).strip().lower() in ['id', 'outage id']), None)
    
#     # # 2. Define the strict combination of columns for deduplication
#     # target_cols = [id_col, 'Zone', 'Circle', 'Division', 'Feeder ID', 'Feeder', 'Schedule Created At', 'Start Time']
    
#     # # 3. Filter out any columns that might be missing to prevent KeyErrors
#     # dedup_cols = [c for c in target_cols if c and c in df_master.columns]
    
#     # # 4. Drop duplicates using this exact combination
#     # if dedup_cols:
#     #     df_master = df_master.drop_duplicates(subset=dedup_cols, keep='last')
#     # else:
#     #     df_master = df_master.drop_duplicates(keep='last')
# else:
#     df_master = pd.DataFrame()


# def render_date_selector(tab_key):
#     """Reusable global date selector widget matching the horizontal UI"""
#     st.markdown("📅 **Select Time Period:**")
    
#     # Horizontal radio buttons
#     period = st.radio(
#         "Select Time Period",
#         options=["Today", "Current Month", "Last Month", "Last 3 Months", "Last 6 Months", "Custom"],
#         horizontal=True,
#         label_visibility="collapsed",
#         key=f"{tab_key}_radio"
#     )
    
#     today = now_ist.date()
    
#     # Calculate dates based on the radio selection
#     if period == "Today":
#         calc_start, calc_end = today, today
#     elif period == "Current Month":
#         calc_start, calc_end = today.replace(day=1), today
#     elif period == "Last Month":
#         first_of_this_month = today.replace(day=1)
#         last_of_last_month = first_of_this_month - timedelta(days=1)
#         calc_start, calc_end = last_of_last_month.replace(day=1), last_of_last_month
#     elif period == "Last 3 Months":
#         calc_start, calc_end = today - timedelta(days=90), today
#     elif period == "Last 6 Months":
#         calc_start, calc_end = today - timedelta(days=180), today
#     else: 
#         # For 'Custom', preserve what they pick in session state, defaulting to today
#         calc_start = st.session_state.get(f"{tab_key}_custom_start", today)
#         calc_end = st.session_state.get(f"{tab_key}_custom_end", today)

#     # Render From and To inputs side-by-side without keys so they respect the calculated 'value'
#     col1, col2 = st.columns(2)
#     with col1:
#         start_date = st.date_input(
#             "From Date", 
#             value=calc_start, 
#             format="DD/MM/YYYY", 
#             disabled=(period != "Custom")
#         )
#     with col2:
#         end_date = st.date_input(
#             "To Date", 
#             value=calc_end, 
#             format="DD/MM/YYYY", 
#             disabled=(period != "Custom")
#         )
        
#     # Save the custom dates if Custom is selected so they don't reset
#     if period == "Custom":
#         st.session_state[f"{tab_key}_custom_start"] = start_date
#         st.session_state[f"{tab_key}_custom_end"] = end_date
        
#     return start_date, end_date

# def safe_ly_date(dt):
#     try: return dt.replace(year=dt.year - 1)
#     except ValueError: return dt.replace(year=dt.year - 1, day=28)

# def generate_yoy_dist_expanded(df_curr, df_ly, group_col):
#     def _agg(df, prefix):
#         if df.empty: return pd.DataFrame({group_col: []}).set_index(group_col)
#         df['Diff in mins'] = pd.to_numeric(df['Diff in mins'], errors='coerce').fillna(0)
#         g = df.groupby([group_col, 'Type of Outage']).agg(
#             Count=('Type of Outage', 'size'),
#             TotalHrs=('Diff in mins', lambda x: round(x.sum() / 60, 2)),
#             AvgHrs=('Diff in mins', lambda x: round(x.mean() / 60, 2))
#         ).unstack(fill_value=0)
#         g.columns = [f"{prefix} {outage} ({metric})" for metric, outage in g.columns]
#         return g

#     c_grp = _agg(df_curr, 'Curr')
#     l_grp = _agg(df_ly, 'LY')
#     merged = pd.merge(c_grp, l_grp, on=group_col, how='outer').fillna(0).reset_index()
    
#     expected_cols = []
#     for prefix in ['Curr', 'LY']:
#         for outage in ['Planned Outage', 'Unplanned Outage']:
#             for metric in ['Count', 'TotalHrs', 'AvgHrs']:
#                 col_name = f"{prefix} {outage} ({metric})"
#                 expected_cols.append(col_name)
#                 if col_name not in merged.columns: merged[col_name] = 0
                    
#     for col in expected_cols:
#         if '(Count)' in col: merged[col] = merged[col].astype(int)
#         else: merged[col] = merged[col].astype(float).round(2)
            
#     merged['Curr Total (Count)'] = merged['Curr Planned Outage (Count)'] + merged['Curr Unplanned Outage (Count)']
#     merged['LY Total (Count)'] = merged['LY Planned Outage (Count)'] + merged['LY Unplanned Outage (Count)']
#     merged['YoY Delta (Total)'] = merged['Curr Total (Count)'] - merged['LY Total (Count)']
    
#     cols_order = [group_col, 
#                   'Curr Planned Outage (Count)', 'Curr Planned Outage (TotalHrs)', 'Curr Planned Outage (AvgHrs)',
#                   'LY Planned Outage (Count)', 'LY Planned Outage (TotalHrs)', 'LY Planned Outage (AvgHrs)',
#                   'Curr Unplanned Outage (Count)', 'Curr Unplanned Outage (TotalHrs)', 'Curr Unplanned Outage (AvgHrs)',
#                   'LY Unplanned Outage (Count)', 'LY Unplanned Outage (TotalHrs)', 'LY Unplanned Outage (AvgHrs)',
#                   'Curr Total (Count)', 'LY Total (Count)', 'YoY Delta (Total)']
#     cols_order = [c for c in cols_order if c in merged.columns]
#     merged = merged[cols_order]

#     if not merged.empty:
#         gt_row = pd.Series(index=cols_order, dtype=object)
#         gt_row[group_col] = 'Grand Total'
#         for col in cols_order:
#             if col == group_col: continue
#             if '(Count)' in col or 'Delta' in col or '(TotalHrs)' in col:
#                 gt_row[col] = merged[col].sum()
        
#         for prefix in ['Curr', 'LY']:
#             for outage in ['Planned Outage', 'Unplanned Outage']:
#                 count_col = f"{prefix} {outage} (Count)"
#                 tot_col = f"{prefix} {outage} (TotalHrs)"
#                 avg_col = f"{prefix} {outage} (AvgHrs)"
#                 if count_col in cols_order and tot_col in cols_order and avg_col in cols_order:
#                     gt_row[avg_col] = round(gt_row[tot_col] / gt_row[count_col], 2) if gt_row[count_col] > 0 else 0
        
#         merged = pd.concat([merged, pd.DataFrame([gt_row])], ignore_index=True)

#     return merged

# def apply_pu_gradient(styler, df):
#     p_cols = [c for c in df.columns if 'Planned' in str(c) and pd.api.types.is_numeric_dtype(df[c])]
#     u_cols = [c for c in df.columns if 'Unplanned' in str(c) and pd.api.types.is_numeric_dtype(df[c])]
#     pc_cols = [c for c in df.columns if 'Power Off By PC' in str(c) and pd.api.types.is_numeric_dtype(df[c])]
    
#     if 'Grand Total' in df.index: row_idx = df.index.drop('Grand Total')
#     else:
#         try:
#             group_col = df.columns[0]
#             if not df.empty and df.iloc[-1][group_col] == 'Grand Total': row_idx = df.index[:-1]
#             else: row_idx = df.index
#         except: row_idx = df.index
            
#     if p_cols: styler = styler.background_gradient(subset=pd.IndexSlice[row_idx, p_cols], cmap='Blues', vmin=0)
#     if pc_cols: styler = styler.background_gradient(subset=pd.IndexSlice[row_idx, pc_cols], cmap='Purples', vmin=0)
#     if u_cols: styler = styler.background_gradient(subset=pd.IndexSlice[row_idx, u_cols], cmap='Reds', vmin=0)
#     return styler

# def highlight_delta(val):
#     if isinstance(val, (int, float)):
#         if val > 0: return 'color: #D32F2F; font-weight: bold;'
#         elif val < 0: return 'color: #388E3C; font-weight: bold;'
#     return ''

# def create_bucket_pivot(df, bucket_order):
#     if df.empty: return pd.DataFrame(columns=bucket_order + ['Total'])
#     pivot = pd.crosstab(df['Circle'], df['Duration Bucket'])
#     pivot = pivot.reindex(columns=[c for c in bucket_order if c in pivot.columns], fill_value=0)
#     pivot['Total'] = pivot.sum(axis=1)
#     return pivot


# # --- MAIN DASHBOARD RENDER ---
# #st.title("⚡ Power Outage Monitoring Dashboard")
# st.title("⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡ Under maintenance ⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡")
# tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📈 YoY Comparison", "🛠️ PTW Frequency"])

# # Add this temporary debug line:
# st.warning(f"🛠️ DEBUG | Total Raw Rows in df_master: {len(df_master)}")

# # ==========================================
# # TAB 1: DASHBOARD (Unified & Filtered)
# # ==========================================
# with tab1:
#     st.header("📊 Outage Dashboard")
#     start_d1, end_d1 = render_date_selector("tab1")
#     st.divider()

#     if not df_master.empty:
#         mask_t1 = (df_master['Outage Date'] >= start_d1) & (df_master['Outage Date'] <= end_d1)
#         filtered_tab1 = df_master[mask_t1].copy()
#         st.warning(f"🛠️ DEBUG | Total Filtered Rows for selected dates: {len(filtered_tab1)}")
#     else:
#         filtered_tab1 = pd.DataFrame()

#     if filtered_tab1.empty:
#         st.info("No outage data found for the selected time period.")
#     else:
#         planned_df = filtered_tab1[filtered_tab1['Type of Outage'] == 'Planned Outage']
#         pc_df = filtered_tab1[filtered_tab1['Type of Outage'] == 'Power Off By PC']
#         unplanned_df = filtered_tab1[filtered_tab1['Type of Outage'] == 'Unplanned Outage']

#         # --- 1. KPI WIDGETS ---
#         kpi1, kpi2, kpi3 = st.columns(3)
#         with kpi1:
#             active_p = len(planned_df[planned_df['Status_Calc'] == 'Active']) if 'Status_Calc' in planned_df else 0
#             closed_p = len(planned_df[planned_df['Status_Calc'] == 'Closed']) if 'Status_Calc' in planned_df else len(planned_df)
#             st.markdown(f'<div class="kpi-card"><div><div class="kpi-title">Planned Outages</div><div class="kpi-value">{len(planned_df)}</div></div><div class="kpi-subtext"><span class="status-badge">🔴 Active: {active_p}</span> <span class="status-badge">🟢 Closed: {closed_p}</span></div></div>', unsafe_allow_html=True)
#         with kpi2:
#             active_pc = len(pc_df[pc_df['Status_Calc'] == 'Active']) if 'Status_Calc' in pc_df else 0
#             closed_pc = len(pc_df[pc_df['Status_Calc'] == 'Closed']) if 'Status_Calc' in pc_df else len(pc_df)
#             st.markdown(f'<div class="kpi-card"><div><div class="kpi-title">Power Off By PC</div><div class="kpi-value">{len(pc_df)}</div></div><div class="kpi-subtext"><span class="status-badge">🔴 Active: {active_pc}</span> <span class="status-badge">🟢 Closed: {closed_pc}</span></div></div>', unsafe_allow_html=True)
#         with kpi3:
#             active_u = len(unplanned_df[unplanned_df['Status_Calc'] == 'Active']) if 'Status_Calc' in unplanned_df else 0
#             closed_u = len(unplanned_df[unplanned_df['Status_Calc'] == 'Closed']) if 'Status_Calc' in unplanned_df else len(unplanned_df)
#             st.markdown(f'<div class="kpi-card"><div><div class="kpi-title">Unplanned Outages</div><div class="kpi-value">{len(unplanned_df)}</div></div><div class="kpi-subtext"><span class="status-badge">🔴 Active: {active_u}</span> <span class="status-badge">🟢 Closed: {closed_u}</span></div></div>', unsafe_allow_html=True)

#         st.divider()

#         # --- 2. ZONE-WISE DISTRIBUTION ---
#         st.subheader("📍 Zone-wise Distribution")
#         zone_df = filtered_tab1.groupby(['Zone', 'Type of Outage']).size().unstack(fill_value=0).reset_index()
#         for col in ['Planned Outage', 'Power Off By PC', 'Unplanned Outage']:
#             if col not in zone_df: zone_df[col] = 0
            
#         zone_df['Total'] = zone_df['Planned Outage'] + zone_df['Power Off By PC'] + zone_df['Unplanned Outage']
#         gt_row_zone = pd.Series(zone_df.sum(numeric_only=True), name='Grand Total')
#         gt_row_zone['Zone'] = 'Grand Total'
#         zone_df = pd.concat([zone_df, pd.DataFrame([gt_row_zone])], ignore_index=True)
        
#         st.dataframe(apply_pu_gradient(zone_df.style, zone_df).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)

#         st.divider()

#         # --- 3. NOTORIOUS FEEDERS ---
#         st.subheader("🚨 Notorious Feeders (3+ Days of Outages)")
#         st.caption("Top 5 worst-performing feeders per circle based on days with outages in the selected period.")

#         noto_col1, noto_col2 = st.columns(2)
#         all_circles = sorted(filtered_tab1['Circle'].dropna().unique().tolist())
#         with noto_col1: selected_notorious_circle = st.selectbox("Filter by Circle:", ["All Circles"] + all_circles, index=0, key="noto_circ")
#         with noto_col2: selected_notorious_type = st.selectbox("Filter by Outage Type:", ["All Types", "Planned Outage", "Power Off By PC", "Unplanned Outage"], index=0, key="noto_type")

#         dyn_noto_df = filtered_tab1.copy()
#         if selected_notorious_type != "All Types": dyn_noto_df = dyn_noto_df[dyn_noto_df['Type of Outage'] == selected_notorious_type]

#         if not dyn_noto_df.empty:
#             dyn_days = dyn_noto_df.groupby(['Circle', 'Feeder'])['Outage Date'].nunique().reset_index(name='Days with Outages')
#             dyn_noto = dyn_days[dyn_days['Days with Outages'] >= 3]

#             if not dyn_noto.empty:
#                 dyn_stats = dyn_noto_df.groupby(['Circle', 'Feeder']).agg(Total_Events=('Start Time', 'size'), Max_Mins=('Diff in mins', 'max'), Total_Mins=('Diff in mins', 'sum')).reset_index()
#                 dyn_stats.rename(columns={'Total_Events': 'Total Outage Events'}, inplace=True)
#                 dyn_stats['Total Duration (Hours)'] = (dyn_stats['Total_Mins'] / 60).round(2)
#                 dyn_stats['Max Duration (Hours)'] = (dyn_stats['Max_Mins'] / 60).round(2)
#                 dyn_stats = dyn_stats.drop(columns=['Max_Mins', 'Total_Mins'])

#                 dyn_noto = dyn_noto.merge(dyn_stats, on=['Circle', 'Feeder']).sort_values(by=['Circle', 'Days with Outages', 'Total Outage Events'], ascending=[True, False, False])
#                 dyn_top5 = dyn_noto.groupby('Circle').head(5)
                
#                 # Global notorious set to flag rows in drill-down
#                 global_notorious_set = set(zip(dyn_top5['Circle'], dyn_top5['Feeder']))
                
#                 filtered_notorious = dyn_top5[dyn_top5['Circle'] == selected_notorious_circle] if selected_notorious_circle != "All Circles" else dyn_top5

#                 if not filtered_notorious.empty:
#                     st.dataframe(filtered_notorious.style.format({'Max Duration (Hours)': '{:.2f}', 'Total Duration (Hours)': '{:.2f}'}).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#                 else: st.info(f"No notorious feeders found for {selected_notorious_circle} matching the criteria.")
#             else: 
#                 global_notorious_set = set()
#                 st.info(f"No notorious feeders identified (no feeder had 3+ days of outages in this timeframe).")
#         else: 
#             global_notorious_set = set()
#             st.info("No data available for the selected outage type.")


#         st.divider()

#         # --- 4. COMPREHENSIVE CIRCLE-WISE BREAKDOWN & DRILLDOWN ---
#         st.subheader("🔌 Comprehensive Circle-wise Breakdown")
#         st.markdown(" **Click on any row inside the table below** to view the specific Feeder drill-down details.")

#         bucket_order = ["Up to 2 Hrs", "2-4 Hrs", "4-8 Hrs", "Above 8 Hrs", "Active/Unknown"]
#         p_piv = create_bucket_pivot(planned_df, bucket_order)
#         pc_piv = create_bucket_pivot(pc_df, bucket_order)
#         u_piv = create_bucket_pivot(unplanned_df, bucket_order)

#         circle_piv = pd.concat(
#             [p_piv, pc_piv, u_piv], 
#             axis=1, 
#             keys=['Planned Outages', 'Power Off By PC', 'Unplanned Outages']
#         ).fillna(0).astype(int)

#         if not circle_piv.empty:
#             circle_piv[('Overall Total', 'Total Events')] = circle_piv.loc[:, (slice(None), 'Total')].sum(axis=1)
#             circle_piv.loc['Grand Total'] = circle_piv.sum(numeric_only=True)

#             styled_circle = apply_pu_gradient(circle_piv.style, circle_piv).set_table_styles(HEADER_STYLES)
            
#             selection_circle = st.dataframe(styled_circle, width="stretch", on_select="rerun", selection_mode="single-row")

#             if len(selection_circle.selection.rows) > 0:
#                 selected_circle = circle_piv.index[selection_circle.selection.rows[0]]
                
#                 if selected_circle != 'Grand Total':
#                     st.markdown(f"#### 🔍 Feeder Details for: **{selected_circle}**")
#                     def highlight_noto(row): return ['background-color: rgba(220, 53, 69, 0.15); color: #850000; font-weight: bold'] * len(row) if (selected_circle, row['Feeder']) in global_notorious_set else [''] * len(row)

#                     c_left, c_mid, c_right = st.columns(3)
#                     cols_to_show = ['Outage Date', 'Feeder', 'Diff in mins', 'Status_Calc', 'Duration Bucket']
#                     format_dict = {'Diff in Hours': '{:.2f}'}
                    
#                     def prep_feeder_df(df_sub):
#                         if df_sub.empty: return pd.DataFrame(columns=['Outage Date', 'Feeder', 'Diff in Hours', 'Status', 'Duration Bucket'])
#                         res = df_sub[df_sub['Circle'] == selected_circle][cols_to_show].rename(columns={'Status_Calc': 'Status'}).copy()
#                         res['Diff in Hours'] = (res['Diff in mins'] / 60).round(2)
#                         return res.drop(columns=['Diff in mins'])

#                     with c_left:
#                         st.markdown(f"**🔵 Planned Outages**")
#                         st.dataframe(prep_feeder_df(planned_df).style.apply(highlight_noto, axis=1).format(format_dict).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#                     with c_mid:
#                         st.markdown(f"**🟣 Power Off By PC**")
#                         st.dataframe(prep_feeder_df(pc_df).style.apply(highlight_noto, axis=1).format(format_dict).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#                     with c_right:
#                         st.markdown(f"**🔴 Unplanned Outages**")
#                         st.dataframe(prep_feeder_df(unplanned_df).style.apply(highlight_noto, axis=1).format(format_dict).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)


# # ==========================================
# # TAB 2: DYNAMIC YOY DRILL-DOWN
# # ==========================================
# with tab2:
#     st.header("📈 Historical Year-over-Year Drilldown")
#     start_d2, end_d2 = render_date_selector("tab2")
#     st.divider()
    
#     if df_hist_curr.empty or df_hist_ly.empty:
#         st.error("Historical Master Data not found in directory.")
#     else:
#         # Calculate equivalent Last Year bounds automatically
#         ly_start_d2 = safe_ly_date(start_d2)
#         ly_end_d2 = safe_ly_date(end_d2)
        
#         mask_curr = (df_hist_curr['Outage Date'] >= start_d2) & (df_hist_curr['Outage Date'] <= end_d2)
#         filtered_curr = df_hist_curr[mask_curr]
        
#         mask_ly = (df_hist_ly['Outage Date'] >= ly_start_d2) & (df_hist_ly['Outage Date'] <= ly_end_d2)
#         filtered_ly = df_hist_ly[mask_ly]

#         st.markdown(f"### 📍 1. Zone-wise Distribution")
#         st.caption("Includes total counts, total hours, and average hours. Click any row to drill down.")
        
#         yoy_zone = generate_yoy_dist_expanded(filtered_curr, filtered_ly, 'Zone')
        
#         zone_selection = st.dataframe(
#             yoy_zone.style.map(highlight_delta, subset=['YoY Delta (Total)']).format(precision=2).set_table_styles(HEADER_STYLES), 
#             width="stretch", hide_index=True, on_select="rerun", selection_mode="single-row"
#         )

#         if len(zone_selection.selection.rows) > 0:
#             selected_zone = yoy_zone.iloc[zone_selection.selection.rows[0]]['Zone']
            
#             if selected_zone != 'Grand Total':
#                 st.markdown(f"### 🎯 2. Circle-wise Distribution for **{selected_zone}**")
#                 st.caption("Click any row to drill down into Feeder-wise data.")
                
#                 curr_zone_df = filtered_curr[filtered_curr['Zone'] == selected_zone]
#                 ly_zone_df = filtered_ly[filtered_ly['Zone'] == selected_zone]
                
#                 yoy_circle = generate_yoy_dist_expanded(curr_zone_df, ly_zone_df, 'Circle')
                
#                 circle_selection = st.dataframe(
#                     yoy_circle.style.map(highlight_delta, subset=['YoY Delta (Total)']).format(precision=2).set_table_styles(HEADER_STYLES), 
#                     width="stretch", hide_index=True, on_select="rerun", selection_mode="single-row"
#                 )

#                 if len(circle_selection.selection.rows) > 0:
#                     selected_circle = yoy_circle.iloc[circle_selection.selection.rows[0]]['Circle']
                    
#                     if selected_circle != 'Grand Total':
#                         st.markdown(f"### 🔌 3. Feeder-wise Distribution for **{selected_circle}**")
                        
#                         curr_circle_df = curr_zone_df[curr_zone_df['Circle'] == selected_circle]
#                         ly_circle_df = ly_zone_df[ly_zone_df['Circle'] == selected_circle]
                        
#                         yoy_feeder = generate_yoy_dist_expanded(curr_circle_df, ly_circle_df, 'Feeder')
#                         st.dataframe(yoy_feeder.style.map(highlight_delta, subset=['YoY Delta (Total)']).format(precision=2).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)


# # ==========================================
# # TAB 3: PTW FREQUENCY
# # ==========================================
# with tab3:
#     st.header("🛠️ PTW Frequency Tracker")
#     start_d3, end_d3 = render_date_selector("tab3")
#     st.divider()
    
#     st.markdown("Identifies specific feeders that had a Permit to Work (PTW) taken against them **two or more times** in separate requests over the selected timeframe.")

#     if df_ptw.empty:
#         st.info("No PTW data available in the current files.")
#     else:
#         # Make sure PTW dates are parsed correctly
#         date_col = next((c for c in df_ptw.columns if 'date' in c.lower() or 'time' in c.lower()), None)
#         if date_col:
#             df_ptw['Temp_Date'] = pd.to_datetime(df_ptw[date_col], errors='coerce').dt.date
#             mask_ptw = (df_ptw['Temp_Date'] >= start_d3) & (df_ptw['Temp_Date'] <= end_d3)
#             filtered_ptw = df_ptw[mask_ptw].copy()
#         else:
#             # Fallback if no date column is found, just use the whole PTW
#             filtered_ptw = df_ptw.copy()
            
#         if filtered_ptw.empty:
#             st.warning("⚠️ No PTW data found for the selected time period. (Note: The automated scraper currently only caches the most recent 7 days of PTW data).")
#         else:
#             ptw_col = next((c for c in filtered_ptw.columns if 'ptw' in c.lower() or 'request' in c.lower() or 'id' in c.lower()), None)
#             feeder_col = next((c for c in filtered_ptw.columns if 'feeder' in c.lower()), None)
#             status_col = next((c for c in filtered_ptw.columns if 'status' in c.lower()), None)
#             circle_col = next((c for c in filtered_ptw.columns if 'circle' in c.lower()), None)

#             if not ptw_col or not feeder_col:
#                 st.error("Could not dynamically map required columns from the PTW export.")
#             else:
#                 ptw_clean = filtered_ptw.copy()
#                 if status_col:
#                     ptw_clean = ptw_clean[~ptw_clean[status_col].astype(str).str.contains('Cancellation', na=False, case=False)]

#                 ptw_clean[feeder_col] = ptw_clean[feeder_col].astype(str).str.replace('|', ',', regex=False)
#                 ptw_clean[feeder_col] = ptw_clean[feeder_col].str.split(',')
#                 ptw_clean = ptw_clean.explode(feeder_col)
#                 ptw_clean[feeder_col] = ptw_clean[feeder_col].str.strip()
#                 ptw_clean = ptw_clean[ptw_clean[feeder_col] != '']

#                 group_cols = [feeder_col]
#                 if circle_col: group_cols.insert(0, circle_col)
                    
#                 ptw_counts = ptw_clean.groupby(group_cols).agg(Unique_PTWs=(ptw_col, 'nunique'), PTW_IDs=(ptw_col, lambda x: ', '.join(x.dropna().astype(str).unique()))).reset_index()
#                 repeat_feeders = ptw_counts[ptw_counts['Unique_PTWs'] >= 2].sort_values(by='Unique_PTWs', ascending=False)
#                 repeat_feeders = repeat_feeders.rename(columns={'Unique_PTWs': 'PTW Request Count', 'PTW_IDs': 'Associated PTW Request Numbers'})

#                 if not repeat_feeders.empty:
#                     gt_dict = {c: '' for c in repeat_feeders.columns}
#                     gt_dict[repeat_feeders.columns[0]] = 'Grand Total'
#                     gt_dict['PTW Request Count'] = int(repeat_feeders['PTW Request Count'].sum())
#                     repeat_feeders = pd.concat([repeat_feeders, pd.DataFrame([gt_dict])], ignore_index=True)

#                 kpi1, kpi2 = st.columns(2)
#                 with kpi1: st.markdown(f'<div class="kpi-card"><div><div class="kpi-title">Total Active PTW Requests</div><div class="kpi-value">{filtered_ptw[ptw_col].nunique()}</div></div><div class="kpi-subtext"><span class="status-badge">Selected Timeframe</span></div></div>', unsafe_allow_html=True)
#                 with kpi2: st.markdown(f'<div class="kpi-card"><div><div class="kpi-title">Feeders with Multiple PTWs</div><div class="kpi-value">{len(repeat_feeders) - 1 if not repeat_feeders.empty else 0}</div></div><div class="kpi-subtext"><span class="status-badge" style="background-color: #D32F2F;">🔴 Needs Review</span></div></div>', unsafe_allow_html=True) 

#                 st.divider()
#                 st.subheader("⚠️ Repeat PTW Feeders Detail View")
#                 if not repeat_feeders.empty:
#                     st.dataframe(repeat_feeders.style.set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#                 else:
#                     st.success("No feeders had multiple PTWs requested against them in the selected timeframe! 🎉")


# # # #  =======================================================================================================================================
# # # #  =======================================================================================================================================
# # # #V7
# # # #  =======================================================================================================================================
# # # #  =======================================================================================================================================


# import os
# import time
# import requests
# import streamlit as st
# import pandas as pd
# from datetime import datetime, timedelta, timezone

# # --- PAGE CONFIGURATION ---
# st.set_page_config(page_title="Power Outage Monitoring Dashboard", layout="wide")

# # --- GLOBAL TABLE HEADER STYLING ---
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
#         'selector': 'th div',
#         'props': [
#             ('color', '#FFC107 !important'),
#             ('font-weight', 'bold !important')
#         ]
#     }
# ]

# # --- COLOR THEME & ENTERPRISE CSS ---
# st.markdown("""
#     <style>
#         .block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
#         p, span, div, caption, .stMarkdown { color: #000000 !important; }
#         h1, h2, h3, h4, h5, h6, div.block-container h1 { color: #004085 !important; font-weight: 700 !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
#         div.block-container h1 { text-align: center; border-bottom: 3px solid #004085 !important; padding-bottom: 10px; margin-bottom: 30px !important; font-size: 2.2rem !important; }
#         h2 { font-size: 1.3rem !important; border-bottom: 2px solid #004085 !important; padding-bottom: 5px; margin-bottom: 10px !important; }
#         h3 { font-size: 1.05rem !important; margin-bottom: 12px !important; text-transform: uppercase; letter-spacing: 0.5px; }
#         hr { border: 0; border-top: 1px solid #004085; margin: 1.5rem 0; opacity: 0.3; }
        
#         .kpi-card { background: linear-gradient(135deg, #004481 0%, #0066cc 100%); border-radius: 6px; padding: 1.2rem 1.2rem; display: flex; flex-direction: column; justify-content: space-between; height: 100%; box-shadow: 0 2px 4px rgba(0,0,0,0.08); transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out; border: 1px solid #003366; }
#         .kpi-card:hover { transform: translateY(-4px); box-shadow: 0 8px 16px rgba(0, 68, 129, 0.2); }
#         .kpi-card .kpi-title, .kpi-title { color: #FFC107 !important; font-weight: 600; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.4rem; }
#         .kpi-card .kpi-value, .kpi-value { color: #FFFFFF !important; font-weight: 700; font-size: 2.6rem; margin-bottom: 0; line-height: 1.1; }
#         .kpi-card .kpi-subtext, .kpi-subtext { color: #F8F9FA !important; font-size: 0.85rem; margin-top: 1rem; padding-top: 0.6rem; border-top: 1px solid rgba(255, 255, 255, 0.2); display: flex; justify-content: flex-start; gap: 15px; }
        
#         .status-badge { background-color: rgba(0, 0, 0, 0.25); padding: 3px 8px; border-radius: 4px; font-weight: 500; color: #FFFFFF !important; }
#         [data-testid="stDataFrame"] > div { border: 2px solid #004085 !important; border-radius: 6px; overflow: hidden; }
#     </style>
# """, unsafe_allow_html=True)

# # --- IST TIMEZONE SETUP ---
# IST = timezone(timedelta(hours=5, minutes=30))

# # --- GITHUB TRIGGER LOGIC ---
# def trigger_scraper():
#     repo_owner = "jamjayjoshi108"
#     repo_name = "pspcl_daily_outage_dashboard" 
#     url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/263899469/dispatches"
#     headers = {"Accept": "application/vnd.github.v3+json", "Authorization": f"token {st.secrets['GITHUB_TOKEN']}"}
#     response = requests.post(url, headers=headers, json={"ref": "main"})
    
#     if response.status_code == 204:
#         st.toast("✅ Scraper triggered successfully in the cloud!")
#         return True
#     else:
#         st.error(f"❌ Failed to trigger scraper. GitHub responded: {response.text}")
#         return False

# # --- 1. FILE DEFINITIONS & CHECKING LOGIC ---
# now_ist = datetime.now(IST)
# if now_ist.hour < 8: now_ist -= timedelta(days=1)
# today_str = now_ist.strftime("%Y-%m-%d")

# try: ly_date = now_ist.replace(year=now_ist.year - 1)
# except ValueError: ly_date = now_ist.replace(year=now_ist.year - 1, day=28)
# ly_str = ly_date.strftime("%Y-%m-%d")

# file_today = f"{today_str}_Outages_Today.csv"
# file_5day = f"{today_str}_Outages_Last_5_Days.csv"
# file_ptw = f"{today_str}_PTW_Last_7_Days.csv"

# files_missing = not (os.path.exists(file_today) and os.path.exists(file_5day) and os.path.exists(file_ptw))

# if files_missing:
#     lock_file = "scraper_lock.txt"
#     should_trigger = True
#     if os.path.exists(lock_file) and time.time() - os.path.getmtime(lock_file) < 300: 
#         should_trigger = False
            
#     if should_trigger:
#         if trigger_scraper():
#             with open(lock_file, "w") as f: f.write(str(time.time()))
#             st.warning(f"⚠️ Data for {today_str} is missing. Automatically fetching fresh data from PSPCL...")
#             st.info("⏳ Please wait ~2 minutes and refresh this page.")
#         else:
#             st.error("🚨 Could not fetch data due to GitHub API error. Fix the token to continue.")
#     else:
#         st.info("⏳ The scraper is currently running in the background. Please wait a moment and refresh.")
#     st.stop()

# # --- 2. DATA LOADING LOGIC ---
# @st.cache_data(ttl="10m")
# def load_live_data(f_today, f_5day, f_ptw):
#     df_today = pd.read_csv(f_today)
#     df_5day = pd.read_csv(f_5day)
#     df_ptw = pd.read_csv(f_ptw)
    
#     df_today['Type of Outage'] = df_today['Type of Outage'].replace('Power Off By PC', 'Planned Outage')
#     df_5day['Type of Outage'] = df_5day['Type of Outage'].replace('Power Off By PC', 'Planned Outage')
    
#     time_cols = ['Schedule Created At', 'Start Time', 'End Time', 'Last Updated At']
#     for df in [df_today, df_5day]:
#         for col in time_cols: df[col] = pd.to_datetime(df[col], errors='coerce')
#         df['Status_Calc'] = df['Status'].apply(lambda x: 'Active' if str(x).strip().title() == 'Open' else 'Closed')
        
#         def assign_bucket(mins):
#             if pd.isna(mins) or mins < 0: return "Active/Unknown"
#             hrs = mins / 60
#             if hrs <= 2: return "Up to 2 Hrs"
#             elif hrs <= 4: return "2-4 Hrs"
#             elif hrs <= 8: return "4-8 Hrs"
#             else: return "Above 8 Hrs"
#         df['Duration Bucket'] = df['Diff in mins'].apply(assign_bucket)
        
#     return df_today, df_5day, df_ptw

# @st.cache_data
# def load_historical_data():
#     if os.path.exists('Historical_2026.csv') and os.path.exists('Historical_2025.csv'):
#         df_26, df_25 = pd.read_csv('Historical_2026.csv'), pd.read_csv('Historical_2025.csv')
#         for df in [df_26, df_25]:
#             df['Type of Outage'] = df['Type of Outage'].replace('Power Off By PC', 'Planned Outage')
#             df['Outage Date'] = pd.to_datetime(df['Start Time'], errors='coerce').dt.date
#         return df_26, df_25
#     return pd.DataFrame(), pd.DataFrame()

# df_today, df_5day, df_ptw = load_live_data(file_today, file_5day, file_ptw)
# df_hist_curr, df_hist_ly = load_historical_data()

# # --- HELPER FUNCTIONS ---
# def generate_yoy_dist_expanded(df_curr, df_ly, group_col):
#     def _agg(df, prefix):
#         if df.empty: return pd.DataFrame({group_col: []}).set_index(group_col)
#         df['Diff in mins'] = pd.to_numeric(df['Diff in mins'], errors='coerce').fillna(0)
#         g = df.groupby([group_col, 'Type of Outage']).agg(Count=('Type of Outage', 'size'), TotalHrs=('Diff in mins', lambda x: round(x.sum() / 60, 2)), AvgHrs=('Diff in mins', lambda x: round(x.mean() / 60, 2))).unstack(fill_value=0)
#         g.columns = [f"{prefix} {outage} ({metric})" for metric, outage in g.columns]
#         return g

#     c_grp = _agg(df_curr, 'Curr')
#     l_grp = _agg(df_ly, 'LY')
#     merged = pd.merge(c_grp, l_grp, on=group_col, how='outer').fillna(0).reset_index()
    
#     expected_cols = []
#     for prefix in ['Curr', 'LY']:
#         for outage in ['Planned Outage', 'Unplanned Outage']:
#             for metric in ['Count', 'TotalHrs', 'AvgHrs']:
#                 col_name = f"{prefix} {outage} ({metric})"
#                 expected_cols.append(col_name)
#                 if col_name not in merged.columns: merged[col_name] = 0
                    
#     for col in expected_cols:
#         if '(Count)' in col: merged[col] = merged[col].astype(int)
#         else: merged[col] = merged[col].astype(float).round(2)
            
#     merged['Curr Total (Count)'] = merged['Curr Planned Outage (Count)'] + merged['Curr Unplanned Outage (Count)']
#     merged['LY Total (Count)'] = merged['LY Planned Outage (Count)'] + merged['LY Unplanned Outage (Count)']
#     merged['YoY Delta (Total)'] = merged['Curr Total (Count)'] - merged['LY Total (Count)']
    
#     cols_order = [group_col, 'Curr Planned Outage (Count)', 'Curr Planned Outage (TotalHrs)', 'Curr Planned Outage (AvgHrs)', 'LY Planned Outage (Count)', 'LY Planned Outage (TotalHrs)', 'LY Planned Outage (AvgHrs)', 'Curr Unplanned Outage (Count)', 'Curr Unplanned Outage (TotalHrs)', 'Curr Unplanned Outage (AvgHrs)', 'LY Unplanned Outage (Count)', 'LY Unplanned Outage (TotalHrs)', 'LY Unplanned Outage (AvgHrs)', 'Curr Total (Count)', 'LY Total (Count)', 'YoY Delta (Total)']
#     return merged[cols_order]

# def apply_pu_gradient(styler, df):
#     p_cols = [c for c in df.columns if 'Planned' in str(c) and pd.api.types.is_numeric_dtype(df[c])]
#     u_cols = [c for c in df.columns if 'Unplanned' in str(c) and pd.api.types.is_numeric_dtype(df[c])]
#     if p_cols: styler = styler.background_gradient(subset=p_cols, cmap='Blues', vmin=0)
#     if u_cols: styler = styler.background_gradient(subset=u_cols, cmap='Reds', vmin=0)
#     return styler

# def highlight_delta(val):
#     if isinstance(val, int):
#         if val > 0: return 'color: #D32F2F; font-weight: bold;'
#         elif val < 0: return 'color: #388E3C; font-weight: bold;'
#     return ''

# def create_bucket_pivot(df, bucket_order):
#     if df.empty: return pd.DataFrame(columns=bucket_order + ['Total'])
#     pivot = pd.crosstab(df['Circle'], df['Duration Bucket'])
#     pivot = pivot.reindex(columns=[c for c in bucket_order if c in pivot.columns], fill_value=0)
#     pivot['Total'] = pivot.sum(axis=1)
#     return pivot


# # --- NOTORIOUS FEEDERS CALCULATION (Tab 1) ---
# df_5day['Outage Date'] = df_5day['Start Time'].dt.date
# feeder_days = df_5day.groupby(['Circle', 'Feeder'])['Outage Date'].nunique().reset_index(name='Days with Outages')
# notorious = feeder_days[feeder_days['Days with Outages'] >= 3]

# feeder_stats = df_5day.groupby(['Circle', 'Feeder']).agg(Total_Events=('Start Time', 'size'), Avg_Mins=('Diff in mins', 'mean'), Total_Mins=('Diff in mins', 'sum')).reset_index()
# feeder_stats.rename(columns={'Total_Events': 'Total Outage Events'}, inplace=True)
# feeder_stats['Total Duration (Hours)'] = (feeder_stats['Total_Mins'] / 60).round(2)
# feeder_stats['Average Duration (Hours)'] = (feeder_stats['Avg_Mins'] / 60).round(2)
# feeder_stats = feeder_stats.drop(columns=['Avg_Mins', 'Total_Mins'])

# notorious = notorious.merge(feeder_stats, on=['Circle', 'Feeder']).sort_values(by=['Circle', 'Days with Outages', 'Total Outage Events'], ascending=[True, False, False])
# top_5_notorious = notorious.groupby('Circle').head(5)
# notorious_set = set(zip(top_5_notorious['Circle'], top_5_notorious['Feeder']))


# # # --- MAIN DASHBOARD RENDER ---
# # st.title("⚡ Power Outage Monitoring Dashboard")
# # tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📈 YoY Comparison", "🛠️ PTW Frequency"])


# # --- MAIN DASHBOARD RENDER ---
# header_col1, header_col2 = st.columns([0.8, 0.2])

# with header_col1:
#     st.title("⚡ Power Outage Monitoring Dashboard")

# with header_col2:
#     # A clean, collapsed-label password box
#     admin_pwd = st.text_input("Admin Passcode", type="password", placeholder="Enter passcode to refresh...", label_visibility="collapsed")
    
#     if st.button("🔄 Refresh Data", type="primary", use_container_width=True):
#         if admin_pwd == "PsPcL":
#             if trigger_scraper():
#                 with open("scraper_lock.txt", "w") as f:
#                     f.write(str(time.time()))
#                 st.info("⏳ Cloud scraper started. Please wait ~2 minutes and refresh.")
#         elif admin_pwd == "":
#             st.warning("⚠️ Please enter a passcode to refresh.")
#         else:
#             st.error("❌ Incorrect passcode.")

# # (Ensure your tabs line is right here below the header!)
# tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📈 YoY Comparison", "🛠️ PTW Frequency"])


# # ==========================================
# # TAB 3: PTW FREQUENCY
# # ==========================================
# with tab3:
#     st.header("🛠️ PTW Frequency Tracker (Last 7 Days)")
#     st.markdown("Identifies specific feeders that had a Permit to Work (PTW) taken against them **two or more times** in separate requests over the last 7 days.")

#     if df_ptw.empty:
#         st.info("No PTW data found for the last 7 days.")
#     else:
#         ptw_col = next((c for c in df_ptw.columns if 'ptw' in c.lower() or 'request' in c.lower() or 'id' in c.lower()), None)
#         feeder_col = next((c for c in df_ptw.columns if 'feeder' in c.lower()), None)
#         status_col = next((c for c in df_ptw.columns if 'status' in c.lower()), None)
#         circle_col = next((c for c in df_ptw.columns if 'circle' in c.lower()), None)
        
#         # Dynamically map start/end times for PTW
#         start_col_ptw = next((c for c in df_ptw.columns if ('start' in c.lower() or 'from' in c.lower()) and ('date' in c.lower() or 'time' in c.lower())), None)
#         end_col_ptw = next((c for c in df_ptw.columns if ('end' in c.lower() or 'to' in c.lower()) and ('date' in c.lower() or 'time' in c.lower())), None)

#         if not ptw_col or not feeder_col:
#             st.error("Could not dynamically map required columns from the PTW export.")
#         else:
#             ptw_clean = df_ptw.copy()
#             if status_col:
#                 ptw_clean = ptw_clean[~ptw_clean[status_col].astype(str).str.contains('Cancellation', na=False, case=False)]

#             ptw_clean[feeder_col] = ptw_clean[feeder_col].astype(str).str.replace('|', ',', regex=False)
#             ptw_clean[feeder_col] = ptw_clean[feeder_col].str.split(',')
#             ptw_clean = ptw_clean.explode(feeder_col)
#             ptw_clean[feeder_col] = ptw_clean[feeder_col].str.strip()
#             ptw_clean = ptw_clean[ptw_clean[feeder_col] != '']

#             group_cols = [feeder_col]
#             if circle_col: group_cols.insert(0, circle_col)
                
#             ptw_counts = ptw_clean.groupby(group_cols).agg(Unique_PTWs=(ptw_col, 'nunique'), PTW_IDs=(ptw_col, lambda x: ', '.join(x.dropna().astype(str).unique()))).reset_index()
#             repeat_feeders = ptw_counts[ptw_counts['Unique_PTWs'] >= 2].sort_values(by='Unique_PTWs', ascending=False)
#             repeat_feeders = repeat_feeders.rename(columns={'Unique_PTWs': 'PTW Request Count', 'PTW_IDs': 'Associated PTW Request Numbers'})

#             kpi1, kpi2 = st.columns(2)
#             with kpi1: st.markdown(f'<div class="kpi-card"><div><div class="kpi-title">Total Active PTW Requests</div><div class="kpi-value">{df_ptw[ptw_col].nunique()}</div></div><div class="kpi-subtext"><span class="status-badge">Last 7 Days</span></div></div>', unsafe_allow_html=True)
#             with kpi2: st.markdown(f'<div class="kpi-card"><div><div class="kpi-title">Feeders with Multiple PTWs</div><div class="kpi-value">{len(repeat_feeders)}</div></div><div class="kpi-subtext"><span class="status-badge" style="background-color: #D32F2F;">🔴 Needs Review</span></div></div>', unsafe_allow_html=True)

#             st.divider()
#             st.subheader("⚠️ Repeat PTW Feeders Detail View")
#             if not repeat_feeders.empty:
#                 st.dataframe(repeat_feeders.style.set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#             else:
#                 st.success("No feeders had multiple PTWs requested against them in the last 7 days! 🎉")

#             # --- NEW ADDITION: TODAY'S PTW DETAILED VIEW ---
#             st.divider()
#             st.subheader("⏳ Today's PTW Requests (Detailed Breakdown)")
            
#             if start_col_ptw and end_col_ptw:
#                 today_ptws = ptw_clean.copy()
                
#                 # FORCE dayfirst=True for Indian date formats to prevent bad filtering
#                 today_ptws[start_col_ptw] = pd.to_datetime(today_ptws[start_col_ptw], dayfirst=True, errors='coerce')
#                 today_ptws[end_col_ptw] = pd.to_datetime(today_ptws[end_col_ptw], dayfirst=True, errors='coerce')
                
#                 # Check if there is a 'Request Date' column to be safe
#                 req_date_col = next((c for c in df_ptw.columns if 'request' in c.lower() and ('date' in c.lower() or 'time' in c.lower())), None)
#                 if req_date_col:
#                     today_ptws[req_date_col] = pd.to_datetime(today_ptws[req_date_col], dayfirst=True, errors='coerce')
#                     # Filter: Request Date is today OR Start Date is today
#                     mask = (today_ptws[start_col_ptw].dt.date == pd.to_datetime(today_str).date()) | \
#                            (today_ptws[req_date_col].dt.date == pd.to_datetime(today_str).date())
#                 else:
#                     mask = (today_ptws[start_col_ptw].dt.date == pd.to_datetime(today_str).date())
                
#                 today_ptws = today_ptws[mask]
                
#                 if not today_ptws.empty:
#                     # Calculate durations and buckets
#                     today_ptws['Duration (Hours)'] = (today_ptws[end_col_ptw] - today_ptws[start_col_ptw]).dt.total_seconds() / 3600.0
#                     today_ptws['Duration (Hours)'] = today_ptws['Duration (Hours)'].apply(lambda x: max(x, 0)).round(2)
                    
#                     def ptw_bucket(hrs):
#                         if pd.isna(hrs): return "Unknown"
#                         if hrs <= 2: return "0-2 Hrs"
#                         elif hrs <= 4: return "2-4 Hrs"
#                         elif hrs <= 8: return "4-8 Hrs"
#                         else: return "Above 8 Hrs"
                    
#                     today_ptws['Time Bucket'] = today_ptws['Duration (Hours)'].apply(ptw_bucket)
                    
#                     display_cols_ptw = [feeder_col, start_col_ptw, end_col_ptw, 'Duration (Hours)', 'Time Bucket']
#                     if circle_col: display_cols_ptw.insert(0, circle_col)
                    
#                     final_today_ptws = today_ptws[display_cols_ptw].dropna(subset=[start_col_ptw]).sort_values(by='Duration (Hours)', ascending=False)
                    
#                     # Highlight logic for > 5 hours
#                     def highlight_long_ptw(row):
#                         if pd.notna(row['Duration (Hours)']) and row['Duration (Hours)'] > 5:
#                             return ['background-color: rgba(220, 53, 69, 0.15); color: #850000; font-weight: bold'] * len(row)
#                         return [''] * len(row)
                        
#                     # Calculate unique feeders exceeding 5 hours
#                     over_5_count = final_today_ptws[final_today_ptws['Duration (Hours)'] > 5][feeder_col].nunique()
#                     st.markdown(f"**Total Feeders under PTW today exceeding 5 Hours:** `{over_5_count}`")
                    
#                     st.dataframe(final_today_ptws.style.apply(highlight_long_ptw, axis=1).format({'Duration (Hours)': '{:.2f}'}).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#                 else:
#                     st.info("No PTW requests recorded specifically for today.")
#             else:
#                 st.warning("Could not dynamically identify Start and End time columns in the PTW report.")


# # ==========================================
# # TAB 2: DYNAMIC YOY DRILL-DOWN
# # ==========================================
# with tab2:
#     st.header("📈 Historical Year-over-Year Drilldown")
    
#     if df_hist_curr.empty or df_hist_ly.empty:
#         st.error("Historical Master Data (Historical_2025.csv & Historical_2026.csv) not found in directory.")
#     else:
#         timeframe_options = {
#             "March (Entire Month)": (("2026-03-01", "2026-03-31"), ("2025-03-01", "2025-03-31")),
#             "1st Apr to 7th Apr": (("2026-04-01", "2026-04-07"), ("2025-04-01", "2025-04-07")),
#             "8th Apr to 14th Apr": (("2026-04-08", "2026-04-14"), ("2025-04-08", "2025-04-14")),
#             "15th Apr to 22nd Apr": (("2026-04-15", "2026-04-22"), ("2025-04-15", "2025-04-22")),
#             "1st Apr to 23rd Apr": (("2026-04-01", "2026-04-23"), ("2025-04-01", "2025-04-23"))
#         }

#         selected_tf = st.radio("Select Comparison Period:", list(timeframe_options.keys()), horizontal=True)
#         st.divider()

#         curr_bounds, ly_bounds = timeframe_options[selected_tf]
        
#         mask_curr = (df_hist_curr['Outage Date'] >= pd.to_datetime(curr_bounds[0]).date()) & (df_hist_curr['Outage Date'] <= pd.to_datetime(curr_bounds[1]).date())
#         filtered_curr = df_hist_curr[mask_curr]
        
#         mask_ly = (df_hist_ly['Outage Date'] >= pd.to_datetime(ly_bounds[0]).date()) & (df_hist_ly['Outage Date'] <= pd.to_datetime(ly_bounds[1]).date())
#         filtered_ly = df_hist_ly[mask_ly]

#         st.markdown(f"### 📍 1. Zone-wise Distribution ({selected_tf})")
#         st.caption("Includes total counts, total hours, and average hours. Click any row to drill down.")
        
#         yoy_zone = generate_yoy_dist_expanded(filtered_curr, filtered_ly, 'Zone')
        
#         zone_selection = st.dataframe(
#             yoy_zone.style.map(highlight_delta, subset=['YoY Delta (Total)']).format(precision=2).set_table_styles(HEADER_STYLES), 
#             width="stretch", hide_index=True, on_select="rerun", selection_mode="single-row"
#         )

#         if len(zone_selection.selection.rows) > 0:
#             selected_zone = yoy_zone.iloc[zone_selection.selection.rows[0]]['Zone']
            
#             st.markdown(f"### 🎯 2. Circle-wise Distribution for **{selected_zone}**")
#             st.caption("Click any row to drill down into Feeder-wise data.")
            
#             curr_zone_df = filtered_curr[filtered_curr['Zone'] == selected_zone]
#             ly_zone_df = filtered_ly[filtered_ly['Zone'] == selected_zone]
            
#             yoy_circle = generate_yoy_dist_expanded(curr_zone_df, ly_zone_df, 'Circle')
            
#             circle_selection = st.dataframe(
#                 yoy_circle.style.map(highlight_delta, subset=['YoY Delta (Total)']).format(precision=2).set_table_styles(HEADER_STYLES), 
#                 width="stretch", hide_index=True, on_select="rerun", selection_mode="single-row"
#             )

#             if len(circle_selection.selection.rows) > 0:
#                 selected_circle = yoy_circle.iloc[circle_selection.selection.rows[0]]['Circle']
#                 st.markdown(f"### 🔌 3. Feeder-wise Distribution for **{selected_circle}**")
                
#                 curr_circle_df = curr_zone_df[curr_zone_df['Circle'] == selected_circle]
#                 ly_circle_df = ly_zone_df[ly_zone_df['Circle'] == selected_circle]
                
#                 yoy_feeder = generate_yoy_dist_expanded(curr_circle_df, ly_circle_df, 'Feeder')
#                 st.dataframe(yoy_feeder.style.map(highlight_delta, subset=['YoY Delta (Total)']).format(precision=2).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)


# # ==========================================
# # TAB 1: ORIGINAL DASHBOARD
# # ==========================================
# with tab1:
#     col_left, col_right = st.columns(2, gap="large")

#     with col_left:
#         st.header(f"📅 Today's Outages ({now_ist.strftime('%d %b %Y')})")
#         today_planned = df_today[df_today['Type of Outage'] == 'Planned Outage']
#         today_unplanned = df_today[df_today['Type of Outage'] == 'Unplanned Outage']
        
#         st.subheader("Outage Summary")
#         kpi1, kpi2 = st.columns(2)
#         with kpi1:
#             active_p, closed_p = len(today_planned[today_planned['Status_Calc'] == 'Active']), len(today_planned[today_planned['Status_Calc'] == 'Closed'])
#             st.markdown(f'<div class="kpi-card"><div><div class="kpi-title">Total Planned Outages</div><div class="kpi-value">{len(today_planned)}</div></div><div class="kpi-subtext"><span class="status-badge">🔴 Active: {active_p}</span> <span class="status-badge">🟢 Closed: {closed_p}</span></div></div>', unsafe_allow_html=True)
#         with kpi2:
#             active_u, closed_u = len(today_unplanned[today_unplanned['Status_Calc'] == 'Active']), len(today_unplanned[today_unplanned['Status_Calc'] == 'Closed'])
#             st.markdown(f'<div class="kpi-card"><div><div class="kpi-title">Total Unplanned Outages</div><div class="kpi-value">{len(today_unplanned)}</div></div><div class="kpi-subtext"><span class="status-badge">🔴 Active: {active_u}</span> <span class="status-badge">🟢 Closed: {closed_u}</span></div></div>', unsafe_allow_html=True)

#         st.divider()
#         st.subheader("Zone-wise Distribution (Today)")
#         if not df_today.empty:
#             zone_today = df_today.groupby(['Zone', 'Type of Outage']).size().unstack(fill_value=0).reset_index()
#             for col in ['Planned Outage', 'Unplanned Outage']:
#                 if col not in zone_today: zone_today[col] = 0
#             zone_today['Total'] = zone_today['Planned Outage'] + zone_today['Unplanned Outage']
            
#             styled_zone_today = apply_pu_gradient(zone_today.style, zone_today).set_table_styles(HEADER_STYLES)
#             st.dataframe(styled_zone_today, width="stretch", hide_index=True)
#         else: st.info("No data available for today.")

#     with col_right:
#         st.header("⏳ Last 5 Days Trends")
#         fiveday_planned = df_5day[df_5day['Type of Outage'] == 'Planned Outage']
#         fiveday_unplanned = df_5day[df_5day['Type of Outage'] == 'Unplanned Outage']
        
#         st.subheader("Outage Summary (5 Days)")
#         kpi3, kpi4 = st.columns(2)
#         with kpi3: st.markdown(f'<div class="kpi-card"><div><div class="kpi-title">Total Planned Outages</div><div class="kpi-value">{len(fiveday_planned)}</div></div><div class="kpi-subtext" style="visibility: hidden;">Spacer</div></div>', unsafe_allow_html=True)
#         with kpi4: st.markdown(f'<div class="kpi-card"><div><div class="kpi-title">Total Unplanned Outages</div><div class="kpi-value">{len(fiveday_unplanned)}</div></div><div class="kpi-subtext" style="visibility: hidden;">Spacer</div></div>', unsafe_allow_html=True)

#         st.divider()
#         st.subheader("Zone-wise Distribution (5 Days)")
#         if not df_5day.empty:
#             zone_5day = df_5day.groupby(['Zone', 'Type of Outage']).size().unstack(fill_value=0).reset_index()
#             for col in ['Planned Outage', 'Unplanned Outage']:
#                 if col not in zone_5day: zone_5day[col] = 0
#             zone_5day['Total'] = zone_5day['Planned Outage'] + zone_5day['Unplanned Outage']
            
#             styled_zone_5day = apply_pu_gradient(zone_5day.style, zone_5day).set_table_styles(HEADER_STYLES)
#             st.dataframe(styled_zone_5day, width="stretch", hide_index=True)
#         else: st.info("No data available for the last 5 days.")

#     st.divider()
#     st.header("🚨 Notorious Feeders (3+ Days of Outages in Last 5 Days)")
#     st.caption("Top 5 worst-performing feeders per circle based on continuous outage days.")

#     noto_col1, noto_col2 = st.columns(2)
#     with noto_col1: selected_notorious_circle = st.selectbox("Filter by Circle:", ["All Circles"] + sorted(top_5_notorious['Circle'].unique().tolist()), index=0)
#     with noto_col2: selected_notorious_type = st.selectbox("Filter by Outage Type:", ["All Types", "Planned Outage", "Unplanned Outage"], index=0)

#     df_dyn = df_5day.copy()
#     if selected_notorious_type != "All Types": df_dyn = df_dyn[df_dyn['Type of Outage'] == selected_notorious_type]

#     if not df_dyn.empty:
#         dyn_days = df_dyn.groupby(['Circle', 'Feeder'])['Outage Date'].nunique().reset_index(name='Days with Outages')
#         dyn_noto = dyn_days[dyn_days['Days with Outages'] >= 3]

#         if not dyn_noto.empty:
#             dyn_stats = df_dyn.groupby(['Circle', 'Feeder']).agg(Total_Events=('Start Time', 'size'), Avg_Mins=('Diff in mins', 'mean'), Total_Mins=('Diff in mins', 'sum')).reset_index()
#             dyn_stats.rename(columns={'Total_Events': 'Total Outage Events'}, inplace=True)
#             dyn_stats['Total Duration (Hours)'] = (dyn_stats['Total_Mins'] / 60).round(2)
#             dyn_stats['Average Duration (Hours)'] = (dyn_stats['Avg_Mins'] / 60).round(2)
#             dyn_stats = dyn_stats.drop(columns=['Avg_Mins', 'Total_Mins'])

#             dyn_noto = dyn_noto.merge(dyn_stats, on=['Circle', 'Feeder']).sort_values(by=['Circle', 'Days with Outages', 'Total Outage Events'], ascending=[True, False, False])
#             dyn_top5 = dyn_noto.groupby('Circle').head(5)
#             filtered_notorious = dyn_top5[dyn_top5['Circle'] == selected_notorious_circle] if selected_notorious_circle != "All Circles" else dyn_top5

#             if not filtered_notorious.empty:
#                 st.dataframe(filtered_notorious.style.format({'Average Duration (Hours)': '{:.2f}', 'Total Duration (Hours)': '{:.2f}'}).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#             else: st.info(f"No notorious feeders found for {selected_notorious_circle} matching the criteria.")
#         else: st.info(f"No notorious feeders identified for {selected_notorious_type}.")
#     else: st.info("No data available for the selected outage type.")

#     st.divider()
#     st.header("Comprehensive Circle-wise Breakdown")
#     bucket_order = ["Up to 2 Hrs", "2-4 Hrs", "4-8 Hrs", "Above 8 Hrs", "Active/Unknown"]

#     curr_1d_p_tab1 = create_bucket_pivot(df_today[df_today['Type of Outage'] == 'Planned Outage'], bucket_order)
#     curr_1d_u_tab1 = create_bucket_pivot(df_today[df_today['Type of Outage'] == 'Unplanned Outage'], bucket_order)
#     curr_5d_p_tab1 = create_bucket_pivot(df_5day[df_5day['Type of Outage'] == 'Planned Outage'], bucket_order)
#     curr_5d_u_tab1 = create_bucket_pivot(df_5day[df_5day['Type of Outage'] == 'Unplanned Outage'], bucket_order)

#     combined_circle = pd.concat(
#         [curr_1d_p_tab1, curr_1d_u_tab1, curr_5d_p_tab1, curr_5d_u_tab1], 
#         axis=1, 
#         keys=['TODAY (Planned Outages)', 'TODAY (Unplanned Outages)', 'LAST 5 DAYS (Planned Outages)', 'LAST 5 DAYS (Unplanned Outages)']
#     ).fillna(0).astype(int)

#     st.markdown(" **Click on any row inside the table below** to view the specific Feeder drill-down details.")

#     if not combined_circle.empty:
#         styled_combined = apply_pu_gradient(combined_circle.style, combined_circle).set_table_styles(HEADER_STYLES)
        
#         selection_event = st.dataframe(styled_combined, width="stretch", on_select="rerun", selection_mode="single-row")

#         if len(selection_event.selection.rows) > 0:
#             selected_circle = combined_circle.index[selection_event.selection.rows[0]]
#             st.subheader(f"Feeder Details for: {selected_circle}")
            
#             circle_dates = sorted(list(df_5day[df_5day['Circle'] == selected_circle]['Outage Date'].dropna().unique()))
#             selected_dates = st.multiselect("Filter 5-Days View by Date:", options=circle_dates, default=circle_dates, format_func=lambda x: x.strftime('%d %b %Y'))
            
#             def highlight_notorious(row): return ['background-color: rgba(220, 53, 69, 0.15); color: #850000; font-weight: bold'] * len(row) if (selected_circle, row['Feeder']) in notorious_set else [''] * len(row)

#             today_left, today_right = st.columns(2)
#             with today_left:
#                 st.markdown(f"**🔴 TODAY: Planned Outages**")
#                 feeder_list_tp = today_planned[today_planned['Circle'] == selected_circle][['Feeder', 'Diff in mins', 'Status_Calc', 'Duration Bucket']].rename(columns={'Status_Calc': 'Status'})
#                 st.dataframe(feeder_list_tp.style.apply(highlight_notorious, axis=1).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#             with today_right:
#                 st.markdown(f"**🔴 TODAY: Unplanned Outages**")
#                 feeder_list_tu = today_unplanned[today_unplanned['Circle'] == selected_circle][['Feeder', 'Diff in mins', 'Status_Calc', 'Duration Bucket']].rename(columns={'Status_Calc': 'Status'})
#                 st.dataframe(feeder_list_tu.style.apply(highlight_notorious, axis=1).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
                
#             st.write("") 
#             fiveday_left, fiveday_right = st.columns(2)
            
#             with fiveday_left:
#                 st.markdown(f"**🟢 5-DAYS: Planned Outages**")
#                 feeder_list_fp = fiveday_planned[(fiveday_planned['Circle'] == selected_circle) & (fiveday_planned['Outage Date'].isin(selected_dates))].copy()
#                 if not feeder_list_fp.empty:
#                     feeder_list_fp['Diff in Hours'] = (feeder_list_fp['Diff in mins'] / 60).round(2)
#                     st.dataframe(feeder_list_fp[['Outage Date', 'Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket']].style.apply(highlight_notorious, axis=1).format({'Diff in Hours': '{:.2f}'}).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#                 else: st.dataframe(pd.DataFrame(columns=['Outage Date', 'Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket']).style.set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
                
#             with fiveday_right:
#                 st.markdown(f"**🟢 5-DAYS: Unplanned Outages**")
#                 feeder_list_fu = fiveday_unplanned[(fiveday_unplanned['Circle'] == selected_circle) & (fiveday_unplanned['Outage Date'].isin(selected_dates))].copy()
#                 if not feeder_list_fu.empty:
#                     feeder_list_fu['Diff in Hours'] = (feeder_list_fu['Diff in mins'] / 60).round(2)
#                     st.dataframe(feeder_list_fu[['Outage Date', 'Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket']].style.apply(highlight_notorious, axis=1).format({'Diff in Hours': '{:.2f}'}).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#                 else: st.dataframe(pd.DataFrame(columns=['Outage Date', 'Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket']).style.set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#     else: st.info("No circle data available.")

#     # --- NEW ADDITION: TODAY'S PLANNED OUTAGES > 5 HOURS ---
#     st.divider()
#     st.header("⚠️ Planned Outages Exceeding 5 Hours (Today)")
    
#     long_planned = today_planned[pd.to_numeric(today_planned['Diff in mins'], errors='coerce').fillna(0) > 300].copy()
    
#     if not long_planned.empty:
#         long_planned['Duration (Hours)'] = (long_planned['Diff in mins'] / 60).round(2)
#         cols_to_show = ['Zone', 'Circle', 'Feeder', 'Start Time', 'End Time', 'Duration (Hours)', 'Status_Calc']
        
#         # Ensure columns exist before displaying
#         cols_to_show = [c for c in cols_to_show if c in long_planned.columns]
        
#         def highlight_long(row):
#             return ['background-color: rgba(220, 53, 69, 0.15); color: #850000; font-weight: bold'] * len(row)
            
#         # 1A. Add Feeder Counts
#         total_long_feeders = long_planned['Feeder'].nunique()
#         st.markdown(f"**Total Feeders with Planned Outages > 5 Hours:** `{total_long_feeders}`")
        
#         st.dataframe(
#             long_planned[cols_to_show].sort_values(by='Duration (Hours)', ascending=False).style.apply(highlight_long, axis=1).format({'Duration (Hours)': '{:.2f}'}).set_table_styles(HEADER_STYLES), 
#             width="stretch", 
#             hide_index=True
#         )

#         # 1B. Add Zone-wise Summary Table
#         st.subheader("📍 Zone-wise Summary (> 5 Hrs Planned Outages)")
        
#         zone_summary = long_planned.groupby('Zone').agg(
#             Total_Feeders=('Feeder', 'nunique'),
#             Total_Duration_Hours=('Duration (Hours)', 'sum')
#         ).reset_index()
        
#         zone_summary.rename(columns={
#             'Total_Feeders': 'Total Feeders', 
#             'Total_Duration_Hours': 'Total Duration (Hours)'
#         }, inplace=True)
        
#         st.dataframe(
#             zone_summary.style.format({'Total Duration (Hours)': '{:.2f}'}).set_table_styles(HEADER_STYLES), 
#             width="stretch", 
#             hide_index=True
#         )
        
#     else:
#         st.success("No Planned Outages exceeded 5 hours today! 🎉")


# #  =======================================================================================================================================
# #  =======================================================================================================================================
# #V6
# #  =======================================================================================================================================
# #  =======================================================================================================================================
# import os
# import time
# import requests
# import streamlit as st
# import pandas as pd
# from datetime import datetime, timedelta, timezone

# # --- PAGE CONFIGURATION ---
# st.set_page_config(page_title="Power Outage Monitoring Dashboard", layout="wide")

# # --- GLOBAL TABLE HEADER STYLING ---
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
#         'selector': 'th div',
#         'props': [
#             ('color', '#FFC107 !important'),
#             ('font-weight', 'bold !important')
#         ]
#     }
# ]

# # --- COLOR THEME & ENTERPRISE CSS ---
# st.markdown("""
#     <style>
#         .block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
#         p, span, div, caption, .stMarkdown { color: #000000 !important; }
#         h1, h2, h3, h4, h5, h6, div.block-container h1 { color: #004085 !important; font-weight: 700 !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
#         div.block-container h1 { text-align: center; border-bottom: 3px solid #004085 !important; padding-bottom: 10px; margin-bottom: 30px !important; font-size: 2.2rem !important; }
#         h2 { font-size: 1.3rem !important; border-bottom: 2px solid #004085 !important; padding-bottom: 5px; margin-bottom: 10px !important; }
#         h3 { font-size: 1.05rem !important; margin-bottom: 12px !important; text-transform: uppercase; letter-spacing: 0.5px; }
#         hr { border: 0; border-top: 1px solid #004085; margin: 1.5rem 0; opacity: 0.3; }
        
#         .kpi-card { background: linear-gradient(135deg, #004481 0%, #0066cc 100%); border-radius: 6px; padding: 1.2rem 1.2rem; display: flex; flex-direction: column; justify-content: space-between; height: 100%; box-shadow: 0 2px 4px rgba(0,0,0,0.08); transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out; border: 1px solid #003366; }
#         .kpi-card:hover { transform: translateY(-4px); box-shadow: 0 8px 16px rgba(0, 68, 129, 0.2); }
#         .kpi-card .kpi-title, .kpi-title { color: #FFC107 !important; font-weight: 600; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.4rem; }
#         .kpi-card .kpi-value, .kpi-value { color: #FFFFFF !important; font-weight: 700; font-size: 2.6rem; margin-bottom: 0; line-height: 1.1; }
#         .kpi-card .kpi-subtext, .kpi-subtext { color: #F8F9FA !important; font-size: 0.85rem; margin-top: 1rem; padding-top: 0.6rem; border-top: 1px solid rgba(255, 255, 255, 0.2); display: flex; justify-content: flex-start; gap: 15px; }
        
#         .status-badge { background-color: rgba(0, 0, 0, 0.25); padding: 3px 8px; border-radius: 4px; font-weight: 500; color: #FFFFFF !important; }
#         [data-testid="stDataFrame"] > div { border: 2px solid #004085 !important; border-radius: 6px; overflow: hidden; }
#     </style>
# """, unsafe_allow_html=True)

# # --- IST TIMEZONE SETUP ---
# IST = timezone(timedelta(hours=5, minutes=30))

# # --- GITHUB TRIGGER LOGIC ---
# def trigger_scraper():
#     repo_owner = "jamjayjoshi108"
#     repo_name = "pspcl_daily_outage_dashboard" 
#     url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/263899469/dispatches"
#     headers = {"Accept": "application/vnd.github.v3+json", "Authorization": f"token {st.secrets['GITHUB_TOKEN']}"}
#     response = requests.post(url, headers=headers, json={"ref": "main"})
    
#     if response.status_code == 204:
#         st.toast("✅ Scraper triggered successfully in the cloud!")
#         return True
#     else:
#         st.error(f"❌ Failed to trigger scraper. GitHub responded: {response.text}")
#         return False

# # --- 1. FILE DEFINITIONS & CHECKING LOGIC ---
# now_ist = datetime.now(IST)
# if now_ist.hour < 8: now_ist -= timedelta(days=1)
# today_str = now_ist.strftime("%Y-%m-%d")

# try: ly_date = now_ist.replace(year=now_ist.year - 1)
# except ValueError: ly_date = now_ist.replace(year=now_ist.year - 1, day=28)
# ly_str = ly_date.strftime("%Y-%m-%d")

# file_today = f"{today_str}_Outages_Today.csv"
# file_5day = f"{today_str}_Outages_Last_5_Days.csv"
# file_ptw = f"{today_str}_PTW_Last_7_Days.csv"

# files_missing = not (os.path.exists(file_today) and os.path.exists(file_5day) and os.path.exists(file_ptw))

# if files_missing:
#     lock_file = "scraper_lock.txt"
#     should_trigger = True
#     if os.path.exists(lock_file) and time.time() - os.path.getmtime(lock_file) < 300: 
#         should_trigger = False
            
#     if should_trigger:
#         if trigger_scraper():
#             with open(lock_file, "w") as f: f.write(str(time.time()))
#             st.warning(f"⚠️ Data for {today_str} is missing. Automatically fetching fresh data from PSPCL...")
#             st.info("⏳ Please wait ~2 minutes and refresh this page.")
#         else:
#             st.error("🚨 Could not fetch data due to GitHub API error. Fix the token to continue.")
#     else:
#         st.info("⏳ The scraper is currently running in the background. Please wait a moment and refresh.")
#     st.stop()

# # --- 2. DATA LOADING LOGIC ---
# @st.cache_data(ttl="10m")
# def load_live_data(f_today, f_5day, f_ptw):
#     df_today = pd.read_csv(f_today)
#     df_5day = pd.read_csv(f_5day)
#     df_ptw = pd.read_csv(f_ptw)
    
#     df_today = df_today[~df_today['Status'].astype(str).str.contains('Cancel', na=False, case=False)]
#     df_5day = df_5day[~df_5day['Status'].astype(str).str.contains('Cancel', na=False, case=False)]
    
#     time_cols = ['Schedule Created At', 'Start Time', 'End Time', 'Last Updated At']
#     for df in [df_today, df_5day]:
#         for col in time_cols: df[col] = pd.to_datetime(df[col], errors='coerce')
#         df['Status_Calc'] = df['Status'].apply(lambda x: 'Active' if str(x).strip().title() == 'Open' else 'Closed')
        
#         def assign_bucket(mins):
#             if pd.isna(mins) or mins < 0: return "Active/Unknown"
#             hrs = mins / 60
#             if hrs <= 2: return "Up to 2 Hrs"
#             elif hrs <= 4: return "2-4 Hrs"
#             elif hrs <= 8: return "4-8 Hrs"
#             else: return "Above 8 Hrs"
#         df['Duration Bucket'] = df['Diff in mins'].apply(assign_bucket)
        
#     return df_today, df_5day, df_ptw

# @st.cache_data
# def load_historical_data():
#     if os.path.exists('Historical_2026.csv') and os.path.exists('Historical_2025.csv'):
#         df_26, df_25 = pd.read_csv('Historical_2026.csv'), pd.read_csv('Historical_2025.csv')
#         for df in [df_26, df_25]:
#             df['Outage Date'] = pd.to_datetime(df['Start Time'], errors='coerce').dt.date
#         return df_26, df_25
#     return pd.DataFrame(), pd.DataFrame()

# df_today, df_5day, df_ptw = load_live_data(file_today, file_5day, file_ptw)
# df_hist_curr, df_hist_ly = load_historical_data()

# # --- HELPER FUNCTIONS ---
# def generate_yoy_dist_expanded(df_curr, df_ly, group_col):
#     def _agg(df, prefix):
#         if df.empty: return pd.DataFrame({group_col: []}).set_index(group_col)
#         df['Diff in mins'] = pd.to_numeric(df['Diff in mins'], errors='coerce').fillna(0)
#         g = df.groupby([group_col, 'Type of Outage']).agg(
#             Count=('Type of Outage', 'size'),
#             TotalHrs=('Diff in mins', lambda x: round(x.sum() / 60, 2)),
#             AvgHrs=('Diff in mins', lambda x: round(x.mean() / 60, 2))
#         ).unstack(fill_value=0)
#         g.columns = [f"{prefix} {outage} ({metric})" for metric, outage in g.columns]
#         return g

#     c_grp = _agg(df_curr, 'Curr')
#     l_grp = _agg(df_ly, 'LY')
#     merged = pd.merge(c_grp, l_grp, on=group_col, how='outer').fillna(0).reset_index()
    
#     expected_cols = []
#     for prefix in ['Curr', 'LY']:
#         for outage in ['Planned Outage', 'Unplanned Outage']:
#             for metric in ['Count', 'TotalHrs', 'AvgHrs']:
#                 col_name = f"{prefix} {outage} ({metric})"
#                 expected_cols.append(col_name)
#                 if col_name not in merged.columns: merged[col_name] = 0
                    
#     for col in expected_cols:
#         if '(Count)' in col: merged[col] = merged[col].astype(int)
#         else: merged[col] = merged[col].astype(float).round(2)
            
#     merged['Curr Total (Count)'] = merged['Curr Planned Outage (Count)'] + merged['Curr Unplanned Outage (Count)']
#     merged['LY Total (Count)'] = merged['LY Planned Outage (Count)'] + merged['LY Unplanned Outage (Count)']
#     merged['YoY Delta (Total)'] = merged['Curr Total (Count)'] - merged['LY Total (Count)']
    
#     cols_order = [group_col, 
#                   'Curr Planned Outage (Count)', 'Curr Planned Outage (TotalHrs)', 'Curr Planned Outage (AvgHrs)',
#                   'LY Planned Outage (Count)', 'LY Planned Outage (TotalHrs)', 'LY Planned Outage (AvgHrs)',
#                   'Curr Unplanned Outage (Count)', 'Curr Unplanned Outage (TotalHrs)', 'Curr Unplanned Outage (AvgHrs)',
#                   'LY Unplanned Outage (Count)', 'LY Unplanned Outage (TotalHrs)', 'LY Unplanned Outage (AvgHrs)',
#                   'Curr Total (Count)', 'LY Total (Count)', 'YoY Delta (Total)']
#     cols_order = [c for c in cols_order if c in merged.columns]
#     merged = merged[cols_order]

#     # Add Grand Total Row logically
#     if not merged.empty:
#         gt_row = pd.Series(index=cols_order, dtype=object)
#         gt_row[group_col] = 'Grand Total'
#         for col in cols_order:
#             if col == group_col: continue
#             if '(Count)' in col or 'Delta' in col or '(TotalHrs)' in col:
#                 gt_row[col] = merged[col].sum()
        
#         # Correctly recalculate Averages for the Grand Total row
#         for prefix in ['Curr', 'LY']:
#             for outage in ['Planned Outage', 'Unplanned Outage']:
#                 count_col = f"{prefix} {outage} (Count)"
#                 tot_col = f"{prefix} {outage} (TotalHrs)"
#                 avg_col = f"{prefix} {outage} (AvgHrs)"
#                 if count_col in cols_order and tot_col in cols_order and avg_col in cols_order:
#                     gt_row[avg_col] = round(gt_row[tot_col] / gt_row[count_col], 2) if gt_row[count_col] > 0 else 0
        
#         merged = pd.concat([merged, pd.DataFrame([gt_row])], ignore_index=True)

#     return merged

# def apply_pu_gradient(styler, df):
#     p_cols = [c for c in df.columns if 'Planned' in str(c) and pd.api.types.is_numeric_dtype(df[c])]
#     u_cols = [c for c in df.columns if 'Unplanned' in str(c) and pd.api.types.is_numeric_dtype(df[c])]
#     pc_cols = [c for c in df.columns if 'Power Off By PC' in str(c) and pd.api.types.is_numeric_dtype(df[c])]
    
#     # Safely isolate the Grand Total row to exclude it from background gradients
#     if 'Grand Total' in df.index:
#         row_idx = df.index.drop('Grand Total')
#     else:
#         try:
#             group_col = df.columns[0]
#             if not df.empty and df.iloc[-1][group_col] == 'Grand Total':
#                 row_idx = df.index[:-1]
#             else:
#                 row_idx = df.index
#         except:
#             row_idx = df.index
            
#     if p_cols: styler = styler.background_gradient(subset=pd.IndexSlice[row_idx, p_cols], cmap='Blues', vmin=0)
#     if pc_cols: styler = styler.background_gradient(subset=pd.IndexSlice[row_idx, pc_cols], cmap='Purples', vmin=0)
#     if u_cols: styler = styler.background_gradient(subset=pd.IndexSlice[row_idx, u_cols], cmap='Reds', vmin=0)
#     return styler

# def highlight_delta(val):
#     if isinstance(val, (int, float)):
#         if val > 0: return 'color: #D32F2F; font-weight: bold;'
#         elif val < 0: return 'color: #388E3C; font-weight: bold;'
#     return ''

# def create_bucket_pivot(df, bucket_order):
#     if df.empty: return pd.DataFrame(columns=bucket_order + ['Total'])
#     pivot = pd.crosstab(df['Circle'], df['Duration Bucket'])
#     pivot = pivot.reindex(columns=[c for c in bucket_order if c in pivot.columns], fill_value=0)
#     pivot['Total'] = pivot.sum(axis=1)
#     return pivot


# # --- NOTORIOUS FEEDERS CALCULATION (Tab 1) ---
# df_5day['Outage Date'] = df_5day['Start Time'].dt.date
# feeder_days = df_5day.groupby(['Circle', 'Feeder'])['Outage Date'].nunique().reset_index(name='Days with Outages')
# notorious = feeder_days[feeder_days['Days with Outages'] >= 3]

# feeder_stats = df_5day.groupby(['Circle', 'Feeder']).agg(Total_Events=('Start Time', 'size'), Max_Mins=('Diff in mins', 'max'), Total_Mins=('Diff in mins', 'sum')).reset_index()
# feeder_stats.rename(columns={'Total_Events': 'Total Outage Events'}, inplace=True)
# feeder_stats['Total Duration (Hours)'] = (feeder_stats['Total_Mins'] / 60).round(2)
# feeder_stats['Max Duration (Hours)'] = (feeder_stats['Max_Mins'] / 60).round(2)
# feeder_stats = feeder_stats.drop(columns=['Max_Mins', 'Total_Mins'])

# notorious = notorious.merge(feeder_stats, on=['Circle', 'Feeder']).sort_values(by=['Circle', 'Days with Outages', 'Total Outage Events'], ascending=[True, False, False])
# top_5_notorious = notorious.groupby('Circle').head(5)
# notorious_set = set(zip(top_5_notorious['Circle'], top_5_notorious['Feeder']))


# # --- MAIN DASHBOARD RENDER ---
# st.title("⚡ Power Outage Monitoring Dashboard")
# tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📈 YoY Comparison", "🛠️ PTW Frequency"])

# # ==========================================
# # TAB 3: PTW FREQUENCY
# # ==========================================
# with tab3:
#     st.header("🛠️ PTW Frequency Tracker (Last 7 Days)")
#     st.markdown("Identifies specific feeders that had a Permit to Work (PTW) taken against them **two or more times** in separate requests over the last 7 days.")

#     if df_ptw.empty:
#         st.info("No PTW data found for the last 7 days.")
#     else:
#         ptw_col = next((c for c in df_ptw.columns if 'ptw' in c.lower() or 'request' in c.lower() or 'id' in c.lower()), None)
#         feeder_col = next((c for c in df_ptw.columns if 'feeder' in c.lower()), None)
#         status_col = next((c for c in df_ptw.columns if 'status' in c.lower()), None)
#         circle_col = next((c for c in df_ptw.columns if 'circle' in c.lower()), None)

#         if not ptw_col or not feeder_col:
#             st.error("Could not dynamically map required columns from the PTW export.")
#         else:
#             ptw_clean = df_ptw.copy()
#             if status_col:
#                 ptw_clean = ptw_clean[~ptw_clean[status_col].astype(str).str.contains('Cancellation', na=False, case=False)]

#             ptw_clean[feeder_col] = ptw_clean[feeder_col].astype(str).str.replace('|', ',', regex=False)
#             ptw_clean[feeder_col] = ptw_clean[feeder_col].str.split(',')
#             ptw_clean = ptw_clean.explode(feeder_col)
#             ptw_clean[feeder_col] = ptw_clean[feeder_col].str.strip()
#             ptw_clean = ptw_clean[ptw_clean[feeder_col] != '']

#             group_cols = [feeder_col]
#             if circle_col: group_cols.insert(0, circle_col)
                
#             ptw_counts = ptw_clean.groupby(group_cols).agg(Unique_PTWs=(ptw_col, 'nunique'), PTW_IDs=(ptw_col, lambda x: ', '.join(x.dropna().astype(str).unique()))).reset_index()
#             repeat_feeders = ptw_counts[ptw_counts['Unique_PTWs'] >= 2].sort_values(by='Unique_PTWs', ascending=False)
#             repeat_feeders = repeat_feeders.rename(columns={'Unique_PTWs': 'PTW Request Count', 'PTW_IDs': 'Associated PTW Request Numbers'})

#             # Add Grand Total Row
#             if not repeat_feeders.empty:
#                 gt_dict = {c: '' for c in repeat_feeders.columns}
#                 gt_dict[repeat_feeders.columns[0]] = 'Grand Total'
#                 gt_dict['PTW Request Count'] = int(repeat_feeders['PTW Request Count'].sum())
#                 repeat_feeders = pd.concat([repeat_feeders, pd.DataFrame([gt_dict])], ignore_index=True)

#             kpi1, kpi2 = st.columns(2)
#             with kpi1: st.markdown(f'<div class="kpi-card"><div><div class="kpi-title">Total Active PTW Requests</div><div class="kpi-value">{df_ptw[ptw_col].nunique()}</div></div><div class="kpi-subtext"><span class="status-badge">Last 7 Days</span></div></div>', unsafe_allow_html=True)
#             with kpi2: st.markdown(f'<div class="kpi-card"><div><div class="kpi-title">Feeders with Multiple PTWs</div><div class="kpi-value">{len(repeat_feeders) - 1}</div></div><div class="kpi-subtext"><span class="status-badge" style="background-color: #D32F2F;">🔴 Needs Review</span></div></div>', unsafe_allow_html=True) # subtracted 1 for GT row

#             st.divider()
#             st.subheader("⚠️ Repeat PTW Feeders Detail View")
#             if not repeat_feeders.empty:
#                 st.dataframe(repeat_feeders.style.set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#             else:
#                 st.success("No feeders had multiple PTWs requested against them in the last 7 days! 🎉")

# # ==========================================
# # TAB 2: DYNAMIC YOY DRILL-DOWN
# # ==========================================
# with tab2:
#     st.header("📈 Historical Year-over-Year Drilldown")
    
#     if df_hist_curr.empty or df_hist_ly.empty:
#         st.error("Historical Master Data (Historical_2025.csv & Historical_2026.csv) not found in directory.")
#     else:
#         timeframe_options = {
#             "March (Entire Month)": (("2026-03-01", "2026-03-31"), ("2025-03-01", "2025-03-31")),
#             "1st Apr to 7th Apr": (("2026-04-01", "2026-04-07"), ("2025-04-01", "2025-04-07")),
#             "8th Apr to 14th Apr": (("2026-04-08", "2026-04-14"), ("2025-04-08", "2025-04-14")),
#             "15th Apr to 22nd Apr": (("2026-04-15", "2026-04-22"), ("2025-04-15", "2025-04-22")),
#             "1st Apr to 23rd Apr": (("2026-04-01", "2026-04-23"), ("2025-04-01", "2025-04-23"))
#         }

#         selected_tf = st.radio("Select Comparison Period:", list(timeframe_options.keys()), horizontal=True)
#         st.divider()

#         curr_bounds, ly_bounds = timeframe_options[selected_tf]
        
#         mask_curr = (df_hist_curr['Outage Date'] >= pd.to_datetime(curr_bounds[0]).date()) & (df_hist_curr['Outage Date'] <= pd.to_datetime(curr_bounds[1]).date())
#         filtered_curr = df_hist_curr[mask_curr]
        
#         mask_ly = (df_hist_ly['Outage Date'] >= pd.to_datetime(ly_bounds[0]).date()) & (df_hist_ly['Outage Date'] <= pd.to_datetime(ly_bounds[1]).date())
#         filtered_ly = df_hist_ly[mask_ly]

#         st.markdown(f"### 📍 1. Zone-wise Distribution ({selected_tf})")
#         st.caption("Includes total counts, total hours, and average hours. Click any row to drill down.")
        
#         yoy_zone = generate_yoy_dist_expanded(filtered_curr, filtered_ly, 'Zone')
        
#         zone_selection = st.dataframe(
#             yoy_zone.style.map(highlight_delta, subset=['YoY Delta (Total)']).format(precision=2).set_table_styles(HEADER_STYLES), 
#             width="stretch", hide_index=True, on_select="rerun", selection_mode="single-row"
#         )

#         if len(zone_selection.selection.rows) > 0:
#             selected_zone = yoy_zone.iloc[zone_selection.selection.rows[0]]['Zone']
            
#             if selected_zone != 'Grand Total':
#                 st.markdown(f"### 🎯 2. Circle-wise Distribution for **{selected_zone}**")
#                 st.caption("Click any row to drill down into Feeder-wise data.")
                
#                 curr_zone_df = filtered_curr[filtered_curr['Zone'] == selected_zone]
#                 ly_zone_df = filtered_ly[filtered_ly['Zone'] == selected_zone]
                
#                 yoy_circle = generate_yoy_dist_expanded(curr_zone_df, ly_zone_df, 'Circle')
                
#                 circle_selection = st.dataframe(
#                     yoy_circle.style.map(highlight_delta, subset=['YoY Delta (Total)']).format(precision=2).set_table_styles(HEADER_STYLES), 
#                     width="stretch", hide_index=True, on_select="rerun", selection_mode="single-row"
#                 )

#                 if len(circle_selection.selection.rows) > 0:
#                     selected_circle = yoy_circle.iloc[circle_selection.selection.rows[0]]['Circle']
                    
#                     if selected_circle != 'Grand Total':
#                         st.markdown(f"### 🔌 3. Feeder-wise Distribution for **{selected_circle}**")
                        
#                         curr_circle_df = curr_zone_df[curr_zone_df['Circle'] == selected_circle]
#                         ly_circle_df = ly_zone_df[ly_zone_df['Circle'] == selected_circle]
                        
#                         yoy_feeder = generate_yoy_dist_expanded(curr_circle_df, ly_circle_df, 'Feeder')
#                         st.dataframe(yoy_feeder.style.map(highlight_delta, subset=['YoY Delta (Total)']).format(precision=2).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)


# # ==========================================
# # TAB 1: ORIGINAL DASHBOARD
# # ==========================================
# with tab1:
#     col_left, col_right = st.columns(2, gap="large")

#     with col_left:
#         st.header(f"📅 Today's Outages ({now_ist.strftime('%d %b %Y')})")
#         today_planned = df_today[df_today['Type of Outage'] == 'Planned Outage']
#         today_pc = df_today[df_today['Type of Outage'] == 'Power Off By PC']
#         today_unplanned = df_today[df_today['Type of Outage'] == 'Unplanned Outage']
        
#         st.subheader("Outage Summary")
#         kpi1, kpi2, kpi3 = st.columns(3)
#         with kpi1:
#             active_p, closed_p = len(today_planned[today_planned['Status_Calc'] == 'Active']), len(today_planned[today_planned['Status_Calc'] == 'Closed'])
#             st.markdown(f'<div class="kpi-card"><div><div class="kpi-title">Planned Outages</div><div class="kpi-value">{len(today_planned)}</div></div><div class="kpi-subtext"><span class="status-badge">🔴 Active: {active_p}</span> <span class="status-badge">🟢 Closed: {closed_p}</span></div></div>', unsafe_allow_html=True)
#         with kpi2:
#             active_pc, closed_pc = len(today_pc[today_pc['Status_Calc'] == 'Active']), len(today_pc[today_pc['Status_Calc'] == 'Closed'])
#             st.markdown(f'<div class="kpi-card"><div><div class="kpi-title">Power Off By PC</div><div class="kpi-value">{len(today_pc)}</div></div><div class="kpi-subtext"><span class="status-badge">🔴 Active: {active_pc}</span> <span class="status-badge">🟢 Closed: {closed_pc}</span></div></div>', unsafe_allow_html=True)
#         with kpi3:
#             active_u, closed_u = len(today_unplanned[today_unplanned['Status_Calc'] == 'Active']), len(today_unplanned[today_unplanned['Status_Calc'] == 'Closed'])
#             st.markdown(f'<div class="kpi-card"><div><div class="kpi-title">Unplanned Outages</div><div class="kpi-value">{len(today_unplanned)}</div></div><div class="kpi-subtext"><span class="status-badge">🔴 Active: {active_u}</span> <span class="status-badge">🟢 Closed: {closed_u}</span></div></div>', unsafe_allow_html=True)

#         st.divider()
#         st.subheader("Zone-wise Distribution (Today)")
#         if not df_today.empty:
#             zone_today = df_today.groupby(['Zone', 'Type of Outage']).size().unstack(fill_value=0).reset_index()
#             for col in ['Planned Outage', 'Power Off By PC', 'Unplanned Outage']:
#                 if col not in zone_today: zone_today[col] = 0
            
#             # Horizontal Overall Total
#             zone_today['Total'] = zone_today['Planned Outage'] + zone_today['Power Off By PC'] + zone_today['Unplanned Outage']
            
#             # Vertical Grand Total
#             gt_row = pd.Series(zone_today.sum(numeric_only=True), name='Grand Total')
#             gt_row['Zone'] = 'Grand Total'
#             zone_today = pd.concat([zone_today, pd.DataFrame([gt_row])], ignore_index=True)
            
#             styled_zone_today = apply_pu_gradient(zone_today.style, zone_today).set_table_styles(HEADER_STYLES)
#             st.dataframe(styled_zone_today, width="stretch", hide_index=True)
#         else: st.info("No data available for today.")

#     with col_right:
#         st.header("⏳ Last 5 Days Trends")
        
#         # --- MOVED DATE FILTER UP ---
#         all_zone_5d_dates = sorted(list(df_5day['Outage Date'].dropna().unique()))
#         selected_zone_dates_5d = st.multiselect(
#             "Filter 5-Days View by Date:", 
#             options=all_zone_5d_dates, 
#             default=all_zone_5d_dates, 
#             format_func=lambda x: x.strftime('%d %b %Y'),
#             key="zone_5d_date_filter"
#         )
        
#         # Filter the dataframe based on the selection FIRST
#         filtered_zone_5day = df_5day[df_5day['Outage Date'].isin(selected_zone_dates_5d)]

#         # --- KPIs NOW USE FILTERED DATA ---
#         fiveday_planned = filtered_zone_5day[filtered_zone_5day['Type of Outage'] == 'Planned Outage']
#         fiveday_pc = filtered_zone_5day[filtered_zone_5day['Type of Outage'] == 'Power Off By PC']
#         fiveday_unplanned = filtered_zone_5day[filtered_zone_5day['Type of Outage'] == 'Unplanned Outage']
        
#         st.subheader("Outage Summary (Filtered)")
#         kpi4, kpi5, kpi6 = st.columns(3)
#         with kpi4: st.markdown(f'<div class="kpi-card"><div><div class="kpi-title">Planned Outages</div><div class="kpi-value">{len(fiveday_planned)}</div></div><div class="kpi-subtext" style="visibility: hidden;">Spacer</div></div>', unsafe_allow_html=True)
#         with kpi5: st.markdown(f'<div class="kpi-card"><div><div class="kpi-title">Power Off By PC</div><div class="kpi-value">{len(fiveday_pc)}</div></div><div class="kpi-subtext" style="visibility: hidden;">Spacer</div></div>', unsafe_allow_html=True)
#         with kpi6: st.markdown(f'<div class="kpi-card"><div><div class="kpi-title">Unplanned Outages</div><div class="kpi-value">{len(fiveday_unplanned)}</div></div><div class="kpi-subtext" style="visibility: hidden;">Spacer</div></div>', unsafe_allow_html=True)

#         st.divider()
#         st.subheader("Zone-wise Distribution (Filtered)")

#         if not filtered_zone_5day.empty:
#             zone_5day = filtered_zone_5day.groupby(['Zone', 'Type of Outage']).size().unstack(fill_value=0).reset_index()
#             for col in ['Planned Outage', 'Power Off By PC', 'Unplanned Outage']:
#                 if col not in zone_5day: zone_5day[col] = 0
            
#             # Horizontal Overall Total
#             zone_5day['Total'] = zone_5day['Planned Outage'] + zone_5day['Power Off By PC'] + zone_5day['Unplanned Outage']
            
#             # Vertical Grand Total
#             gt_row_5d = pd.Series(zone_5day.sum(numeric_only=True), name='Grand Total')
#             gt_row_5d['Zone'] = 'Grand Total'
#             zone_5day = pd.concat([zone_5day, pd.DataFrame([gt_row_5d])], ignore_index=True)
            
#             styled_zone_5day = apply_pu_gradient(zone_5day.style, zone_5day).set_table_styles(HEADER_STYLES)
#             st.dataframe(styled_zone_5day, width="stretch", hide_index=True)
#         else: 
#             st.info("No data available for the selected dates.")

#     st.divider()
#     st.header("🚨 Notorious Feeders (3+ Days of Outages in Last 5 Days)")
#     st.caption("Top 5 worst-performing feeders per circle based on continuous outage days.")

#     noto_col1, noto_col2 = st.columns(2)
#     with noto_col1: selected_notorious_circle = st.selectbox("Filter by Circle:", ["All Circles"] + sorted(top_5_notorious['Circle'].unique().tolist()), index=0)
#     with noto_col2: selected_notorious_type = st.selectbox("Filter by Outage Type:", ["All Types", "Planned Outage", "Power Off By PC", "Unplanned Outage"], index=0)

#     df_dyn = df_5day.copy()
#     if selected_notorious_type != "All Types": df_dyn = df_dyn[df_dyn['Type of Outage'] == selected_notorious_type]

#     if not df_dyn.empty:
#         dyn_days = df_dyn.groupby(['Circle', 'Feeder'])['Outage Date'].nunique().reset_index(name='Days with Outages')
#         dyn_noto = dyn_days[dyn_days['Days with Outages'] >= 3]

#         if not dyn_noto.empty:
#             dyn_stats = df_dyn.groupby(['Circle', 'Feeder']).agg(Total_Events=('Start Time', 'size'), Max_Mins=('Diff in mins', 'max'), Total_Mins=('Diff in mins', 'sum')).reset_index()
#             dyn_stats.rename(columns={'Total_Events': 'Total Outage Events'}, inplace=True)
#             dyn_stats['Total Duration (Hours)'] = (dyn_stats['Total_Mins'] / 60).round(2)
#             dyn_stats['Max Duration (Hours)'] = (dyn_stats['Max_Mins'] / 60).round(2)
#             dyn_stats = dyn_stats.drop(columns=['Max_Mins', 'Total_Mins'])

#             dyn_noto = dyn_noto.merge(dyn_stats, on=['Circle', 'Feeder']).sort_values(by=['Circle', 'Days with Outages', 'Total Outage Events'], ascending=[True, False, False])
#             dyn_top5 = dyn_noto.groupby('Circle').head(5)
#             filtered_notorious = dyn_top5[dyn_top5['Circle'] == selected_notorious_circle] if selected_notorious_circle != "All Circles" else dyn_top5

#             if not filtered_notorious.empty:
#                 st.dataframe(filtered_notorious.style.format({'Max Duration (Hours)': '{:.2f}', 'Total Duration (Hours)': '{:.2f}'}).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#             else: st.info(f"No notorious feeders found for {selected_notorious_circle} matching the criteria.")
#         else: st.info(f"No notorious feeders identified for {selected_notorious_type}.")
#     else: st.info("No data available for the selected outage type.")


#     st.divider()
#     st.header("Comprehensive Circle-wise Breakdown")
#     bucket_order = ["Up to 2 Hrs", "2-4 Hrs", "4-8 Hrs", "Above 8 Hrs", "Active/Unknown"]

#     # --- TODAY'S BREAKDOWN ---
#     st.subheader("📅 Today's Breakdown")
#     st.markdown(" **Click on any row inside the table below** to view the specific Feeder drill-down details for Today.")

#     curr_1d_p_tab1 = create_bucket_pivot(df_today[df_today['Type of Outage'] == 'Planned Outage'], bucket_order)
#     curr_1d_pc_tab1 = create_bucket_pivot(df_today[df_today['Type of Outage'] == 'Power Off By PC'], bucket_order)
#     curr_1d_u_tab1 = create_bucket_pivot(df_today[df_today['Type of Outage'] == 'Unplanned Outage'], bucket_order)

#     today_circle = pd.concat(
#         [curr_1d_p_tab1, curr_1d_pc_tab1, curr_1d_u_tab1], 
#         axis=1, 
#         keys=['Planned Outages', 'Power Off By PC', 'Unplanned Outages']
#     ).fillna(0).astype(int)

#     if not today_circle.empty:
#         # 1. Add horizontal 'Overall Total'
#         today_circle[('Overall Total', 'Total Events')] = today_circle.loc[:, (slice(None), 'Total')].sum(axis=1)
#         # 2. Add vertical 'Grand Total'
#         today_circle.loc['Grand Total'] = today_circle.sum(numeric_only=True)

#         styled_today = apply_pu_gradient(today_circle.style, today_circle).set_table_styles(HEADER_STYLES)
        
#         selection_today = st.dataframe(
#             styled_today, 
#             width="stretch",
#             on_select="rerun",
#             selection_mode="single-row" 
#         )

#         if len(selection_today.selection.rows) > 0:
#             selected_circle_today = today_circle.index[selection_today.selection.rows[0]]
            
#             # Safeguard drill-down if they click 'Grand Total'
#             if selected_circle_today != 'Grand Total':
#                 st.markdown(f"#### 🔍 Today's Feeder Details for: {selected_circle_today}")
                
#                 def highlight_notorious_today(row): return ['background-color: rgba(220, 53, 69, 0.15); color: #850000; font-weight: bold'] * len(row) if (selected_circle_today, row['Feeder']) in notorious_set else [''] * len(row)

#                 today_left, today_mid, today_right = st.columns(3)
#                 with today_left:
#                     st.markdown(f"**🔵 Planned Outages**")
#                     feeder_list_tp = today_planned[today_planned['Circle'] == selected_circle_today][['Feeder', 'Diff in mins', 'Status_Calc', 'Duration Bucket']].rename(columns={'Status_Calc': 'Status'})
#                     st.dataframe(feeder_list_tp.style.apply(highlight_notorious_today, axis=1).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#                 with today_mid:
#                     st.markdown(f"**🟣 Power Off By PC**")
#                     feeder_list_tpc = today_pc[today_pc['Circle'] == selected_circle_today][['Feeder', 'Diff in mins', 'Status_Calc', 'Duration Bucket']].rename(columns={'Status_Calc': 'Status'})
#                     st.dataframe(feeder_list_tpc.style.apply(highlight_notorious_today, axis=1).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#                 with today_right:
#                     st.markdown(f"**🔴 Unplanned Outages**")
#                     feeder_list_tu = today_unplanned[today_unplanned['Circle'] == selected_circle_today][['Feeder', 'Diff in mins', 'Status_Calc', 'Duration Bucket']].rename(columns={'Status_Calc': 'Status'})
#                     st.dataframe(feeder_list_tu.style.apply(highlight_notorious_today, axis=1).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#     else:
#         st.info("No circle data available for today.")


#     # --- LAST 5 DAYS BREAKDOWN ---
#     st.divider()
#     st.subheader("⏳ Last 5 Days Breakdown")
#     st.markdown(" **Filter by dates** below and **click on any row** to view specific Feeder drill-down details.")

#     all_5d_dates = sorted(list(df_5day['Outage Date'].dropna().unique()))
#     selected_dates_5d = st.multiselect("Filter 5-Days View by Date:", options=all_5d_dates, default=all_5d_dates, format_func=lambda x: x.strftime('%d %b %Y'))

#     filtered_5d = df_5day[df_5day['Outage Date'].isin(selected_dates_5d)]

#     curr_5d_p_tab1 = create_bucket_pivot(filtered_5d[filtered_5d['Type of Outage'] == 'Planned Outage'], bucket_order)
#     curr_5d_pc_tab1 = create_bucket_pivot(filtered_5d[filtered_5d['Type of Outage'] == 'Power Off By PC'], bucket_order)
#     curr_5d_u_tab1 = create_bucket_pivot(filtered_5d[filtered_5d['Type of Outage'] == 'Unplanned Outage'], bucket_order)

#     fiveday_circle = pd.concat(
#         [curr_5d_p_tab1, curr_5d_pc_tab1, curr_5d_u_tab1], 
#         axis=1, 
#         keys=['Planned Outages', 'Power Off By PC', 'Unplanned Outages']
#     ).fillna(0).astype(int)

#     if not fiveday_circle.empty:
#         # 1. Add horizontal 'Overall Total'
#         fiveday_circle[('Overall Total', 'Total Events')] = fiveday_circle.loc[:, (slice(None), 'Total')].sum(axis=1)
#         # 2. Add vertical 'Grand Total'
#         fiveday_circle.loc['Grand Total'] = fiveday_circle.sum(numeric_only=True)

#         styled_fiveday = apply_pu_gradient(fiveday_circle.style, fiveday_circle).set_table_styles(HEADER_STYLES)
        
#         selection_fiveday = st.dataframe(
#             styled_fiveday, 
#             width="stretch",
#             on_select="rerun",
#             selection_mode="single-row" 
#         )

#         if len(selection_fiveday.selection.rows) > 0:
#             selected_circle_5d = fiveday_circle.index[selection_fiveday.selection.rows[0]]
            
#             # Safeguard drill-down if they click 'Grand Total'
#             if selected_circle_5d != 'Grand Total':
#                 st.markdown(f"#### 🔍 5-Days Feeder Details for: {selected_circle_5d}")
                
#                 def highlight_notorious_5d(row): return ['background-color: rgba(220, 53, 69, 0.15); color: #850000; font-weight: bold'] * len(row) if (selected_circle_5d, row['Feeder']) in notorious_set else [''] * len(row)

#                 fiveday_left, fiveday_mid, fiveday_right = st.columns(3)
                
#                 with fiveday_left:
#                     st.markdown(f"**🔵 Planned Outages**")
#                     feeder_list_fp = filtered_5d[(filtered_5d['Type of Outage'] == 'Planned Outage') & (filtered_5d['Circle'] == selected_circle_5d)].copy()
#                     if not feeder_list_fp.empty:
#                         feeder_list_fp['Diff in Hours'] = (feeder_list_fp['Diff in mins'] / 60).round(2)
#                         st.dataframe(feeder_list_fp[['Outage Date', 'Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket']].style.apply(highlight_notorious_5d, axis=1).format({'Diff in Hours': '{:.2f}'}).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#                     else: st.dataframe(pd.DataFrame(columns=['Outage Date', 'Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket']).style.set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
                
#                 with fiveday_mid:
#                     st.markdown(f"**🟣 Power Off By PC**")
#                     feeder_list_fpc = filtered_5d[(filtered_5d['Type of Outage'] == 'Power Off By PC') & (filtered_5d['Circle'] == selected_circle_5d)].copy()
#                     if not feeder_list_fpc.empty:
#                         feeder_list_fpc['Diff in Hours'] = (feeder_list_fpc['Diff in mins'] / 60).round(2)
#                         st.dataframe(feeder_list_fpc[['Outage Date', 'Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket']].style.apply(highlight_notorious_5d, axis=1).format({'Diff in Hours': '{:.2f}'}).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#                     else: st.dataframe(pd.DataFrame(columns=['Outage Date', 'Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket']).style.set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)

#                 with fiveday_right:
#                     st.markdown(f"**🔴 Unplanned Outages**")
#                     feeder_list_fu = filtered_5d[(filtered_5d['Type of Outage'] == 'Unplanned Outage') & (filtered_5d['Circle'] == selected_circle_5d)].copy()
#                     if not feeder_list_fu.empty:
#                         feeder_list_fu['Diff in Hours'] = (feeder_list_fu['Diff in mins'] / 60).round(2)
#                         st.dataframe(feeder_list_fu[['Outage Date', 'Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket']].style.apply(highlight_notorious_5d, axis=1).format({'Diff in Hours': '{:.2f}'}).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#                     else: st.dataframe(pd.DataFrame(columns=['Outage Date', 'Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket']).style.set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#     else:
#         st.info("No circle data available for the selected dates.")


# #  =======================================================================================================================================
# #  =======================================================================================================================================
# #V5
# #  =======================================================================================================================================
# #  =======================================================================================================================================

# import os
# import time
# import requests
# import streamlit as st
# import pandas as pd
# from datetime import datetime, timedelta, timezone

# # --- PAGE CONFIGURATION ---
# st.set_page_config(page_title="Power Outage Monitoring Dashboard", layout="wide")

# # --- GLOBAL TABLE HEADER STYLING ---
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
#         'selector': 'th div',
#         'props': [
#             ('color', '#FFC107 !important'),
#             ('font-weight', 'bold !important')
#         ]
#     }
# ]

# # --- COLOR THEME & ENTERPRISE CSS ---
# st.markdown("""
#     <style>
#         .block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
#         p, span, div, caption, .stMarkdown { color: #000000 !important; }
#         h1, h2, h3, h4, h5, h6, div.block-container h1 { color: #004085 !important; font-weight: 700 !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
#         div.block-container h1 { text-align: center; border-bottom: 3px solid #004085 !important; padding-bottom: 10px; margin-bottom: 30px !important; font-size: 2.2rem !important; }
#         h2 { font-size: 1.3rem !important; border-bottom: 2px solid #004085 !important; padding-bottom: 5px; margin-bottom: 10px !important; }
#         h3 { font-size: 1.05rem !important; margin-bottom: 12px !important; text-transform: uppercase; letter-spacing: 0.5px; }
#         hr { border: 0; border-top: 1px solid #004085; margin: 1.5rem 0; opacity: 0.3; }
        
#         .kpi-card { background: linear-gradient(135deg, #004481 0%, #0066cc 100%); border-radius: 6px; padding: 1.2rem 1.2rem; display: flex; flex-direction: column; justify-content: space-between; height: 100%; box-shadow: 0 2px 4px rgba(0,0,0,0.08); transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out; border: 1px solid #003366; }
#         .kpi-card:hover { transform: translateY(-4px); box-shadow: 0 8px 16px rgba(0, 68, 129, 0.2); }
#         .kpi-card .kpi-title, .kpi-title { color: #FFC107 !important; font-weight: 600; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.4rem; }
#         .kpi-card .kpi-value, .kpi-value { color: #FFFFFF !important; font-weight: 700; font-size: 2.6rem; margin-bottom: 0; line-height: 1.1; }
#         .kpi-card .kpi-subtext, .kpi-subtext { color: #F8F9FA !important; font-size: 0.85rem; margin-top: 1rem; padding-top: 0.6rem; border-top: 1px solid rgba(255, 255, 255, 0.2); display: flex; justify-content: flex-start; gap: 15px; }
        
#         .status-badge { background-color: rgba(0, 0, 0, 0.25); padding: 3px 8px; border-radius: 4px; font-weight: 500; color: #FFFFFF !important; }
#         [data-testid="stDataFrame"] > div { border: 2px solid #004085 !important; border-radius: 6px; overflow: hidden; }
#     </style>
# """, unsafe_allow_html=True)

# # --- IST TIMEZONE SETUP ---
# IST = timezone(timedelta(hours=5, minutes=30))

# # --- GITHUB TRIGGER LOGIC ---
# def trigger_scraper():
#     repo_owner = "jamjayjoshi108"
#     repo_name = "pspcl_daily_outage_dashboard" 
#     url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/263899469/dispatches"
#     headers = {"Accept": "application/vnd.github.v3+json", "Authorization": f"token {st.secrets['GITHUB_TOKEN']}"}
#     response = requests.post(url, headers=headers, json={"ref": "main"})
    
#     if response.status_code == 204:
#         st.toast("✅ Scraper triggered successfully in the cloud!")
#         return True
#     else:
#         st.error(f"❌ Failed to trigger scraper. GitHub responded: {response.text}")
#         return False

# # --- 1. FILE DEFINITIONS & CHECKING LOGIC ---
# now_ist = datetime.now(IST)
# if now_ist.hour < 8: now_ist -= timedelta(days=1)
# today_str = now_ist.strftime("%Y-%m-%d")

# try: ly_date = now_ist.replace(year=now_ist.year - 1)
# except ValueError: ly_date = now_ist.replace(year=now_ist.year - 1, day=28)
# ly_str = ly_date.strftime("%Y-%m-%d")

# file_today = f"{today_str}_Outages_Today.csv"
# file_5day = f"{today_str}_Outages_Last_5_Days.csv"
# file_ptw = f"{today_str}_PTW_Last_7_Days.csv"

# # Added PTW file to the missing files check
# files_missing = not (os.path.exists(file_today) and os.path.exists(file_5day) and os.path.exists(file_ptw))

# if files_missing:
#     lock_file = "scraper_lock.txt"
#     should_trigger = True
#     if os.path.exists(lock_file) and time.time() - os.path.getmtime(lock_file) < 300: 
#         should_trigger = False
            
#     if should_trigger:
#         if trigger_scraper():
#             with open(lock_file, "w") as f: f.write(str(time.time()))
#             st.warning(f"⚠️ Data for {today_str} is missing. Automatically fetching fresh data from PSPCL...")
#             st.info("⏳ Please wait ~2 minutes and refresh this page.")
#         else:
#             st.error("🚨 Could not fetch data due to GitHub API error. Fix the token to continue.")
#     else:
#         st.info("⏳ The scraper is currently running in the background. Please wait a moment and refresh.")
#     st.stop()

# # --- 2. DATA LOADING LOGIC ---
# @st.cache_data(ttl="10m")
# def load_live_data(f_today, f_5day, f_ptw):
#     df_today = pd.read_csv(f_today)
#     df_5day = pd.read_csv(f_5day)
#     df_ptw = pd.read_csv(f_ptw)
    
#     df_today['Type of Outage'] = df_today['Type of Outage'].replace('Power Off By PC', 'Planned Outage')
#     df_5day['Type of Outage'] = df_5day['Type of Outage'].replace('Power Off By PC', 'Planned Outage')
    
#     time_cols = ['Schedule Created At', 'Start Time', 'End Time', 'Last Updated At']
#     for df in [df_today, df_5day]:
#         for col in time_cols: df[col] = pd.to_datetime(df[col], errors='coerce')
#         df['Status_Calc'] = df['Status'].apply(lambda x: 'Active' if str(x).strip().title() == 'Open' else 'Closed')
        
#         def assign_bucket(mins):
#             if pd.isna(mins) or mins < 0: return "Active/Unknown"
#             hrs = mins / 60
#             if hrs <= 2: return "Up to 2 Hrs"
#             elif hrs <= 4: return "2-4 Hrs"
#             elif hrs <= 8: return "4-8 Hrs"
#             else: return "Above 8 Hrs"
#         df['Duration Bucket'] = df['Diff in mins'].apply(assign_bucket)
        
#     return df_today, df_5day, df_ptw

# @st.cache_data
# def load_historical_data():
#     if os.path.exists('Historical_2026.csv') and os.path.exists('Historical_2025.csv'):
#         df_26, df_25 = pd.read_csv('Historical_2026.csv'), pd.read_csv('Historical_2025.csv')
#         for df in [df_26, df_25]:
#             df['Type of Outage'] = df['Type of Outage'].replace('Power Off By PC', 'Planned Outage')
#             df['Outage Date'] = pd.to_datetime(df['Start Time'], errors='coerce').dt.date
#         return df_26, df_25
#     return pd.DataFrame(), pd.DataFrame()

# df_today, df_5day, df_ptw = load_live_data(file_today, file_5day, file_ptw)
# df_hist_curr, df_hist_ly = load_historical_data()

# # --- HELPER FUNCTIONS ---
# def generate_yoy_dist(df_curr, df_ly, group_col):
#     c_grp = pd.DataFrame(columns=[group_col, 'Planned Outage', 'Unplanned Outage']) if df_curr.empty else df_curr.groupby([group_col, 'Type of Outage']).size().unstack(fill_value=0).reset_index()
#     l_grp = pd.DataFrame(columns=[group_col, 'Planned Outage', 'Unplanned Outage']) if df_ly.empty else df_ly.groupby([group_col, 'Type of Outage']).size().unstack(fill_value=0).reset_index()

#     for col in ['Planned Outage', 'Unplanned Outage']:
#         if col not in c_grp.columns: c_grp[col] = 0
#         if col not in l_grp.columns: l_grp[col] = 0

#     c_grp['Curr Total'] = c_grp['Planned Outage'] + c_grp['Unplanned Outage']
#     l_grp['LY Total'] = l_grp['Planned Outage'] + l_grp['Unplanned Outage']
#     c_grp, l_grp = c_grp.rename(columns={'Planned Outage': 'Curr Planned', 'Unplanned Outage': 'Curr Unplanned'}), l_grp.rename(columns={'Planned Outage': 'LY Planned', 'Unplanned Outage': 'LY Unplanned'})
    
#     merged = pd.merge(c_grp, l_grp, on=group_col, how='outer').fillna(0)
#     for col in ['Curr Planned', 'Curr Unplanned', 'Curr Total', 'LY Planned', 'LY Unplanned', 'LY Total']: merged[col] = merged[col].astype(int)
#     merged['YoY Delta (Total)'] = merged['Curr Total'] - merged['LY Total']
#     return merged[[group_col, 'Curr Planned', 'LY Planned', 'Curr Unplanned', 'LY Unplanned', 'Curr Total', 'LY Total', 'YoY Delta (Total)']]

# def highlight_delta(val):
#     if isinstance(val, int):
#         if val > 0: return 'color: #D32F2F; font-weight: bold;'
#         elif val < 0: return 'color: #388E3C; font-weight: bold;'
#     return ''

# def generate_yoy_kpi_html(title, current_val, delta_val):
#     delta_str, delta_color = (f"⬆ +{delta_val}", "#FF8A80") if delta_val > 0 else (f"⬇ {delta_val}", "#69F0AE") if delta_val < 0 else ("➖ 0", "#FFFFFF")
#     return f'''
#         <div class="kpi-card">
#             <div><div class="kpi-title">{title}</div><div class="kpi-value">{current_val}</div></div>
#             <div class="kpi-subtext"><span class="status-badge" style="color: {delta_color} !important; font-weight: bold;">{delta_str} vs Last Year</span></div>
#         </div>
#     '''

# def create_bucket_pivot(df, bucket_order):
#     if df.empty: return pd.DataFrame(columns=bucket_order + ['Total'])
#     pivot = pd.crosstab(df['Circle'], df['Duration Bucket'])
#     pivot = pivot.reindex(columns=[c for c in bucket_order if c in pivot.columns], fill_value=0)
#     pivot['Total'] = pivot.sum(axis=1)
#     return pivot

# # --- NOTORIOUS FEEDERS CALCULATION (Tab 1) ---
# df_5day['Outage Date'] = df_5day['Start Time'].dt.date
# feeder_days = df_5day.groupby(['Circle', 'Feeder'])['Outage Date'].nunique().reset_index(name='Days with Outages')
# notorious = feeder_days[feeder_days['Days with Outages'] >= 3]

# feeder_stats = df_5day.groupby(['Circle', 'Feeder']).agg(Total_Events=('Start Time', 'size'), Avg_Mins=('Diff in mins', 'mean'), Total_Mins=('Diff in mins', 'sum')).reset_index()
# feeder_stats.rename(columns={'Total_Events': 'Total Outage Events'}, inplace=True)
# feeder_stats['Total Duration (Hours)'] = (feeder_stats['Total_Mins'] / 60).round(2)
# feeder_stats['Average Duration (Hours)'] = (feeder_stats['Avg_Mins'] / 60).round(2)
# feeder_stats = feeder_stats.drop(columns=['Avg_Mins', 'Total_Mins'])

# notorious = notorious.merge(feeder_stats, on=['Circle', 'Feeder']).sort_values(by=['Circle', 'Days with Outages', 'Total Outage Events'], ascending=[True, False, False])
# top_5_notorious = notorious.groupby('Circle').head(5)
# notorious_set = set(zip(top_5_notorious['Circle'], top_5_notorious['Feeder']))


# # --- MAIN DASHBOARD RENDER ---
# st.title("⚡ Power Outage Monitoring Dashboard")

# tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📈 YoY Comparison", "🛠️ PTW Frequency"])

# # ==========================================
# # TAB 3: PTW FREQUENCY (NEW)
# # ==========================================
# with tab3:
#     st.header("🛠️ PTW Frequency Tracker (Last 7 Days)")
#     st.markdown("Identifies specific feeders that had a Permit to Work (PTW) taken against them **two or more times** in separate requests over the last 7 days.")

#     if df_ptw.empty:
#         st.info("No PTW data found for the last 7 days.")
#     else:
#         # Robust column identification
#         ptw_col = next((c for c in df_ptw.columns if 'ptw' in c.lower() or 'request' in c.lower() or 'id' in c.lower()), None)
#         feeder_col = next((c for c in df_ptw.columns if 'feeder' in c.lower()), None)
#         status_col = next((c for c in df_ptw.columns if 'status' in c.lower()), None)
#         circle_col = next((c for c in df_ptw.columns if 'circle' in c.lower()), None)

#         if not ptw_col or not feeder_col:
#             st.error("Could not dynamically map required columns from the PTW export.")
#         else:
#             ptw_clean = df_ptw.copy()
            
#             # Step 1: Filter out explicitly Cancelled PTWs
#             if status_col:
#                 ptw_clean = ptw_clean[~ptw_clean[status_col].astype(str).str.contains('Cancellation', na=False, case=False)]

#             # Step 2: Split multiple feeders grouped in one PTW row (handles commas and pipes)
#             ptw_clean[feeder_col] = ptw_clean[feeder_col].astype(str).str.replace('|', ',', regex=False)
#             ptw_clean[feeder_col] = ptw_clean[feeder_col].str.split(',')
#             ptw_clean = ptw_clean.explode(feeder_col)
#             ptw_clean[feeder_col] = ptw_clean[feeder_col].str.strip()
            
#             # Remove blanks
#             ptw_clean = ptw_clean[ptw_clean[feeder_col] != '']

#             # Step 3: Group by Feeder and Count Unique PTWs
#             group_cols = [feeder_col]
#             if circle_col: group_cols.insert(0, circle_col) # Group by Circle if available to prevent name collisions
                
#             ptw_counts = ptw_clean.groupby(group_cols).agg(
#                 Unique_PTWs=(ptw_col, 'nunique'),
#                 PTW_IDs=(ptw_col, lambda x: ', '.join(x.dropna().astype(str).unique()))
#             ).reset_index()

#             # Step 4: Filter for >= 2 occurrences
#             repeat_feeders = ptw_counts[ptw_counts['Unique_PTWs'] >= 2].sort_values(by='Unique_PTWs', ascending=False)
#             repeat_feeders = repeat_feeders.rename(columns={'Unique_PTWs': 'PTW Request Count', 'PTW_IDs': 'Associated PTW Request Numbers'})

#             kpi1, kpi2 = st.columns(2)
#             with kpi1:
#                 st.markdown(f'''
#                     <div class="kpi-card">
#                         <div><div class="kpi-title">Total Active PTW Requests</div><div class="kpi-value">{df_ptw[ptw_col].nunique()}</div></div>
#                         <div class="kpi-subtext"><span class="status-badge">Last 7 Days</span></div>
#                     </div>
#                 ''', unsafe_allow_html=True)
#             with kpi2:
#                 st.markdown(f'''
#                     <div class="kpi-card">
#                         <div><div class="kpi-title">Feeders with Multiple PTWs</div><div class="kpi-value">{len(repeat_feeders)}</div></div>
#                         <div class="kpi-subtext"><span class="status-badge" style="background-color: #D32F2F;">🔴 Needs Review</span></div>
#                     </div>
#                 ''', unsafe_allow_html=True)

#             st.divider()
            
#             st.subheader("⚠️ Repeat PTW Feeders Detail View")
#             if not repeat_feeders.empty:
#                 st.dataframe(repeat_feeders.style.set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#             else:
#                 st.success("No feeders had multiple PTWs requested against them in the last 7 days! 🎉")


# # ==========================================
# # TAB 2: DYNAMIC YOY DRILL-DOWN
# # ==========================================
# with tab2:
#     st.header("📈 Historical Year-over-Year Drilldown")
    
#     if df_hist_curr.empty or df_hist_ly.empty:
#         st.error("Historical Master Data (Historical_2025.csv & Historical_2026.csv) not found in directory.")
#     else:
#         timeframe_options = {
#             "March (Entire Month)": (("2026-03-01", "2026-03-31"), ("2025-03-01", "2025-03-31")),
#             "1st Apr to 7th Apr": (("2026-04-01", "2026-04-07"), ("2025-04-01", "2025-04-07")),
#             "8th Apr to 14th Apr": (("2026-04-08", "2026-04-14"), ("2025-04-08", "2025-04-14")),
#             "15th Apr to 22nd Apr": (("2026-04-15", "2026-04-22"), ("2025-04-15", "2025-04-22")),
#             "1st Apr to 23rd Apr": (("2026-04-01", "2026-04-23"), ("2025-04-01", "2025-04-23"))
#         }

#         selected_tf = st.radio("Select Comparison Period:", list(timeframe_options.keys()), horizontal=True)
#         st.divider()

#         curr_bounds, ly_bounds = timeframe_options[selected_tf]
        
#         mask_curr = (df_hist_curr['Outage Date'] >= pd.to_datetime(curr_bounds[0]).date()) & (df_hist_curr['Outage Date'] <= pd.to_datetime(curr_bounds[1]).date())
#         filtered_curr = df_hist_curr[mask_curr]
        
#         mask_ly = (df_hist_ly['Outage Date'] >= pd.to_datetime(ly_bounds[0]).date()) & (df_hist_ly['Outage Date'] <= pd.to_datetime(ly_bounds[1]).date())
#         filtered_ly = df_hist_ly[mask_ly]

#         st.markdown(f"### 📍 1. Zone-wise Distribution ({selected_tf})")
#         st.caption("Click any row to drill down into Circle-wise data.")
        
#         yoy_zone = generate_yoy_dist(filtered_curr, filtered_ly, 'Zone')
        
#         zone_selection = st.dataframe(
#             yoy_zone.style.map(highlight_delta, subset=['YoY Delta (Total)']).set_table_styles(HEADER_STYLES), 
#             width="stretch", hide_index=True, on_select="rerun", selection_mode="single-row"
#         )

#         if len(zone_selection.selection.rows) > 0:
#             selected_zone = yoy_zone.iloc[zone_selection.selection.rows[0]]['Zone']
            
#             st.markdown(f"### 🎯 2. Circle-wise Distribution for **{selected_zone}**")
#             st.caption("Click any row to drill down into Feeder-wise data.")
            
#             curr_zone_df = filtered_curr[filtered_curr['Zone'] == selected_zone]
#             ly_zone_df = filtered_ly[filtered_ly['Zone'] == selected_zone]
#             yoy_circle = generate_yoy_dist(curr_zone_df, ly_zone_df, 'Circle')
            
#             circle_selection = st.dataframe(
#                 yoy_circle.style.map(highlight_delta, subset=['YoY Delta (Total)']).set_table_styles(HEADER_STYLES), 
#                 width="stretch", hide_index=True, on_select="rerun", selection_mode="single-row"
#             )

#             if len(circle_selection.selection.rows) > 0:
#                 selected_circle = yoy_circle.iloc[circle_selection.selection.rows[0]]['Circle']
#                 st.markdown(f"### 🔌 3. Feeder-wise Distribution for **{selected_circle}**")
                
#                 curr_circle_df = curr_zone_df[curr_zone_df['Circle'] == selected_circle]
#                 ly_circle_df = ly_zone_df[ly_zone_df['Circle'] == selected_circle]
#                 yoy_feeder = generate_yoy_dist(curr_circle_df, ly_circle_df, 'Feeder')
                
#                 st.dataframe(yoy_feeder.style.map(highlight_delta, subset=['YoY Delta (Total)']).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)


# # ==========================================
# # TAB 1: ORIGINAL DASHBOARD
# # ==========================================
# with tab1:
#     col_left, col_right = st.columns(2, gap="large")

#     with col_left:
#         st.header(f"📅 Today's Outages ({now_ist.strftime('%d %b %Y')})")
#         today_planned = df_today[df_today['Type of Outage'] == 'Planned Outage']
#         today_unplanned = df_today[df_today['Type of Outage'] == 'Unplanned Outage']
        
#         st.subheader("Outage Summary")
#         kpi1, kpi2 = st.columns(2)
#         with kpi1:
#             active_p, closed_p = len(today_planned[today_planned['Status_Calc'] == 'Active']), len(today_planned[today_planned['Status_Calc'] == 'Closed'])
#             st.markdown(f'<div class="kpi-card"><div><div class="kpi-title">Total Planned Outages</div><div class="kpi-value">{len(today_planned)}</div></div><div class="kpi-subtext"><span class="status-badge">🔴 Active: {active_p}</span> <span class="status-badge">🟢 Closed: {closed_p}</span></div></div>', unsafe_allow_html=True)
#         with kpi2:
#             active_u, closed_u = len(today_unplanned[today_unplanned['Status_Calc'] == 'Active']), len(today_unplanned[today_unplanned['Status_Calc'] == 'Closed'])
#             st.markdown(f'<div class="kpi-card"><div><div class="kpi-title">Total Unplanned Outages</div><div class="kpi-value">{len(today_unplanned)}</div></div><div class="kpi-subtext"><span class="status-badge">🔴 Active: {active_u}</span> <span class="status-badge">🟢 Closed: {closed_u}</span></div></div>', unsafe_allow_html=True)

#         st.divider()
#         st.subheader("Zone-wise Distribution (Today)")
#         if not df_today.empty:
#             zone_today = df_today.groupby(['Zone', 'Type of Outage']).size().unstack(fill_value=0).reset_index()
#             for col in ['Planned Outage', 'Unplanned Outage']:
#                 if col not in zone_today: zone_today[col] = 0
#             zone_today['Total'] = zone_today['Planned Outage'] + zone_today['Unplanned Outage']
#             st.dataframe(zone_today.style.set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#         else: st.info("No data available for today.")

#     with col_right:
#         st.header("⏳ Last 5 Days Trends")
#         fiveday_planned = df_5day[df_5day['Type of Outage'] == 'Planned Outage']
#         fiveday_unplanned = df_5day[df_5day['Type of Outage'] == 'Unplanned Outage']
        
#         st.subheader("Outage Summary (5 Days)")
#         kpi3, kpi4 = st.columns(2)
#         with kpi3: st.markdown(f'<div class="kpi-card"><div><div class="kpi-title">Total Planned Outages</div><div class="kpi-value">{len(fiveday_planned)}</div></div><div class="kpi-subtext" style="visibility: hidden;">Spacer</div></div>', unsafe_allow_html=True)
#         with kpi4: st.markdown(f'<div class="kpi-card"><div><div class="kpi-title">Total Unplanned Outages</div><div class="kpi-value">{len(fiveday_unplanned)}</div></div><div class="kpi-subtext" style="visibility: hidden;">Spacer</div></div>', unsafe_allow_html=True)

#         st.divider()
#         st.subheader("Zone-wise Distribution (5 Days)")
#         if not df_5day.empty:
#             zone_5day = df_5day.groupby(['Zone', 'Type of Outage']).size().unstack(fill_value=0).reset_index()
#             for col in ['Planned Outage', 'Unplanned Outage']:
#                 if col not in zone_5day: zone_5day[col] = 0
#             zone_5day['Total'] = zone_5day['Planned Outage'] + zone_5day['Unplanned Outage']
#             st.dataframe(zone_5day.style.set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#         else: st.info("No data available for the last 5 days.")

#     st.divider()
#     st.header("🚨 Notorious Feeders (3+ Days of Outages in Last 5 Days)")
#     st.caption("Top 5 worst-performing feeders per circle based on continuous outage days.")

#     noto_col1, noto_col2 = st.columns(2)
#     with noto_col1: selected_notorious_circle = st.selectbox("Filter by Circle:", ["All Circles"] + sorted(top_5_notorious['Circle'].unique().tolist()), index=0)
#     with noto_col2: selected_notorious_type = st.selectbox("Filter by Outage Type:", ["All Types", "Planned Outage", "Unplanned Outage"], index=0)

#     df_dyn = df_5day.copy()
#     if selected_notorious_type != "All Types": df_dyn = df_dyn[df_dyn['Type of Outage'] == selected_notorious_type]

#     if not df_dyn.empty:
#         dyn_days = df_dyn.groupby(['Circle', 'Feeder'])['Outage Date'].nunique().reset_index(name='Days with Outages')
#         dyn_noto = dyn_days[dyn_days['Days with Outages'] >= 3]

#         if not dyn_noto.empty:
#             dyn_stats = df_dyn.groupby(['Circle', 'Feeder']).agg(Total_Events=('Start Time', 'size'), Avg_Mins=('Diff in mins', 'mean'), Total_Mins=('Diff in mins', 'sum')).reset_index()
#             dyn_stats.rename(columns={'Total_Events': 'Total Outage Events'}, inplace=True)
#             dyn_stats['Total Duration (Hours)'] = (dyn_stats['Total_Mins'] / 60).round(2)
#             dyn_stats['Average Duration (Hours)'] = (dyn_stats['Avg_Mins'] / 60).round(2)
#             dyn_stats = dyn_stats.drop(columns=['Avg_Mins', 'Total_Mins'])

#             dyn_noto = dyn_noto.merge(dyn_stats, on=['Circle', 'Feeder']).sort_values(by=['Circle', 'Days with Outages', 'Total Outage Events'], ascending=[True, False, False])
#             dyn_top5 = dyn_noto.groupby('Circle').head(5)
#             filtered_notorious = dyn_top5[dyn_top5['Circle'] == selected_notorious_circle] if selected_notorious_circle != "All Circles" else dyn_top5

#             if not filtered_notorious.empty:
#                 st.dataframe(filtered_notorious.style.format({'Average Duration (Hours)': '{:.2f}', 'Total Duration (Hours)': '{:.2f}'}).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#             else: st.info(f"No notorious feeders found for {selected_notorious_circle} matching the criteria.")
#         else: st.info(f"No notorious feeders identified for {selected_notorious_type}.")
#     else: st.info("No data available for the selected outage type.")

#     st.divider()
#     st.header("Comprehensive Circle-wise Breakdown")
#     bucket_order = ["Up to 2 Hrs", "2-4 Hrs", "4-8 Hrs", "Above 8 Hrs", "Active/Unknown"]

#     curr_5d_p_tab1 = create_bucket_pivot(df_5day[df_5day['Type of Outage'] == 'Planned Outage'], bucket_order)
#     curr_5d_u_tab1 = create_bucket_pivot(df_5day[df_5day['Type of Outage'] == 'Unplanned Outage'], bucket_order)

#     combined_circle = pd.concat([curr_5d_p_tab1, curr_5d_u_tab1], axis=1, keys=['LAST 5 DAYS (Planned Outages)', 'LAST 5 DAYS (Unplanned Outages)']).fillna(0).astype(int)

#     st.markdown(" **Click on any row inside the table below** to view the specific Feeder drill-down details.")

#     if not combined_circle.empty:
#         selection_event = st.dataframe(combined_circle.style.set_table_styles(HEADER_STYLES), width="stretch", on_select="rerun", selection_mode="single-row")

#         if len(selection_event.selection.rows) > 0:
#             selected_circle = combined_circle.index[selection_event.selection.rows[0]]
#             st.subheader(f"Feeder Details for: {selected_circle}")
            
#             circle_dates = sorted(list(df_5day[df_5day['Circle'] == selected_circle]['Outage Date'].dropna().unique()))
#             selected_dates = st.multiselect("Filter 5-Days View by Date:", options=circle_dates, default=circle_dates, format_func=lambda x: x.strftime('%d %b %Y'))
            
#             def highlight_notorious(row): return ['background-color: rgba(220, 53, 69, 0.15); color: #850000; font-weight: bold'] * len(row) if (selected_circle, row['Feeder']) in notorious_set else [''] * len(row)

#             today_left, today_right = st.columns(2)
#             with today_left:
#                 st.markdown(f"**🔴 TODAY: Planned Outages**")
#                 feeder_list_tp = today_planned[today_planned['Circle'] == selected_circle][['Feeder', 'Diff in mins', 'Status_Calc', 'Duration Bucket']].rename(columns={'Status_Calc': 'Status'})
#                 st.dataframe(feeder_list_tp.style.apply(highlight_notorious, axis=1).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#             with today_right:
#                 st.markdown(f"**🔴 TODAY: Unplanned Outages**")
#                 feeder_list_tu = today_unplanned[today_unplanned['Circle'] == selected_circle][['Feeder', 'Diff in mins', 'Status_Calc', 'Duration Bucket']].rename(columns={'Status_Calc': 'Status'})
#                 st.dataframe(feeder_list_tu.style.apply(highlight_notorious, axis=1).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
                
#             st.write("") 
#             fiveday_left, fiveday_right = st.columns(2)
            
#             with fiveday_left:
#                 st.markdown(f"**🟢 5-DAYS: Planned Outages**")
#                 feeder_list_fp = fiveday_planned[(fiveday_planned['Circle'] == selected_circle) & (fiveday_planned['Outage Date'].isin(selected_dates))].copy()
#                 if not feeder_list_fp.empty:
#                     feeder_list_fp['Diff in Hours'] = (feeder_list_fp['Diff in mins'] / 60).round(2)
#                     st.dataframe(feeder_list_fp[['Outage Date', 'Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket']].style.apply(highlight_notorious, axis=1).format({'Diff in Hours': '{:.2f}'}).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#                 else: st.dataframe(pd.DataFrame(columns=['Outage Date', 'Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket']).style.set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
                
#             with fiveday_right:
#                 st.markdown(f"**🟢 5-DAYS: Unplanned Outages**")
#                 feeder_list_fu = fiveday_unplanned[(fiveday_unplanned['Circle'] == selected_circle) & (fiveday_unplanned['Outage Date'].isin(selected_dates))].copy()
#                 if not feeder_list_fu.empty:
#                     feeder_list_fu['Diff in Hours'] = (feeder_list_fu['Diff in mins'] / 60).round(2)
#                     st.dataframe(feeder_list_fu[['Outage Date', 'Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket']].style.apply(highlight_notorious, axis=1).format({'Diff in Hours': '{:.2f}'}).set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#                 else: st.dataframe(pd.DataFrame(columns=['Outage Date', 'Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket']).style.set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#     else: st.info("No circle data available.")




#  =======================================================================================================================================
#  =======================================================================================================================================
#V4
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
#         'selector': 'th div',
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

#         /* UNIFIED HEADERS */
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

#         /* TABLE BORDERS */
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
    
#     url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/263899469/dispatches"
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

# # --- 1. FILE DEFINITIONS & CHECKING LOGIC ---
# now_ist = datetime.now(IST)

# # PORTAL DELAY FIX
# if now_ist.hour < 8:
#     now_ist -= timedelta(days=1)

# today_str = now_ist.strftime("%Y-%m-%d")

# file_today = f"{today_str}_Outages_Today.csv"
# file_5day = f"{today_str}_Outages_Last_5_Days.csv"

# # ONLY Check live files. We assume Historical files are manually uploaded and safe.
# files_missing = not (os.path.exists(file_today) and os.path.exists(file_5day))

# if files_missing:
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
# def load_live_data(f_today, f_5day):
#     df_today = pd.read_csv(f_today)
#     df_5day = pd.read_csv(f_5day)
    
#     df_today['Type of Outage'] = df_today['Type of Outage'].replace('Power Off By PC', 'Planned Outage')
#     df_5day['Type of Outage'] = df_5day['Type of Outage'].replace('Power Off By PC', 'Planned Outage')
    
#     time_cols = ['Schedule Created At', 'Start Time', 'End Time', 'Last Updated At']
#     for df in [df_today, df_5day]:
#         for col in time_cols:
#             df[col] = pd.to_datetime(df[col], errors='coerce')
            
#         df['Status_Calc'] = df['Status'].apply(lambda x: 'Active' if str(x).strip().title() == 'Open' else 'Closed')
        
#         def assign_bucket(mins):
#             if pd.isna(mins) or mins < 0: return "Active/Unknown"
#             hrs = mins / 60
#             if hrs <= 2: return "Up to 2 Hrs"
#             elif hrs <= 4: return "2-4 Hrs"
#             elif hrs <= 8: return "4-8 Hrs"
#             else: return "Above 8 Hrs"
            
#         df['Duration Bucket'] = df['Diff in mins'].apply(assign_bucket)
        
#     return df_today, df_5day

# # Load Historical Data separately (Cache permanently since it doesn't change)
# @st.cache_data
# def load_historical_data():
#     if os.path.exists('Historical_2026.csv') and os.path.exists('Historical_2025.csv'):
#         df_26 = pd.read_csv('Historical_2026.csv')
#         df_25 = pd.read_csv('Historical_2025.csv')
        
#         df_26['Type of Outage'] = df_26['Type of Outage'].replace('Power Off By PC', 'Planned Outage')
#         df_25['Type of Outage'] = df_25['Type of Outage'].replace('Power Off By PC', 'Planned Outage')
        
#         df_26['Outage Date'] = pd.to_datetime(df_26['Start Time'], errors='coerce').dt.date
#         df_25['Outage Date'] = pd.to_datetime(df_25['Start Time'], errors='coerce').dt.date
        
#         return df_26, df_25
#     return pd.DataFrame(), pd.DataFrame()

# df_today, df_5day = load_live_data(file_today, file_5day)
# df_hist_curr, df_hist_ly = load_historical_data()

# # --- HELPER FUNCTIONS FOR TABLES ---
# def generate_yoy_dist(df_curr, df_ly, group_col):
#     if df_curr.empty:
#         c_grp = pd.DataFrame(columns=[group_col, 'Planned Outage', 'Unplanned Outage'])
#     else:
#         c_grp = df_curr.groupby([group_col, 'Type of Outage']).size().unstack(fill_value=0).reset_index()
        
#     if df_ly.empty:
#         l_grp = pd.DataFrame(columns=[group_col, 'Planned Outage', 'Unplanned Outage'])
#     else:
#         l_grp = df_ly.groupby([group_col, 'Type of Outage']).size().unstack(fill_value=0).reset_index()

#     for col in ['Planned Outage', 'Unplanned Outage']:
#         if col not in c_grp.columns: c_grp[col] = 0
#         if col not in l_grp.columns: l_grp[col] = 0

#     c_grp['2025 Total'] = c_grp['Planned Outage'] + c_grp['Unplanned Outage']
#     l_grp['2026 Total'] = l_grp['Planned Outage'] + l_grp['Unplanned Outage']
    
#     c_grp = c_grp.rename(columns={'Planned Outage': '2025 Planned', 'Unplanned Outage': '2025 Unplanned'})
#     l_grp = l_grp.rename(columns={'Planned Outage': '2026 Planned', 'Unplanned Outage': '2026 Unplanned'})
    
#     merged = pd.merge(c_grp, l_grp, on=group_col, how='outer').fillna(0)
    
#     for col in ['2025 Planned', '2025 Unplanned', '2025 Total', '2026 Planned', '2026 Unplanned', '2026 Total']:
#         merged[col] = merged[col].astype(int)
        
#     merged['YoY Delta (Total)'] = merged['2025 Total'] - merged['2026 Total']
#     return merged[[group_col, '2025 Planned', '2026 Planned', '2025 Unplanned', '2026 Unplanned', '2025 Total', '2026 Total', 'YoY Delta (Total)']]

# def highlight_delta(val):
#     if isinstance(val, int):
#         if val > 0: return 'color: #D32F2F; font-weight: bold;'
#         elif val < 0: return 'color: #388E3C; font-weight: bold;'
#     return ''

# # --- NOTORIOUS FEEDERS CALCULATION (For Tab 1) ---
# df_5day['Outage Date'] = df_5day['Start Time'].dt.date
# feeder_days = df_5day.groupby(['Circle', 'Feeder'])['Outage Date'].nunique().reset_index(name='Days with Outages')
# notorious = feeder_days[feeder_days['Days with Outages'] >= 3]

# feeder_stats = df_5day.groupby(['Circle', 'Feeder']).agg(
#     Total_Events=('Start Time', 'size'),
#     Avg_Mins=('Diff in mins', 'mean'),
#     Total_Mins=('Diff in mins', 'sum')
# ).reset_index()

# feeder_stats.rename(columns={'Total_Events': 'Total Outage Events'}, inplace=True)
# feeder_stats['Total Duration (Hours)'] = (feeder_stats['Total_Mins'] / 60).round(2)
# feeder_stats['Average Duration (Hours)'] = (feeder_stats['Avg_Mins'] / 60).round(2)
# feeder_stats = feeder_stats.drop(columns=['Avg_Mins', 'Total_Mins'])

# notorious = notorious.merge(feeder_stats, on=['Circle', 'Feeder'])
# notorious = notorious.sort_values(by=['Circle', 'Days with Outages', 'Total Outage Events'], ascending=[True, False, False])
# top_5_notorious = notorious.groupby('Circle').head(5)
# notorious_set = set(zip(top_5_notorious['Circle'], top_5_notorious['Feeder']))


# # --- MAIN DASHBOARD RENDER ---
# st.title("⚡ Power Outage Monitoring Dashboard")

# # --- TAB SYSTEM INTEGRATION ---
# tab1, tab2 = st.tabs(["📊 Dashboard", "📈 YoY Comparison"])

# # ==========================================
# # TAB 2: DYNAMIC YOY DRILL-DOWN
# # ==========================================
# with tab2:
#     st.header("📈 Historical Year-over-Year Drilldown")
    
#     if df_hist_curr.empty or df_hist_ly.empty:
#         st.error("Historical Master Data (Historical_2025.csv & Historical_2026.csv) not found in directory.")
#     else:
#         # Toggles requested by manager
#         timeframe_options = {
#             "March (Entire Month)": (("2026-03-01", "2026-03-31"), ("2025-03-01", "2025-03-31")),
#             "1st Apr to 7th Apr": (("2026-04-01", "2026-04-07"), ("2025-04-01", "2025-04-07")),
#             "8th Apr to 14th Apr": (("2026-04-08", "2026-04-14"), ("2025-04-08", "2025-04-14")),
#             "15th Apr to 22nd Apr": (("2026-04-15", "2026-04-22"), ("2025-04-15", "2025-04-22")),
#             "1st Apr to 23rd Apr": (("2026-04-01", "2026-04-23"), ("2025-04-01", "2025-04-23"))
#         }

#         selected_tf = st.radio("Select Comparison Period:", list(timeframe_options.keys()), horizontal=True)
#         st.divider()

#         # Date Filtering Logic
#         curr_bounds, ly_bounds = timeframe_options[selected_tf]
        
#         # Filter Current Year
#         mask_curr = (df_hist_curr['Outage Date'] >= pd.to_datetime(curr_bounds[0]).date()) & \
#                     (df_hist_curr['Outage Date'] <= pd.to_datetime(curr_bounds[1]).date())
#         filtered_curr = df_hist_curr[mask_curr]
        
#         # Filter Last Year
#         mask_ly = (df_hist_ly['Outage Date'] >= pd.to_datetime(ly_bounds[0]).date()) & \
#                   (df_hist_ly['Outage Date'] <= pd.to_datetime(ly_bounds[1]).date())
#         filtered_ly = df_hist_ly[mask_ly]

#         st.markdown(f"### 📍 1. Zone-wise Distribution ({selected_tf})")
#         st.caption("Click any row to drill down into Circle-wise data.")
        
#         yoy_zone = generate_yoy_dist(filtered_curr, filtered_ly, 'Zone')
        
#         zone_selection = st.dataframe(
#             yoy_zone.style.map(highlight_delta, subset=['YoY Delta (Total)']).set_table_styles(HEADER_STYLES), 
#             width="stretch", 
#             hide_index=True,
#             on_select="rerun",
#             selection_mode="single-row"
#         )

#         # Drilldown to Circle
#         if len(zone_selection.selection.rows) > 0:
#             selected_zone = yoy_zone.iloc[zone_selection.selection.rows[0]]['Zone']
            
#             st.markdown(f"### 🎯 2. Circle-wise Distribution for **{selected_zone}**")
#             st.caption("Click any row to drill down into Feeder-wise data.")
            
#             curr_zone_df = filtered_curr[filtered_curr['Zone'] == selected_zone]
#             ly_zone_df = filtered_ly[filtered_ly['Zone'] == selected_zone]
            
#             yoy_circle = generate_yoy_dist(curr_zone_df, ly_zone_df, 'Circle')
            
#             circle_selection = st.dataframe(
#                 yoy_circle.style.map(highlight_delta, subset=['YoY Delta (Total)']).set_table_styles(HEADER_STYLES), 
#                 width="stretch", 
#                 hide_index=True,
#                 on_select="rerun",
#                 selection_mode="single-row"
#             )

#             # Drilldown to Feeder
#             if len(circle_selection.selection.rows) > 0:
#                 selected_circle = yoy_circle.iloc[circle_selection.selection.rows[0]]['Circle']
                
#                 st.markdown(f"### 🔌 3. Feeder-wise Distribution for **{selected_circle}**")
                
#                 curr_circle_df = curr_zone_df[curr_zone_df['Circle'] == selected_circle]
#                 ly_circle_df = ly_zone_df[ly_zone_df['Circle'] == selected_circle]
                
#                 yoy_feeder = generate_yoy_dist(curr_circle_df, ly_circle_df, 'Feeder')
                
#                 st.dataframe(
#                     yoy_feeder.style.map(highlight_delta, subset=['YoY Delta (Total)']).set_table_styles(HEADER_STYLES), 
#                     width="stretch", 
#                     hide_index=True
#                 )


# # ==========================================
# # TAB 1: ORIGINAL DASHBOARD (Untouched)
# # ==========================================
# with tab1:
#     col_left, col_right = st.columns(2, gap="large")

#     with col_left:
#         st.header(f"📅 Today's Outages ({now_ist.strftime('%d %b %Y')})")
        
#         today_planned = df_today[df_today['Type of Outage'] == 'Planned Outage']
#         today_unplanned = df_today[df_today['Type of Outage'] == 'Unplanned Outage']
        
#         st.subheader("Outage Summary")
#         kpi1, kpi2 = st.columns(2)
        
#         with kpi1:
#             active_p = len(today_planned[today_planned['Status_Calc'] == 'Active'])
#             closed_p = len(today_planned[today_planned['Status_Calc'] == 'Closed'])
#             st.markdown(f'''
#                 <div class="kpi-card">
#                     <div>
#                         <div class="kpi-title">Total Planned Outages</div>
#                         <div class="kpi-value">{len(today_planned)}</div>
#                     </div>
#                     <div class="kpi-subtext">
#                         <span class="status-badge">🔴 Active: {active_p}</span> 
#                         <span class="status-badge">🟢 Closed: {closed_p}</span>
#                     </div>
#                 </div>
#             ''', unsafe_allow_html=True)
            
#         with kpi2:
#             active_u = len(today_unplanned[today_unplanned['Status_Calc'] == 'Active'])
#             closed_u = len(today_unplanned[today_unplanned['Status_Calc'] == 'Closed'])
#             st.markdown(f'''
#                 <div class="kpi-card">
#                     <div>
#                         <div class="kpi-title">Total Unplanned Outages</div>
#                         <div class="kpi-value">{len(today_unplanned)}</div>
#                     </div>
#                     <div class="kpi-subtext">
#                         <span class="status-badge">🔴 Active: {active_u}</span> 
#                         <span class="status-badge">🟢 Closed: {closed_u}</span>
#                     </div>
#                 </div>
#             ''', unsafe_allow_html=True)

#         st.divider()

#         st.subheader("Zone-wise Distribution (Today)")
#         if not df_today.empty:
#             zone_today = df_today.groupby(['Zone', 'Type of Outage']).size().unstack(fill_value=0).reset_index()
#             if 'Planned Outage' not in zone_today: zone_today['Planned Outage'] = 0
#             if 'Unplanned Outage' not in zone_today: zone_today['Unplanned Outage'] = 0
#             zone_today['Total'] = zone_today['Planned Outage'] + zone_today['Unplanned Outage']
            
#             st.dataframe(zone_today.style.set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#         else:
#             st.info("No data available for today.")


#     with col_right:
#         st.header("⏳ Last 5 Days Trends")
        
#         fiveday_planned = df_5day[df_5day['Type of Outage'] == 'Planned Outage']
#         fiveday_unplanned = df_5day[df_5day['Type of Outage'] == 'Unplanned Outage']
        
#         st.subheader("Outage Summary (5 Days)")
#         kpi3, kpi4 = st.columns(2)
        
#         with kpi3:
#             st.markdown(f'''
#                 <div class="kpi-card">
#                     <div>
#                         <div class="kpi-title">Total Planned Outages</div>
#                         <div class="kpi-value">{len(fiveday_planned)}</div>
#                     </div>
#                     <div class="kpi-subtext" style="visibility: hidden;">Spacer</div> 
#                 </div>
#             ''', unsafe_allow_html=True)
            
#         with kpi4:
#             st.markdown(f'''
#                 <div class="kpi-card">
#                     <div>
#                         <div class="kpi-title">Total Unplanned Outages</div>
#                         <div class="kpi-value">{len(fiveday_unplanned)}</div>
#                     </div>
#                     <div class="kpi-subtext" style="visibility: hidden;">Spacer</div>
#                 </div>
#             ''', unsafe_allow_html=True)

#         st.divider()

#         st.subheader("Zone-wise Distribution (5 Days)")
#         if not df_5day.empty:
#             zone_5day = df_5day.groupby(['Zone', 'Type of Outage']).size().unstack(fill_value=0).reset_index()
#             if 'Planned Outage' not in zone_5day: zone_5day['Planned Outage'] = 0
#             if 'Unplanned Outage' not in zone_5day: zone_5day['Unplanned Outage'] = 0
#             zone_5day['Total'] = zone_5day['Planned Outage'] + zone_5day['Unplanned Outage']
            
#             st.dataframe(zone_5day.style.set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#         else:
#             st.info("No data available for the last 5 days.")


#     st.divider()
#     st.header("🚨 Notorious Feeders (3+ Days of Outages in Last 5 Days)")
#     st.caption("Top 5 worst-performing feeders per circle based on continuous outage days.")

#     noto_col1, noto_col2 = st.columns(2)

#     with noto_col1:
#         circle_options = ["All Circles"] + sorted(top_5_notorious['Circle'].unique().tolist())
#         selected_notorious_circle = st.selectbox("Filter by Circle:", options=circle_options, index=0)

#     with noto_col2:
#         outage_type_options = ["All Types", "Planned Outage", "Unplanned Outage"]
#         selected_notorious_type = st.selectbox("Filter by Outage Type:", options=outage_type_options, index=0)

#     df_dyn = df_5day.copy()
#     if selected_notorious_type != "All Types":
#         df_dyn = df_dyn[df_dyn['Type of Outage'] == selected_notorious_type]

#     if not df_dyn.empty:
#         dyn_days = df_dyn.groupby(['Circle', 'Feeder'])['Outage Date'].nunique().reset_index(name='Days with Outages')
#         dyn_noto = dyn_days[dyn_days['Days with Outages'] >= 3]

#         if not dyn_noto.empty:
#             dyn_stats = df_dyn.groupby(['Circle', 'Feeder']).agg(
#                 Total_Events=('Start Time', 'size'),
#                 Avg_Mins=('Diff in mins', 'mean'),
#                 Total_Mins=('Diff in mins', 'sum')
#             ).reset_index()

#             dyn_stats.rename(columns={'Total_Events': 'Total Outage Events'}, inplace=True)
#             dyn_stats['Total Duration (Hours)'] = (dyn_stats['Total_Mins'] / 60).round(2)
#             dyn_stats['Average Duration (Hours)'] = (dyn_stats['Avg_Mins'] / 60).round(2)
#             dyn_stats = dyn_stats.drop(columns=['Avg_Mins', 'Total_Mins'])

#             dyn_noto = dyn_noto.merge(dyn_stats, on=['Circle', 'Feeder'])
#             dyn_noto = dyn_noto.sort_values(by=['Circle', 'Days with Outages', 'Total Outage Events'], ascending=[True, False, False])
#             dyn_top5 = dyn_noto.groupby('Circle').head(5)

#             if selected_notorious_circle != "All Circles":
#                 filtered_notorious = dyn_top5[dyn_top5['Circle'] == selected_notorious_circle]
#             else:
#                 filtered_notorious = dyn_top5

#             if not filtered_notorious.empty:
#                 styled_notorious = filtered_notorious.style.format({
#                     'Average Duration (Hours)': '{:.2f}',
#                     'Total Duration (Hours)': '{:.2f}'
#                 }).set_table_styles(HEADER_STYLES)
#                 st.dataframe(styled_notorious, width="stretch", hide_index=True)
#             else:
#                 st.info(f"No notorious feeders found for {selected_notorious_circle} matching the criteria.")
#         else:
#             st.info(f"No notorious feeders identified for {selected_notorious_type}.")
#     else:
#         st.info("No data available for the selected outage type.")


#     st.divider()
#     st.header("Comprehensive Circle-wise Breakdown")
    
#     def create_bucket_pivot(df, bucket_order):
#         if df.empty:
#             return pd.DataFrame(columns=bucket_order + ['Total'])
#         pivot = pd.crosstab(df['Circle'], df['Duration Bucket'])
#         pivot = pivot.reindex(columns=[c for c in bucket_order if c in pivot.columns], fill_value=0)
#         pivot['Total'] = pivot.sum(axis=1)
#         return pivot
        
#     bucket_order = ["Up to 2 Hrs", "2-4 Hrs", "4-8 Hrs", "Above 8 Hrs", "Active/Unknown"]

#     curr_5d_p_tab1 = create_bucket_pivot(df_5day[df_5day['Type of Outage'] == 'Planned Outage'], bucket_order)
#     curr_5d_u_tab1 = create_bucket_pivot(df_5day[df_5day['Type of Outage'] == 'Unplanned Outage'], bucket_order)

#     combined_circle = pd.concat([curr_5d_p_tab1, curr_5d_u_tab1], axis=1, keys=['LAST 5 DAYS (Planned Outages)', 'LAST 5 DAYS (Unplanned Outages)']).fillna(0).astype(int)

#     st.markdown(" **Click on any row inside the table below** to view the specific Feeder drill-down details.")

#     if not combined_circle.empty:
#         styled_combined = combined_circle.style.set_table_styles(HEADER_STYLES)
        
#         selection_event = st.dataframe(
#             styled_combined, 
#             width="stretch",
#             on_select="rerun",
#             selection_mode="single-row" 
#         )

#         if len(selection_event.selection.rows) > 0:
#             selected_index = selection_event.selection.rows[0]
#             selected_circle = combined_circle.index[selected_index]
            
#             st.subheader(f"Feeder Details for: {selected_circle}")
            
#             circle_dates_raw = df_5day[df_5day['Circle'] == selected_circle]['Outage Date'].dropna().unique()
#             circle_dates = sorted(list(circle_dates_raw))

#             selected_dates = st.multiselect(
#                 "Filter 5-Days View by Date:",
#                 options=circle_dates,
#                 default=circle_dates,
#                 format_func=lambda x: x.strftime('%d %b %Y')
#             )
            
#             def highlight_notorious(row):
#                 if (selected_circle, row['Feeder']) in notorious_set:
#                     return ['background-color: rgba(220, 53, 69, 0.15); color: #850000; font-weight: bold'] * len(row)
#                 return [''] * len(row)

#             today_left, today_right = st.columns(2)
            
#             with today_left:
#                 st.markdown(f"**🔴 TODAY: Planned Outages**")
#                 feeder_list_tp = today_planned[today_planned['Circle'] == selected_circle][['Feeder', 'Diff in mins', 'Status_Calc', 'Duration Bucket']]
#                 feeder_list_tp = feeder_list_tp.rename(columns={'Status_Calc': 'Status'})
#                 styled_tp = feeder_list_tp.style.apply(highlight_notorious, axis=1).set_table_styles(HEADER_STYLES)
#                 st.dataframe(styled_tp, width="stretch", hide_index=True)
                
#             with today_right:
#                 st.markdown(f"**🔴 TODAY: Unplanned Outages**")
#                 feeder_list_tu = today_unplanned[today_unplanned['Circle'] == selected_circle][['Feeder', 'Diff in mins', 'Status_Calc', 'Duration Bucket']]
#                 feeder_list_tu = feeder_list_tu.rename(columns={'Status_Calc': 'Status'})
#                 styled_tu = feeder_list_tu.style.apply(highlight_notorious, axis=1).set_table_styles(HEADER_STYLES)
#                 st.dataframe(styled_tu, width="stretch", hide_index=True)
                
#             st.write("") 
            
#             fiveday_left, fiveday_right = st.columns(2)
            
#             with fiveday_left:
#                 st.markdown(f"**🟢 5-DAYS: Planned Outages**")
#                 feeder_list_fp = fiveday_planned[fiveday_planned['Circle'] == selected_circle].copy()
                
#                 if not feeder_list_fp.empty:
#                     feeder_list_fp = feeder_list_fp[feeder_list_fp['Outage Date'].isin(selected_dates)]
                    
#                 if not feeder_list_fp.empty:
#                     feeder_list_fp['Diff in Hours'] = (feeder_list_fp['Diff in mins'] / 60).round(2)
#                     feeder_list_fp = feeder_list_fp[['Outage Date', 'Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket']]
#                     styled_fp = feeder_list_fp.style.apply(highlight_notorious, axis=1).format({'Diff in Hours': '{:.2f}'}).set_table_styles(HEADER_STYLES)
#                     st.dataframe(styled_fp, width="stretch", hide_index=True)
#                 else:
#                     empty_df = pd.DataFrame(columns=['Outage Date', 'Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket'])
#                     st.dataframe(empty_df.style.set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
                
#             with fiveday_right:
#                 st.markdown(f"**🟢 5-DAYS: Unplanned Outages**")
#                 feeder_list_fu = fiveday_unplanned[fiveday_unplanned['Circle'] == selected_circle].copy()
                
#                 if not feeder_list_fu.empty:
#                     feeder_list_fu = feeder_list_fu[feeder_list_fu['Outage Date'].isin(selected_dates)]
                    
#                 if not feeder_list_fu.empty:
#                     feeder_list_fu['Diff in Hours'] = (feeder_list_fu['Diff in mins'] / 60).round(2)
#                     feeder_list_fu = feeder_list_fu[['Outage Date', 'Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket']]
#                     styled_fu = feeder_list_fu.style.apply(highlight_notorious, axis=1).format({'Diff in Hours': '{:.2f}'}).set_table_styles(HEADER_STYLES)
#                     st.dataframe(styled_fu, width="stretch", hide_index=True)
#                 else:
#                     empty_df = pd.DataFrame(columns=['Outage Date', 'Start Time', 'Feeder', 'Diff in Hours', 'Duration Bucket'])
#                     st.dataframe(empty_df.style.set_table_styles(HEADER_STYLES), width="stretch", hide_index=True)
#     else:
#         st.info("No circle data available.")
        
        

#  =======================================================================================================================================
#  =======================================================================================================================================
# V3
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
