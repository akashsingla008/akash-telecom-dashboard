import streamlit as st
import pandas as pd
import os
import glob
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import base64
import io
import re
import json
import sys
import zipfile
import subprocess
import tempfile
from typing import Dict, List, Any, Optional

# Import the TMF717Converter class from the csv_to_tmf717.py script
try:
    from csv_to_tmf717 import TMF717Converter
    TMF717_AVAILABLE = True
except ImportError:
    TMF717_AVAILABLE = False
    st.warning("csv_to_tmf717.py not found in the current directory. TMF717 conversion will use command line execution.")

# Set page config (must be the first Streamlit command)
st.set_page_config(
    page_title="Telecom Customer Data Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def add_download_button(df, button_text='Download CSV', filename='data.csv'):
    """
    Adds a download button to download a dataframe as CSV without the index column
    """
    # Create a CSV string from dataframe without the index
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_str = csv_buffer.getvalue()
    
    # Encode the CSV string as base64
    b64 = base64.b64encode(csv_str.encode()).decode()
    
    # Create download link
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}" class="btn">⬇️ {button_text}</a>'
    
    # Display the link
    st.markdown(href, unsafe_allow_html=True)

# Function to add a download button for JSON data
def add_json_download_button(json_data, button_text='Download JSON', filename='data.json'):
    """
    Adds a download button for JSON data
    """
    # Convert to JSON string
    json_str = json.dumps(json_data, indent=2)
    
    # Encode as base64
    b64 = base64.b64encode(json_str.encode()).decode()
    
    # Create download link
    href = f'<a href="data:file/json;base64,{b64}" download="{filename}" class="btn">⬇️ {button_text}</a>'
    
    # Display the link
    st.markdown(href, unsafe_allow_html=True)

# Function to format customer insight text
def format_insight_text(text):
    """
    Enhanced formatting for customer insight text with more comprehensive pattern matching
    """
    if not text:
        return ""
    
    # First apply specific pattern replacements for common issues
    patterns = [
        # Format sections related to CLTV
        ("CLTV)", "CLTV) "),
        ("CLTV)shows", "CLTV) shows"),
        ("CLTV ", "CLTV "),
        
        # Format churn risk sections
        ("showsmoderate", "shows moderate"),
        ("churnrisk", "churn risk"),
        ("Score:", "Score: "),
        
        # Fix run-together words
        ("despitehaving", "despite having"),
        ("noimmediateissues", "no immediate issues"),
        ("Themoderate", "The moderate"),
        ("satisfactionscore", "satisfaction score"),
        ("andaverage", "and average"),
        ("complaints(", "complaints ("),
        ("indicatepotential", "indicate potential"),
        ("dissatisfaction", "dissatisfaction "),
        ("withvalue", "with value"),
        ("receivedfor", "received for"),
        ("forthe", "for the"),
        ("planincluding", "plan including"),
        ("datadownload", "data download"),
        ("minutesand", "minutes and"),
        ("featurelimitations", "feature limitations"),
        
        # Fix spacing around punctuation
        (".The", ". The"),
        (").", "). "),
        (".).", ". "),
        (";", "; "),
    ]
    
    # Apply all specific patterns
    for old, new in patterns:
        text = text.replace(old, new)
    
    # Apply regular expressions for more general patterns
    
    # Add space after closing parenthesis when followed by a letter
    text = re.sub(r'\)([a-zA-Z])', r') \1', text)
    
    # Add space between number and opening parenthesis
    text = re.sub(r'(\d)\(', r'\1 (', text)
    
    # Add space between number and GB
    text = re.sub(r'(\d)GB', r'\1 GB', text)
    
    # Fix spacing around $/currencies
    text = re.sub(r'\$(\d)', r'$ \1', text)
    
    # Add space after commas if followed by a non-space
    text = re.sub(r',([^\s])', r', \1', text)
    
    # Clean up any double spaces that might have been introduced
    text = re.sub(r'\s{2,}', ' ', text)
    
    return text

