import os
import requests
import pandas as pd
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.filedatalake import (
    DataLakeServiceClient,
    DataLakeDirectoryClient,
    generate_directory_sas,
    DirectorySasPermissions,
)

def get_reviews_csv_url(country: str = "spain") -> list | None:
    """
    Fetches all review CSV URLs for a specified country from the Inside Airbnb data page.

    Args:
        country (str): The name of the country to filter URLs for (default is "spain").

    Returns:
        list | None: 
            - A list of URLs (strings) pointing to review CSV files for the specified country.
            - Returns None if the HTTP request fails.

    Example:
        >>> get_reviews_csv_url("spain")
        ['https://data.insideairbnb.com/spain/barcelona/2024-01-01/data/reviews.csv',
         'https://data.insideairbnb.com/spain/madrid/2024-01-01/data/reviews.csv']

    Notes:
        - This function relies on the structure of the Inside Airbnb data page.
        - It uses BeautifulSoup to parse HTML and filters `<a>` tags based on `href` attributes.
        - The HTTP status of the response is checked before processing.
    """
    # Target page URL
    url = "https://insideairbnb.com/get-the-data/"
    # Make an HTTP request to get the page content
    response = requests.get(url)
    if response.status_code == 200:
        # Parse the HTML content of the page with BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Find all <a> tags on the page
        links = soup.find_all("a", href=True)
        
        # Filter links that start with the prefix and end with reviews.csv
        hrefs = [
            link["href"] for link in links
            if link["href"].startswith(f"https://data.insideairbnb.com/{country}/") and link["href"].endswith("reviews.csv")
        ]
        
        return hrefs

def upload_reviews_csv_in_dl(csv_url: str, dl_client: DataLakeDirectoryClient) -> None:
    """
    Fetches a reviews CSV file from a specified URL, generates a descriptive filename 
    (including country, city, and date), and uploads its content to an Azure Data Lake.

    Args:
        csv_url (str): The URL of the reviews CSV file to fetch.
        dl_client (DataLakeDirectoryClient): The Azure DataLakeDirectoryClient representing 
            the target directory in the Azure Data Lake where the file will be uploaded.

    Returns:
        None: This function does not return any value.

    """
    try:
        # Parse the URL to extract components
        parsed_url = urlparse(csv_url)
        path_parts = parsed_url.path.strip("/").split("/")
        
        # Extract country, city, and date
        country = path_parts[0]
        city = path_parts[2]
        date = path_parts[3]
        
        # Generate a file name
        new_file_name = f"{country}_{city}_{date}_reviews.csv"
        file_client = dl_client.get_file_client(new_file_name)
        
        # Load the CSV from the provided URL into a Pandas DataFrame
        df = pd.read_csv(csv_url)
        
        # Convert the DataFrame to a CSV string
        file_data = df.to_csv(index=False)
        
        # Upload the CSV data to the Data Lake
        file_client.upload_data(file_data, overwrite=True)

    except Exception as e:
        print(f"An error occurred while uploading the file: {e}")

# Load environment variables from the .env file
load_dotenv()

# Extract required environment variables for authentication and configuration
tenant_id = os.environ.get('TENANT_ID')  # Azure tenant ID
client_id_sp_key_vault = os.environ.get('SP_ID_SECONDARY')  # Service principal ID for Key Vault access
client_secret_sp_key_vault = os.environ.get('SP_SECONDARY_PASSWORD')  # Secret for Key Vault service principal
key_vault_url = os.environ.get('KEYVAULT_URL')  # Azure Key Vault URL
secret_name = os.environ.get('SECRET_NAME')  # Name of the secret containing Data Lake credentials
client_id_sp_data_lake = os.environ.get('SP_ID_PRINCIPAL')  # Service principal ID for Data Lake access
data_lake_name = os.environ.get('STORAGE_ACCOUNT_NAME')  # Azure Storage account name
file_system_name = os.environ.get('FILE_SYSTEM_NAME')  # Azure Data Lake file system name
airbnb_dir_name = os.environ.get('AIRBNB_DIR_NAME')  # Directory name for Airbnb data
hf_dir_name = os.environ.get('HUGGING_FACE_DIR_NAME')  # Directory name for Hugging Face data

# Authenticate with Azure Key Vault using a service principal
credential_sp_key_vault = ClientSecretCredential(
    tenant_id, client_id_sp_key_vault, client_secret_sp_key_vault
)
client_key_vault = SecretClient(vault_url=key_vault_url, credential=credential_sp_key_vault)

# Retrieve the secret value (Data Lake service principal secret) from Key Vault
client_secret_sp_datalake = client_key_vault.get_secret(secret_name).value

# Authenticate with Azure Data Lake using the retrieved service principal credentials
credential_sp_data_lake = ClientSecretCredential(
    tenant_id, client_id_sp_data_lake, client_secret_sp_datalake
)
dl_service_client = DataLakeServiceClient(
    account_url=f"https://{data_lake_name}.dfs.core.windows.net/",
    credential=credential_sp_data_lake
)

# Generate a SAS token for the target directory
start_time = datetime.now(timezone.utc)  # SAS token start time
expiry_time = start_time + timedelta(hours=6)  # SAS token expiry time
user_delegation_key = dl_service_client.get_user_delegation_key(start_time, expiry_time)

sas_token = generate_directory_sas(
    account_name=data_lake_name,
    file_system_name=file_system_name,
    directory_name=airbnb_dir_name,
    credential=user_delegation_key,
    start=start_time,
    expiry=expiry_time,
    permission=DirectorySasPermissions(read=True, write=True),  # Allow read and write permissions
)

# Create a Data Lake directory client using the SAS token
dl_client_sas = DataLakeDirectoryClient(
    account_url=f"https://{data_lake_name}.dfs.core.windows.net/",
    file_system_name=file_system_name,
    directory_name=airbnb_dir_name,
    credential=sas_token
)

# Get the list of review CSV URLs for a specific country (e.g., "spain")
reviews_links = get_reviews_csv_url("spain")

for reviews in reviews_links:
    # Upload each review CSV file to the Azure Data Lake using the provided directory client
    upload_reviews_csv_in_dl(reviews, dl_client_sas)