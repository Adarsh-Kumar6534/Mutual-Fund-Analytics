import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Bluestock MF Dashboard", layout="wide")

# Theme styling (Bluestock colors: Blue/Teal accents)
st.markdown("""
    <style>
    .stApp {
        background-color: #f8f9fa;
    }
    .css-1d391kg {
        background-color: #003366;
    }
    h1, h2, h3 {
        color: #003366;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data(query):
    with sqlite3.connect('bluestock_mf.db') as conn:
        return pd.read_sql(query, conn)

st.sidebar.title("Bluestock Analytics")
page = st.sidebar.radio("Navigation", ["Industry Overview", "Fund Performance", "Investor Analytics", "SIP & Market Trends"])

if page == "Industry Overview":
    st.title("Industry Overview")
    
    df_aum = load_data("SELECT * FROM fact_aum")
    latest_date = df_aum['date'].max()
    latest_aum = df_aum[df_aum['date'] == latest_date]['aum_crore'].sum()
    
    df_txns = load_data("SELECT * FROM fact_transactions WHERE transaction_type = 'Sip'")
    # the raw data is in actual INR
    total_sip = df_txns['amount_inr'].sum() 
    
    try:
        df_folios = pd.read_csv('data/processed/06_industry_folio_count.csv')
        total_folios = df_folios['total_folios_cr'].iloc[-1]
    except:
        total_folios = 26.12
    
    total_schemes = df_aum[df_aum['date'] == latest_date]['num_schemes'].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    # AUM is usually in Lakh Crores format if it's 81L Cr. 8,100,000 Cr = 81L Cr.
    # We will display whatever the DB sums to.
    col1.metric("Total AUM (Cr)", f"₹ {latest_aum:,.0f}")
    col2.metric("Total SIP Inflows", f"₹ {total_sip/10000000:,.2f} Cr") # assuming amount in actual INR, convert to Cr
    col3.metric("Total Folios (Cr)", f"{total_folios}")
    col4.metric("Active Schemes", f"{total_schemes:,.0f}")
    
    st.markdown("---")
    
    aum_trend = df_aum.groupby('date')['aum_crore'].sum().reset_index()
    fig1 = px.line(aum_trend, x='date', y='aum_crore', title="Industry AUM Trend (2022-2025)", template="plotly_white")
    
    aum_amc = df_aum[df_aum['date'] == latest_date].sort_values('aum_crore', ascending=False)
    fig2 = px.bar(aum_amc, x='aum_crore', y='fund_house', orientation='h', title="AUM by AMC", template="plotly_white")
    fig2.update_layout(yaxis={'categoryorder':'total ascending'})
    
    c1, c2 = st.columns(2)
    c1.plotly_chart(fig1, use_container_width=True)
    c2.plotly_chart(fig2, use_container_width=True)

elif page == "Fund Performance":
    st.title("Fund Performance & Scorecard")
    
    df_fund = load_data("SELECT * FROM dim_fund")
    fund_houses = ["All"] + list(df_fund['fund_house'].unique())
    categories = ["All"] + list(df_fund['category'].unique())
    plans = ["All"] + list(df_fund['plan'].unique())
    
    col1, col2, col3 = st.columns(3)
    sel_house = col1.selectbox("Fund House", fund_houses)
    sel_cat = col2.selectbox("Category", categories)
    sel_plan = col3.selectbox("Plan", plans)
    
    df_perf = load_data("""
        SELECT f.amfi_code, f.scheme_name, f.fund_house, f.category, f.plan,
               p.return_3yr_pct, p.std_dev_ann_pct, p.aum_crore
        FROM dim_fund f
        JOIN fact_performance p ON f.amfi_code = p.amfi_code
    """)
    
    filtered_perf = df_perf.copy()
    if sel_house != "All": filtered_perf = filtered_perf[filtered_perf['fund_house'] == sel_house]
    if sel_cat != "All": filtered_perf = filtered_perf[filtered_perf['category'] == sel_cat]
    if sel_plan != "All": filtered_perf = filtered_perf[filtered_perf['plan'] == sel_plan]
    
    fig = px.scatter(filtered_perf, x="std_dev_ann_pct", y="return_3yr_pct", 
                     size="aum_crore", color="category", hover_name="scheme_name",
                     title="Return vs Risk (Bubble Size = AUM)", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)
    
    try:
        df_score = pd.read_csv('reports/fund_scorecard.csv')
        st.subheader("Fund Scorecard")
        st.dataframe(df_score[['scheme_name', 'Scorecard', 'CAGR_3Yr', 'Sharpe_Ratio', 'Alpha', 'Max_Drawdown']], use_container_width=True)
    except:
        st.warning("Scorecard not found.")

    st.subheader("NAV Drill-through")
    sel_fund = st.selectbox("Select Fund for NAV Trend", filtered_perf['scheme_name'].unique())
    if sel_fund:
        amfi = df_fund[df_fund['scheme_name'] == sel_fund]['amfi_code'].iloc[0]
        df_nav = load_data(f"SELECT date, nav FROM fact_nav WHERE amfi_code = {amfi} ORDER BY date")
        fig_nav = px.line(df_nav, x='date', y='nav', title=f"{sel_fund} - NAV History", template="plotly_white")
        st.plotly_chart(fig_nav, use_container_width=True)

elif page == "Investor Analytics":
    st.title("Investor Analytics")
    
    df_txns = load_data("SELECT * FROM fact_transactions")
    
    col1, col2, col3 = st.columns(3)
    sel_state = col1.selectbox("State", ["All"] + list(df_txns['state'].unique()))
    sel_age = col2.selectbox("Age Group", ["All"] + list(df_txns['age_group'].unique()))
    sel_tier = col3.selectbox("City Tier", ["All"] + list(df_txns['city_tier'].unique()))
    
    filtered_txns = df_txns.copy()
    if sel_state != "All": filtered_txns = filtered_txns[filtered_txns['state'] == sel_state]
    if sel_age != "All": filtered_txns = filtered_txns[filtered_txns['age_group'] == sel_age]
    if sel_tier != "All": filtered_txns = filtered_txns[filtered_txns['city_tier'] == sel_tier]
    
    c1, c2 = st.columns(2)
    
    state_amt = filtered_txns.groupby('state')['amount_inr'].sum().reset_index().sort_values('amount_inr', ascending=False)
    fig_state = px.bar(state_amt.head(10), x='amount_inr', y='state', orientation='h', title="Top 10 States by Transaction Amount", template="plotly_white")
    fig_state.update_layout(yaxis={'categoryorder':'total ascending'})
    c1.plotly_chart(fig_state, use_container_width=True)
    
    split_amt = filtered_txns.groupby('transaction_type')['amount_inr'].sum().reset_index()
    fig_split = px.pie(split_amt, names='transaction_type', values='amount_inr', hole=0.5, title="Transaction Split", template="plotly_white")
    c2.plotly_chart(fig_split, use_container_width=True)
    
    c3, c4 = st.columns(2)
    sip_txns = filtered_txns[filtered_txns['transaction_type'] == 'Sip']
    age_sip = sip_txns.groupby('age_group')['amount_inr'].mean().reset_index()
    fig_age = px.bar(age_sip, x='age_group', y='amount_inr', title="Avg SIP Amount by Age Group", template="plotly_white")
    c3.plotly_chart(fig_age, use_container_width=True)
    
    filtered_txns['month'] = pd.to_datetime(filtered_txns['transaction_date']).dt.to_period('M').astype(str)
    month_vol = filtered_txns.groupby('month').size().reset_index(name='volume')
    fig_vol = px.line(month_vol, x='month', y='volume', title="Monthly Transaction Volume", template="plotly_white")
    c4.plotly_chart(fig_vol, use_container_width=True)

elif page == "SIP & Market Trends":
    st.title("SIP & Market Trends")
    
    df_sip = pd.read_csv('data/processed/04_monthly_sip_inflows.csv')
    df_sip['month'] = pd.to_datetime(df_sip['month'])
    
    df_bench = pd.read_csv('data/processed/10_benchmark_indices.csv')
    df_nifty = df_bench[df_bench['index_name'] == 'NIFTY50'].copy()
    df_nifty['month'] = pd.to_datetime(df_nifty['date']).dt.to_period('M').dt.to_timestamp()
    nifty_monthly = df_nifty.groupby('month')['close_value'].last().reset_index()
    
    merged = pd.merge(df_sip, nifty_monthly, on='month', how='inner')
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=merged['month'], y=merged['sip_inflow_cr'], name="SIP Inflow (Cr)", marker_color='#003366'))
    fig.add_trace(go.Scatter(x=merged['month'], y=merged['close_value'], name="Nifty 50", yaxis='y2', line=dict(color='#FF9900', width=2)))
    
    fig.update_layout(
        title="Monthly SIP Inflows vs Nifty 50",
        yaxis=dict(title="SIP Inflow (Cr)"),
        yaxis2=dict(title="Nifty 50", overlaying='y', side='right'),
        template="plotly_white",
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    c1, c2 = st.columns(2)
    df_cat = pd.read_csv('data/processed/05_category_inflows.csv')
    fig_heat = px.density_heatmap(df_cat, x="month", y="category", z="net_inflow_cr", title="Category Inflow Heatmap", template="plotly_white")
    c1.plotly_chart(fig_heat, use_container_width=True)
    
    top_cat = df_cat.groupby('category')['net_inflow_cr'].sum().reset_index().sort_values('net_inflow_cr', ascending=False).head(5)
    fig_top = px.bar(top_cat, x='net_inflow_cr', y='category', orientation='h', title="Top 5 Categories by Net Inflow", template="plotly_white")
    fig_top.update_layout(yaxis={'categoryorder':'total ascending'})
    c2.plotly_chart(fig_top, use_container_width=True)
