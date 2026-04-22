import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Power Outage Operations Dashboard", layout="wide")

# --- CUSTOM CSS FOR COLORS ---
st.markdown("""
    <style>
    /* Styling to match your red/teal color theme */
    div[data-testid="stMetricValue"] { font-size: 1.8rem; }
    </style>
""", unsafe_allow_html=True)

# --- DATA LOADING & CLEANING ---
@st.cache_data
def load_data():
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # Load files dynamically based on today's date
    try:
        df_today = pd.read_csv(f"{today_str}_Outages_Today.csv")
        df_5day = pd.read_csv(f"{today_str}_Outages_Last_5_Days.csv")
    except FileNotFoundError:
        st.error("Data files for today not found. Please ensure the scraper has run.")
        st.stop()
    
    # Map outage types
    df_today['Type of Outage'] = df_today['Type of Outage'].replace('Power Off By PC', 'Planned Outage')
    df_5day['Type of Outage'] = df_5day['Type of Outage'].replace('Power Off By PC', 'Planned Outage')
    
    # Convert time columns
    time_cols = ['Schedule Created At', 'Start Time', 'End Time', 'Last Updated At']
    for df in [df_today, df_5day]:
        for col in time_cols:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            
        # Determine Status (Active if End Time is NaT)
        df['Status_Calc'] = df['End Time'].apply(lambda x: 'Active' if pd.isna(x) else 'Closed')
        
        # Create Time Buckets
        def assign_bucket(mins):
            if pd.isna(mins) or mins < 0: return "Active/Unknown"
            hrs = mins / 60
            if hrs <= 2: return "Up to 2 Hrs"
            elif hrs <= 4: return "2-4 Hrs"
            elif hrs <= 8: return "4-8 Hrs"
            else: return "Above 8 Hrs"
            
        df['Duration Bucket'] = df['Diff in mins'].apply(assign_bucket)
        
    return df_today, df_5day

df_today, df_5day = load_data()

# Colors based on your uploaded image legend
COLOR_PLANNED = "#ea4335" # Red
COLOR_UNPLANNED = "#45a29e" # Teal/Green

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
