# import streamlit as st
# import pandas as pd
# import plotly.express as px
# from pathlib import Path
# from pandas.api.types import is_numeric_dtype
# from pycountry_convert import country_name_to_country_alpha3

# # --- PAGE CONFIGURATION ---
# st.set_page_config(page_title="IT Industry Data Explorer", page_icon="💻", layout="wide")

# # --- HELPER FUNCTIONS ---
# @st.cache_data
# def load_data(file_path):
#     """Loads and cleans the survey data, now robustly handling errors."""
#     try:
#         # THE FINAL FIX: Add on_bad_lines='warn' to skip broken rows instead of crashing.
#         df = pd.read_csv(file_path, sep='\t', on_bad_lines='warn', low_memory=False)
        
#         # Data cleaning logic
#         df = df.rename(columns={'YearsCodePro': 'YearsCode'})
#         df['ConvertedCompYearly'] = pd.to_numeric(df['ConvertedCompYearly'], errors='coerce')
#         df['YearsCode'] = pd.to_numeric(df['YearsCode'], errors='coerce')
#         df = df.dropna(subset=['ConvertedCompYearly', 'YearsCode', 'Country'])
#         return df
#     except Exception as e:
#         st.error(f"A critical error occurred while processing the data: {e}")
#         return None

# # (The rest of the code remains exactly the same as the previous version)
# def get_iso_alpha3(country_name):
#     try: return country_name_to_country_alpha3(country_name)
#     except: return None

# if 'df' not in st.session_state: st.session_state.df = None

# with st.sidebar:
#     st.title("💻 IT Industry Data Explorer")
#     st.write("Analyze trends from the Industry Survey Data.")
#     st.header("1. Load Data")
#     st.write("Upload a CSV/TSV or use the sample survey data.")
    
#     uploaded_file = st.file_uploader("Choose a file", type=["csv", "tsv", "txt"])
#     if uploaded_file is not None:
#         df = load_data(uploaded_file)
#         if df is not None:
#             st.session_state.df = df
#             st.success("File processed successfully!")

#     if st.button("Load Sample Survey Data"):
#         sample_data_path = Path(__file__).parent / "Industry_Survey_Data.csv" 
#         df = load_data(sample_data_path)
#         if df is not None:
#             st.session_state.df = df
#             st.success("Sample data loaded successfully!")

#     if st.session_state.df is not None:
#         st.markdown("---")
#         st.write("### Data Overview")
#         st.write(f"**Rows:** {st.session_state.df.shape[0]}")
#         st.write(f"**Columns:** {st.session_state.df.shape[1]}")
    
#     st.markdown("---")
#     st.header("2. Choose Analysis Page")
#     page = st.radio("Go to", ["Home", "Data Explorer", "Technology Analysis", "Career Analysis", "Global Insights"])

# if page == "Home":
#     st.header("Welcome!")
#     st.markdown("""
#     This application is an interactive tool to analyze and visualize insights from Industry Survey Data.
#     **How to use:** Load data from the sidebar to activate the analysis pages.
#     """)
# elif st.session_state.df is None:
#     st.warning("Please load data in the sidebar to get started.")
# elif page == "Data Explorer":
#     st.title("📊 Data Explorer")
#     df = st.session_state.df.copy()
#     st.dataframe(df)
# elif page == "Technology Analysis":
#     st.title("📈 Technology Analysis")
#     df = st.session_state.df
#     if 'LanguageHaveWorkedWith' in df.columns:
#         tech_counts = df['LanguageHaveWorkedWith'].str.split(';', expand=True).stack().value_counts()
#         tech_df = pd.DataFrame({'Technology': tech_counts.index, 'Count': tech_counts.values})
#         fig = px.bar(tech_df.head(15), x='Count', y='Technology', orientation='h', title='Top 15 Most Used Technologies')
#         fig.update_layout(yaxis={'categoryorder': 'total ascending'})
#         st.plotly_chart(fig, use_container_width=True)
#     else:
#         st.error("Column 'LanguageHaveWorkedWith' not found.")
# elif page == "Career Analysis":
#     st.title("📉 Career Analysis")
#     df = st.session_state.df
#     df_filtered = df[(df['ConvertedCompYearly'] < 400000) & (df['ConvertedCompYearly'] > 1000)]
#     df_filtered = df_filtered[df_filtered['YearsCode'] <= 40]
#     fig_scatter = px.scatter(df_filtered, x='YearsCode', y='ConvertedCompYearly', color='DevType', hover_name='Country', title='Salary vs. Years of Professional Coding Experience', labels={'YearsCode': 'Years of Professional Coding Experience', 'ConvertedCompYearly': 'Annual Salary (USD)'})
#     st.plotly_chart(fig_scatter, use_container_width=True)
# elif page == "Global Insights":
#     st.title("🌍 Global Insights")
#     df = st.session_state.df
#     country_stats = df.groupby('Country').agg(RespondentCount=('ResponseId', 'count'), MedianSalary=('ConvertedCompYearly', 'median')).reset_index()
#     country_stats['iso_alpha'] = country_stats['Country'].apply(get_iso_alpha3)
#     country_stats = country_stats.dropna(subset=['iso_alpha'])
#     map_type = st.selectbox("Select Map to Display", ["Median Annual Salary (USD)", "Number of Survey Respondents"])
#     if map_type == "Median Annual Salary (USD)":
#         fig = px.choropleth(country_stats, locations="iso_alpha", color="MedianSalary", hover_name="Country", color_continuous_scale=px.colors.sequential.Plasma, title="Global Median Developer Salaries")
#     else:
#         fig = px.choropleth(country_stats, locations="iso_alpha", color="RespondentCount", hover_name="Country", color_continuous_scale=px.colors.sequential.Viridis, title="Global Distribution of Survey Respondents")
#     st.plotly_chart(fig, use_container_width=True)


