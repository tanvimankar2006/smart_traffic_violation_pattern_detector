import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
import datetime
import seaborn as sns

# --- Plotting Theme & Helper Functions (Light Background, Dark Bars) ---
sns.set_theme(style='whitegrid', palette='Set2')
plt.rcParams.update({
    'figure.facecolor': '#ffffff',
    'axes.facecolor': '#ffffff',
    'axes.edgecolor': '#cccccc',
    'xtick.color': '#333333',
    'ytick.color': '#333333',
    'text.color': '#333333',
    'font.size': 11,
    'grid.color': '#e0e0e0',
    'grid.alpha': 0.5
})

ACCENT = '#2563eb'  # blue for light theme headings

def plot_count(ax, series, title):
    """Count plot using bar chart."""
    vals = series.value_counts()
    sns.barplot(x=vals.index, y=vals.values, palette='Set2', ax=ax)
    ax.set_title(title, color=ACCENT, fontsize=13, fontweight='bold')
    ax.set_xlabel('')
    ax.set_ylabel('Count', color='#333333')
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', color='#333333')
    ax.grid(axis='y', alpha=0.3)

def plot_hist(ax, series, title, bins=30, color='#1e40af'):
    """Histogram plot."""
    ax.hist(series.dropna(), bins=bins, color=color, alpha=0.8, edgecolor='white')
    ax.set_title(title, color=ACCENT, fontsize=13, fontweight='bold')
    ax.set_xlabel(series.name or '', color='#333333')
    ax.set_ylabel('Frequency', color='#333333')
    ax.grid(axis='y', alpha=0.3)

def plot_line(ax, x_idx, y_vals, title):
    """Line chart."""
    # Accept pandas Series or numpy arrays
    y = y_vals.values if hasattr(y_vals, 'values') else np.asarray(y_vals)
    y = np.asarray(y).flatten()
    ax.plot(range(len(x_idx)), y, color='#1e40af', marker='o', linewidth=2)
    ax.set_title(title, color=ACCENT, fontsize=13, fontweight='bold')
    ax.set_xticks(range(len(x_idx)))
    ax.set_xticklabels(list(x_idx), rotation=45, ha='right', color='#333333')
    ax.set_ylabel('Count', color='#333333')
    ax.grid(axis='y', alpha=0.3)

def plot_bar(ax, labels, values, title):
    """Vertical bar chart."""
    sns.barplot(x=list(labels), y=list(values), palette='Set2', ax=ax)
    ax.set_title(title, color=ACCENT, fontsize=13, fontweight='bold')
    ax.set_xlabel('')
    ax.set_ylabel('Count', color='#333333')
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', color='#333333')
    ax.grid(axis='y', alpha=0.3)

def plot_barh(ax, labels, values, title):
    """Horizontal bar chart."""
    idx = np.arange(len(labels))
    ax.barh(idx, values, color=sns.color_palette('Set2', len(labels)))
    ax.set_yticks(idx)
    ax.set_yticklabels(labels, color='#333333')
    ax.set_title(title, color=ACCENT, fontsize=13, fontweight='bold')
    ax.set_xlabel('Count', color='#333333')
    ax.grid(axis='x', alpha=0.3)

def plot_scatter_with_ref(ax, x, y, title):
    """Scatter plot with y=x reference line."""
    sns.scatterplot(x=x, y=y, color='#1e40af', s=36, alpha=0.75, ax=ax)
    # safe min/max
    try:
        minv = int(min(x.min(), y.min()))
        maxv = int(max(x.max(), y.max()))
    except Exception:
        minv, maxv = 0, max(int(x.max()) if hasattr(x, 'max') else 0, int(y.max()) if hasattr(y, 'max') else 0)
    ax.plot([minv, maxv], [minv, maxv], ls='--', color='#666666', linewidth=1.5)
    ax.set_title(title, color=ACCENT, fontsize=13, fontweight='bold')
    ax.set_xlabel('Speed Limit (km/h)', color='#333333')
    ax.set_ylabel('Recorded Speed (km/h)', color='#333333')
    # compute excess safely
    xv = np.asarray(x)
    yv = np.asarray(y)
    if xv.size == yv.size:
        tmp = yv - xv
        pct_over = (tmp > 0).mean() * 100 if xv.size else 0
        avg_excess = tmp[tmp > 0].mean() if (tmp > 0).any() else 0
    else:
        pct_over = 0
        avg_excess = 0
    ax.text(0.02, 0.98, f"{len(xv):,} records\n% Over Limit: {pct_over:.1f}%\nAvg Excess: {avg_excess:.1f} km/h",
            transform=ax.transAxes, va='top', color='#333333', fontsize=9, bbox=dict(facecolor='#f5f5f5', alpha=0.9))
    ax.grid(alpha=0.3)

