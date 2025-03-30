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

# Set page config (must be the first Streamlit command)
st.set_page_config(
    page_title="Telecom Customer Data Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# Function to create churn analysis visualizations
def display_churn_analysis(df):
    """Create and display churn analysis visualizations"""
    if df is None or df.empty:
        st.warning("No data available for churn analysis")
        return
    
    st.subheader("Churn Analysis")
    
    col1, col2 = st.columns(2)
    
    # Churn by category pie chart
    with col1:
        # Filter only churned customers
        churned_df = df[df['Churn Status'] == 'Churned']
        if not churned_df.empty:
            churn_category_counts = churned_df['Churn Category'].value_counts()
            fig = px.pie(
                values=churn_category_counts.values, 
                names=churn_category_counts.index,
                title="Churn Reasons Distribution",
                color_discrete_sequence=px.colors.qualitative.Vivid
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No churned customers in this dataset")
    
    # Satisfaction vs Churn Score scatter plot
    with col2:
        fig = px.scatter(
            df, 
            x="Satisfaction Score (Out of 5)", 
            y="Churn Score",
            color="Churn Status",
            size="CLTV",
            hover_data=["Customer Plan Name", "Price", "Number of Compaints Raised"],
            title="Satisfaction vs Churn Score",
            color_discrete_sequence=px.colors.qualitative.Vivid
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Churn by plan type
    col1, col2 = st.columns(2)
    
    with col1:
        plan_churn = pd.crosstab(df['Customer Plan Name'], df['Churn Status'])
        if 'Churned' in plan_churn.columns:
            plan_churn['Churn Rate'] = plan_churn['Churned'] / plan_churn.sum(axis=1)
            fig = px.bar(
                plan_churn, 
                y=plan_churn.index, 
                x='Churn Rate',
                title="Churn Rate by Plan Type",
                labels={'y': 'Plan Name', 'x': 'Churn Rate'},
                orientation='h'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Data usage vs churn
        fig = px.box(
            df,
            x="Churn Status",
            y=df["Product.Networkproduct.ConsumptionSummary.value (Data Download (In GB))"].astype(float),
            color="Churn Status",
            title="Data Usage Distribution by Churn Status",
            labels={"y": "Data Download (GB)"}
        )
        st.plotly_chart(fig, use_container_width=True)

# Function to display customer segments
def display_customer_segments(df):
    """Display customer segment analysis"""
    if df is None or df.empty:
        st.warning("No data available for customer segmentation")
        return
    
    st.subheader("Customer Segments")
    
    col1, col2 = st.columns(2)
    
    # Age distribution by churn status
    with col1:
        age_bins = [0, 25, 35, 45, 55, 100]
        age_labels = ["18-25", "26-35", "36-45", "46-55", "56+"]
        df['Age Group Binned'] = pd.cut(
            df["Party.Party Demographic.PartyDemographicValue.value(Age)"].astype(int),
            bins=age_bins,
            labels=age_labels
        )
        
        age_churn = pd.crosstab(df['Age Group Binned'], df['Churn Status'], normalize='index')
        fig = px.bar(
            age_churn, 
            barmode='stack',
            title="Churn Status by Age Group",
            labels={'value': 'Proportion', 'Age Group Binned': 'Age Group'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Location analysis
    with col2:
        location_churn = pd.crosstab(
            df['Location.Geographic Place.GeographicState.name'], 
            df['Churn Status'],
            normalize='index'
        )
        fig = px.bar(
            location_churn, 
            barmode='stack',
            title="Churn Status by Location",
            labels={'value': 'Proportion', 'Location.Geographic Place.GeographicState.name': 'Location'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # CLTV by market segment
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.box(
            df,
            x="productOffering.market segment",
            y="CLTV",
            color="Churn Status",
            title="Customer Lifetime Value by Market Segment",
            labels={"productOffering.market segment": "Market Segment", "CLTV": "Customer Lifetime Value ($)"}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Convert to numeric for correlation
        num_df = df.copy()
        
        # Pick relevant numeric columns
        numeric_cols = [
            "Churn Score", 
            "CLTV",
            "Satisfaction Score (Out of 5)",
            "Number of Compaints Raised",
            "Party.Party Demographic.PartyDemographicValue.value(Age)"
        ]
        
        # Create correlation matrix
        corr_df = num_df[numeric_cols].corr()
        
        # Plot heatmap
        fig = px.imshow(
            corr_df,
            text_auto=True,
            title="Correlation Between Key Metrics",
            color_continuous_scale='RdBu_r',
            zmin=-1, zmax=1
        )
        st.plotly_chart(fig, use_container_width=True)

# Function to display individual customer data
def display_customer_details(df, insights_df):
    """Display detailed information for individual customers"""
    if df is None or df.empty:
        st.warning("No customer data available")
        return
    
    st.subheader("Individual Customer Analysis")
    
    # Allow selection of a specific customer
    customer_ids = df["Customer Billing Account.CustomerBillingAccount.ID"].tolist()
    customer_id = st.selectbox("Select a customer to view details:", customer_ids)
    
    if customer_id:
        customer_data = df[df["Customer Billing Account.CustomerBillingAccount.ID"] == customer_id].iloc[0]
        
        # Find matching insight if available
        customer_insight = None
        if insights_df is not None and not insights_df.empty:
            insight_row = insights_df[insights_df["account_id"] == customer_id]
            if not insight_row.empty:
                # Format the insight text before displaying
                customer_insight = format_insight_text(insight_row.iloc[0]["insight"])
        
        # Display customer details in columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### Customer Information")
            info_data = []
            info_fields = {
                "Account ID": customer_data["Customer Billing Account.CustomerBillingAccount.ID"],
                "MSISDN": customer_data["Digital Identity.NetworkCredential.ID (MSISDN)"],
                "Plan": customer_data["Customer Plan Name"],
                "Price": f"${customer_data['Price']}",
                "Start Date": customer_data["Customer Subscription Start Date"],
                "End Date": customer_data["Customer subscription end date"] or "Active",
                "Age": customer_data["Party.Party Demographic.PartyDemographicValue.value(Age)"],
                "Gender": customer_data["Party.Individual.gender"],
                "Location": customer_data["Location.Geographic Place.GeographicState.name"],
                "Income Level": customer_data["Party.Party Demographic.PartyDemographicValue.value(Income Level)"],
                "Education": customer_data["Party.Party Demographic.PartyDemographicValue.value(Education)"],
                "Relationship Status": customer_data["Individual.maritalStatus (Family Structure)"]
            }
            
            # Create a list of field-value dictionaries
            for field, value in info_fields.items():
                info_data.append({"Field": field, "Value": str(value)})
            
            # Create a DataFrame and display (with reset_index to remove the index column)
            info_df = pd.DataFrame(info_data).reset_index(drop=True)
            st.table(info_df)  # Use st.table instead of st.dataframe
        
        with col2:
            st.write("### Usage & Churn Data")
            usage_data = []
            usage_fields = {
                "Churn Status": customer_data["Churn Status"],
                "Churn Score": customer_data["Churn Score"],
                "Churn Category": customer_data["Churn Category"] or "N/A",
                "Reason of Churn": customer_data["Reason Of Churn"] or "N/A",
                "CLTV": f"${customer_data['CLTV']}",
                "Satisfaction Score": f"{customer_data['Satisfaction Score (Out of 5)']}/5",
                "Complaints": customer_data["Number of Compaints Raised"],
                "Data Download (GB)": customer_data["Product.Networkproduct.ConsumptionSummary.value (Data Download (In GB))"],
                "Data Upload (GB)": customer_data["Product.Networkproduct.ConsumptionSummary.value (Data Upload (In GB))"],
                "Voice Minutes": customer_data["Product.Networkproduct.ConsumptionSummary.value Voice (in Minutes)"],
                "SMS Count": customer_data["Product.Networkproduct.ConsumptionSummary.value (SMS (In Numbers))"],
                "OTT Usage (GB)": customer_data["Product.Networkproduct.ConsumptionSummary.value (Consumed OTT usage (In GB))"]
            }
            
            # Create a list of field-value dictionaries
            for field, value in usage_fields.items():
                usage_data.append({"Field": field, "Value": str(value)})
            
            # Create a DataFrame and display (with reset_index to remove the index column)
            usage_df = pd.DataFrame(usage_data).reset_index(drop=True)
            st.table(usage_df)  # Use st.table instead of st.dataframe
        
        # Display customer insight
        if customer_insight:
            st.write("### Customer Insight")
            st.info(customer_insight)
        
        # Create simple visualizations for this customer
        st.write("### Customer Usage Patterns")
        col1, col2 = st.columns(2)
        
        with col1:
            # Usage pie chart
            usage_labels = ["Data", "Voice", "SMS", "OTT"]
            # Convert data to float values where needed and ensure they're strings first
            try:
                usage_values = [
                    float(str(customer_data["Product.Networkproduct.ConsumptionSummary.value (Data Download (In GB))"])) + 
                    float(str(customer_data["Product.Networkproduct.ConsumptionSummary.value (Data Upload (In GB))"])),
                    float(str(customer_data["Product.Networkproduct.ConsumptionSummary.value Voice (in Minutes)"])) / 10,  # Scale for visibility
                    float(str(customer_data["Product.Networkproduct.ConsumptionSummary.value (SMS (In Numbers))"])),
                    float(str(customer_data["Product.Networkproduct.ConsumptionSummary.value (Consumed OTT usage (In GB))"]))
                ]
                
                fig = px.pie(
                    values=usage_values, 
                    names=usage_labels,
                    title="Usage Distribution",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(fig, use_container_width=True)
            except (ValueError, TypeError) as e:
                st.error(f"Could not generate usage chart: {str(e)}")
        
        with col2:
            # Churn Score Gauge
            try:
                churn_score = int(float(str(customer_data["Churn Score"])))
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=churn_score,
                    title={'text': "Churn Score"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 30], 'color': "green"},
                            {'range': [30, 60], 'color': "yellow"},
                            {'range': [60, 100], 'color': "red"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': churn_score
                        }
                    }
                ))
                st.plotly_chart(fig, use_container_width=True)
            except (ValueError, TypeError) as e:
                st.error(f"Could not generate gauge chart: {str(e)}")

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
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Churn Analysis", "Customer Segments", "Individual Customers"])
    
    with tab1:
        # Show dataset info
        st.subheader("Dataset Information")
        st.info(f"Data file: {os.path.basename(selected_records_file)} generated on {selected_pair['display_time']}")
        st.write(f"Total records: {len(records_df)}")
        
        # Display basic statistics
        display_statistics(records_df)
        
        # Show sample records and provide download option
        with st.expander("View Sample Data"):
            # Convert to string format to avoid Arrow issues
            sample_df = records_df.head(5).astype(str)
            st.dataframe(sample_df, use_container_width=True, hide_index=True)
            
            st.write("Download options:")
            # Add download button for the full dataset
            add_download_button(
                records_df, 
                'Download Complete Dataset', 
                f'telecom_customer_data_{os.path.basename(selected_records_file)}'
            )
    
    with tab2:
        display_churn_analysis(records_df)
    
    with tab3:
        display_customer_segments(records_df)
    
    with tab4:
        display_customer_details(records_df, insights_df)

if __name__ == "__main__":
    main()