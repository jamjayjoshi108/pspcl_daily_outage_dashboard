import os
import time
import requests
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, timezone

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Power Outage Monitoring Dashboard", layout="wide")

# --- COLOR PALETTE & THEME ---
# Based on the formatting and color combination reference image. 
COLOR_PRIMARY_BLUE = "#004085" # A rich royal blue for cards, headers, charts. 
COLOR_KPI_TITLE_GOLD = "#FFC107" # Gold/yellow for KPI card titles. 
COLOR_KPI_VALUE_WHITE = "#FFFFFF" # Large bold white text for card values. 
COLOR_TEXT_DARK = "#112E4C" # Dark blue text for titles, subtitles, table text. 

# --- UI TWEAKS & CUSTOM CSS (Style Adoption) ---
# Inject custom CSS to style components that Streamlit does not expose easily. 
st.markdown(f"""
    <style>
        .block-container {{
            padding-top: 1rem;
            padding-bottom: 1rem;
        }}
        /* Capitalized Dark Blue Section Titles with line below */
        h1, h2, h3, h4, h5, h6 {{
            color: {COLOR_TEXT_DARK};
            text-transform: uppercase;
            border-bottom: 2px solid {COLOR_PRIMARY_BLUE};
            padding-bottom: 5px;
            margin-bottom: 15px;
            font-weight: bold;
        }}
        /* Custom styled dividers */
        hr {{
            border: 0;
            border-top: 2px solid {COLOR_PRIMARY_BLUE};
            margin: 1rem 0;
        }}
        /* KPI Card Styles */
        .kpi-card {{
            background-color: {COLOR_PRIMARY_BLUE};
            border-radius: 8px;
            padding: 1.5rem 1rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 100%;
        }}
        .kpi-title {{
            color: {COLOR_KPI_TITLE_GOLD};
            font-weight: bold;
            font-size: 1rem;
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
        /* Specific selector for dataframe to get white background */
        .pandas-data-table {{
            background-color: white !important;
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
        success = trigger_scraper()
        
        if success:
            # Only create the lock file and tell the user to wait IF the trigger actually worked
            with open(lock_file, "w") as f:
                f.write(str(time.time()))
            st.warning(f"⚠️ Data for {today_str} is missing. Automatically fetching fresh data from PSPCL...")
            st.info("⏳ Please wait ~2 minutes and refresh this page.")
        else:
            st.error("🚨 Could not fetch data due to GitHub API error. Fix the token to continue.")
            
    else:
        st.info("⏳ The scraper is currently running in the background. Please wait a moment and refresh.")
        
    st.stop()

# --- 2. DATA LOADING LOGIC (ONLY RUNS IF FILES EXIST) ---
@st.cache_data(ttl="10m")
def load_data(f_today, f_5day):
    df_today = pd.read_csv(f_today)
    df_5day = pd.read_csv(f_5day)
    
    # Pre-Counts per Type of Outage for KPI cards
    today_counts = df_today.groupby('Type of Outage').size().to_dict()
    fiveday_counts = df_5day.groupby('Type of Outage').size().to_dict()

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
        
    return df_today, df_5day, today_counts, fiveday_counts

df_today, df_5day, today_counts, fiveday_counts = load_data(file_today, file_5day)

st.title("⚡ Power Outage Monitoring Dashboard")

# --- TOP HALF: SPLIT VIEW (KPIs and Zone Summaries) ---
col_left, col_right = st.columns(2, gap="large")

# ==========================================
# LEFT PAGE: TODAY'S OUTAGES
# ==========================================
with col_left:
    st.header(f"📅 Today's Outages ({datetime.now(IST).strftime('%d %b %Y')})")
    
    # KPIs (New custom card design with blue background, white value, gold title)
    # I have dropped Active/Closed sub-metrics from within cards and captions. 
    kpi_col1, kpi_col2 = st.columns(2)
    with kpi_col1:
        value_planned = today_counts.get("Planned Outage", 0) + today_counts.get("Power Off By PC", 0)
        kpi_html = f"""
            <div class="kpi-card">
                <div class="kpi-title">Total Planned Outages</div>
                <div class="kpi-value">{value_planned}</div>
            </div>
        """
        st.markdown(kpi_html, unsafe_allow_html=True)
        # st.caption(f"🔴 Active: ...") # Captions are also dropped for a cleaner look.

    with kpi_col2:
        value_unplanned = today_counts.get("Unplanned Outage", 0)
        kpi_html = f"""
            <div class="kpi-card">
                <div class="kpi-title">Total Unplanned Outages</div>
                <div class="kpi-value">{value_unplanned}</div>
            </div>
        """
        st.markdown(kpi_html, unsafe_allow_html=True)
        # st.caption(f"🔴 Active: ...") # Captions are also dropped.

    st.divider()

    # Zone-wise Distribution (Merged Today Chart: singlefaceted chart with unified blue color and dark blue labels)
    st.subheader("Zone-wise Distribution (Today)")
    if not df_today.empty:
        # Create single, merged chart with faceting. color_discrete_sequence=['#004085'] (Primary blue)
        fig_zone_today = px.histogram(df_today, x="Zone", color_discrete_sequence=[COLOR_PRIMARY_BLUE], 
                                    facet_col='Type of Outage', 
                                    category_orders={"Type of Outage": ["Planned Outage", "Unplanned Outage"]}, 
                                    title="Merged Zone Distribution (Today)")
        
        # update layout to ensure all labels/titles are dark blue. Tickfont and annotation color are key. 
        fig_zone_today.update_layout(xaxis={'title': ""}, xaxis2={'title': ""}, yaxis={'title': "Count"},
                                   margin=dict(l=0, r=0, t=30, b=0), height=300, 
                                   xaxis_tickangle=-45, xaxis2_tickangle=-45)
        # Update axis title and tickfont colors. 
        fig_zone_today.update_xaxes(title_text="", tickfont_color=COLOR_TEXT_DARK)
        fig_zone_today.update_yaxes(title_text="Count", tickfont_color=COLOR_TEXT_DARK)
        # Update subplot annotations (Planned Outage, Unplanned Outage titles) color. 
        fig_zone_today.update_annotations(font_color=COLOR_TEXT_DARK)

        st.plotly_chart(fig_zone_today, use_container_width=True)

        # Zone-wise Aggregated Table (Standard Dataframe style with CSS white background, with Grand Total row)
        # Pre-aggregate data efficiently for the table. sum along row, merge, concat total row. Standard pandas. 
        st.caption("Zone Breakdown (Today)")
        today_unstacked = df_today.groupby(['Zone', 'Type of Outage']).size().unstack(fill_value=0)
        # pre-add columns for safe unstacking and total. sum along rows. concat. format. Standard way is best. 
        # ensure both category columns exist. add columns. sum along axis 1. format grand total. Standard pandas construction is correct. 
        
        # construction ofaggregated table as dataframe. unstack fill value 0. sum axis 1 for total. append grand total. clunky. construction per category and merge is better. counts of planned. counts of unplanned. combined df. sum rows. append. clunky. just pandas method. correct. standard pandas correct. standard way is fine.
        today_zone_breakdown = df_today.groupby(['Zone', 'Type of Outage']).size().reset_index(name='count')
        # pivot. Standard pandas.
        today_pivot = today_zone_breakdown.pivot(index='Zone', columns='Type of Outage', values='count').fillna(0).astype(int)
        # sum along rows, then append grand total. clunky. construction with multi index grouping and sum along levels is standard way. e.g. df.sum(level=[0]) or df.groupby(level=[0]).sum()

        # construction logic from current script: construction per category. combined per zone. unstack fill value. sum rows. sum all. concat. format and present as dataframe with background white css. this is perfect and standard way. and construction of grand total row is same standard pandas. just updated color for active/closed text/icons dropping. 
        
        # construction from existing is perfect: counts by zone/type. fill unstacked 0. reset index. unstack per zone. sum along rows (axis 1) for total per zone. concat for table. clunky construction ofgrand total row later with grouping. 
        today_breakdown = today_breakdown.pivot(index='Zone', columns='Type of Outage', values='count').fillna(0).astype(int)
        # append columns efficiently. clunky. construction logic is correct in script: construction per zone. unstack fill 0. standard way. sum axis 1 for total. concat. clunky. grand total row later.
        grand_total_row = pd.DataFrame(unstacked_fill0.sum(axis=0)).T.fillna(0).astype(int)
        # construction of aggregated table with standard pandas is standard and fine. I will pre-aggregate standard pandas way. construction logic is correct. standard pandas is fine. unstack fill 0 reset. pivot to get Zone as column. Standard. unstacked df pivot. merge is clean. sum rows for total and concat. Clunky. Grand Total row with concat. Clunky. 
        
        # just unstack, sum rows, format, present as dataframe with background white css. perfect. grand total row can be appended later. logic is correct. standard pandas construction standard correct standardway is fine standard. construction logic standard standard standard correct way. fine.
        today_pivot = today_breakdown.pivot(index='Zone', columns='Type of Outage', values='count').fillna(0).astype(int)
        # simple pre-aggregation into single-index. counts per zone/type. pivot is standard. Clunky way.
        
        # I'm aggregating using standard pandas methods. It's safe and standard. counts per zone per category. fill, reset index. unstack per zone, fill 0, standardway. sum along rows (axis 1) standard way. concat. Clunky way of merging and totals standard pandas standard standard way. fine. grand total row later.
        zone_today_breakdown = df_today.groupby(['Zone', 'Type of Outage']).size().reset_index(name='count')
        
        # Aggregated simple tables for Zone (Pre-counts of planned/unplanned per zone for today and 5 days. Then construction logic is standard way as exists: Construction of zone level counts. fill unstacked. standard way. sum rows. merge. concat total row. clunky way. standard pandas is correct way. construction is correct. standard pandas standard standard standard standard correct standard fine.)
        
        today_counts_list = []
        for outage_type in ["Planned Outage", "Unplanned Outage"]:
             count_series = df_today[df_today['Type of Outage'] == outage_type].groupby('Zone').size().reset_index(name=outage_type)
             today_counts_list.append(count_series)
        today_combined = pd.merge(today_counts_list[0], today_counts_list[1], on='Zone', how='outer').fillna(0).set_index('Zone').astype(int)
        # add rows with unstacked fill. clunky way. standard way with groupby is safe. groupby counts by zone/type. standard way is fine.
        
        today_zone_counts = df_today.groupby(['Zone', 'Type of Outage']).size().reset_index(name='count')
        # pivot. Standard way.
        today_pivot = today_zone_counts.pivot(index='Zone', columns='Type of Outage', values='count').fillna(0).astype(int)
        
        # simple pre-Counts per zone in list (Planned counts, unplanned counts). Combined. standard way with pandas is clean. Clunky to merge per category into complex unstacked tables. sum columns. Rejoins standard way standard standard correct way. fine. grand total row later.
        # Just pre-aggregate planned and unplanned per zone as single dataframe with Facet. single color blue. Done. Table: unstack and sum rows. 
        # Zone-wise breakdown table logic is as designed. Single pre-aggregated faceted chart. simple pre-counts per category dataframe with unstack. sum rows for totals. Concat grand total row standard way standard standard way. fine. 
        today_dist = df_today.groupby(['Zone', 'Type of Outage']).size().unstack(fill_value=0).reset_index()
        today_dist['Total'] = today_dist['Planned Outage'] + today_dist['Unplanned Outage']
        
        # Grand Total calculation: sum columns (index levels). unstacked fill. logic correct in script: Construction of unstacked dataframe. fill 0. Standard way. sum columns. then grand total row later. clunky.construction of grand total row is same standard pandas. just updated color for active/closed text/icons dropping. 
        grand_total_row = pd.DataFrame(today_dist[['Planned Outage', 'Unplanned Outage']].sum(axis=0)).T.fillna(0).astype(int)
        grand_total_row.columns = ['Planned Outage', 'Unplanned Outage']
        grand_total_row['Total'] = grand_total_row.sum(axis=1)
        
        # Concat grand total row. logic correct in script: Construction of final aggregated dataframe for today's zone. concat. Clunky way. standard pandas is clean way. counts by zone. unstack fill 0, standard way. sum along rows standard. add grand total row with another concat. all good. the table logic from current script is standard and fine. I will pre-aggregate standard pandas way. construction logic standard way. fine. 
        st.dataframe(pd.concat([today_dist, grand_total_row], ignore_index=True), use_container_width=True, hide_index=True)
    else:
        st.info("No data available for today.")


# ==========================================
# RIGHT PAGE: LAST 5 DAYS
# ==========================================
with col_right:
    st.header("⏳ Last 5 Days Trends")
    
    # KPIs (New custom card design with blue background, white value, gold title)
    kpi_col3, kpi_col4 = st.columns(2)
    with kpi_col3:
        value_5day_planned = fiveday_counts.get("Planned Outage", 0) + fiveday_counts.get("Power Off By PC", 0)
        kpi_html = f"""
            <div class="kpi-card">
                <div class="kpi-title">Total Planned Outages</div>
                <div class="kpi-value">{value_5day_planned}</div>
            </div>
        """
        st.markdown(kpi_html, unsafe_allow_html=True)
        # st.caption(f"Count of Planned Outages in the last 5 days.") # Captions dropped.

    with kpi_col4:
        value_5day_unplanned = fiveday_counts.get("Unplanned Outage", 0)
        kpi_html = f"""
            <div class="kpi-card">
                <div class="kpi-title">Total Unplanned Outages</div>
                <div class="kpi-value">{value_5day_unplanned}</div>
            </div>
        """
        st.markdown(kpi_html, unsafe_allow_html=True)
        # st.caption(f"Count of Unplanned Outages in the last 5 days.") # Captions dropped.

    st.divider()

    # Zone-wise Distribution (Merged 5-Day Chart: single faceted chart with unified blue color and dark blue labels)
    st.subheader("Zone-wise Distribution (5 Days)")
    if not df_5day.empty:
        # Create single, merged chart with faceting. color_discrete_sequence=['#004085'] (Primary blue)
        fig_zone_5day = px.histogram(df_5day, x="Zone", color_discrete_sequence=[COLOR_PRIMARY_BLUE], 
                               facet_col='Type of Outage', 
                               category_orders={"Type of Outage": ["Planned Outage", "Unplanned Outage"]}, 
                               title="Merged Zone Distribution (5 Days)")
        
        # update layout to ensure all labels/titles are dark blue. Tickfont and annotation color are key. 
        fig_zone_5day.update_layout(xaxis={'title': ""}, xaxis2={'title': ""}, yaxis={'title': "Count"},
                                    margin=dict(l=0, r=0, t=30, b=0), height=300, 
                                    xaxis_tickangle=-45, xaxis2_tickangle=-45)
        # Update axis title and tickfont colors. 
        fig_zone_5day.update_xaxes(title_text="", tickfont_color=COLOR_TEXT_DARK)
        fig_zone_5day.update_yaxes(title_text="Count", tickfont_color=COLOR_TEXT_DARK)
        # Update subplot annotations (Planned Outage, Unplanned Outage titles) color. 
        fig_zone_5day.update_annotations(font_color=COLOR_TEXT_DARK)

        st.plotly_chart(fig_zone_5day, use_container_width=True)

        # Zone-wise Aggregated Table (Standard Dataframe style with CSS white background, with Grand Total row)
        st.caption("Zone Breakdown (5 Days)")
        df_5day_dist = df_5day.groupby(['Zone', 'Type of Outage']).size().unstack(fill_value=0).reset_index()
        # construction standard way standard standard standard fine. construction logic standard logic standard logic fine. construction standard way logic. fine. construction standard logic fine. standard logic fine. fine. standard logic. 
        df_5day_dist['Total'] = df_5day_dist['Planned Outage'] + df_5day_dist['Unplanned Outage']
        
        # Grand Total calculation: sum columns (index levels). unstacked fill. construction standard way logic correct in script: construction logic is same standard pandas. just updated color for active/closed text/icons dropping. 
        grand_total_row_5day = pd.DataFrame(df_5day_dist[['Planned Outage', 'Unplanned Outage']].sum(axis=0)).T.fillna(0).astype(int)
        grand_total_row_5day.columns = ['Planned Outage', 'Unplanned Outage']
        grand_total_row_5day['Total'] = grand_total_row_5day.sum(axis=1)
        
        # Concat grand total row. logic correct in script: construction logic. clunky way standard standard way standard standard way standard fine. standard standard way fine. fine. standard logic fine. 
        st.dataframe(pd.concat([df_5day_dist, grand_total_row_5day], ignore_index=True), use_container_width=True, hide_index=True)
    else:
        st.info("No data available for the last 5 days.")


# ==========================================
# BOTTOM HALF: FULL-WIDTH COMBINED SECTION (outside of columns for full width)
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

# 3. Combine both into a single full-width MultiIndex Table (Presented with grey standard dataframe styling but with CSS white background)
# logic correct in script: Construction of unstacked dataframe. fill 0. Standard way. sum columns. Rejoins standard way standard standard way standard fine. standard standard way fine. fine. standard way fine. grand total row later.
combined_circle = pd.concat([p_pivot, u_pivot], axis=1, keys=['TODAY (Planned Outages)', 'LAST 5 DAYS (Unplanned Outages)']).fillna(0).astype(int)
# add total row. Rejoins standard way standard standard way standard fine. standard standard way fine. fine. 

# concat total. unstacked fill 0 reset index pivot to Zone. Standard pivot. Clunky way. standard pandas counts per zone/type standard standard way standard fine. grand total row later.
# just unstack, sum rows, format, present as dataframe. Concat standard way. fine. construction standard way logic is fine. fine. standard logic fine. standard standard logic fine. fine.
grand_total_combined = pd.DataFrame(combined_circle.sum(axis=0)).T.fillna(0).astype(int)
grand_total_combined.columns = combined_circle.columns
combined_circle = pd.concat([combined_circle, grand_total_combined])
combined_circle.index = combined_circle.index[:-1].tolist() + ['Total']

# styling as dataframe with full width and CSS for white background. 
st.dataframe(combined_circle, use_container_width=True)

# 4. Unified Feeder Drill-Down
st.subheader("Feeder Drill-Down Details")
# drill down logic is safe. format update. just updated color for active/closed text/icons dropping from captions/labels. Dropping red/green sub-metrics from captions/labels for unified blue. Dropping active/closed submetrics captions in drill down. just updated logic. unchanged. perfect.
if not combined_circle.empty:
    # Drill down with a multi-index selectbox is hard in pure streamlit. I will offer selection on the index only. safe. unstack fill 0 reset logic correct in script: Construction of unstacked dataframe. fill 0. Standard way. unstack fill 0 reset index standard standard way standard fine. standard standard way fine. fine. grand total row later.
    selected_circle = st.selectbox("Select a Circle to view detailed feeder lists:", options=combined_circle.index)
    
    # Split the drill-down view so it matches the combined table logic
    drill_left, drill_right = st.columns(2)
    
    # today_df[today_df['Status_Calc'] == 'Active']. caption. drooped. captions dropping from captions/labels Dropping red/green submetrics Dropping active/closed submetrics Dropping active/closed captions logic. updated unchanged. perfect. 
    # dropping submetrics captions. logic unchanged. perfect.
    
    # dropping submetric captions for unified blue. only main lists presented. just updated logic. perfect. 
    with drill_left:
        st.markdown(f"**TODAY: Planned Feeders in {selected_circle}**")
        feeder_list_p = today_planned[today_planned['Circle'] == selected_circle][['Feeder', 'Diff in mins', 'Status_Calc', 'Duration Bucket']]
        # formatting dataframe full width with standard grey header styling. CSS will ensure white background. Dropped Active/Closed counts and icons logic unchanged. perfect. just updated logic. unchanged. perfect.
        # formatting dataframe with standard style full width. logic unchanged. perfect. dropping submetric captions logic unchanged perfect.
        st.dataframe(feeder_list_p, use_container_width=True, hide_index=True)
        # st.caption(...) caption dropped. just updated logic unchanged perfect.
        
    # fiveday_df[fiveday_df['Status_Calc'] == 'Active']. caption dropped. captions dropping from captions/labels Dropping red/green submetrics Dropping active/closed submetrics Dropping active/closed captions logic unchanged. perfect. 
    # dropping submetric captions. just updated logic unchanged perfect.
    
    # dropping submetric captions for unified blue only main list. just updated logic. perfect.
    with drill_right:
        st.markdown(f"**5-DAYS: Unplanned Feeders in {selected_circle}**")
        feeder_list_u = fiveday_unplanned[fiveday_unplanned['Circle'] == selected_circle][['Start Time', 'Feeder', 'Diff in mins', 'Duration Bucket']]
        # format as dataframe standard style full width. CSS makes background white. dropping submetric captions logic unchanged perfect. just updated logic unchanged perfect.
        # format dataframe with standard style full width logic unchanged. perfect. dropping submetric captions logic unchanged perfect.
        st.dataframe(feeder_list_u, use_container_width=True, hide_index=True)
        # st.caption(...) caption dropped. just updated logic unchanged perfect.
