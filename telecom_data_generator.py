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

def load_plans_from_csv(csv_file):
    """
    Load plans from the CSV file starting from row 6
    
    Args:
        csv_file (str): Path to the CSV file
        
    Returns:
        dict: Dictionary of operators and their plans
    """
    operators = {}
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            
            # Skip the first 5 rows (headers and rules)
            for _ in range(5):
                next(csv_reader)
            
            # Read the data rows
            for row in csv_reader:
                if not row or len(row) < 10:  # Skip empty rows
                    continue
                
                operator_name = row[0].strip()
                plan_id = row[1].strip()
                market_segment = row[2].strip()
                business_type = row[3].strip()
                location = row[4].strip()
                popularity = row[5].strip()
                customer_type = row[8].strip()
                plan_name = row[9].strip()
                
                # Determine pricing based on customer type
                price = None
                if customer_type == "Individual" and row[10]:
                    price = row[10].strip()
                elif customer_type == "Family & CUG":
                    # Find the first non-empty price column for family plans
                    for i in range(11, 14):
                        if row[i].strip():
                            price = row[i].strip()
                            break
                
                # Skip if no price was found
                if not price:
                    continue
                
                # Get data allowance
                data_allowance = row[19].strip() if len(row) > 19 else ""
                
                # Get streaming quality
                streaming_quality = row[27].strip() if len(row) > 27 else ""
                
                # Get activation fee
                activation_fee = row[15].strip() if len(row) > 15 else "0"
                
                # Get international data if available
                international_data = ""
                if len(row) > 28:
                    international_data = row[28].strip()
                
                # Get international voice if available
                international_voice = ""
                if len(row) > 29:
                    international_voice = row[29].strip()
                
                # Get international SMS if available
                international_sms = ""
                if len(row) > 30:
                    international_sms = row[30].strip()
                
                # Get international countries if available
                international_countries = ""
                if len(row) > 31:
                    international_countries = row[31].strip()
                
                # Get hotspot data if available
                hotspot_data = ""
                if len(row) > 33:
                    hotspot_data = row[33].strip()
                
                # Create plan data
                plan_data = {
                    "planID": plan_id,
                    "name": plan_name,
                    "price": price,
                    "customerType": customer_type,
                    "dataAllowance": data_allowance,
                    "marketSegment": market_segment,
                    "streamingQuality": streaming_quality,
                    "businessType": business_type,
                    "activationFee": activation_fee,
                    "popularity": popularity,
                    "international_data": international_data,
                    "international_voice": international_voice,
                    "international_sms": international_sms,
                    "international_countries": international_countries,
                    "hotspot_data": hotspot_data
                }
                
                # Add to operators dictionary
                if operator_name not in operators:
                    operators[operator_name] = {"plans": []}
                
                operators[operator_name]["plans"].append(plan_data)
        
        return operators
    
    except Exception as e:
        print(f"Error loading plans from CSV: {e}")
        # Return the default operators as a fallback
        return get_default_operators()
