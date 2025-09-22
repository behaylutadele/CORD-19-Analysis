# CORD-19 Research Dataset Analysis

## Project Overview
This project provides a comprehensive analysis of the CORD-19 research dataset with an interactive Streamlit dashboard for exploring COVID-19 research papers metadata.
## Features
- **Data Exploration**: Basic statistics, missing values analysis, and data filtering
- **Visualizations**: Publication trends, journal analysis, word distributions
- **Interactive Dashboard**: Streamlit web application with filtering capabilities
- **Word Analysis**: Frequency analysis and word cloud generation

## Installation

1. Clone the repository:
```bash
git clone https://github.com/behaylutadele/CORD-19-Analysis/tree/main
cd CORD-19-Analysis

2. Install required packages:

```bash
pip install -r requirements.txt
```

3. Download the dataset from Kaggle:
   · Visit: https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge
   · Download metadata.csv
   · Place it in the data/ folder

Usage

Run the Streamlit Application:

```bash
streamlit run app.py
```

Run Individual Analysis:

```bash
python data_analysis.py
```

Project Structure

```
CORD-19-Analysis/
├── app.py                 # Main Streamlit application
├── data_analysis.py       # Data analysis functions
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
└── data/
    └── metadata.csv      # Dataset file
```

Key Findings

Publication Trends

· Rapid increase in COVID-19 research publications starting 2020
· Peak publication years and monthly trends

Journal Analysis

· Top journals publishing COVID-19 research
· Distribution across different publishers

Text Analysis

· Most frequent words in titles and abstracts
· Word clouds showing research focus areas

Technologies Used

· Python 3.7+
· Pandas (Data manipulation)
· Matplotlib/Seaborn (Visualization)
· Streamlit (Web application)
· WordCloud (Text visualization)

Author

Behaylu Tadele

License

This project is for educational purposes as part of the Frameworks assignment.

```

## 5. How to Run the Project

### Step 1: Setup Environment
```bash
# Create and activate virtual environment (optional but recommended)
python -m venv cord19_env
source cord19_env/bin/activate  # On Windows: cord19_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

Step 2: Download Data

1. Go to https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge
2. Download metadata.csv
3. Create a data folder and place the file there

Step 3: Run the Application

```bash
streamlit run app.py
```

Step 4: Explore the Analysis

```bash
python data_analysis.py
```