import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
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
    """Loads the clean, pre-processed IT Industry CSV file."""
    try:
        df = pd.read_csv(file_path)
        # Rename columns for consistency in our app
        df = df.rename(columns={'YearsCodePro': 'YearsCode'})
        # Ensure data types are correct for plotting
        df['ConvertedCompYearly'] = pd.to_numeric(df['ConvertedCompYearly'], errors='coerce')
        # Handle non-numeric values like "Less than 1 year"
        df['YearsCode'] = pd.to_numeric(df['YearsCode'], errors='coerce')
        # Remove any rows with missing data in key columns to prevent errors
        df = df.dropna(subset=['ConvertedCompYearly', 'YearsCode', 'Country', 'LanguageHaveWorkedWith', 'DevType'])
        return df
    except FileNotFoundError:
        st.error(f"FATAL ERROR: The data file was not found. Please make sure the file named 'IT_Industry_Data.csv' is in the same folder as your app.py script.")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred while processing the data: {e}")
        return None

def get_iso_alpha3(country_name):
    """Converts country name to ISO alpha-3 code for mapping."""
    try:
        if country_name == 'United Kingdom of Great Britain and Northern Ireland':
            return 'GBR'
        if country_name == 'Russian Federation':
            return 'RUS'
        return country_name_to_country_alpha3(country_name)
    except:
        return None

# --- SESSION STATE INITIALIZATION ---
if 'df' not in st.session_state:
    st.session_state.df = None

# --- SIDEBAR ---
with st.sidebar:
    st.title("💻 IT Industry Data Explorer")
    st.write("An interactive dashboard analyzing IT Industry Survey Data.")
    
    st.header("Load Data")
    
    # Simplified to one button to eliminate all other sources of error
    if st.button("Load Survey Data"):
        # This filename is now hardcoded to match YOUR specific filename
        sample_data_path = Path(__file__).parent / "IT_Industry_Data.csv"
        
        df = load_data(sample_data_path)
        if df is not None:
            st.session_state.df = df
            st.success("Data loaded successfully!")

    if st.session_state.df is not None:
        st.markdown("---")
        st.write("### Data Overview")
        st.write(f"**Rows:** {st.session_state.df.shape[0]}")
        st.write(f"**Columns:** {st.session_state.df.shape[1]}")
    
    st.markdown("---")
    st.header("Choose Analysis Page")
    page = st.radio("Go to", ["Home", "Data Explorer", "Technology Analysis", "Career Analysis", "Global Insights"])

# --- MAIN PAGE CONTENT ---
if page == "Home":
    st.header("Welcome!")
    st.markdown("""
    This application analyzes trends from IT Industry Survey Data.
    **To begin, click the "Load Survey Data" button in the sidebar.** This will load a pre-cleaned dataset of professional responses and activate the analysis pages.
    """)

elif st.session_state.df is None:
    st.warning("Please load the data in the sidebar to get started.")

elif page == "Data Explorer":
    st.title("📊 Data Explorer")
    st.header("Explore the Dataset")
    
    df_explorer = st.session_state.df.copy()

    # ADDED FEATURE: Search by Employee Name
    st.subheader("Search by Employee Name")
    search_name = st.text_input("Enter a name to search for:")
    
    if search_name:
        df_explorer = df_explorer[df_explorer['EmployeeName'].str.contains(search_name, case=False, na=False)]

    st.dataframe(df_explorer)

elif page == "Technology Analysis":
    st.title("📈 Technology Analysis")
    st.header("Most Popular Technologies")
    df = st.session_state.df
    tech_counts = df['LanguageHaveWorkedWith'].str.split(';', expand=True).stack().value_counts()
    tech_df = pd.DataFrame({'Technology': tech_counts.index, 'Count': tech_counts.values})
    fig = px.bar(tech_df.head(15), x='Count', y='Technology', orientation='h', title='Top 15 Most Used Technologies')
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

elif page == "Career Analysis":
    st.title("📉 Career Analysis")
    st.header("Experience vs. Compensation")
    df = st.session_state.df
    # Filter for better visualization
    df_filtered = df[(df['ConvertedCompYearly'] < 400000) & (df['ConvertedCompYearly'] > 1000)]
    df_filtered = df_filtered[pd.to_numeric(df_filtered['YearsCode'], errors='coerce') <= 40]
    fig_scatter = px.scatter(df_filtered, x='YearsCode', y='ConvertedCompYearly', color='DevType',
                             hover_name='EmployeeName', title='Salary vs. Years of Professional Coding Experience',
                             labels={'YearsCode': 'Years of Professional Coding Experience', 'ConvertedCompYearly': 'Annual Salary (USD)'})
    st.plotly_chart(fig, use_container_width=True)

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





