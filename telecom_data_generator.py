import csv
import random
import datetime
import os

# Helper functions
def random_int(min_val, max_val):
    """Generate a random integer between min_val and max_val (inclusive)"""
    return random.randint(min_val, max_val)

def random_float(min_val, max_val, decimal_places=2):
    """Generate a random float between min_val and max_val with specified decimal places"""
    val = random.uniform(min_val, max_val)
    return round(val, decimal_places)

def random_choice(values):
    """Select a random element from the values list"""
    return random.choice(values)

def random_date(start_date, end_date):
    """Generate a random date between start_date and end_date"""
    delta = (end_date - start_date).days
    random_days = random.randint(0, delta)
    return start_date + datetime.timedelta(days=random_days)

def format_date(date):
    """Format a date as DD-MMM-YY"""
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return f"{date.day:02d}-{months[date.month-1]}-{str(date.year)[2:]}"

def generate_account_id():
    """Generate a random account ID in the format XXXX-XXXXX"""
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    id_part1 = ''.join(random.choice(chars) for _ in range(4))
    id_part2 = ''.join(random.choice(chars) for _ in range(5))
    return f"{id_part1}-{id_part2}"

def generate_msisdn():
    """Generate a random mobile number starting with 91"""
    return "91" + ''.join(str(random.randint(0, 9)) for _ in range(8))

