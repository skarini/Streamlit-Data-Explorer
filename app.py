import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from pandas.api.types import is_numeric_dtype
from pycountry_convert import country_name_to_country_alpha3

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="IT Industry Data Explorer",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- HELPER FUNCTIONS ---
@st.cache_data
def load_data(file_path):
    """Loads and cleans the Stack Overflow survey data."""
    try:
        # THE CRITICAL FIX: Specify the separator as a tab ('\t')
        df = pd.read_csv(file_path, sep='\t', low_memory=False)
        
        # The rest of the cleaning logic
        df = df.rename(columns={'YearsCodePro': 'YearsCode'})
        df['ConvertedCompYearly'] = pd.to_numeric(df['ConvertedCompYearly'], errors='coerce')
        df['YearsCode'] = pd.to_numeric(df['YearsCode'], errors='coerce')
        df = df.dropna(subset=['ConvertedCompYearly', 'YearsCode', 'Country'])
        return df
    except Exception as e:
        st.error(f"Error processing the data: {e}")
        return None

def get_iso_alpha3(country_name):
    """Converts country name to ISO alpha-3 code for mapping."""
    try:
        return country_name_to_country_alpha3(country_name)
    except:
        return None

# --- SESSION STATE INITIALIZATION ---
if 'df' not in st.session_state:
    st.session_state.df = None

# --- SIDEBAR ---
with st.sidebar:
    st.title("💻 IT Industry Data Explorer")
    st.write("Analyze trends from the Industry Survey Data.")
    
    st.header("1. Load Data")
    st.write("Upload a CSV/TSV or use the sample survey data.")
    
    # The uploader will still work because it passes the file object, not the name
    uploaded_file = st.file_uploader("Choose a file", type=["csv", "tsv", "txt"])
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        if df is not None:
            st.session_state.df = df
            st.success("File processed successfully!")

    if st.button("Load Sample Survey Data"):
        # This line uses your specific filename
        sample_data_path = Path(__file__).parent / "Industry_Survey_Data.csv" 
        
        df = load_data(sample_data_path)
        if df is not None:
            st.session_state.df = df
            st.success("Sample data loaded successfully!")

    if st.session_state.df is not None:
        st.markdown("---")
        st.write("### Data Overview")
        st.write(f"**Rows:** {st.session_state.df.shape[0]}")
        st.write(f"**Columns:** {st.session_state.df.shape[1]}")
    
    st.markdown("---")
    st.header("2. Choose Analysis Page")
    page = st.radio("Go to", ["Home", "Data Explorer", "Technology Analysis", "Career Analysis", "Global Insights"])

# --- MAIN PAGE CONTENT ---
# (The rest of the code is exactly the same and does not need to be changed)
if page == "Home":
    st.header("Welcome!")
    st.markdown("""
    This application is an interactive tool to analyze and visualize insights from Industry Survey Data.
    **How to use:** Load data from the sidebar to activate the analysis pages.
    """)

elif st.session_state.df is None:
    st.warning("Please load data in the sidebar to get started.")

elif page == "Data Explorer":
    st.title("📊 Data Explorer")
    st.header("Explore and Filter the Dataset")
    
    df = st.session_state.df.copy()
    
    filter_container = st.container()
    with filter_container:
        st.markdown("#### Filter Data")
        cols = st.columns(4)
        for i, col in enumerate(df.columns[:12]):
            with cols[i % 4]:
                if is_numeric_dtype(df[col]):
                    min_val, max_val = float(df[col].min()), float(df[col].max())
                    if min_val < max_val:
                        filter_val = st.slider(f"Filter {col}", min_val, max_val, (min_val, max_val))
                        df = df[df[col].between(filter_val[0], filter_val[1])]
                else:
                    unique_vals = df[col].dropna().unique()
                    if len(unique_vals) > 1 and len(unique_vals) < 50:
                        filter_val = st.multiselect(f"Filter {col}", unique_vals, default=unique_vals)
                        df = df[df[col].isin(filter_val)]
    
    st.dataframe(df)
    st.markdown("---")
    st.header("Dataset Summary")
    st.write(df.describe())

elif page == "Technology Analysis":
    st.title("📈 Technology Analysis")
    st.header("Most Popular Technologies")
    
    df = st.session_state.df
    if 'LanguageHaveWorkedWith' in df.columns:
        tech_counts = df['LanguageHaveWorkedWith'].str.split(';', expand=True).stack().value_counts()
        tech_df = pd.DataFrame({'Technology': tech_counts.index, 'Count': tech_counts.values})
        
        fig = px.bar(tech_df.head(15), x='Count', y='Technology', orientation='h', title='Top 15 Most Used Technologies')
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Column 'LanguageHaveWorkedWith' not found.")

elif page == "Career Analysis":
    st.title("📉 Career Analysis")
    st.header("Experience vs. Compensation")
    
    df = st.session_state.df
    df_filtered = df[(df['ConvertedCompYearly'] < 400000) & (df['ConvertedCompYearly'] > 1000)]
    df_filtered = df_filtered[df_filtered['YearsCode'] <= 40]

    fig_scatter = px.scatter(df_filtered, x='YearsCode', y='ConvertedCompYearly', color='DevType',
                             hover_name='Country', title='Salary vs. Years of Professional Coding Experience',
                             labels={'YearsCode': 'Years of Professional Coding Experience', 'ConvertedCompYearly': 'Annual Salary (USD)'})
    st.plotly_chart(fig_scatter, use_container_width=True)

elif page == "Global Insights":
    st.title("🌍 Global Insights")
    st.header("Global Developer Distribution and Salaries")

    df = st.session_state.df
    country_stats = df.groupby('Country').agg(
        RespondentCount=('ResponseId', 'count'),
        MedianSalary=('ConvertedCompYearly', 'median')
    ).reset_index()

    country_stats['iso_alpha'] = country_stats['Country'].apply(get_iso_alpha3)
    country_stats = country_stats.dropna(subset=['iso_alpha'])

    map_type = st.selectbox("Select Map to Display", ["Median Annual Salary (USD)", "Number of Survey Respondents"])
    if map_type == "Median Annual Salary (USD)":
        fig = px.choropleth(country_stats, locations="iso_alpha", color="MedianSalary",
                            hover_name="Country", color_continuous_scale=px.colors.sequential.Plasma,
                            title="Global Median Developer Salaries")
    else:
        fig = px.choropleth(country_stats, locations="iso_alpha", color="RespondentCount",
                            hover_name="Country", color_continuous_scale=px.colors.sequential.Viridis,
                            title="Global Distribution of Survey Respondents")
    
    st.plotly_chart(fig, use_container_width=True)