# Function to extract timestamp from filename
def extract_timestamp_string(filename):
    """Extract the timestamp string from filename"""
    try:
        # Extract timestamp part (format: YYYYMMDD_HHMMSS)
        timestamp_str = filename.split('_')[-1].split('.')[0]
        return timestamp_str
    except:
        return None

# Function to extract formatted timestamp for display
def extract_timestamp(filename):
    """Extract and format the timestamp from filename for display"""
    try:
        # Extract timestamp part
        timestamp_str = extract_timestamp_string(filename)
        if timestamp_str:
            # Parse and reformat
            timestamp_dt = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
            return timestamp_dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        pass
    return "Unknown"

# Define function to list matching CSV files in the output directory
def get_matching_csv_files(directory='output'):
    """
    Get all CSV files in the specified directory where records and insights timestamps match.
    Return them sorted by date (newest first).
    """
    st.sidebar.write(f"Scanning for files in: {os.path.abspath(directory)}")
    
    if not os.path.exists(directory):
        os.makedirs(directory)
        return []
    
    # Get all records and insights files
    records_files = glob.glob(os.path.join(directory, 'telecom_customer_records_*.csv'))
    insights_files = glob.glob(os.path.join(directory, 'telecom_customer_insights_*.csv'))
    
    # Debug info
    st.sidebar.write(f"Found {len(records_files)} record files and {len(insights_files)} insight files")
    
    # Build a dict of insights files by timestamp
    insights_by_timestamp = {}
    for insights_file in insights_files:
        timestamp = extract_timestamp_string(insights_file)
        if timestamp:
            insights_by_timestamp[timestamp] = insights_file
    
    # Filter records files to only those with matching insights
    matched_pairs = []
    for records_file in records_files:
        timestamp = extract_timestamp_string(records_file)
        if timestamp and timestamp in insights_by_timestamp:
            matched_pairs.append({
                'timestamp': timestamp,
                'records_file': records_file,
                'insights_file': insights_by_timestamp[timestamp],
                'display_time': extract_timestamp(records_file)
            })
    
    # Sort by timestamp (newest first)
    matched_pairs = sorted(matched_pairs, key=lambda x: x['timestamp'], reverse=True)
    
    # Debug matched pairs
    st.sidebar.write(f"Found {len(matched_pairs)} matching file pairs")
    
    return matched_pairs

# Load data function
@st.cache_data(ttl=60)  # Cache data for 1 minute only
def load_data(file_path):
    """Load CSV data with appropriate types"""
    if not os.path.exists(file_path):
        return None
    
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        st.error(f"Error loading file {file_path}: {str(e)}")
        return None

