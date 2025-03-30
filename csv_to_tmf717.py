import csv
import json
import os
import sys
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("conversion_log.txt"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TMF717Converter:
    """
    Class to convert CSV data to TMF717 Customer 360 Management API JSON format
    """
    
    def __init__(self, input_file: str, output_dir: str = "tmf717"):
        """
        Initialize the converter with input and output paths
        
        Args:
            input_file: Path to the CSV input file
            output_dir: Directory for output JSON files
        """
        self.input_file = input_file
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def process_file(self) -> None:
        """Process the input CSV file and generate JSON output files"""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                # Try to detect the CSV dialect
                try:
                    dialect = csv.Sniffer().sniff(f.read(4096))
                    f.seek(0)
                except:
                    # If sniffer fails, default to comma delimiter
                    dialect = csv.excel
                    f.seek(0)
                
                # Read CSV with the detected dialect
                reader = csv.reader(f, dialect)
                
                # Extract headers from the first row
                try:
                    headers = next(reader)
                except StopIteration:
                    logger.error("Empty CSV file")
                    return
                
                # Process each row
                for i, row in enumerate(reader, 1):
                    try:
                        # Convert row to JSON and save
                        self.row_to_json(headers, row, i)
                    except Exception as e:
                        logger.error(f"Error processing row {i}: {str(e)}")
                        # Continue with next row instead of failing
                        continue
                
            logger.info(f"Conversion completed. Output files stored in {self.output_dir}")
        
        except FileNotFoundError:
            logger.error(f"Input file not found: {self.input_file}")
        except Exception as e:
            logger.error(f"Unexpected error processing file: {str(e)}")
    
    def row_to_json(self, headers: List[str], row: List[str], row_index: int) -> None:
        """
        Convert a single CSV row to TMF717 JSON and save to file
        
        Args:
            headers: List of column headers
            row: List of values for current row
            row_index: Index of the current row (for filename)
        """
        # Create a dictionary from headers and row values
        # Handle cases where row might be shorter than headers
        row_dict = {}
        for i, header in enumerate(headers):
            if i < len(row):
                row_dict[header] = row[i]
            else:
                # If row is missing values, set to empty string
                row_dict[header] = ""
        
        # Extract customer ID for filename
        try:
            customer_id = row_dict.get("Customer Billing Account.CustomerBillingAccount.ID", f"customer_{row_index}")
            if not customer_id:
                customer_id = f"customer_{row_index}"
            
            # Clean the ID for use as filename (remove invalid chars)
            clean_id = ''.join(c if c.isalnum() else '_' for c in customer_id)
            
            # Generate TMF717 JSON structure
            customer_360 = self.create_customer_360(row_dict)
            
            # Write to JSON file
            output_file = os.path.join(self.output_dir, f"{clean_id}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(customer_360, f, indent=2)
            
            logger.info(f"Created JSON for customer {customer_id}")
        
        except Exception as e:
            logger.error(f"Error converting row {row_index} to JSON: {str(e)}")
            raise
    
    def create_customer_360(self, row_dict: Dict[str, str]) -> Dict[str, Any]:
        """
        Create TMF717 Customer 360 structure from a row dictionary
        
        Args:
            row_dict: Dictionary mapping headers to row values
            
        Returns:
            Dict containing TMF717 Customer 360 structure
        """
        # Helper function to safely get value
        def safe_get(key: str, default: Any = "") -> Any:
            return row_dict.get(key, default) or default
        
        # Get key values
        customer_id = safe_get("Customer Billing Account.CustomerBillingAccount.ID")
        msisdn = safe_get("Digital Identity.NetworkCredential.ID (MSISDN)")
        
        # Create the base Customer 360 object
        customer_360 = {
            "id": customer_id,
            "href": f"/customer360/{customer_id}",
            "customerReferredId": customer_id,
            "customerReferredName": f"Customer {msisdn}",
            "status": safe_get("Subscription Status"),
            "statusReason": safe_get("Churn Status") == "At Risk" and "At Risk of Churn" or 
                           (safe_get("Churn Status") == "Churned" and safe_get("Reason Of Churn")) or "",
            "accountHierarchy": [
                {
                    "id": customer_id,
                    "href": f"/account/{customer_id}",
                    "name": "Main Account",
                    "referredType": "Account"
                }
            ],
            "associatedParty": [
                {
                    "id": msisdn,
                    "href": f"/individual/{msisdn}",
                    "role": "MainUser",
                    "name": f"Customer {msisdn}",
                    "referredType": "Individual"
                }
            ],
            "characteristic": self.create_characteristics(row_dict),
            "relatedEntity": self.create_related_entities(row_dict),
            "relatedParty": [
                {
                    "id": msisdn,
                    "href": f"/individual/{msisdn}",
                    "role": "owner",
                    "name": f"Customer {msisdn}",
                    "referredType": "Individual"
                }
            ],
            "contactMedium": [
                {
                    "mediumType": "mobileNumber",
                    "preferred": True,
                    "characteristic": {
                        "phoneNumber": msisdn
                    }
                }
            ],
            "validFor": {
                "startDateTime": safe_get("Customer Subscription Start Date"),
                "endDateTime": safe_get("Customer subscription end date") or None
            },
            "@baseType": "Customer360",
            "@schemaLocation": "https://tmforum.org/oda/open-apis/Customer360-v4.0.0.json",
            "@type": "Customer360"
        }
        
        return customer_360
    
    def create_characteristics(self, row_dict: Dict[str, str]) -> List[Dict[str, Any]]:
        """Create characteristic array from row data"""
        # Helper function to safely get value
        def safe_get(key: str, default: Any = "") -> Any:
            return row_dict.get(key, default) or default
            
        # Demographic characteristics
        characteristics = [
            {
                "name": "age",
                "valueType": "number",
                "value": safe_get("Party.Party Demographic.PartyDemographicValue.value(Age)")
            },
            {
                "name": "ageGroup",
                "valueType": "string",
                "value": safe_get("Age Group")
            },
            {
                "name": "gender",
                "valueType": "string",
                "value": safe_get("Party.Individual.gender")
            },
            {
                "name": "incomeLevel",
                "valueType": "string",
                "value": safe_get("Party.Party Demographic.PartyDemographicValue.value(Income Level)")
            },
            {
                "name": "education",
                "valueType": "string", 
                "value": safe_get("Party.Party Demographic.PartyDemographicValue.value(Education)")
            },
            {
                "name": "maritalStatus",
                "valueType": "string",
                "value": safe_get("Individual.maritalStatus (Family Structure)")
            },
            {
                "name": "vipStatus",
                "valueType": "string",
                "value": safe_get("VIP Group")
            },
            {
                "name": "churnScore",
                "valueType": "number",
                "value": safe_get("Churn Score")
            },
            {
                "name": "churnStatus",
                "valueType": "string",
                "value": safe_get("Churn Status")
            },
            {
                "name": "cltv",
                "valueType": "number",
                "value": safe_get("CLTV")
            },
            {
                "name": "satisfactionScore",
                "valueType": "number",
                "value": safe_get("Satisfaction Score (Out of 5)")
            },
            {
                "name": "noOfLines",
                "valueType": "number",
                "value": safe_get("No Of Lines")
            },
            {
                "name": "atRiskCustomer",
                "valueType": "boolean",
                "value": safe_get("At Risk Customer(Based on usage or behaviour patterns)") == "Yes"
            },
            {
                "name": "numberOfComplaints",
                "valueType": "number",
                "value": safe_get("Number of Compaints Raised")
            },
            {
                "name": "relationshipLengthMonths",
                "valueType": "number",
                "value": safe_get("Length of customer relationship (In Months)")
            },
            {
                "name": "timeSinceLastEngagementMonths",
                "valueType": "number",
                "value": safe_get("Time Since last purchase or engagement (In Months)")
            }
        ]
        
        # Add usage period
        characteristics.append({
            "name": "usagePeriod",
            "valueType": "object",
            "value": {
                "from": safe_get("Usage From Period"),
                "to": safe_get("Usage To Period")
            }
        })
        
        # Add consumption metrics
        consumption_metrics = [
            {"name": "dataUploadGB", "key": "Product.Networkproduct.ConsumptionSummary.value (Data Upload (In GB))"},
            {"name": "dataDownloadGB", "key": "Product.Networkproduct.ConsumptionSummary.value (Data Download (In GB))"},
            {"name": "voiceMinutes", "key": "Product.Networkproduct.ConsumptionSummary.value Voice (in Minutes)"},
            {"name": "smsCount", "key": "Product.Networkproduct.ConsumptionSummary.value (SMS (In Numbers))"},
            {"name": "roamingVoiceMinutes", "key": "Product.Networkproduct.ConsumptionSummary.value (International Roaming Voice (In Minutes)"},
            {"name": "roamingDataUploadGB", "key": "Product.Networkproduct.ConsumptionSummary.value (International Roaming Data Upload (In GB))"},
            {"name": "roamingDataDownloadGB", "key": "Product.Networkproduct.ConsumptionSummary.value (International Romaing Data Download (In GB))"},
            {"name": "roamingSmsCount", "key": "Product.Networkproduct.ConsumptionSummary.value (International Romaing SMS)"},
            {"name": "ottUsageGB", "key": "Product.Networkproduct.ConsumptionSummary.value (Consumed OTT usage (In GB))"},
            {"name": "cloudStorage", "key": "Product.Networkproduct.ConsumptionSummary.value (Cloud Storage)"}
        ]
        
        for metric in consumption_metrics:
            characteristics.append({
                "name": metric["name"],
                "valueType": "number",
                "value": safe_get(metric["key"])
            })
        
        # Add rating group
        characteristics.append({
            "name": "ratingGroup",
            "valueType": "string",
            "value": safe_get("Rating Group (Google, Youtube)")
        })
        
        # Add product offering details
        product_details = [
            {"name": "planType", "key": "productOffering.planType"},
            {"name": "businessType", "key": "productOffering.businessType"},
            {"name": "marketSegment", "key": "productOffering.market segment"},
            {"name": "customerType", "key": "productOffering.customerType"},
            {"name": "price", "key": "Price"},
            {"name": "activationFee", "key": "Activation Fee"},
            {"name": "contract", "key": "Contract"}
        ]
        
        for detail in product_details:
            characteristics.append({
                "name": detail["name"],
                "valueType": "number" if detail["name"] in ["price", "activationFee"] else "string",
                "value": safe_get(detail["key"])
            })
        
        # Add location
        characteristics.append({
            "name": "location",
            "valueType": "string",
            "value": safe_get("Location.Geographic Place.GeographicState.name")
        })
        
        # Add churn reason if present
        if safe_get("Reason Of Churn"):
            characteristics.append({
                "name": "churnReason",
                "valueType": "string",
                "value": safe_get("Reason Of Churn")
            })
        
        return characteristics
    
    def create_related_entities(self, row_dict: Dict[str, str]) -> List[Dict[str, Any]]:
        """Create related entities array from row data"""
        # Helper function to safely get value
        def safe_get(key: str, default: Any = "") -> Any:
            return row_dict.get(key, default) or default
            
        plan_id = safe_get("Plan ID")
        plan_name = safe_get("Customer Plan Name")
        msisdn = safe_get("Digital Identity.NetworkCredential.ID (MSISDN)")
        
        related_entities = [
            {
                "id": plan_id,
                "href": f"/productOffering/{plan_id}",
                "role": "SubscribedPlan",
                "name": plan_name,
                "referredType": "ProductOffering"
            },
            {
                "id": msisdn,
                "href": f"/productInstance/{msisdn}",
                "role": "SubscribedProduct",
                "name": "Mobile Service",
                "referredType": "Product"
            }
        ]
        
        return related_entities


def main():
    """Main entry point for the script"""
    if len(sys.argv) < 2:
        print("Usage: python csv_to_tmf717.py <input_csv_file> [output_directory]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "tmf717_output"
    
    converter = TMF717Converter(input_file, output_dir)
    converter.process_file()


if __name__ == "__main__":
    main()