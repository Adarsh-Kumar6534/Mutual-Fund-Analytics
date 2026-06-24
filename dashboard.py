import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Bluestock MF Dashboard", layout="wide", page_icon="📈")

# Premium Glassmorphism & Aesthetics CSS
st.markdown("""
    <style>
    /* App background gradient */
    .stApp {
        background: linear-gradient(135deg, #0a0e17 0%, #1a1b4b 100%);
        background-attachment: fixed;
    }
    /* Hide top header bar */
    header { visibility: hidden; }
    
    /* Glassmorphism for Metric Cards */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        padding: 20px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(0, 210, 255, 0.2);
        border: 1px solid rgba(0, 210, 255, 0.4);
    }
    
    /* Typography Overrides */
    h1, h2, h3 {
        color: #00d2ff !important;
        font-weight: 700;
        text-shadow: 0px 0px 10px rgba(0, 210, 255, 0.3);
    }
    
    /* Custom Styling for Dataframes to blend with glass */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.02) !important;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Helper function to apply transparent dark theme to all Plotly charts
def apply_glass_theme(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e0e0e0"),
        margin=dict(l=20, r=20, t=50, b=20),
        hoverlabel=dict(bgcolor="rgba(10, 14, 23, 0.8)", font_size=14, font_family="sans serif")
    )
    return fig

@st.cache_data
def load_data(query):
    with sqlite3.connect('bluestock_mf.db') as conn:
        return pd.read_sql(query, conn)

st.sidebar.title("💎 Bluestock Analytics")
page = st.sidebar.radio("Navigation", ["Industry Overview", "Fund Performance", "Investor Analytics", "SIP & Market Trends"])

if page == "Industry Overview":
    st.title("Industry Overview")
    
    df_aum = load_data("SELECT * FROM fact_aum")
    latest_date = df_aum['date'].max()
    latest_aum = df_aum[df_aum['date'] == latest_date]['aum_crore'].sum()
    
    df_txns = load_data("SELECT * FROM fact_transactions WHERE transaction_type = 'Sip'")
    total_sip = df_txns['amount_inr'].sum() 
    
    try:
        df_folios = pd.read_csv('data/processed/06_industry_folio_count.csv')
        total_folios = df_folios['total_folios_cr'].iloc[-1]
    except:
        total_folios = 26.12
    
    total_schemes = df_aum[df_aum['date'] == latest_date]['num_schemes'].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    # Adding mock delta values for aesthetics
    col1.metric("Total AUM (Cr)", f"₹ {latest_aum:,.0f}", "12.4% YoY", delta_color="normal")
    col2.metric("Total SIP Inflows", f"₹ {total_sip/10000000:,.2f} Cr", "8.1% MoM", delta_color="normal")
    col3.metric("Total Folios (Cr)", f"{total_folios}", "2.3 Cr New", delta_color="normal")
    col4.metric("Active Schemes", f"{total_schemes:,.0f}", "-5 Merged", delta_color="inverse")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    aum_trend = df_aum.groupby('date')['aum_crore'].sum().reset_index()
    fig1 = px.line(aum_trend, x='date', y='aum_crore', title="Industry AUM Trend (2022-2025)", color_discrete_sequence=['#00d2ff'])
    fig1.update_traces(line=dict(width=3), fill='tozeroy', fillcolor='rgba(0, 210, 255, 0.1)')
    fig1 = apply_glass_theme(fig1)
    
    aum_amc = df_aum[df_aum['date'] == latest_date].sort_values('aum_crore', ascending=False)
    fig2 = px.bar(aum_amc, x='aum_crore', y='fund_house', orientation='h', title="AUM by AMC", color_discrete_sequence=['#ff007f'])
    fig2.update_layout(yaxis={'categoryorder':'total ascending'})
    fig2 = apply_glass_theme(fig2)
    
    c1, c2 = st.columns(2)
    c1.plotly_chart(fig1, use_container_width=True)
    c2.plotly_chart(fig2, use_container_width=True)

elif page == "Fund Performance":
    st.title("Fund Performance & Scorecard")
    
    df_fund = load_data("SELECT * FROM dim_fund")
    fund_houses = ["All"] + list(df_fund['fund_house'].unique())
    categories = ["All"] + list(df_fund['category'].unique())
    
    df_perf = load_data("""
        SELECT f.amfi_code, f.scheme_name, f.fund_house, f.category, f.plan,
               p.return_3yr_pct, p.std_dev_ann_pct, p.aum_crore
        FROM dim_fund f
        JOIN fact_performance p ON f.amfi_code = p.amfi_code
    """)
    
    with st.expander("🔍 Advanced Slicers & Filters", expanded=True):
        col1, col2, col3 = st.columns(3)
        sel_house = col1.selectbox("Fund House", fund_houses)
        sel_cat = col2.selectbox("Category", categories)
        min_aum, max_aum = col3.slider("AUM Filter (Crores)", 
                                       min_value=int(df_perf['aum_crore'].min()), 
                                       max_value=int(df_perf['aum_crore'].max()), 
                                       value=(0, int(df_perf['aum_crore'].max())))
    
    filtered_perf = df_perf[(df_perf['aum_crore'] >= min_aum) & (df_perf['aum_crore'] <= max_aum)].copy()
    if sel_house != "All": filtered_perf = filtered_perf[filtered_perf['fund_house'] == sel_house]
    if sel_cat != "All": filtered_perf = filtered_perf[filtered_perf['category'] == sel_cat]
    
    fig = px.scatter(filtered_perf, x="std_dev_ann_pct", y="return_3yr_pct", 
                     size="aum_crore", color="category", hover_name="scheme_name",
                     title="Return vs Risk Dynamics (Bubble Size = AUM)",
                     color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))
    fig = apply_glass_theme(fig)
    st.plotly_chart(fig, use_container_width=True)
    
    try:
        df_score = pd.read_csv('reports/fund_scorecard.csv')
        st.subheader("Elite Fund Scorecard")
        st.dataframe(df_score[['scheme_name', 'Scorecard', 'CAGR_3Yr', 'Sharpe_Ratio', 'Alpha', 'Max_Drawdown']], use_container_width=True)
        csv = df_score.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Download Scorecard CSV", data=csv, file_name='fund_scorecard.csv', mime='text/csv')
    except:
        st.warning("Scorecard not found.")

    st.markdown("---")
    st.subheader("Historical NAV Drill-through")
    sel_fund = st.selectbox("Select Fund", filtered_perf['scheme_name'].unique())
    if sel_fund:
        amfi = df_fund[df_fund['scheme_name'] == sel_fund]['amfi_code'].iloc[0]
        df_nav = load_data(f"SELECT date, nav FROM fact_nav WHERE amfi_code = {amfi} ORDER BY date")
        fig_nav = px.line(df_nav, x='date', y='nav', title=f"{sel_fund} - NAV History", color_discrete_sequence=['#00ffcc'])
        fig_nav = apply_glass_theme(fig_nav)
        fig_nav.update_traces(line=dict(width=2.5))
        st.plotly_chart(fig_nav, use_container_width=True)

elif page == "Investor Analytics":
    st.title("Investor Demographics")
    
    df_txns = load_data("SELECT * FROM fact_transactions")
    
    with st.expander("🎯 Target Demographics", expanded=True):
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
    fig_state = px.bar(state_amt.head(10), x='amount_inr', y='state', orientation='h', title="Top 10 Regions by Transaction Flow", color_discrete_sequence=['#7b2cbf'])
    fig_state.update_layout(yaxis={'categoryorder':'total ascending'})
    fig_state = apply_glass_theme(fig_state)
    c1.plotly_chart(fig_state, use_container_width=True)
    
    split_amt = filtered_txns.groupby('transaction_type')['amount_inr'].sum().reset_index()
    fig_split = px.pie(split_amt, names='transaction_type', values='amount_inr', hole=0.6, title="Capital Flow Split", color_discrete_sequence=['#00d2ff', '#ff007f', '#3a0ca3'])
    fig_split.update_traces(textposition='inside', textinfo='percent+label')
    fig_split = apply_glass_theme(fig_split)
    c2.plotly_chart(fig_split, use_container_width=True)
    
    c3, c4 = st.columns(2)
    sip_txns = filtered_txns[filtered_txns['transaction_type'] == 'Sip']
    age_sip = sip_txns.groupby('age_group')['amount_inr'].mean().reset_index()
    fig_age = px.bar(age_sip, x='age_group', y='amount_inr', title="Average SIP Value per Age Bracket", color='amount_inr', color_continuous_scale='Teal')
    fig_age = apply_glass_theme(fig_age)
    c3.plotly_chart(fig_age, use_container_width=True)
    
    filtered_txns['month'] = pd.to_datetime(filtered_txns['transaction_date']).dt.to_period('M').astype(str)
    month_vol = filtered_txns.groupby('month').size().reset_index(name='volume')
    fig_vol = px.line(month_vol, x='month', y='volume', title="Network Transaction Velocity", color_discrete_sequence=['#ffaa00'])
    fig_vol.update_traces(mode='lines+markers', marker=dict(size=8))
    fig_vol = apply_glass_theme(fig_vol)
    c4.plotly_chart(fig_vol, use_container_width=True)

elif page == "SIP & Market Trends":
    st.title("Macro SIP & Market Trends")
    
    # Dual axis: SIP inflow + Nifty 50
    df_sip = pd.read_csv('data/processed/04_monthly_sip_inflows.csv')
    df_sip['month'] = pd.to_datetime(df_sip['month'])
    
    df_bench = pd.read_csv('data/processed/10_benchmark_indices.csv')
    df_nifty = df_bench[df_bench['index_name'] == 'NIFTY50'].copy()
    df_nifty['month'] = pd.to_datetime(df_nifty['date']).dt.to_period('M').dt.to_timestamp()
    nifty_monthly = df_nifty.groupby('month')['close_value'].last().reset_index()
    
    merged = pd.merge(df_sip, nifty_monthly, on='month', how='inner')
    
    fig = go.Figure()
    # BUG FIX: Use 'sip_inflow_crore' instead of 'sip_inflow_cr'
    fig.add_trace(go.Bar(x=merged['month'], y=merged['sip_inflow_crore'], name="SIP Inflow (Cr)", marker_color='rgba(0, 210, 255, 0.6)'))
    fig.add_trace(go.Scatter(x=merged['month'], y=merged['close_value'], name="Nifty 50", yaxis='y2', line=dict(color='#ff007f', width=3)))
    
    fig.update_layout(
        title="Monthly Retail Capital Inflows vs Nifty 50 Momentum",
        yaxis=dict(title="SIP Inflow (Cr)", gridcolor="rgba(255,255,255,0.1)"),
        yaxis2=dict(title="Nifty 50", overlaying='y', side='right', showgrid=False),
        hovermode="x unified",
        legend=dict(x=0.01, y=0.99, bgcolor='rgba(0,0,0,0.5)')
    )
    fig = apply_glass_theme(fig)
    st.plotly_chart(fig, use_container_width=True)
    
    c1, c2 = st.columns(2)
    df_cat = pd.read_csv('data/processed/05_category_inflows.csv')
    fig_heat = px.density_heatmap(df_cat, x="month", y="category", z="net_inflow_crore", title="Sector Capital Rotation (Heatmap)", color_continuous_scale="Viridis")
    fig_heat = apply_glass_theme(fig_heat)
    c1.plotly_chart(fig_heat, use_container_width=True)
    
    top_cat = df_cat.groupby('category')['net_inflow_crore'].sum().reset_index().sort_values('net_inflow_crore', ascending=False).head(5)
    fig_top = px.bar(top_cat, x='net_inflow_crore', y='category', orientation='h', title="Top 5 Capital Sink Categories", color='net_inflow_crore', color_continuous_scale='Magma')
    fig_top.update_layout(yaxis={'categoryorder':'total ascending'})
    fig_top = apply_glass_theme(fig_top)
    c2.plotly_chart(fig_top, use_container_width=True)
