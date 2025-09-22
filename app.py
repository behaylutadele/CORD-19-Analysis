import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from data_analysis import CORD19Analyzer
import os

# Page configuration
st.set_page_config(
    page_title="CORD-19 Data Explorer",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 2rem;
        color: #2e86ab;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🔬 CORD-19 Research Dataset Explorer</h1>', 
                unsafe_allow_html=True)
    
    st.write("""
    This interactive dashboard explores the COVID-19 Open Research Dataset (CORD-19), 
    containing metadata about scientific papers related to COVID-19 and coronavirus research.
    """)
    
    # Sidebar
    st.sidebar.title("Navigation")
    section = st.sidebar.radio("Go to:", [
        "Dataset Overview", 
        "Data Exploration", 
        "Visualizations", 
        "Word Analysis",
        "About"
    ])
    
    # File upload
    st.sidebar.markdown("---")
    st.sidebar.header("Data Upload")
    uploaded_file = st.sidebar.file_uploader("Upload metadata.csv", type="csv")
    
    if uploaded_file is not None:
        # Save uploaded file
        with open("data/metadata.csv", "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.sidebar.success("File uploaded successfully!")
    
    # Check if data file exists
    if not os.path.exists("data/metadata.csv"):
        st.warning("""
        ⚠️ Please upload the metadata.csv file using the sidebar uploader.
        You can download it from: https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge
        """)
        return
    
    # Initialize analyzer
    try:
        analyzer = CORD19Analyzer("data/metadata.csv")
        df_clean = analyzer.clean_data()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return
    
    if section == "Dataset Overview":
        show_dataset_overview(analyzer, df_clean)
    
    elif section == "Data Exploration":
        show_data_exploration(analyzer, df_clean)
    
    elif section == "Visualizations":
        show_visualizations(analyzer, df_clean)
    
    elif section == "Word Analysis":
        show_word_analysis(analyzer, df_clean)
    
    elif section == "About":
        show_about_section()

def show_dataset_overview(analyzer, df_clean):
    """Display dataset overview"""
    st.markdown('<h2 class="section-header">📊 Dataset Overview</h2>', 
                unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Papers", f"{analyzer.df.shape[0]:,}")
    
    with col2:
        st.metric("Columns", analyzer.df.shape[1])
    
    with col3:
        st.metric("After Cleaning", f"{df_clean.shape[0]:,}")
    
    # Basic statistics
    st.subheader("Data Summary")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**First 5 Rows:**")
        st.dataframe(analyzer.df.head(10))
    
    with col2:
        st.write("**Column Information:**")
        col_info = pd.DataFrame({
            'Column': analyzer.df.columns,
            'Data Type': analyzer.df.dtypes.values,
            'Non-Null Count': analyzer.df.notnull().sum().values
        })
        st.dataframe(col_info)

def show_data_exploration(analyzer, df_clean):
    """Interactive data exploration"""
    st.markdown('<h2 class="section-header">🔍 Data Exploration</h2>', 
                unsafe_allow_html=True)
    
    # Missing values analysis
    st.subheader("Missing Values Analysis")
    missing_data = analyzer.df.isnull().sum()
    missing_data = missing_data[missing_data > 0].sort_values(ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Columns with Missing Values:**")
        missing_df = pd.DataFrame({
            'Column': missing_data.index,
            'Missing Count': missing_data.values,
            'Missing Percentage': (missing_data.values / len(analyzer.df) * 100).round(2)
        })
        st.dataframe(missing_df)
    
    with col2:
        fig, ax = plt.subplots(figsize=(10, 6))
        missing_data.head(10).plot(kind='bar', ax=ax, color='coral')
        ax.set_title('Top 10 Columns with Missing Values')
        ax.set_ylabel('Missing Count')
        plt.xticks(rotation=45)
        st.pyplot(fig)
    
    # Interactive filters
    st.subheader("Interactive Data Filtering")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_year = int(df_clean['publication_year'].min())
        max_year = int(df_clean['publication_year'].max())
        year_range = st.slider(
            "Publication Year Range",
            min_year, max_year, (2020, max_year)
        )
    
    with col2:
        min_words = int(df_clean['abstract_word_count'].quantile(0.1))
        max_words = int(df_clean['abstract_word_count'].quantile(0.9))
        word_range = st.slider(
            "Abstract Word Count Range",
            min_words, max_words, (min_words, 300)
        )
    
    with col3:
        selected_source = st.selectbox(
            "Data Source",
            ['All'] + df_clean['source_x'].dropna().unique().tolist()[:10]
        )
    
    # Apply filters
    filtered_df = df_clean[
        (df_clean['publication_year'] >= year_range[0]) & 
        (df_clean['publication_year'] <= year_range[1]) &
        (df_clean['abstract_word_count'] >= word_range[0]) & 
        (df_clean['abstract_word_count'] <= word_range[1])
    ]
    
    if selected_source != 'All':
        filtered_df = filtered_df[filtered_df['source_x'] == selected_source]
    
    st.write(f"**Filtered Results:** {len(filtered_df):,} papers")
    st.dataframe(filtered_df[['title', 'publication_year', 'journal', 'abstract_word_count']].head(10))

def show_visualizations(analyzer, df_clean):
    """Display various visualizations"""
    st.markdown('<h2 class="section-header">📈 Data Visualizations</h2>', 
                unsafe_allow_html=True)
    
    # Create tabs for different visualizations
    tab1, tab2, tab3, tab4 = st.tabs([
        "Publication Trends", 
        "Journal Analysis", 
        "Word Distribution", 
        "Source Analysis"
    ])
    
    with tab1:
        st.subheader("Publication Trends Over Time")
        yearly_counts = analyzer.analyze_publications_over_time(df_clean)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(yearly_counts.index, yearly_counts.values, color='steelblue', alpha=0.7)
        ax.set_xlabel('Year')
        ax.set_ylabel('Number of Publications')
        ax.set_title('COVID-19 Research Publications by Year')
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for i, v in enumerate(yearly_counts.values):
            ax.text(yearly_counts.index[i], v + 10, str(v), ha='center', va='bottom')
        
        st.pyplot(fig)
        
        # Show data table
        st.write("**Yearly Publication Counts:**")
        st.dataframe(yearly_counts.reset_index().rename(
            columns={'index': 'Year', 'publication_year': 'Count'}
        ))
    
    with tab2:
        st.subheader("Top Publishing Journals")
        top_n = st.slider("Number of top journals to show", 5, 20, 10)
        top_journals = analyzer.analyze_top_journals(df_clean, top_n=top_n)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.barh(range(len(top_journals)), top_journals.values, color='lightseagreen', alpha=0.7)
        ax.set_yticks(range(len(top_journals)))
        ax.set_yticklabels([journal[:50] + '...' if len(journal) > 50 else journal 
                          for journal in top_journals.index])
        ax.set_xlabel('Number of Publications')
        ax.set_title(f'Top {top_n} Journals Publishing COVID-19 Research')
        ax.grid(axis='x', alpha=0.3)
        
        st.pyplot(fig)
    
    with tab3:
        st.subheader("Abstract Word Count Distribution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Histogram
            word_counts = df_clean['abstract_word_count'][df_clean['abstract_word_count'] > 0]
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.hist(word_counts, bins=50, color='lightcoral', alpha=0.7, edgecolor='black')
            ax.set_xlabel('Word Count')
            ax.set_ylabel('Frequency')
            ax.set_title('Distribution of Abstract Word Counts')
            ax.grid(alpha=0.3)
            st.pyplot(fig)
        
        with col2:
            # Box plot
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.boxplot(word_counts, vert=False)
            ax.set_xlabel('Word Count')
            ax.set_title('Abstract Word Count - Box Plot')
            st.pyplot(fig)
            
            # Statistics
            stats_df = pd.DataFrame({
                'Statistic': ['Mean', 'Median', 'Std Dev', 'Min', 'Max'],
                'Value': [
                    word_counts.mean(), 
                    word_counts.median(), 
                    word_counts.std(), 
                    word_counts.min(), 
                    word_counts.max()
                ]
            })
            st.dataframe(stats_df)
    
    with tab4:
        st.subheader("Data Source Analysis")
        source_counts = df_clean['source_x'].value_counts().head(10)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.pie(source_counts.values, labels=source_counts.index, autopct='%1.1f%%', startangle=90)
        ax.set_title('Top 10 Data Sources')
        st.pyplot(fig)

def show_word_analysis(analyzer, df_clean):
    """Word frequency and word cloud analysis"""
    st.markdown('<h2 class="section-header">📝 Word Analysis</h2>', 
                unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Word Frequency Analysis")
        
        analysis_type = st.radio(
            "Analyze words in:",
            ['Titles', 'Abstracts']
        )
        
        column = 'title' if analysis_type == 'Titles' else 'abstract'
        top_n = st.slider("Number of top words to show", 10, 50, 20)
        
        word_freq = analyzer.analyze_word_frequency(df_clean, column=column, top_n=top_n)
        
        if word_freq:
            words, counts = zip(*word_freq)
            
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.barh(range(len(words)), counts, color='mediumpurple', alpha=0.7)
            ax.set_yticks(range(len(words)))
            ax.set_yticklabels(words)
            ax.set_xlabel('Frequency')
            ax.set_title(f'Top {top_n} Words in {analysis_type}')
            ax.grid(axis='x', alpha=0.3)
            
            st.pyplot(fig)
            
            # Display as table
            freq_df = pd.DataFrame(word_freq, columns=['Word', 'Frequency'])
            st.dataframe(freq_df)
    
    with col2:
        st.subheader("Word Cloud Visualization")
        
        wc_type = st.radio(
            "Generate word cloud for:",
            ['Titles', 'Abstracts'],
            key='wc'
        )
        
        wc_column = 'title' if wc_type == 'Titles' else 'abstract'
        
        if st.button("Generate Word Cloud"):
            with st.spinner("Generating word cloud..."):
                fig = analyzer.generate_wordcloud(df_clean, column=wc_column)
                st.pyplot(fig)

def show_about_section():
    """About section"""
    st.markdown('<h2 class="section-header">ℹ️ About This Project</h2>', 
                unsafe_allow_html=True)
    
    st.write("""
    ## CORD-19 Research Dataset Explorer
    
    This interactive dashboard provides an exploration of the COVID-19 Open Research Dataset (CORD-19), 
    which contains metadata about scientific papers related to COVID-19 and coronavirus research.
    
    ### Features:
    - **Dataset Overview**: Basic statistics and information about the dataset
    - **Data Exploration**: Interactive filtering and missing values analysis
    - **Visualizations**: Various charts showing publication trends and patterns
    - **Word Analysis**: Word frequency analysis and word cloud generation
    
    ### Dataset Information:
    The CORD-19 dataset is a resource of over 1,000,000 scholarly articles, including over 400,000 
    with full text, about COVID-19 and the coronavirus family of viruses.
    
    ### Technical Stack:
    - **Python**: Data analysis and processing
    - **Pandas**: Data manipulation
    - **Matplotlib/Seaborn**: Data visualization
    - **Streamlit**: Interactive web application
    - **WordCloud**: Text visualization
    
    ### Learning Objectives:
    This project demonstrates fundamental data analysis skills including:
    - Data loading and exploration
    - Data cleaning and preprocessing
    - Statistical analysis and visualization
    - Interactive dashboard creation
    - Presentation of data insights
    """)

if __name__ == "__main__":
    main()