# Display basic statistics for the records data
def display_statistics(df):
    """Display key statistics about the telecom customer data"""
    if df is None or df.empty:
        st.warning("No data available for statistics")
        return
    
    st.subheader("Key Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    # Count by churn status
    churn_counts = df['Churn Status'].value_counts()
    col1.metric("Total Customers", len(df))
    if 'Churned' in churn_counts:
        col2.metric("Churned Customers", churn_counts['Churned'])
    if 'At Risk' in churn_counts:
        col3.metric("At-Risk Customers", churn_counts.get('At Risk', 0))
    
    # Additional metrics in a second row
    col1, col2, col3 = st.columns(3)
    
    # Average churn score
    avg_churn_score = df['Churn Score'].mean()
    col1.metric("Avg. Churn Score", f"{avg_churn_score:.1f}")
    
    # Average CLTV
    avg_cltv = df['CLTV'].mean()
    col2.metric("Avg. Customer Lifetime Value", f"${avg_cltv:.2f}")
    
    # Average satisfaction
    avg_satisfaction = df['Satisfaction Score (Out of 5)'].mean()
    col3.metric("Avg. Satisfaction Score", f"{avg_satisfaction:.1f}/5")

# Function to get TMF717 JSON for a customer
def get_customer_tmf717_json(df, customer_id):
    """
    Get TMF717 JSON for a specific customer using the TMF717Converter
    or by running the csv_to_tmf717.py script
    """
    if TMF717_AVAILABLE:
        # Create a single-row dataframe for the customer
        customer_df = df[df["Customer Billing Account.CustomerBillingAccount.ID"] == customer_id]
        
        if customer_df.empty:
            return None
        
        # Create a temporary CSV with just this customer
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w', newline='') as temp_csv:
            customer_df.to_csv(temp_csv.name, index=False)
            temp_csv_path = temp_csv.name
        
        # Create temp directory for output
        temp_output_dir = tempfile.mkdtemp()
        
        # Create a converter and process the single-customer file
        converter = TMF717Converter(temp_csv_path, temp_output_dir)
        converter.process_file()
        
        # Read the generated JSON file
        clean_id = ''.join(c if c.isalnum() else '_' for c in str(customer_id))
        json_file_path = os.path.join(temp_output_dir, f"{clean_id}.json")
        
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as f:
                tmf717_json = json.load(f)
                
            # Clean up temp files
            os.remove(temp_csv_path)
            os.remove(json_file_path)
            os.rmdir(temp_output_dir)
            
            return tmf717_json
    else:
        # Fall back to running the script via command line
        # Create a temporary CSV with just this customer
        customer_df = df[df["Customer Billing Account.CustomerBillingAccount.ID"] == customer_id]
        
        if customer_df.empty:
            return None
        
        # Create a temporary CSV with just this customer
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w', newline='') as temp_csv:
            customer_df.to_csv(temp_csv.name, index=False)
            temp_csv_path = temp_csv.name
        
        # Create temp directory for output
        temp_output_dir = tempfile.mkdtemp()
        
        # Run the csv_to_tmf717.py script on this file
        try:
            subprocess.run(
                [sys.executable, "csv_to_tmf717.py", temp_csv_path, temp_output_dir],
                check=True,
                capture_output=True,
                text=True
            )
            
            # Read the generated JSON file
            clean_id = ''.join(c if c.isalnum() else '_' for c in str(customer_id))
            json_file_path = os.path.join(temp_output_dir, f"{clean_id}.json")
            
            if os.path.exists(json_file_path):
                with open(json_file_path, 'r') as f:
                    tmf717_json = json.load(f)
                    
                # Clean up temp files
                os.remove(temp_csv_path)
                os.remove(json_file_path)
                os.rmdir(temp_output_dir)
                
                return tmf717_json
        except Exception as e:
            st.error(f"Error running csv_to_tmf717.py: {str(e)}")
            
            # Clean up temp files
            if os.path.exists(temp_csv_path):
                os.remove(temp_csv_path)
            if os.path.exists(temp_output_dir):
                for file in os.listdir(temp_output_dir):
                    os.remove(os.path.join(temp_output_dir, file))
                os.rmdir(temp_output_dir)
    
    return None

# Display customer TMF717 JSON
def display_customer_tmf717(df, customer_id=None):
    """Display TMF717 JSON for a specific customer or let user select one"""
    if df is None or df.empty:
        st.warning("No customer data available for TMF717 conversion")
        return
    
    st.subheader("TMF717 Customer 360 JSON")
    
    # Allow selection of a specific customer if not provided
    if customer_id is None:
        customer_ids = df["Customer Billing Account.CustomerBillingAccount.ID"].tolist()
        customer_id = st.selectbox("Select a customer:", customer_ids)
    
    if customer_id:
        # Show loading message
        with st.spinner(f"Generating TMF717 JSON for customer {customer_id}..."):
            # Get TMF717 JSON for this customer
            tmf717_json = get_customer_tmf717_json(df, customer_id)
            
            if tmf717_json:
                # Display JSON with download option
                st.json(tmf717_json)
                
                # Add download button for this customer's JSON
                add_json_download_button(
                    tmf717_json,
                    f'Download TMF717 JSON for {customer_id}',
                    f'customer_{customer_id}_tmf717.json'
                )
            else:
                st.error(f"Failed to generate TMF717 JSON for customer {customer_id}")
        
        return tmf717_json
    
    return None

# Function to convert all records to TMF717 JSON
def convert_all_to_tmf717(df, output_dir="tmf717_output"):
    """
    Convert all records to TMF717 JSON format using the csv_to_tmf717.py script
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create a temporary CSV file with all records
    temp_csv_path = os.path.join(output_dir, "temp_all_records.csv")
    df.to_csv(temp_csv_path, index=False)
    
    try:
        # Run the csv_to_tmf717.py script on this file
        process = subprocess.run(
            [sys.executable, "csv_to_tmf717.py", temp_csv_path, output_dir],
            check=True,
            capture_output=True,
            text=True
        )
        
        # Remove the temporary CSV
        os.remove(temp_csv_path)
        
        return True, process.stdout
    except subprocess.CalledProcessError as e:
        # Remove the temporary CSV
        if os.path.exists(temp_csv_path):
            os.remove(temp_csv_path)
        
        return False, f"Error: {e.stderr}"

# Main app layout
def main():
    st.title("Telecom Customer Data Analysis Dashboard")
    
    # Add refresh button to manually refresh file list
    if st.sidebar.button("🔄 Refresh File List"):
        # Use the proper method for clearing cache
        st.cache_data.clear()
        # Rerun using the current Streamlit method
        st.rerun()
    
    # Get available files with matching timestamps
    matched_pairs = get_matching_csv_files()
    
    if not matched_pairs:
        st.warning("No matching data files found in the 'output' directory. Only file pairs where customer records and insights have matching timestamps will be shown.")
        st.info("Looking for CSV files in: " + os.path.abspath('output'))
        return
    
    # Sidebar for file selection
    with st.sidebar:
        st.header("Data Selection")
        
        # Format options for display
        file_options = [f"{os.path.basename(pair['records_file'])} ({pair['display_time']})" for pair in matched_pairs]
        
        selected_pair_idx = st.selectbox(
            "Select Data File Pair:",
            range(len(file_options)),
            format_func=lambda i: file_options[i]
        )
        
        selected_pair = matched_pairs[selected_pair_idx]
        selected_records_file = selected_pair['records_file']
        matching_insights_file = selected_pair['insights_file']
        
        st.success(f"Using matching file pair from {selected_pair['display_time']}")
    
    # Load selected data
    records_df = load_data(selected_records_file)
    insights_df = load_data(matching_insights_file)
    
    if records_df is None or records_df.empty:
        st.error(f"Could not load data from {selected_records_file}")
        return
    
    # Convert data types for numeric columns
    records_df['Churn Score'] = pd.to_numeric(records_df['Churn Score'], errors='coerce')
    records_df['CLTV'] = pd.to_numeric(records_df['CLTV'], errors='coerce')
    records_df['Satisfaction Score (Out of 5)'] = pd.to_numeric(records_df['Satisfaction Score (Out of 5)'], errors='coerce')
    records_df['Number of Compaints Raised'] = pd.to_numeric(records_df['Number of Compaints Raised'], errors='coerce')
    
    # Main content tabs - only Tab 1 (Overview) and TMF717 JSON tab
    tab1, tab2 = st.tabs(["Overview", "TMF717 JSON"])
    
    with tab1:
        # Show dataset info
        st.subheader("Dataset Information")
        st.info(f"Data file: {os.path.basename(selected_records_file)} generated on {selected_pair['display_time']}")
        st.write(f"Total records: {len(records_df)}")
        
        # Display basic statistics
        display_statistics(records_df)
        
        # Show sample records and provide download option
        with st.expander("View Data"):
            # Add a radio button to select sample or all data
            view_option = st.radio("Select data to view:", ["Sample (5 records)", "All Records"], horizontal=True)
            
            if view_option == "Sample (5 records)":
                # Convert to string format to avoid Arrow issues
                sample_df = records_df.head(5).astype(str)
                st.dataframe(sample_df, use_container_width=True, hide_index=True)
            else:
                # Add pagination to view all records
                page_size = st.slider("Records per page:", min_value=10, max_value=100, value=20, step=10)
                total_pages = (len(records_df) + page_size - 1) // page_size
                
                col1, col2, col3 = st.columns([1, 3, 1])
                with col2:
                    page_num = st.number_input("Page:", min_value=1, max_value=total_pages, value=1)
                
                # Calculate start and end indices
                start_idx = (page_num - 1) * page_size
                end_idx = min(start_idx + page_size, len(records_df))
                
                # Display page information
                st.write(f"Showing records {start_idx+1} to {end_idx} of {len(records_df)}")
                
                # Show data for current page
                current_page_df = records_df.iloc[start_idx:end_idx].astype(str)
                st.dataframe(current_page_df, use_container_width=True, hide_index=True)
            
            st.write("Download options:")
            # Add download button for the full dataset
            add_download_button(
                records_df, 
                'Download Complete Dataset', 
                f'telecom_customer_data_{os.path.basename(selected_records_file)}'
            )
    
    with tab2:
        st.subheader("TMF717 Customer 360 JSON View")
        
        # Allow user to select a customer
        customer_ids = records_df["Customer Billing Account.CustomerBillingAccount.ID"].tolist()
        selected_customer = st.selectbox("Select a customer to view TMF717 JSON:", customer_ids)
        
        if selected_customer:
            # Display TMF717 JSON for selected customer
            display_customer_tmf717(records_df, selected_customer)
            
        # Batch conversion option
        with st.expander("Convert All Records to TMF717 Format"):
            if st.button("Generate TMF717 JSONs for All Customers"):
                # Show processing message
                with st.spinner("Converting all records to TMF717 format..."):
                    # Create output directory
                    tmf_output_dir = "tmf717_output"
                    
                    # Process conversion with progress bar
                    st.info("Running csv_to_tmf717.py to convert all records...")
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Update status
                    status_text.text("Starting conversion...")
                    progress_bar.progress(0.1)
                    
                    # Run the conversion
                    success, output = convert_all_to_tmf717(records_df, tmf_output_dir)
                    
                    if success:
                        # Count the number of generated files
                        json_files = glob.glob(os.path.join(tmf_output_dir, "*.json"))
                        num_files = len(json_files)
                        
                        # Update progress
                        progress_bar.progress(1.0)
                        status_text.text(f"Completed! Generated {num_files} TMF717 JSON files.")
                        
                        st.success(f"Conversion completed. {num_files} TMF717 JSON files stored in '{tmf_output_dir}' directory.")
                        
                        # Create a zip file with all JSONs for download
                        zip_path = f"{tmf_output_dir}.zip"
                        with zipfile.ZipFile(zip_path, 'w') as zipf:
                            for json_file in os.listdir(tmf_output_dir):
                                if json_file.endswith('.json'):
                                    zipf.write(os.path.join(tmf_output_dir, json_file), json_file)
                        
                        # Provide download link for the zip file
                        with open(zip_path, "rb") as f:
                            zip_bytes = f.read()
                            b64 = base64.b64encode(zip_bytes).decode()
                            href = f'<a href="data:application/zip;base64,{b64}" download="tmf717_json_files.zip" class="btn">⬇️ Download All TMF717 JSON Files (ZIP)</a>'
                            st.markdown(href, unsafe_allow_html=True)
                    else:
                        progress_bar.progress(1.0)
                        status_text.text("Conversion failed.")
                        st.error(f"Failed to convert records: {output}")

# Run the application if called directly
if __name__ == "__main__":
    main()