def get_default_operators():
    """Return the default operators if CSV loading fails"""
    return {
        "Operator B (champion)": {
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
                    "popularity": "",
                    "international_data": "0",
                    "international_voice": "0",
                    "international_sms": "0",
                    "international_countries": "",
                    "hotspot_data": "5"
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
                    "popularity": "",
                    "international_data": "5",
                    "international_voice": "120",
                    "international_sms": "50",
                    "international_countries": "US,Mexico,Canada",
                    "hotspot_data": "15"
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
                    "popularity": "",
                    "international_data": "5",
                    "international_voice": "120",
                    "international_sms": "50",
                    "international_countries": "US,Mexico,Canada",
                    "hotspot_data": "15"
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
                    "popularity": "Best Value",
                    "international_data": "10",
                    "international_voice": "Unlimited",
                    "international_sms": "Unlimited",
                    "international_countries": "US,Mexico,Canada,UK,Australia,France,Germany,Italy,Spain,Japan",
                    "hotspot_data": "30"
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
                    "popularity": "Best Value",
                    "international_data": "10",
                    "international_voice": "Unlimited",
                    "international_sms": "Unlimited",
                    "international_countries": "US,Mexico,Canada,UK,Australia,France,Germany,Italy,Spain,Japan",
                    "hotspot_data": "30"
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
                    "popularity": "Best Value",
                    "international_data": "10",
                    "international_voice": "Unlimited",
                    "international_sms": "Unlimited",
                    "international_countries": "US,Mexico,Canada,UK,Australia,France,Germany,Italy,Spain,Japan",
                    "hotspot_data": "30"
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
                    "popularity": "",
                    "international_data": "0",
                    "international_voice": "0",
                    "international_sms": "Unlimited",
                    "international_countries": "230+",
                    "hotspot_data": "5"
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
                    "popularity": "",
                    "international_data": "5",
                    "international_voice": "Unlimited",
                    "international_sms": "Unlimited",
                    "international_countries": "230+",
                    "hotspot_data": "15"
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
                    "popularity": "Best Value",
                    "international_data": "5",
                    "international_voice": "Unlimited",
                    "international_sms": "Unlimited",
                    "international_countries": "Mexico,Canada",
                    "hotspot_data": "10"
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
                    "popularity": "",
                    "international_data": "5",
                    "international_voice": "Unlimited",
                    "international_sms": "Unlimited",
                    "international_countries": "Mexico,Canada",
                    "hotspot_data": "10"
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
                    "popularity": "",
                    "international_data": "10",
                    "international_voice": "Unlimited",
                    "international_sms": "Unlimited",
                    "international_countries": "Mexico,Canada,UK,Germany,Italy,France,Spain",
                    "hotspot_data": "20"
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
                    "popularity": "",
                    "international_data": "0",
                    "international_voice": "0",
                    "international_sms": "0",
                    "international_countries": "",
                    "hotspot_data": "1"
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
# Helper functions for the improved customer insights
def extract_price_numeric(price_str):
    """Extract numeric price from price string that might include '/line'"""
    if not price_str:
        return 0
    # Remove '/line' or other text
    price_str = price_str.split('/')[0]
    # Remove $ if present
    price_str = price_str.replace('$', '')
    # Convert to float
    try:
        return float(price_str)
    except ValueError:
        return 0

def find_better_competitor_plan(profile_type, champion_plan, operators, usage_metrics):
    """
    Find a better competitor plan based on customer profile and usage metrics
    
    Args:
        profile_type (str): Customer profile type
        champion_plan (dict): Current Champion plan
        operators (dict): All operators and their plans
        usage_metrics (dict): Customer usage metrics
        
    Returns:
        tuple: (operator_name, plan, reason) or (None, None, None) if no better plan found
    """
    champion_price = extract_price_numeric(champion_plan["price"])
    champion_data = champion_plan["dataAllowance"]
    champion_streaming = champion_plan["streamingQuality"]
    champion_hotspot = champion_plan.get("hotspot_data", "0")
    champion_intl_data = champion_plan.get("international_data", "0")
    champion_market_segment = champion_plan["marketSegment"]
    
    # Convert usage metrics to numerical values where needed
    data_download = float(usage_metrics["data_download"])
    intl_data_usage = float(usage_metrics["intl_data_upload"]) + float(usage_metrics["intl_data_download"])
    ott_usage = float(usage_metrics["ott_usage"])
    
    # For price sensitive customers
    if profile_type == "Price Sensitive":
        cheapest_plan = None
        cheapest_price = float('inf')
        cheapest_operator = None
        reason = ""
        
        for op_name, op_data in operators.items():
            if op_name == "Operator B (champion)":
                continue
                
            for plan in op_data["plans"]:
                price = extract_price_numeric(plan["price"])
                
                # Skip if price is not lower or if data is much worse
                if price >= champion_price:
                    continue
                    
                # For price sensitive, even a small price advantage matters
                price_diff = champion_price - price
                
                if price < cheapest_price:
                    # Make sure data allowance is sufficient for their usage
                    data_sufficient = True
                    if plan["dataAllowance"] != "Unlimited":
                        try:
                            plan_data = float(plan["dataAllowance"].replace("GB", ""))
                            if plan_data < data_download:
                                data_sufficient = False
                        except (ValueError, AttributeError):
                            data_sufficient = False
                    
                    if data_sufficient:
                        cheapest_price = price
                        cheapest_plan = plan
                        cheapest_operator = op_name
                        reason = f"${price_diff:.2f} monthly savings"
        
        if cheapest_plan:
            return (cheapest_operator, cheapest_plan, reason)
    
    # For feature deficiency customers
    elif profile_type == "Feature Deficiency":
        best_feature_plan = None
        best_feature_score = -1
        best_feature_operator = None
        reason = ""
        
        for op_name, op_data in operators.items():
            if op_name == "Operator B (champion)":
                continue
                
            for plan in op_data["plans"]:
                # Skip if price is significantly higher
                price = extract_price_numeric(plan["price"])
                if price > champion_price * 1.3:  # Allow up to 30% higher price for better features
                    continue
                
                # Calculate feature score based on what matters to feature-focused customers
                feature_score = 0
                
                # Streaming quality improvement
                if plan["streamingQuality"] == "4K UHD" and champion_streaming != "4K UHD":
                    feature_score += 2
                elif plan["streamingQuality"] == "HD" and champion_streaming == "SD":
                    feature_score += 1
                
                # International data improvement (especially important for high international usage)
                try:
                    plan_intl_data = plan.get("international_data", "0")
                    if plan_intl_data == "Unlimited":
                        plan_intl_data = "1000"  # Effectively unlimited
                    
                    champion_intl_data_val = 0
                    if champion_intl_data == "Unlimited":
                        champion_intl_data_val = 1000
                    else:
                        try:
                            champion_intl_data_val = float(champion_intl_data)
                        except (ValueError, TypeError):
                            pass
                    
                    plan_intl_data_val = 0
                    try:
                        plan_intl_data_val = float(plan_intl_data)
                    except (ValueError, TypeError):
                        pass
                    
                    if plan_intl_data_val > champion_intl_data_val:
                        improvement = min(3, (plan_intl_data_val - champion_intl_data_val) / 5)
                        feature_score += improvement
                except (ValueError, TypeError):
                    pass
                
                # Hotspot data improvement
                try:
                    plan_hotspot = plan.get("hotspot_data", "0")
                    if plan_hotspot == "Unlimited":
                        plan_hotspot = "1000"  # Effectively unlimited
                    
                    champion_hotspot_val = 0
                    if champion_hotspot == "Unlimited":
                        champion_hotspot_val = 1000
                    else:
                        try:
                            champion_hotspot_val = float(champion_hotspot)
                        except (ValueError, TypeError):
                            pass
                    
                    plan_hotspot_val = 0
                    try:
                        plan_hotspot_val = float(plan_hotspot)
                    except (ValueError, TypeError):
                        pass
                    
                    if plan_hotspot_val > champion_hotspot_val:
                        improvement = min(2, (plan_hotspot_val - champion_hotspot_val) / 10)
                        feature_score += improvement
                except (ValueError, TypeError):
                    pass
                
                # International countries improvement
                plan_countries = plan.get("international_countries", "")
                champion_countries = champion_plan.get("international_countries", "")
                
                if plan_countries and (not champion_countries or len(plan_countries) > len(champion_countries)):
                    feature_score += 1
                
                # If this plan has a better feature score, choose it
                if feature_score > best_feature_score:
                    best_feature_score = feature_score
                    best_feature_plan = plan
                    best_feature_operator = op_name
                    
                    # Determine the primary reason
                    if plan["streamingQuality"] == "4K UHD" and champion_streaming != "4K UHD":
                        reason = "better streaming quality (4K UHD)"
                    elif float(plan.get("international_data", "0").replace("unlimited", "1000")) > float(champion_intl_data.replace("Unlimited", "1000")):
                        reason = "better international data allowance"
                    elif plan_hotspot_val > champion_hotspot_val:
                        reason = f"larger hotspot data allowance ({plan_hotspot_val}GB vs {champion_hotspot_val}GB)"
                    elif plan_countries and (not champion_countries or len(plan_countries) > len(champion_countries)):
                        reason = "wider international coverage"
                    else:
                        reason = "better overall feature set"
        
        if best_feature_plan and best_feature_score > 1:  # Only return if significant improvement
            return (best_feature_operator, best_feature_plan, reason)
    
    # For customer service complaints
    elif profile_type == "Customer Service":
        # Look for operators known for better customer service
        # For this simulation, we'll assume Operator T has better customer service
        service_operator = "Operator T"
        best_service_plan = None
        reason = "better customer service"
        
        if service_operator in operators:
            # Find a comparable plan from this operator
            for plan in operators[service_operator]["plans"]:
                # Skip if plan is significantly more expensive
                price = extract_price_numeric(plan["price"])
                if price > champion_price * 1.2:  # Allow up to 20% higher price
                    continue
                
                # For customers leaving due to service issues, match the market segment if possible
                if plan["marketSegment"] == champion_market_segment:
                    best_service_plan = plan
                    break
            
            # If no market segment match, just take the closest plan by price
            if not best_service_plan and operators[service_operator]["plans"]:
                best_service_plan = min(operators[service_operator]["plans"], 
                                      key=lambda p: abs(extract_price_numeric(p["price"]) - champion_price))
            
            if best_service_plan:
                return (service_operator, best_service_plan, reason)
    
    # For network quality issues
    elif profile_type == "Network Quality":
        # For rural areas, certain operators might have better coverage
        # For this simulation, we'll assume Operator T has better rural coverage
        network_operator = "Operator T"
        best_network_plan = None
        reason = "better network coverage in rural areas"
        
        if network_operator in operators:
            # Find a plan with unlimited data
            for plan in operators[network_operator]["plans"]:
                if plan["dataAllowance"] == "Unlimited":
                    # Skip if significantly more expensive
                    price = extract_price_numeric(plan["price"])
                    if price > champion_price * 1.2:  # Allow up to 20% higher price
                        continue
                    
                    best_network_plan = plan
                    break
            
            # If no unlimited data plan found, choose the best available
            if not best_network_plan and operators[network_operator]["plans"]:
                candidates = [p for p in operators[network_operator]["plans"] 
                             if extract_price_numeric(p["price"]) <= champion_price * 1.2]
                
                if candidates:
                    best_network_plan = max(candidates, 
                                           key=lambda p: p["dataAllowance"] if p["dataAllowance"] != "Unlimited" 
                                                      else float('inf'))
            
            if best_network_plan:
                return (network_operator, best_network_plan, reason)
    
    # For at-risk customers
    elif profile_type == "At Risk":
        # Find plans with better value
        best_value_plan = None
        best_value_operator = None
        best_value_score = -1
        reason = ""
        
        for op_name, op_data in operators.items():
            if op_name == "Operator B (champion)":
                continue
                
            for plan in op_data["plans"]:
                price = extract_price_numeric(plan["price"])
                
                # Skip if price is higher
                if price >= champion_price:
                    continue
                
                # Calculate value score
                value_score = 0
                
                # Price advantage
                price_ratio = champion_price / price if price > 0 else 1
                value_score += min(5, (price_ratio - 1) * 10)  # Up to 5 points for price
                
                # Data allowance
                if plan["dataAllowance"] == "Unlimited" and champion_data != "Unlimited":
                    value_score += 3
                
                # Better segment-specific benefits
                if plan["marketSegment"] == champion_market_segment:
                    value_score += 2
                
                if value_score > best_value_score:
                    best_value_score = value_score
                    best_value_plan = plan
                    best_value_operator = op_name
                    
                    # Calculate savings
                    savings = champion_price - price
                    if savings > 0:
                        reason = f"${savings:.2f} monthly savings with comparable features"
                    else:
                        reason = "better overall value"
        
        if best_value_plan and best_value_score > 2:  # Only return if significant value improvement
            return (best_value_operator, best_value_plan, reason)
    
    # No better plan found
    return (None, None, None)

def find_reasons_to_stay(profile_type, champion_plan, operators, usage_metrics):
    """
    Find reasons why the champion plan might be better than competitor offerings
    
    Args:
        profile_type (str): Customer profile type
        champion_plan (dict): Current Champion plan
        operators (dict): All operators and their plans
        usage_metrics (dict): Customer usage metrics
        
    Returns:
        str: Reason why the champion plan is better, or empty string if not
    """
    champion_price = extract_price_numeric(champion_plan["price"])
    champion_data = champion_plan["dataAllowance"]
    champion_streaming = champion_plan["streamingQuality"]
    champion_market_segment = champion_plan["marketSegment"]
    
    # Convert usage metrics to numerical values where needed
    data_download = float(usage_metrics["data_download"])
    intl_data_usage = float(usage_metrics["intl_data_upload"]) + float(usage_metrics["intl_data_download"])
    ott_usage = float(usage_metrics["ott_usage"])
    
    # Check if this is a "Best Value" plan
    if champion_plan.get("popularity", "") == "Best Value":
        return "optimum combination of price and features in our 'Best Value' plan"
    
    # Check if the plan has segment-specific benefits
    if champion_market_segment != "General":
        # See if competitors have comparable segment-specific plans
        has_comparable_segment_plan = False
        
        for op_name, op_data in operators.items():
            if op_name == "Operator B (champion)":
                continue
                
            for plan in op_data["plans"]:
                if plan["marketSegment"] == champion_market_segment:
                    has_comparable_segment_plan = True
                    break
            
            if has_comparable_segment_plan:
                break
        
        if not has_comparable_segment_plan:
            return f"exclusive benefits for {champion_market_segment.lower()} customers"
    
    # Check if this plan has unique streaming quality features
    if champion_streaming == "4K UHD":
        # Count how many competitor plans offer 4K UHD
        uhd_competitors = 0
        for op_name, op_data in operators.items():
            if op_name == "Operator B (champion)":
                continue
                
            for plan in op_data["plans"]:
                if plan["streamingQuality"] == "4K UHD":
                    uhd_competitors += 1
        
        if uhd_competitors == 0:
            return "exclusive 4K UHD streaming quality not offered by competitors"
        elif uhd_competitors <= 2:
            return "premium 4K UHD streaming quality offered by few competitors"
    
    # Check for price competitiveness
    if champion_data == "Unlimited":
        better_value_exists = False
        
        for op_name, op_data in operators.items():
            if op_name == "Operator B (champion)":
                continue
                
            for plan in op_data["plans"]:
                if plan["dataAllowance"] == "Unlimited" and extract_price_numeric(plan["price"]) < champion_price:
                    better_value_exists = True
                    break
            
            if better_value_exists:
                break
        
        if not better_value_exists:
            return "best price for unlimited data in the market"
    
    # Check for family/group plan advantages
    if "Family" in champion_plan["customerType"] or "CUG" in champion_plan["customerType"]:
        better_family_plan_exists = False
        
        for op_name, op_data in operators.items():
            if op_name == "Operator B (champion)":
                continue
                
            for plan in op_data["plans"]:
                if ("Family" in plan["customerType"] or "CUG" in plan["customerType"]) and extract_price_numeric(plan["price"]) < champion_price:
                    better_family_plan_exists = True
                    break
            
            if better_family_plan_exists:
                break
        
        if not better_family_plan_exists:
            return "best value multi-line family plan"
    
    # No specific advantage found
    return ""

def generate_dynamic_insight(record, operators, profile_type):
    """
    Generate dynamic customer insights based on profile type and actual plan comparisons
    
    Args:
        record (dict): Customer record
        operators (dict): All operators and their plans
        profile_type (str): Customer profile type
        
    Returns:
        str: Insight text
    """
    # Get basic customer info
    plan_name = record["Customer Plan Name"]
    plan_price = record["Price"]
    customer_type = record["productOffering.customerType"]
    market_segment = record["productOffering.market segment"]
    satisfaction = record["Satisfaction Score (Out of 5)"]
    complaints = record["Number of Compaints Raised"]
    cltv = record["CLTV"]
    churn_status = record["Churn Status"]
    churn_score = record["Churn Score"]
    location = record["Location.Geographic Place.GeographicState.name"]
    
    # Find the Champion plan in the operators data
    champion_plan = None
    for plan in operators["Operator B (champion)"]["plans"]:
        if plan["name"] == plan_name:
            champion_plan = plan
            break
    
    # If plan not found, use a generic approach
    if not champion_plan:
        champion_plan = {
            "name": plan_name,
            "price": plan_price,
            "customerType": customer_type,
            "marketSegment": market_segment,
            "dataAllowance": record["productOffering.data"],
            "streamingQuality": "HD"  # Default
        }
    
    # Create usage metrics
    usage_metrics = {
        "data_download": record["Product.Networkproduct.ConsumptionSummary.value (Data Download (In GB))"],
        "data_upload": record["Product.Networkproduct.ConsumptionSummary.value (Data Upload (In GB))"],
        "voice_minutes": record["Product.Networkproduct.ConsumptionSummary.value Voice (in Minutes)"],
        "sms_count": record["Product.Networkproduct.ConsumptionSummary.value (SMS (In Numbers))"],
        "intl_voice": record["Product.Networkproduct.ConsumptionSummary.value (International Roaming Voice (In Minutes)"],
        "intl_data_upload": record["Product.Networkproduct.ConsumptionSummary.value (International Roaming Data Upload (In GB))"],
        "intl_data_download": record["Product.Networkproduct.ConsumptionSummary.value (International Romaing Data Download (In GB))"],
        "intl_sms": record["Product.Networkproduct.ConsumptionSummary.value (International Romaing SMS)"],
        "ott_usage": record["Product.Networkproduct.ConsumptionSummary.value (Consumed OTT usage (In GB))"]
    }
    
    # Generate insight based on profile type and churn status
    if churn_status == "Churned":
        # Find better competitor plan
        better_operator, better_plan, reason = find_better_competitor_plan(
            profile_type, champion_plan, operators, usage_metrics
        )
        
        if better_operator and better_plan:
            if profile_type == "Price Sensitive":
                return f"**Price-Sensitive Churn Insight:** Customer churned from Operator B (Champion)'s \"{plan_name}\" (${plan_price}) due to price sensitivity. Analysis suggests they likely switched to {better_operator}'s \"{better_plan['name']}\" which offers {reason} while still providing sufficient data for their usage pattern ({usage_metrics['data_download']}GB monthly)."
            
            elif profile_type == "Feature Deficiency":
                return f"**Feature Deficiency Churn Insight:** Customer churned from Operator B (Champion)'s \"{plan_name}\" {customer_type} plan due to feature limitations despite acceptable satisfaction score ({satisfaction}/5). Analysis shows heavy international usage ({usage_metrics['intl_voice']} minutes, {float(usage_metrics['intl_data_upload']) + float(usage_metrics['intl_data_download']):.2f}GB total international data) and high OTT consumption ({usage_metrics['ott_usage']}GB), suggesting they switched to {better_operator}'s \"{better_plan['name']}\" which offers {reason}."
            
            elif profile_type == "Customer Service":
                return f"**Customer Service Churn Insight:** This customer churned primarily due to service quality issues, evidenced by the extremely low satisfaction score ({satisfaction}/5) and high number of complaints ({complaints}) over a {record['Length of customer relationship (In Months)']}-month relationship. Despite subscribing to Operator B (Champion)'s premium \"{plan_name}\" plan, they likely switched to {better_operator}'s \"{better_plan['name']}\" which offers {reason}."
            
            elif profile_type == "Network Quality":
                return f"**Network Quality Churn Insight:** This high-value customer (${cltv} CLTV) churned despite subscribing to Operator B (Champion)'s premium \"{plan_name}\" plan due to network issues in {location}. Their extremely high data usage ({usage_metrics['data_download']}GB download) and significant OTT consumption ({usage_metrics['ott_usage']}GB) suggests streaming and connectivity problems in their area. They likely switched to {better_operator}'s \"{better_plan['name']}\" which offers {reason}."
        else:
            # Fallback to standard insights if no specific competitor plan was identified
            return customer_insights[profile_type](record)
    
    elif churn_status == "At Risk":
        # Find better competitor plan that might tempt them
        better_operator, better_plan, reason = find_better_competitor_plan(
            "At Risk", champion_plan, operators, usage_metrics
        )
        
        if better_operator and better_plan:
            return f"**At-Risk Customer Insight:** This medium-value customer (${cltv} CLTV) shows moderate churn risk (Score: {churn_score}) despite having no immediate issues. The moderate satisfaction score ({satisfaction}/5) and average complaints ({complaints}) indicate potential dissatisfaction with value received for the ${plan_price} price point for Operator B (Champion)'s \"{plan_name}\" plan. {better_operator}'s \"{better_plan['name']}\" offers {reason}, making this customer vulnerable to targeted competitor offers."
        else:
            return f"**At-Risk Customer Insight:** This customer shows moderate churn risk (Score: {churn_score}) despite reasonable satisfaction ({satisfaction}/5). Their ${cltv} CLTV and usage pattern suggest they could be exploring competitor offers or experiencing undocumented service issues. Proactive retention offering should focus on plan benefits and service improvements."
    
    else:  # Loyal customer
        # Find reasons why the champion plan might be better
        loyalty_reason = find_reasons_to_stay(profile_type, champion_plan, operators, usage_metrics)
        
        if loyalty_reason:
            return f"**Loyal Customer Insight:** This high-value {customer_type.lower()} plan customer (${cltv} CLTV) shows strong loyalty indicators with excellent satisfaction ({satisfaction}/5) and minimal complaints ({complaints}) despite heavy usage across all services. They fully utilize the premium features of Operator B (Champion)'s \"{plan_name}\" plan including high data consumption ({usage_metrics['data_download']}GB), international usage, and extensive OTT streaming ({usage_metrics['ott_usage']}GB). Our analysis indicates they value the {loyalty_reason}, which competitors cannot easily match."
        else:
            return f"**Loyal Customer Insight:** This high-value {customer_type.lower()} plan customer (${cltv} CLTV) shows strong loyalty indicators with excellent satisfaction ({satisfaction}/5) and minimal complaints ({complaints}) despite heavy usage across all services. They fully utilize the premium features of Operator B (Champion)'s \"{plan_name}\" plan including high data consumption ({usage_metrics['data_download']}GB), international usage, and extensive OTT streaming ({usage_metrics['ott_usage']}GB), justifying the premium price point."
            
# Customer insights based on profile type (fallback options)
customer_insights = {
    "Price Sensitive": lambda record: f"**Price-Sensitive Churn Insight:** Customer churned from Operator B (Champion)'s \"{record['Customer Plan Name']}\" (${record['Price']}) due to price sensitivity. Analysis suggests they likely switched to Operator C's \"$15 Smartphone Plan\" which offers similar basic functionality at a significantly lower price point ($15 vs ${record['Price']}).",
    
    "Feature Deficiency": lambda record: f"**Feature Deficiency Churn Insight:** Customer churned from Operator B (Champion)'s \"{record['Customer Plan Name']}\" {record['productOffering.customerType']} plan due to feature limitations despite acceptable satisfaction score ({record['Satisfaction Score (Out of 5)']}/5). Analysis shows heavy international usage ({record['Product.Networkproduct.ConsumptionSummary.value (International Roaming Voice (In Minutes)']} minutes, {float(record['Product.Networkproduct.ConsumptionSummary.value (International Roaming Data Upload (In GB))']) + float(record['Product.Networkproduct.ConsumptionSummary.value (International Romaing Data Download (In GB))']):.2f}GB total international data) and high OTT consumption ({record['Product.Networkproduct.ConsumptionSummary.value (Consumed OTT usage (In GB))']}GB), suggesting they switched to Operator T's \"Go5G Plus 55\" plan which offers better international coverage and streaming quality.",
    
    "Customer Service": lambda record: f"**Customer Service Churn Insight:** This customer churned primarily due to service quality issues, evidenced by the extremely low satisfaction score ({record['Satisfaction Score (Out of 5)']}/5) and high number of complaints ({record['Number of Compaints Raised']}) over a {record['Length of customer relationship (In Months)']}-month relationship. Despite subscribing to Operator B (Champion)'s premium \"{record['Customer Plan Name']}\" plan, they likely switched to Operator T's \"Go5G Military\" plan which offers dedicated customer care and comparable features.",
    
    "Network Quality": lambda record: f"**Network Quality Churn Insight:** This high-value customer (${record['CLTV']} CLTV) churned despite subscribing to Operator B (Champion)'s premium \"{record['Customer Plan Name']}\" plan due to network issues in {record['Location.Geographic Place.GeographicState.name']}. Their extremely high data usage ({record['Product.Networkproduct.ConsumptionSummary.value (Data Download (In GB))']}GB download) and significant OTT consumption ({record['Product.Networkproduct.ConsumptionSummary.value (Consumed OTT usage (In GB))']}GB) suggests streaming and connectivity problems in their area. They likely switched to Operator T's \"Operator T 5G unlimited\" plan, which has better rural coverage.",
    
    "Loyal Customer": lambda record: f"**Loyal Customer Insight:** This high-value {record['productOffering.customerType'].lower()} plan customer (${record['CLTV']} CLTV) shows strong loyalty indicators with excellent satisfaction ({record['Satisfaction Score (Out of 5)']}/5) and minimal complaints ({record['Number of Compaints Raised']}) despite heavy usage across all services. They fully utilize the premium features of Operator B (Champion)'s \"{record['Customer Plan Name']}\" plan including high data consumption ({record['Product.Networkproduct.ConsumptionSummary.value (Data Download (In GB))']}GB), international usage, and extensive OTT streaming ({record['Product.Networkproduct.ConsumptionSummary.value (Consumed OTT usage (In GB))']}GB), justifying the premium price point. They have not been tempted by Operator A or Operator T's competing family plans.",
    
    "At Risk": lambda record: f"**At-Risk Customer Insight:** This medium-value customer (${record['CLTV']} CLTV) shows moderate churn risk (Score: {record['Churn Score']}) despite having no immediate issues. The moderate satisfaction score ({record['Satisfaction Score (Out of 5)']}/5) and average complaints ({record['Number of Compaints Raised']}) indicate potential dissatisfaction with value received for the ${record['Price']} price point for Operator B (Champion)'s \"{record['Customer Plan Name']}\" plan. Competitor Operator T offers \"Go5G Military\" plan with better military discounts at $30, making this customer vulnerable to targeted competitor offers."
}

def select_appropriate_plan(profile_type, all_plans, is_churned=False):
    """
    Select a plan appropriate for the customer profile and churn status
    
    Args:
        profile_type (str): Customer profile type
        all_plans (list): List of all available plans
        is_churned (bool): Whether the customer is churned
        
    Returns:
        dict: Selected plan
    """
    # Make sure we have plans to choose from
    if not all_plans:
        return None
    
    # Convert all prices to numeric for easier comparison
    for plan in all_plans:
        if "numeric_price" not in plan:
            plan["numeric_price"] = extract_price_numeric(plan["price"])
    
    # Group plans by price tiers
    budget_plans = [p for p in all_plans if p["numeric_price"] < 50]
    mid_range_plans = [p for p in all_plans if 50 <= p["numeric_price"] < 80]
    premium_plans = [p for p in all_plans if p["numeric_price"] >= 80]
    
    # Choose plan based on profile type and churn status
    if profile_type == "Price Sensitive":
        # Price sensitive customers would choose budget plans and are likely to churn if they had premium plans
        if is_churned:
            # They churned, so likely they had a more expensive plan
            candidate_plans = mid_range_plans + premium_plans
            if candidate_plans:
                return random_choice(candidate_plans)
        else:
            # They haven't churned, so they likely have a budget plan
            if budget_plans:
                return random_choice(budget_plans)
    
    elif profile_type == "Feature Deficiency":
        # Feature-focused customers care about quality, are likely to churn from basic plans
        if is_churned:
            # They churned, so likely had a plan with poor features
            candidate_plans = [p for p in all_plans if p["streamingQuality"] != "4K UHD" 
                              and p.get("international_data", "0") == "0"]
            if candidate_plans:
                return random_choice(candidate_plans)
        else:
            # They haven't churned, so likely have a feature-rich plan
            candidate_plans = [p for p in all_plans if p["streamingQuality"] == "4K UHD" 
                              or p.get("international_data", "0") not in ["0", ""]]
            if candidate_plans:
                return random_choice(candidate_plans)
    
    elif profile_type == "Customer Service":
        # For service issues, churn is less dependent on plan type
        # For this case, we'll assume higher-paying customers are more likely to complain
        if is_churned:
            # They churned due to service, probably had a premium plan and were disappointed
            if premium_plans or mid_range_plans:
                return random_choice(premium_plans + mid_range_plans)
        # Non-churned can have any plan
    
    elif profile_type == "Network Quality":
        # Network quality issues affect high-usage customers most
        if is_churned:
            # They churned due to network issues, probably had a premium unlimited plan
            unlimited_plans = [p for p in all_plans if p["dataAllowance"] == "Unlimited"]
            if unlimited_plans:
                return random_choice(unlimited_plans)
        else:
            # Non-churned could have any plan, but likely premium
            if premium_plans:
                return random_choice(premium_plans)
    
    elif profile_type == "Loyal Customer":
        # Loyal customers are typically on value plans or premium plans they like
        best_value_plans = [p for p in all_plans if p.get("popularity", "") == "Best Value"]
        if best_value_plans:
            return random_choice(best_value_plans)
        elif premium_plans:
            return random_choice(premium_plans)
    
    elif profile_type == "At Risk":
        # At risk customers could have any plan but might be more sensitive to mid-range value
        if mid_range_plans:
            return random_choice(mid_range_plans)
    
    # Fallback: return a random plan
    return random_choice(all_plans)

def generate_synthetic_record(profile_type, is_churned=False, operators=None):
    """Generate a synthetic telecom customer record based on profile type"""
    
    # Select profile
    profile = next((p for p in customer_profiles if p["type"] == profile_type), None)
    if not profile:
        raise ValueError(f"Unknown profile type: {profile_type}")
    
    # Determine operator and plan
    is_champion_customer = True  # For this example, all customers are with the champion
    operator_name = "Operator B (champion)"
    
    # Check if operators dictionary has the champion operator
    if operators and "Operator B (champion)" in operators and operators["Operator B (champion)"]["plans"]:
        all_available_plans = operators["Operator B (champion)"]["plans"]
    else:
        # Fallback to default plans
        default_operators = get_default_operators()
        all_available_plans = default_operators["Operator B (champion)"]["plans"]
    
    # Use the new plan selection function to pick a more appropriate plan
    selected_plan = select_appropriate_plan(profile_type, all_available_plans, is_churned)
    
    # Fallback in case no plan was selected
    if not selected_plan and all_available_plans:
        selected_plan = random_choice(all_available_plans)
    
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

def generate_multiple_records(count=10, operators=None):
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
    
    # Make sure we have a variety of plans per profile type
    profile_plan_counter = {
        "Price Sensitive": set(),
        "Feature Deficiency": set(),
        "Customer Service": set(),
        "Network Quality": set(),
        "At Risk": set(),
        "Loyal Customer": set()
    }
    
    # Ensure variety in customer distribution
    min_category_counts = {
        "churned": int(count * 0.4),  # At least 40% churned
        "at_risk": int(count * 0.1),  # At least 10% at risk
        "loyal": int(count * 0.1)     # At least 10% loyal
    }
    
    category_counts = {
        "churned": 0,
        "at_risk": 0,
        "loyal": 0
    }
    
    for i in range(count):
        # Determine if this customer is churned, with proper distribution
        if category_counts["churned"] < min_category_counts["churned"]:
            category = "churned"
        elif category_counts["at_risk"] < min_category_counts["at_risk"]:
            category = "at_risk"
        elif category_counts["loyal"] < min_category_counts["loyal"]:
            category = "loyal"
        else:
            # Random distribution for remaining records
            category = random_choice(["churned", "churned", "at_risk", "loyal"])
        
        category_counts[category] += 1
        
        # Pick a profile type from the category
        if category == "churned":
            profile_type = random_choice(customer_distribution["churned"])
        else:
            profile_type = random_choice(customer_distribution[category])
        
        is_churned = category == "churned"
        
        # Generate the customer record
        record = generate_synthetic_record(profile_type, is_churned, operators)
        records.append(record)
        
        # Add to plan counter for this profile type
        profile_plan_counter[profile_type].add(record["Customer Plan Name"])
        
        # Generate dynamic customer insight using the new dynamic generator
        insight = {
            "account_id": record["Customer Billing Account.CustomerBillingAccount.ID"],
            "msisdn": record["Digital Identity.NetworkCredential.ID (MSISDN)"],
            "churn_status": record["Churn Status"],
            "profile_type": profile_type,
            "insight": generate_dynamic_insight(record, operators, profile_type)
        }
        insights.append(insight)
    
    # Print distribution summary
    print(f"\nGenerated {len(records)} records with distribution:")
    print(f"  - Churned: {category_counts['churned']} ({category_counts['churned']/count*100:.1f}%)")
    print(f"  - At Risk: {category_counts['at_risk']} ({category_counts['at_risk']/count*100:.1f}%)")
    print(f"  - Loyal: {category_counts['loyal']} ({category_counts['loyal']/count*100:.1f}%)")
    
    # Print profile-plan variety
    print("\nPlan variety by profile type:")
    for profile, plans in profile_plan_counter.items():
        if plans:  # Only print profiles that were actually used
            print(f"  - {profile}: {len(plans)} different plans")
    
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
    
    # Use utf-8 encoding explicitly
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    
    print(f"Saved {len(records)} records to {filename}")
    return filename

def sanitize_text(text):
    """Remove or replace special characters that might cause encoding issues"""
    # Replace special trademark/registered symbols with plain text equivalents
    text = text.replace("®", "(R)").replace("℠", "(SM)").replace("™", "(TM)")
    return text

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
    
    # Use utf-8 encoding explicitly
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(insights)
    
    print(f"Saved {len(insights)} insights to {filename}")
    return filename

def main():
    """Main function to generate and save synthetic telecom data"""
    
    # Set random seed for reproducibility (comment out for truly random data each time)
    # random.seed(42)
    
    # Try to load plans from CSV
    plan_repo_csv = "syn_new_planrepo_6.csv"
    print(f"Attempting to load plans from {plan_repo_csv}...")
    
    try:
        operators = load_plans_from_csv(plan_repo_csv)
        print(f"Successfully loaded plans from {plan_repo_csv}")
        
        # Print summary of loaded plans
        plan_count = 0
        for operator, data in operators.items():
            operator_plan_count = len(data["plans"])
            plan_count += operator_plan_count
            print(f"  - {operator}: {operator_plan_count} plans")
        
        print(f"Total plans loaded: {plan_count}")
        
    except Exception as e:
        print(f"Error loading plans from CSV: {e}")
        print("Using default plans instead.")
        operators = get_default_operators()
    
    # Let user specify number of records if desired
    default_record_count = 30
    try:
        user_input = input(f"Number of records to generate (default: {default_record_count}): ")
        record_count = int(user_input) if user_input.strip() else default_record_count
    except ValueError:
        print("Invalid input. Using default value.")
        record_count = default_record_count
    
    # Generate synthetic records using the loaded or default operators
    print(f"Generating {record_count} synthetic telecom customer records...")
    print("This may take a moment...")
    records, insights = generate_multiple_records(record_count, operators)
    
    # Generate statistics
    profile_counts = {}
    churn_counts = {"Churned": 0, "At Risk": 0, "Not Churned": 0}
    plan_counts = {}
    
    for record in records:
        # Count by profile type from insights matching this record
        for insight in insights:
            if insight["account_id"] == record["Customer Billing Account.CustomerBillingAccount.ID"]:
                profile_type = insight["profile_type"]
                profile_counts[profile_type] = profile_counts.get(profile_type, 0) + 1
                break
        
        # Count by churn status
        churn_status = record["Churn Status"]
        churn_counts[churn_status] = churn_counts.get(churn_status, 0) + 1
        
        # Count by plan
        plan_name = record["Customer Plan Name"]
        plan_counts[plan_name] = plan_counts.get(plan_name, 0) + 1
    
    # Save records and insights to CSV files
    records_file = save_records_to_csv(records)
    insights_file = save_insights_to_csv(insights)
    print("\n=== Generation complete! ===")
    print(f"Records saved to: {records_file}")
    print(f"Insights saved to: {insights_file}")
    
    # Print statistics
    print("\n=== Dataset Statistics ===")
    print(f"Total records: {len(records)}")
    
    print("\nProfile Distribution:")
    for profile, count in profile_counts.items():
        print(f"  - {profile}: {count} ({(count/len(records)*100):.1f}%)")
    
    print("\nChurn Status Distribution:")
    for status, count in churn_counts.items():
        print(f"  - {status}: {count} ({(count/len(records)*100):.1f}%)")
    
    print("\nPlan Distribution:")
    for plan, count in sorted(plan_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {plan}: {count} ({(count/len(records)*100):.1f}%)")
    
    # Check if Streamlit dashboard exists and remind user
    dashboard_file = "consolidated_telecom_dashboard_bkup.py"
    if os.path.exists(dashboard_file):
        print("\nTo visualize this data, run the Streamlit dashboard with:")
        print(f"  streamlit run {dashboard_file}")
    
    # If batch file exists, mention it
    batch_file = "launch_consolidated_dashboard.bat"
    if os.path.exists(batch_file):
        print(f"Or double-click the '{batch_file}' file to launch the dashboard.")

if __name__ == "__main__":
    main()