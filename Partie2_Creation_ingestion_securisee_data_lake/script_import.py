import os
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

# Define the name of the file to be uploaded
file_name = "reviews6.csv"
file_client = dl_client_sas.get_file_client(file_name)

# Upload the file to the Data Lake directory
with open(file_name, 'rb') as file_data:
    file_client.upload_data(file_data, overwrite=True)