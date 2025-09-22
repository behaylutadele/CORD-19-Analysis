import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from collections import Counter
import re
from datetime import datetime

class CORD19Analyzer:
    def __init__(self, file_path):
        """
        Initialize the analyzer with the dataset path
        """
        self.df = None
        self.file_path = file_path
        self.load_data()
    
    def load_data(self):
        """
        Load and initial data processing
        """
        try:
            self.df = pd.read_csv(self.file_path)
            print(f"Dataset loaded successfully: {self.df.shape[0]} rows, {self.df.shape[1]} columns")
        except FileNotFoundError:
            print("File not found. Please check the file path.")
            return None
        
        # Basic data info
        print("\nDataset Info:")
        print(self.df.info())
        
        return self.df
    
    def basic_exploration(self):
        """
        Perform basic data exploration
        """
        exploration_results = {}
        
        # Basic statistics
        exploration_results['shape'] = self.df.shape
        exploration_results['columns'] = self.df.columns.tolist()
        exploration_results['dtypes'] = self.df.dtypes.value_counts().to_dict()
        
        # Missing values analysis
        missing_data = self.df.isnull().sum()
        exploration_results['missing_values'] = missing_data[missing_data > 0].sort_values(ascending=False)
        
        # Sample data
        exploration_results['sample'] = self.df.head()
        
        return exploration_results
    
    def clean_data(self):
        """
        Clean and preprocess the data
        """
        # Create a copy for cleaning
        df_clean = self.df.copy()
        
        # Handle publication dates
        df_clean['publish_time'] = pd.to_datetime(df_clean['publish_time'], errors='coerce')
        df_clean['publication_year'] = df_clean['publish_time'].dt.year
        
        # Fill missing years with mode
        mode_year = df_clean['publication_year'].mode()[0]
        df_clean['publication_year'] = df_clean['publication_year'].fillna(mode_year)
        
        # Create abstract word count
        df_clean['abstract_word_count'] = df_clean['abstract'].apply(
            lambda x: len(str(x).split()) if pd.notnull(x) else 0
        )
        
        # Clean journal names
        df_clean['journal_clean'] = df_clean['journal'].str.lower().str.strip()
        
        # Remove papers with no title
        df_clean = df_clean[df_clean['title'].notnull()]
        
        print(f"Data cleaned. Remaining rows: {df_clean.shape[0]}")
        
        return df_clean
    
    def analyze_publications_over_time(self, df_clean):
        """
        Analyze publication trends over time
        """
        # Publications by year
        yearly_counts = df_clean['publication_year'].value_counts().sort_index()
        
        # Filter for recent years (2010 onwards)
        yearly_counts = yearly_counts[yearly_counts.index >= 2010]
        
        return yearly_counts
    
    def analyze_top_journals(self, df_clean, top_n=15):
        """
        Analyze top publishing journals
        """
        # Get top journals
        top_journals = df_clean['journal_clean'].value_counts().head(top_n)
        
        return top_journals
    
    def analyze_word_frequency(self, df_clean, column='title', top_n=20):
        """
        Analyze word frequency in titles or abstracts
        """
        # Combine all text
        all_text = ' '.join(df_clean[column].dropna().astype(str))
        
        # Clean text and get word frequencies
        words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
        word_freq = Counter(words)
        
        # Remove common stop words
        stop_words = {'the', 'and', 'of', 'in', 'to', 'a', 'for', 'with', 'on', 'by', 
                     'as', 'an', 'from', 'that', 'this', 'is', 'are', 'was', 'were', 'be'}
        
        filtered_words = {word: count for word, count in word_freq.items() 
                         if word not in stop_words}
        
        return Counter(filtered_words).most_common(top_n)
    
    def create_visualizations(self, df_clean):
        """
        Create all visualizations
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('CORD-19 Dataset Analysis', fontsize=16, fontweight='bold')
        
        # 1. Publications over time
        yearly_counts = self.analyze_publications_over_time(df_clean)
        axes[0, 0].bar(yearly_counts.index, yearly_counts.values, color='skyblue')
        axes[0, 0].set_title('Publications by Year')
        axes[0, 0].set_xlabel('Year')
        axes[0, 0].set_ylabel('Number of Publications')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 2. Top journals
        top_journals = self.analyze_top_journals(df_clean)
        axes[0, 1].barh(range(len(top_journals)), top_journals.values, color='lightgreen')
        axes[0, 1].set_yticks(range(len(top_journals)))
        axes[0, 1].set_yticklabels([journal[:40] + '...' if len(journal) > 40 else journal 
                                  for journal in top_journals.index])
        axes[0, 1].set_title('Top Publishing Journals')
        axes[0, 1].set_xlabel('Number of Publications')
        
        # 3. Word frequency
        word_freq = self.analyze_word_frequency(df_clean)
        words, counts = zip(*word_freq)
        axes[1, 0].bar(range(len(words)), counts, color='lightcoral')
        axes[1, 0].set_xticks(range(len(words)))
        axes[1, 0].set_xticklabels(words, rotation=45, ha='right')
        axes[1, 0].set_title('Most Frequent Words in Titles')
        axes[1, 0].set_ylabel('Frequency')
        
        # 4. Abstract word count distribution
        word_counts = df_clean['abstract_word_count'][df_clean['abstract_word_count'] > 0]
        axes[1, 1].hist(word_counts, bins=50, color='gold', alpha=0.7)
        axes[1, 1].set_title('Distribution of Abstract Word Counts')
        axes[1, 1].set_xlabel('Word Count')
        axes[1, 1].set_ylabel('Frequency')
        
        plt.tight_layout()
        return fig
    
    def generate_wordcloud(self, df_clean, column='title'):
        """
        Generate a word cloud from titles or abstracts
        """
        text = ' '.join(df_clean[column].dropna().astype(str))
        
        wordcloud = WordCloud(
            width=800, 
            height=400, 
            background_color='white',
            max_words=100,
            colormap='viridis'
        ).generate(text)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title(f'Word Cloud: {column.capitalize()}', fontsize=16, fontweight='bold')
        
        return fig

def main():
    """
    Main function to run the analysis
    """
    # Initialize analyzer
    analyzer = CORD19Analyzer('data/metadata.csv')
    
    if analyzer.df is not None:
        # Basic exploration
        exploration = analyzer.basic_exploration()
        print("\nBasic Exploration Results:")
        print(f"Dataset shape: {exploration['shape']}")
        print(f"Missing values:\n{exploration['missing_values'].head()}")
        
        # Clean data
        df_clean = analyzer.clean_data()
        
        # Generate visualizations
        analyzer.create_visualizations(df_clean)
        plt.show()
        
        # Generate word cloud
        analyzer.generate_wordcloud(df_clean)
        plt.show()

if __name__ == "__main__":
    main()