def generate_timestamped_filename(base_name, extension):
    """Generate a unique filename with timestamp"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}.{extension}"

# Define operators and their plans
operators = {
    "Operator B (Champion)": {
        "plans": [
            {
                "planID": "POCH045",
                "name": "5GB Plan",
                "price": "40",
                "customerType": "Individual",
                "dataAllowance": "5GB",
                "marketSegment": "General",
                "streamingQuality": "HD",
                "businessType": "prepaid",
                "activationFee": "35",
                "popularity": ""
            },
            {
                "planID": "POCH008",
                "name": "Infinite Plus",
                "price": "40/line",
                "customerType": "Family & CUG",
                "dataAllowance": "Unlimited",
                "marketSegment": "Nurses",
                "streamingQuality": "HD",
                "businessType": "prepaid",
                "activationFee": "35",
                "popularity": ""
            },
            {
                "planID": "POCH011",
                "name": "Infinite Plus",
                "price": "70",
                "customerType": "Individual",
                "dataAllowance": "Unlimited",
                "marketSegment": "Military and veterans",
                "streamingQuality": "HD",
                "businessType": "prepaid",
                "activationFee": "35",
                "popularity": ""
            },
            {
                "planID": "POCH023",
                "name": "Infinite Ultimate",
                "price": "90",
                "customerType": "Individual",
                "dataAllowance": "Unlimited",
                "marketSegment": "General",
                "streamingQuality": "4K UHD",
                "businessType": "prepaid",
                "activationFee": "35",
                "popularity": "Best Value"
            },
            {
                "planID": "POCH030",
                "name": "Infinite Ultimate",
                "price": "50/line",
                "customerType": "Family & CUG",
                "dataAllowance": "Unlimited",
                "marketSegment": "Nurses",
                "streamingQuality": "4K UHD",
                "businessType": "prepaid",
                "activationFee": "35",
                "popularity": "Best Value"
            },
            {
                "planID": "POCH031",
                "name": "Infinite Ultimate",
                "price": "80",
                "customerType": "Individual",
                "dataAllowance": "Unlimited",
                "marketSegment": "Students",
                "streamingQuality": "4K UHD",
                "businessType": "prepaid",
                "activationFee": "35",
                "popularity": "Best Value"
            }
        ]
    },
    "Operator A": {
        "plans": [
            {
                "planID": "POA001",
                "name": "Operator A Unlimited Starter® SL",
                "price": "65",
                "customerType": "Individual",
                "dataAllowance": "Unlimited",
                "marketSegment": "General",
                "streamingQuality": "SD",
                "businessType": "prepaid",
                "activationFee": "15",
                "popularity": ""
            },
            {
                "planID": "POA031",
                "name": "Operator A PREPAID Unlimited MAX℠",
                "price": "65",
                "customerType": "Individual",
                "dataAllowance": "Unlimited",
                "marketSegment": "General",
                "streamingQuality": "4K UHD",
                "businessType": "prepaid",
                "activationFee": "15",
                "popularity": ""
            }
        ]
    },
    "Operator T": {
        "plans": [
            {
                "planID": "POT001",
                "name": "Operator T 5G unlimited",
                "price": "55",
                "customerType": "Individual",
                "dataAllowance": "Unlimited",
                "marketSegment": "General",
                "streamingQuality": "HD",
                "businessType": "prepaid",
                "activationFee": "0",
                "popularity": "Best Value"
            },
            {
                "planID": "POT012",
                "name": "Go5G Military",
                "price": "30",
                "customerType": "Individual",
                "dataAllowance": "Unlimited",
                "marketSegment": "Military and veterans",
                "streamingQuality": "HD",
                "businessType": "prepaid",
                "activationFee": "0",
                "popularity": ""
            },
            {
                "planID": "POT019",
                "name": "Go5G Plus 55",
                "price": "75",
                "customerType": "Individual",
                "dataAllowance": "Unlimited",
                "marketSegment": "55+",
                "streamingQuality": "4K UHD",
                "businessType": "prepaid",
                "activationFee": "0",
                "popularity": ""
            }
        ]
    },
    "Operator C": {
        "plans": [
            {
                "planID": "POC001",
                "name": "$15 Smartphone Plan",
                "price": "15",
                "customerType": "Individual",
                "dataAllowance": "1",
                "marketSegment": "General",
                "streamingQuality": "SD",
                "businessType": "prepaid",
                "activationFee": "0",
                "popularity": ""
            }
        ]
    }
}

# Define customer profiles with churn propensity
customer_profiles = [
    {
        "type": "Price Sensitive",
        "churn_risk": "High",
        "demographics": {
            "age_range": (20, 35),
            "income_levels": ["Low", "Medium"],
            "education": ["High School", "College"],
            "marital_status": ["Single", "Married"],
            "locations": ["Dallas", "Los Angeles"]
        },
        "usage": {
            "data_upload": (3, 10),
            "data_download": (15, 50),
            "voice_minutes": (50, 200),
            "sms_count": (10, 50),
            "international": "Low",
            "ott_usage": (0, 5)
        }
    },
    {
        "type": "Feature Deficiency",
        "churn_risk": "Medium",
        "demographics": {
            "age_range": (25, 45),
            "income_levels": ["Medium", "High"],
            "education": ["College", "Professional"],
            "marital_status": ["Married", "Family"],
            "locations": ["Dallas", "New York"]
        },
        "usage": {
            "data_upload": (10, 25),
            "data_download": (50, 120),
            "voice_minutes": (200, 500),
            "sms_count": (30, 100),
            "international": "Medium",
            "ott_usage": (10, 25)
        }
    },
    {
        "type": "Customer Service",
        "churn_risk": "Medium to High",
        "demographics": {
            "age_range": (30, 60),
            "income_levels": ["Medium", "High"],
            "education": ["College", "Professional"],
            "marital_status": ["Married", "Family"],
            "locations": ["Los Angeles", "Las Vegas", "Dallas"]
        },
        "usage": {
            "data_upload": (10, 20),
            "data_download": (40, 100),
            "voice_minutes": (400, 800),
            "sms_count": (50, 200),
            "international": "Low",
            "ott_usage": (5, 20)
        }
    },
    {
        "type": "Network Quality",
        "churn_risk": "High",
        "demographics": {
            "age_range": (25, 50),
            "income_levels": ["Medium", "High"],
            "education": ["College", "Professional"],
            "marital_status": ["Married", "Family"],
            "locations": ["Rural California", "Rural Texas"]
        },
        "usage": {
            "data_upload": (15, 30),
            "data_download": (80, 150),
            "voice_minutes": (100, 300),
            "sms_count": (20, 80),
            "international": "Low",
            "ott_usage": (15, 30)
        }
    },
    {
        "type": "Loyal Customer",
        "churn_risk": "Low",
        "demographics": {
            "age_range": (35, 65),
            "income_levels": ["Medium", "High"],
            "education": ["College", "Professional"],
            "marital_status": ["Married", "Family"],
            "locations": ["Los Angeles", "New York"]
        },
        "usage": {
            "data_upload": (15, 40),
            "data_download": (75, 200),
            "voice_minutes": (300, 700),
            "sms_count": (50, 200),
            "international": "Medium",
            "ott_usage": (15, 40)
        }
    },
    {
        "type": "At Risk",
        "churn_risk": "Medium",
        "demographics": {
            "age_range": (25, 40),
            "income_levels": ["Medium"],
            "education": ["College", "Professional"],
            "marital_status": ["Single", "Married"],
            "locations": ["Dallas", "Las Vegas"]
        },
        "usage": {
            "data_upload": (10, 20),
            "data_download": (50, 100),
            "voice_minutes": (200, 400),
            "sms_count": (30, 80),
            "international": "Low",
            "ott_usage": (10, 25)
        }
    }
]

# Churn reasons based on customer profile type
churn_reasons = {
    "Price Sensitive": "Price sensitivity",
    "Feature Deficiency": "Competitor offered better streaming quality and international options",
    "Customer Service": "Multiple unresolved complaints and poor customer service",
    "Network Quality": "Network coverage and speed issues in their location",
    "Loyal Customer": "",
    "At Risk": ""
}

# Customer insights based on profile type
customer_insights = {
    "Price Sensitive": lambda record: f"**Price-Sensitive Churn Insight:** Customer churned from Operator B (Champion)'s \"{record['Customer Plan Name']}\" (${record['Price']}) due to price sensitivity. Analysis suggests they likely switched to Operator C's \"$15 Smartphone Plan\" which offers similar basic functionality at a significantly lower price point ($15 vs ${record['Price']}).",
    
    "Feature Deficiency": lambda record: f"**Feature Deficiency Churn Insight:** Customer churned from Operator B (Champion)'s \"{record['Customer Plan Name']}\" {record['productOffering.customerType']} plan due to feature limitations despite acceptable satisfaction score ({record['Satisfaction Score (Out of 5)']}/5). Analysis shows heavy international usage ({record['Product.Networkproduct.ConsumptionSummary.value (International Roaming Voice (In Minutes)']} minutes, {float(record['Product.Networkproduct.ConsumptionSummary.value (International Roaming Data Upload (In GB))']) + float(record['Product.Networkproduct.ConsumptionSummary.value (International Romaing Data Download (In GB))']):.2f}GB total international data) and high OTT consumption ({record['Product.Networkproduct.ConsumptionSummary.value (Consumed OTT usage (In GB))']}GB), suggesting they switched to Operator T's \"Go5G Plus 55\" plan which offers better international coverage and streaming quality.",
    
    "Customer Service": lambda record: f"**Customer Service Churn Insight:** This customer churned primarily due to service quality issues, evidenced by the extremely low satisfaction score ({record['Satisfaction Score (Out of 5)']}/5) and high number of complaints ({record['Number of Compaints Raised']}) over a {record['Length of customer relationship (In Months)']}-month relationship. Despite subscribing to Operator B (Champion)'s premium \"{record['Customer Plan Name']}\" plan, they likely switched to Operator T's \"Go5G Military\" plan which offers dedicated customer care and comparable features.",
    
    "Network Quality": lambda record: f"**Network Quality Churn Insight:** This high-value customer (${record['CLTV']} CLTV) churned despite subscribing to Operator B (Champion)'s premium \"{record['Customer Plan Name']}\" plan due to network issues in {record['Location.Geographic Place.GeographicState.name']}. Their extremely high data usage ({record['Product.Networkproduct.ConsumptionSummary.value (Data Download (In GB))']}GB download) and significant OTT consumption ({record['Product.Networkproduct.ConsumptionSummary.value (Consumed OTT usage (In GB))']}GB) suggests streaming and connectivity problems in their area. They likely switched to Operator T's \"Operator T 5G unlimited\" plan, which has better rural coverage.",
    
    "Loyal Customer": lambda record: f"**Loyal Customer Insight:** This high-value {record['productOffering.customerType'].lower()} plan customer (${record['CLTV']} CLTV) shows strong loyalty indicators with excellent satisfaction ({record['Satisfaction Score (Out of 5)']}/5) and minimal complaints ({record['Number of Compaints Raised']}) despite heavy usage across all services. They fully utilize the premium features of Operator B (Champion)'s \"{record['Customer Plan Name']}\" plan including high data consumption ({record['Product.Networkproduct.ConsumptionSummary.value (Data Download (In GB))']}GB), international usage, and extensive OTT streaming ({record['Product.Networkproduct.ConsumptionSummary.value (Consumed OTT usage (In GB))']}GB), justifying the premium price point. They have not been tempted by Operator A or Operator T's competing family plans.",
    
    "At Risk": lambda record: f"**At-Risk Customer Insight:** This medium-value customer (${record['CLTV']} CLTV) shows moderate churn risk (Score: {record['Churn Score']}) despite having no immediate issues. The moderate satisfaction score ({record['Satisfaction Score (Out of 5)']}/5) and average complaints ({record['Number of Compaints Raised']}) indicate potential dissatisfaction with value received for the ${record['Price']} price point for Operator B (Champion)'s \"{record['Customer Plan Name']}\" plan. Competitor Operator T offers \"Go5G Military\" plan with better military discounts at $30, making this customer vulnerable to targeted competitor offers."
}

def generate_synthetic_record(profile_type, is_churned=False):
    """Generate a synthetic telecom customer record based on profile type"""
    
    # Select profile
    profile = next((p for p in customer_profiles if p["type"] == profile_type), None)
    if not profile:
        raise ValueError(f"Unknown profile type: {profile_type}")
    
    # Determine operator and plan
    is_champion_customer = True  # For this example, all customers are with the champion
    operator_name = "Operator B (Champion)"
    available_plans = operators[operator_name]["plans"]
    selected_plan = random_choice(available_plans)
    
    # Generate customer details
    account_id = generate_account_id()
    msisdn = generate_msisdn()
    
    # Generate dates
    now = datetime.date(2025, 3, 28)  # Current date
    start_date = random_date(datetime.date(2022, 1, 1), datetime.date(2024, 1, 1))
    end_date = None
    if is_churned:
        end_date = random_date(datetime.date(2024, 6, 1), datetime.date(2025, 2, 1))
    
    # Calculate relationship length in months
    relationship_months = ((end_date or now) - start_date).days // 30
    
    # Usage period (most recent month)
    usage_from_date = datetime.date(2025, 1, 1)  # Jan 1, 2025
    usage_to_date = datetime.date(2025, 1, 31)  # Jan 31, 2025
    
    # Demographics
    age = random_int(*profile["demographics"]["age_range"])
    gender = random_choice(["Male", "Female"])
    income = random_choice(profile["demographics"]["income_levels"])
    education = random_choice(profile["demographics"]["education"])
    marital_status = random_choice(profile["demographics"]["marital_status"])
    location = random_choice(profile["demographics"]["locations"])
    
    # Calculate usage
    data_upload = random_float(*profile["usage"]["data_upload"])
    data_download = random_float(*profile["usage"]["data_download"])
    voice_minutes = random_int(*profile["usage"]["voice_minutes"])
    sms_count = random_int(*profile["usage"]["sms_count"])
    
    # International usage
    intl_voice = 0
    intl_data_upload = 0
    intl_data_download = 0
    intl_sms = 0
    
    if profile["usage"]["international"] == "Medium":
        intl_voice = random_int(20, 100)
        intl_data_upload = random_float(0.2, 2)
        intl_data_download = random_float(1, 8)
        intl_sms = random_int(10, 50)
    elif profile["usage"]["international"] == "High":
        intl_voice = random_int(100, 300)
        intl_data_upload = random_float(2, 5)
        intl_data_download = random_float(8, 20)
        intl_sms = random_int(50, 150)
    
    # OTT usage
    ott_usage = random_float(*profile["usage"]["ott_usage"])
    
    # Satisfaction and complaints
    if is_churned:
        if profile_type == "Customer Service":
            satisfaction_score = random_int(1, 2)
            complaints = random_int(5, 10)
        elif profile["churn_risk"] == "High":
            satisfaction_score = random_int(1, 3)
            complaints = random_int(2, 6)
        else:
            satisfaction_score = random_int(2, 3)
            complaints = random_int(1, 4)
    elif profile["churn_risk"] in ["Medium", "Medium to High"]:
        satisfaction_score = random_int(2, 4)
        complaints = random_int(1, 3)
    else:
        satisfaction_score = random_int(4, 5)
        complaints = random_int(0, 1)
    
    # Churn status and score
    churn_status = "Not Churned"
    churn_score = 0
    churn_category = ""
    churn_reason = ""
    
    if is_churned:
        churn_status = "Churned"
        churn_score = random_int(70, 100)
        churn_category = profile_type
        churn_reason = churn_reasons[profile_type]
    elif profile_type == "At Risk" or (profile["churn_risk"] in ["High", "Medium to High"]):
        churn_status = "At Risk"
        churn_score = random_int(60, 85)
    elif profile["churn_risk"] == "Medium":
        if random.random() > 0.7:
            churn_status = "At Risk"
            churn_score = random_int(45, 65)
        else:
            churn_score = random_int(30, 45)
    else:
        churn_score = random_int(5, 30)
    
    # Customer Lifetime Value
    if income == "Low":
        cltv = random_int(1000, 3000)
    elif income == "Medium":
        cltv = random_int(3000, 6000)
    else:
        cltv = random_int(6000, 12000)
    
    # Prepare the final record
    record = {
        "Customer Billing Account.CustomerBillingAccount.ID": account_id,
        "Digital Identity.NetworkCredential.ID (MSISDN)": msisdn,
        "Plan ID": selected_plan["planID"],
        "productOffering.planType": "voice and data",
        "Customer Plan Name": selected_plan["name"],
        "productOffering.businessType": selected_plan["businessType"],
        "productOffering.market segment": selected_plan["marketSegment"],
        "productOffering.customerType": selected_plan["customerType"],
        "Price": selected_plan["price"],
        "Activation Fee": selected_plan["activationFee"],
        "Customer Subscription Start Date": format_date(start_date),
        "Customer subscription end date": format_date(end_date) if end_date else "",
        "Length of customer relationship (In Months)": relationship_months,
        "Subscription Status": "Inactive" if end_date else "Active",
        "Time Since last purchase or engagement (In Months)": (now - (end_date or now)).days // 30,
        "Party.Party Demographic.PartyDemographicValue.value(Age)": age,
        "Party.Individual.gender": gender,
        "Party.Party Demographic.PartyDemographicValue.value(Income Level)": income,
        "Party.Party Demographic.PartyDemographicValue.value(Education)": education,
        "Individual.maritalStatus (Family Structure)": marital_status,
        "Location.Geographic Place.GeographicState.name": location,
        "Age Group": "Young" if age < 35 else "Middle Aged" if age < 55 else "Senior",
        "VIP Group": "Y" if income == "High" else "N",
        "No Of Lines": random_int(1, 4),
        "Usage From Period": format_date(usage_from_date),
        "Usage To Period": format_date(usage_to_date),
        "Product.Networkproduct.ConsumptionSummary.value (Data Upload (In GB))": f"{data_upload:.2f}",
        "Product.Networkproduct.ConsumptionSummary.value (Data Download (In GB))": f"{data_download:.2f}",
        "Product.Networkproduct.ConsumptionSummary.value Voice (in Minutes)": voice_minutes,
        "Product.Networkproduct.ConsumptionSummary.value (SMS (In Numbers))": sms_count,
        "Product.Networkproduct.ConsumptionSummary.value (International Roaming Voice (In Minutes)": intl_voice,
        "Product.Networkproduct.ConsumptionSummary.value (International Roaming Data Upload (In GB))": f"{intl_data_upload:.2f}",
        "Product.Networkproduct.ConsumptionSummary.value (International Romaing Data Download (In GB))": f"{intl_data_download:.2f}",
        "Product.Networkproduct.ConsumptionSummary.value (International Romaing SMS)": intl_sms,
        "Product.Networkproduct.ConsumptionSummary.value (Consumed OTT usage (In GB))": f"{ott_usage:.2f}",
        "Product.Networkproduct.ConsumptionSummary.value (Cloud Storage)": "0",
        "Rating Group (Google, Youtube)": random_choice(["Google", "Youtube"]),
        "At Risk Customer(Based on usage or behaviour patterns)": "Yes" if churn_status == "At Risk" else "No",
        "Number of Compaints Raised": complaints,
        "Churn Category": churn_category,
        "Reason Of Churn": churn_reason,
        "Churn Status": churn_status,
        "Churn Score": churn_score,
        "CLTV": cltv,
        "Contract": "N",
        "Satisfaction Score (Out of 5)": satisfaction_score
    }
    
    return record

def generate_multiple_records(count=10):
    """Generate multiple synthetic records"""
    
    records = []
    insights = []
    
    # Distribution of customer types for a realistic dataset
    # 60% churned, 20% at risk, 20% loyal
    customer_distribution = {
        "churned": ["Price Sensitive", "Feature Deficiency", "Customer Service", "Network Quality"],
        "at_risk": ["At Risk"],
        "loyal": ["Loyal Customer"]
    }
    
    for i in range(count):
        # Determine if this customer is churned
        category = random_choice(["churned", "churned", "churned", "at_risk", "loyal"])
        profile_type = random_choice(customer_distribution[category])
        is_churned = category == "churned"
        
        record = generate_synthetic_record(profile_type, is_churned)
        records.append(record)
        
        # Generate customer insight
        insight_generator = customer_insights.get(profile_type)
        if insight_generator:
            insight = {
                "account_id": record["Customer Billing Account.CustomerBillingAccount.ID"],
                "msisdn": record["Digital Identity.NetworkCredential.ID (MSISDN)"],
                "churn_status": record["Churn Status"],
                "profile_type": profile_type,
                "insight": insight_generator(record)
            }
            insights.append(insight)
    
    return records, insights

def save_records_to_csv(records, base_filename="telecom_customer_records"):
    """Save the generated records to a timestamped CSV file"""
    
    if not records:
        return None
    
    # Create output directory if it doesn't exist
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate timestamped filename
    filename = os.path.join(output_dir, f"{base_filename}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    
    # Get field names from the first record
    fieldnames = list(records[0].keys())
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    
    print(f"Saved {len(records)} records to {filename}")
    return filename

def save_insights_to_csv(insights, base_filename="telecom_customer_insights"):
    """Save the customer insights to a timestamped CSV file"""
    
    if not insights:
        return None
    
    # Create output directory if it doesn't exist
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate timestamped filename
    filename = os.path.join(output_dir, f"{base_filename}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    
    # Get field names from the first insight
    fieldnames = list(insights[0].keys())
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(insights)
    
    print(f"Saved {len(insights)} insights to {filename}")
    return filename

def main():
    """Main function to generate and save synthetic telecom data"""
    
    # Set random seed for reproducibility (comment out for truly random data each time)
    # random.seed(42)
    
    # Number of records to generate
    record_count = 20
    
    # Generate synthetic records
    print(f"Generating {record_count} synthetic telecom customer records...")
    records, insights = generate_multiple_records(record_count)
    
    # Save records and insights to CSV files
    records_file = save_records_to_csv(records)
    insights_file = save_insights_to_csv(insights)
    
    print("\nGeneration complete!")
    print(f"Records saved to: {records_file}")
    print(f"Insights saved to: {insights_file}")

if __name__ == "__main__":
    main()