def plot_heatmap(ax, df_numeric, title):
    """Heatmap of numeric correlations."""
    corr = df_numeric.corr()
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', vmin=-1, vmax=1, ax=ax, cbar_kws={'shrink':0.8})
    ax.set_title(title, color=ACCENT, fontsize=13, fontweight='bold')

def plot_pie(ax, series, title, donut=False):
    """Pie or donut chart."""
    counts = series.value_counts()
    colors = sns.color_palette('Set2', len(counts))
    wedges, texts, autotexts = ax.pie(counts, labels=counts.index, autopct='%1.1f%%', colors=colors, startangle=90)
    for text in texts:
        text.set_color('#333333')
    for autotext in autotexts:
        autotext.set_color('#ffffff')
        autotext.set_fontweight('bold')
    if donut:
        centre = plt.Circle((0,0),0.70,fc='#ffffff')
        ax.add_artist(centre)
    ax.set_title(title, color=ACCENT, fontsize=13, fontweight='bold')

# --- Page Config ---
st.set_page_config(page_title="Smart Traffic AI Dashboard", layout="wide", page_icon="🚦")

# --- Light Theme CSS with Black Font ---
st.markdown("""
    <style>
    /* Root styles */
    :root {
        --primary-bg: #ffffff;
        --secondary-bg: #f5f5f5;
        --tertiary-bg: #e8e8e8;
        --text-primary: #000000;
        --text-secondary: #333333;
        --accent-blue: #2563eb;
        --accent-blue-dark: #1e40af;
    }
    
    /* Main container */
    .main {
        background-color: var(--primary-bg) !important;
        color: var(--text-primary) !important;
    }
    
    html {
        background-color: var(--primary-bg) !important;
    }
    
    body {
        background-color: var(--primary-bg) !important;
        color: var(--text-primary) !important;
    }
    
    [data-testid="stAppViewContainer"] {
        background-color: var(--primary-bg) !important;
    }
    
    [data-testid="stDecoration"] {
        background-color: var(--primary-bg) !important;
    }
    
    /* Navbar/Header */
    .navbar {
        background: linear-gradient(90deg, var(--accent-blue) 0%, var(--accent-blue-dark) 100%);
        color: white;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .navbar h1, .navbar h2, .navbar h3, .navbar p {
        color: white !important;
        margin: 5px 0 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: var(--secondary-bg);
        border-radius: 8px;
        padding: 8px;
        border-bottom: 2px solid var(--tertiary-bg);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: var(--tertiary-bg);
        border-radius: 6px;
        color: var(--text-secondary) !important;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, var(--accent-blue) 0%, var(--accent-blue-dark) 100%) !important;
        color: white !important;
    }
    
    /* Metrics */
    .stMetric {
        background-color: var(--secondary-bg) !important;
        border: 1px solid var(--tertiary-bg) !important;
        border-radius: 8px;
        padding: 16px;
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
    }
    
    [data-testid="stMetricValue"] {
        color: var(--text-primary) !important;
        font-size: 24px !important;
        font-weight: bold !important;
    }
    
    [data-testid="stMetricDelta"] {
        color: var(--text-secondary) !important;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: var(--accent-blue) !important;
        color: white !important;
        border-radius: 6px !important;
        border: none !important;
        padding: 12px 20px !important;
        font-weight: bold !important;
    }
    
    .stButton > button:hover {
        background-color: var(--accent-blue-dark) !important;
        border: 2px solid var(--accent-blue) !important;
    }
    
    /* Text elements */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
    }
    
    p, div, span {
        color: var(--text-primary) !important;
    }
    
    label {
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }
    
    /* Markdown */
    .stMarkdown {
        color: var(--text-primary) !important;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: var(--text-primary) !important;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background-color: var(--tertiary-bg) !important;
        color: var(--text-primary) !important;
    }
    
    .streamlit-expanderContent {
        background-color: var(--secondary-bg) !important;
        color: var(--text-primary) !important;
    }
    
    /* Dataframe */
    [data-testid="stDataFrame"] {
        background-color: var(--secondary-bg) !important;
        color: var(--text-primary) !important;
    }
    
    /* Input fields */
    input, select, textarea {
        background-color: var(--secondary-bg) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--tertiary-bg) !important;
    }
    
    /* Multiselect */
    [data-baseweb="select"] {
        background-color: var(--secondary-bg) !important;
        color: var(--text-primary) !important;
    }
    
    /* Dividers */
    hr {
        border-color: var(--tertiary-bg) !important;
    }
    
    /* File uploader */
    [data-testid="stFileUploadDropzone"] {
        background-color: var(--secondary-bg) !important;
        border: 2px dashed var(--tertiary-bg) !important;
    }
    
    /* Sidebar (if visible) */
    .stSidebar {
        background-color: var(--secondary-bg) !important;
        color: var(--text-primary) !important;
    }
    
    .stSidebar h1, .stSidebar h2, .stSidebar h3 {
        color: var(--text-primary) !important;
    }
    
    .stSidebar p, .stSidebar label {
        color: var(--text-secondary) !important;
    }
    
    /* Code blocks */
    .stCodeBlock {
        background-color: var(--secondary-bg) !important;
        color: var(--text-primary) !important;
    }
    
    /* Success/Warning/Error messages */
    .stSuccess, .stWarning, .stError, .stInfo {
        background-color: var(--secondary-bg) !important;
        color: var(--text-primary) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        
        # Basic Cleaning
        df.drop_duplicates(inplace=True)
        df.dropna(subset=["Date", "Time", "Location", "Violation_Type"], inplace=True)
        
        # Convert Date & Time
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
        df["Time_Parsed"] = pd.to_datetime(df["Time"], format="%H:%M", errors='coerce')
        mask_missing = df["Time_Parsed"].isna()
        if mask_missing.any():
            df.loc[mask_missing, "Time_Parsed"] = pd.to_datetime(df.loc[mask_missing, "Time"], format="%H:%M:%S", errors='coerce')
        
        df["Hour"] = df["Time_Parsed"].dt.hour
        df["Day"] = df["Date"].dt.day_name()
        df["Month"] = df["Date"].dt.month_name()
        df["Year"] = df["Date"].dt.year
        
        # Rename 'Location' to 'State'
        df.rename(columns={'Location': 'State'}, inplace=True)
        
        # Numeric parsing
        df["Fine_Amount"] = pd.to_numeric(df["Fine_Amount"], errors='coerce').fillna(0)
        df["Driver_Age"] = pd.to_numeric(df["Driver_Age"], errors='coerce')
        df["Recorded_Speed"] = pd.to_numeric(df["Recorded_Speed"], errors='coerce')
        df["Speed_Limit"] = pd.to_numeric(df["Speed_Limit"], errors='coerce')
        
        if 'Fine_Paid' in df.columns:
            df['Status'] = df['Fine_Paid'].map({'Yes': 'Paid', 'No': 'Unpaid'})
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

DEFAULT_DATASET = "traffic_data.csv"

# --- Initialize Session State ---
if 'df' not in st.session_state:
    try:
        st.session_state.df = load_data(DEFAULT_DATASET)
    except:
        st.session_state.df = pd.DataFrame()

# --- Sidebar Navigation & Global Filters ---
with st.sidebar:
    st.title("🚦 Traffic AI")
    st.markdown("---")
    
    # Feature Selection
    feature = st.radio(
        "📌 Select Feature",
        options=[
            "Overview Dashboard",
            "Violation Distribution",
            "Speed Analysis",
            "Trend Analysis",
            "Weather Risk Analysis",
            "Location & Map",
            "Data Explorer",
            "About"
        ],
        index=0
    )
    
    st.markdown("---")
    st.subheader("🔧 Filters")
    
    # Global filters (applied across all pages)
    selected_states = st.multiselect(
        "States",
        options=st.session_state.df["State"].unique() if not st.session_state.df.empty else [],
        default=st.session_state.df["State"].unique()[:5] if not st.session_state.df.empty else []
    )
    
    selected_violations = st.multiselect(
        "Violation Types",
        options=st.session_state.df["Violation_Type"].unique() if not st.session_state.df.empty else [],
        default=st.session_state.df["Violation_Type"].unique() if not st.session_state.df.empty else []
    )
    
    selected_weather = st.multiselect(
        "Weather Conditions",
        options=st.session_state.df["Weather_Condition"].unique() if not st.session_state.df.empty else [],
        default=st.session_state.df["Weather_Condition"].unique() if not st.session_state.df.empty else []
    )
    
    # Apply filters
    if not st.session_state.df.empty:
        filtered_df = st.session_state.df[
            (st.session_state.df["State"].isin(selected_states)) &
            (st.session_state.df["Violation_Type"].isin(selected_violations)) &
            (st.session_state.df["Weather_Condition"].isin(selected_weather))
        ].copy()
    else:
        filtered_df = st.session_state.df.copy()

# Main page title
st.title("🚦 Traffic Violation Analysis Platform")
st.markdown(f"**Currently Viewing:** {feature}")

# --- Data Check ---
if st.session_state.df.empty and feature not in ["About", "Data Explorer"]:
    st.warning("⚠️ No dataset loaded. Please upload a CSV file to proceed.")
    st.stop()

df = st.session_state.df

# ============================================================================
# PAGE: Overview Dashboard
# ============================================================================
if feature == "Overview Dashboard":
    st.markdown("### 📊 Executive Summary & KPIs")
    
    if not filtered_df.empty:
        # KPI Row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📋 Total Violations", f"{len(filtered_df):,}")
        with col2:
            st.metric("💰 Total Fines", f"₹{filtered_df['Fine_Amount'].sum():,.0f}")
        with col3:
            st.metric("🎯 Violation Types", filtered_df['Violation_Type'].nunique())
        with col4:
            st.metric("📍 States", filtered_df['State'].nunique())
        
        st.markdown("---")
        
        # Main Dashboard Charts
        col_d1, col_d2 = st.columns(2)
        
        with col_d1:
            st.markdown("#### Top Violations")
            fig_v, ax_v = plt.subplots(figsize=(10, 5))
            plot_count(ax_v, filtered_df['Violation_Type'], "Violation Types")
            st.pyplot(fig_v, use_container_width=True)
        
        with col_d2:
            st.markdown("#### Violation Status Distribution")
            fig_s, ax_s = plt.subplots(figsize=(8, 5))
            plot_pie(ax_s, filtered_df['Status'].fillna('Unknown'), "Payment Status", donut=True)
            st.pyplot(fig_s, use_container_width=True)
        
        st.markdown("---")
        
        # Top States
        st.markdown("#### Violations by State (Top 10)")
        top_states = filtered_df['State'].value_counts().head(10)
        fig_st, ax_st = plt.subplots(figsize=(12, 5))
        plot_bar(ax_st, top_states.index, top_states.values, "Top States by Violations")
        st.pyplot(fig_st, use_container_width=True)

# ============================================================================
# PAGE: Violation Distribution
# ============================================================================
elif feature == "Violation Distribution":
    st.markdown("### 📊 Detailed Violation Analysis")
    
    if not filtered_df.empty:
        col_d1, col_d2 = st.columns(2)
        
        with col_d1:
            st.markdown("#### Violation Type Count")
            fig_c, ax_c = plt.subplots(figsize=(10, 6))
            plot_count(ax_c, filtered_df['Violation_Type'], "Count by Violation Type")
            st.pyplot(fig_c, use_container_width=True)
        
        with col_d2:
            st.markdown("#### Violation Type Distribution")
            fig_pie, ax_pie = plt.subplots(figsize=(8, 6))
            plot_pie(ax_pie, filtered_df['Violation_Type'], "Violation Percentage", donut=True)
            st.pyplot(fig_pie, use_container_width=True)
        
        st.markdown("---")
        
        # Payment Method
        st.markdown("#### Payment Method Distribution")
        fig_p, ax_p = plt.subplots(figsize=(12, 5))
        plot_count(ax_p, filtered_df['Payment_Method'], "Payment Methods")
        st.pyplot(fig_p, use_container_width=True)

# ============================================================================
# PAGE: Speed Analysis
# ============================================================================
elif feature == "Speed Analysis":
    st.markdown("### 🏎️ Speed & Safety Analysis")
    
    if not filtered_df.empty:
        col_s1, col_s2 = st.columns(2)
        
        with col_s1:
            st.markdown("#### Recorded Speed Distribution")
            fig_rs, ax_rs = plt.subplots(figsize=(10, 5))
            plot_hist(ax_rs, filtered_df['Recorded_Speed'].dropna(), "Recorded Speed (km/h)", bins=30, color='#4f83cc')
            st.pyplot(fig_rs, use_container_width=True)
        
        with col_s2:
            st.markdown("#### Fine Amount Distribution")
            fig_f, ax_f = plt.subplots(figsize=(10, 5))
            plot_hist(ax_f, filtered_df['Fine_Amount'].dropna(), "Fine Amount (₹)", bins=30, color='#60a5fa')
            st.pyplot(fig_f, use_container_width=True)
        
        st.markdown("---")
        
        # Scatter: Speed Limit vs Recorded Speed
        st.markdown("#### Speed Limit vs Recorded Speed (Scatter)")
        clean_speed = filtered_df.dropna(subset=['Speed_Limit', 'Recorded_Speed']).copy()
        if not clean_speed.empty:
            fig_sc, ax_sc = plt.subplots(figsize=(12, 6))
            plot_scatter_with_ref(ax_sc, clean_speed['Speed_Limit'], clean_speed['Recorded_Speed'], "Speed Analysis")
            st.pyplot(fig_sc, use_container_width=True)
        else:
            st.info("No speed data available for this filter.")
        
        st.markdown("---")
        
        # Correlation Heatmap
        st.markdown("#### Feature Correlations")
        num_cols = ['Recorded_Speed', 'Speed_Limit', 'Fine_Amount', 'Driver_Age']
        available_cols = [col for col in num_cols if col in clean_speed.columns]
        if available_cols:
            fig_heat, ax_heat = plt.subplots(figsize=(8, 6))
            plot_heatmap(ax_heat, clean_speed[available_cols].dropna(), "Numeric Correlations")
            st.pyplot(fig_heat, use_container_width=True)

# ============================================================================
# PAGE: Trend Analysis
# ============================================================================
elif feature == "Trend Analysis":
    st.markdown("### 📈 Temporal Trends & Patterns")
    
    if not filtered_df.empty:
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            st.markdown("#### Hourly Violation Trend")
            hourly = filtered_df['Hour'].value_counts().sort_index()
            if not hourly.empty:
                fig_h, ax_h = plt.subplots(figsize=(10, 5))
                plot_line(ax_h, hourly.index, hourly.values, "Violations by Hour")
                st.pyplot(fig_h, use_container_width=True)
        
        with col_t2:
            st.markdown("#### Daily Violation Trend")
            day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            daily = filtered_df['Day'].value_counts().reindex(day_order).fillna(0).astype(int)
            if not daily.empty:
                fig_d, ax_d = plt.subplots(figsize=(10, 5))
                plot_bar(ax_d, day_order, daily.values, "Violations by Day")
                st.pyplot(fig_d, use_container_width=True)
        
        st.markdown("---")
        
        # Monthly Trend
        st.markdown("#### Monthly Violation Trend")
        month_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        monthly = filtered_df['Month'].value_counts().reindex(month_order).fillna(0).astype(int)
        if not monthly.empty and monthly.sum() > 0:
            fig_m, ax_m = plt.subplots(figsize=(12, 5))
            plot_line(ax_m, month_order, monthly.values, "Violations by Month")
            st.pyplot(fig_m, use_container_width=True)

# ============================================================================
# PAGE: Weather Risk Analysis
# ============================================================================
elif feature == "Weather Risk Analysis":
    st.markdown("### 🌧️ Environmental Risk Assessment")
    
    if not filtered_df.empty:
        col_w1, col_w2 = st.columns(2)
        
        with col_w1:
            st.markdown("#### Violations by Weather Condition")
            fig_w, ax_w = plt.subplots(figsize=(10, 5))
            plot_count(ax_w, filtered_df['Weather_Condition'], "Weather Conditions")
            st.pyplot(fig_w, use_container_width=True)
        
        with col_w2:
            st.markdown("#### Road Condition Impact")
            fig_r, ax_r = plt.subplots(figsize=(10, 5))
            plot_count(ax_r, filtered_df['Road_Condition'], "Road Conditions")
            st.pyplot(fig_r, use_container_width=True)
        
        st.markdown("---")
        
        # Weather vs Fine Heatmap
        st.markdown("#### Weather & Road Condition Interaction")
        if 'Weather_Condition' in filtered_df.columns and 'Road_Condition' in filtered_df.columns:
            weather_road = filtered_df.groupby(['Weather_Condition', 'Road_Condition']).size().unstack(fill_value=0)
            fig_wr, ax_wr = plt.subplots(figsize=(10, 5))
            sns.heatmap(weather_road, annot=True, fmt='d', cmap='coolwarm', ax=ax_wr, cbar_kws={'label': 'Count'})
            ax_wr.set_title("Weather × Road Condition", color='#333333', fontsize=13, fontweight='bold')
            st.pyplot(fig_wr, use_container_width=True)

# ============================================================================
# PAGE: Location & Map Analysis
# ============================================================================
elif feature == "Location & Map":
    st.markdown("### 🗺️ Geographic Hotspot Analysis")
    
    if not filtered_df.empty:
        # Top Violating States (Horizontal Bar)
        st.markdown("#### Top States by Violations")
        top_states = filtered_df['State'].value_counts().head(10)
        fig_top, ax_top = plt.subplots(figsize=(10, 6))
        plot_barh(ax_top, top_states.index, top_states.values, "Violations by State")
        st.pyplot(fig_top, use_container_width=True)
        
        st.markdown("---")
        
        # Folium Map
        st.markdown("#### Violation Hotspot Map")
        state_coords = {
            "Maharashtra": [19.7515, 75.7139],
            "Delhi": [28.7041, 77.1025],
            "Karnataka": [15.3173, 75.7139],
            "Tamil Nadu": [11.1271, 78.6569],
            "Uttar Pradesh": [26.8467, 80.9462],
            "Gujarat": [22.2587, 71.1924],
            "Rajasthan": [27.0238, 74.2179],
            "West Bengal": [22.9868, 87.8550],
            "Kerala": [10.8505, 76.2711],
            "Telangana": [18.1124, 79.0193],
            "Punjab": [31.1471, 75.3412]
        }
        
        state_counts = filtered_df['State'].value_counts()
        m = folium.Map(location=[20.5937, 78.9629], zoom_start=5, tiles="CartoDB positron")
        
        for state, count in state_counts.items():
            if state in state_coords:
                popup_text = f"<b>{state}</b><br>Violations: {count:,}<br>Fines: ₹{filtered_df[filtered_df['State']==state]['Fine_Amount'].sum():,.0f}"
                folium.CircleMarker(
                    location=state_coords[state],
                    radius=max(5, count / 50),
                    popup=folium.Popup(popup_text, max_width=250),
                    color='#2563eb',
                    fill=True,
                    fill_color='#60a5fa',
                    fill_opacity=0.7,
                    weight=2,
                    tooltip=f"{state}: {count:,}"
                ).add_to(m)
        
        st_folium(m, width="100%", height=600)

# ============================================================================
# PAGE: Data Explorer
# ============================================================================
elif feature == "Data Explorer":
    st.markdown("### 📂 Raw Data View")
    st.dataframe(filtered_df, use_container_width=True)
    
    with st.expander("📊 Dataset Info"):
        st.write(f"**Shape:** {filtered_df.shape[0]} rows × {filtered_df.shape[1]} columns")
        st.write(f"**Memory Usage:** {filtered_df.memory_usage().sum() / 1024**2:.2f} MB")
        st.write("**Missing Values:**")
        st.dataframe(filtered_df.isnull().sum())

# ============================================================================
# PAGE: About
# ============================================================================
elif feature == "About":
    st.markdown("""
    # 🚦 Smart Traffic Violation Analysis Platform
    
    ## Overview
    A comprehensive analytics platform for traffic authorities to detect violation patterns, 
    assess risk, and optimize enforcement strategies.
    
    ## Features
    - **📊 Dashboard:** Real-time KPIs and violation summary
    - **📊 Violation Distribution:** Detailed breakdown by type and payment method
    - **🏎️ Speed Analysis:** Speed limit compliance with scatter plots and correlations
    - **📈 Trend Analysis:** Hourly, daily, monthly violation patterns
    - **🌧️ Weather Risk:** Environmental factors influencing violations
    - **🗺️ Location Analysis:** Geospatial hotspots with interactive map
    - **📂 Data Explorer:** Raw data viewing and stats
    
    ## Visualization Types
    - Count Plots (bar charts for categorical data)
    - Histograms (distributions)
    - Line Charts (time trends)
    - Scatter Plots (relationships)
    - Heatmaps (correlations)
    - Pie/Donut Charts (percentages)
    - Interactive Maps (geographic)
    
    ## Tech Stack
    - **Frontend:** Streamlit
    - **Data:** Pandas, NumPy
    - **Visualization:** Matplotlib, Seaborn, Folium
    
    ## Dataset
    Requires CSV with columns: Violation_ID, Date, Time, Location, Violation_Type, 
    Recorded_Speed, Speed_Limit, Fine_Amount, Driver_Age, Weather_Condition, Road_Condition, etc.
    
    Built with ❤️ for safer roads.
    """)

