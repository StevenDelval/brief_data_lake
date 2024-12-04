import os
from datetime import datetime, timedelta,timezone
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.filedatalake import DataLakeServiceClient,DataLakeDirectoryClient,generate_directory_sas,DirectorySasPermissions

# Load environment variables
load_dotenv()

# Environment variable extraction
tenant_id = os.environ.get('TENANT_ID')
client_id_sp_key_vault = os.environ.get('SP_ID_SECONDARY')
client_secret_sp_key_vault = os.environ.get('SP_SECONDARY_PASSWORD')
key_vault_url = os.environ.get('KEYVAULT_URL')
secret_name = os.environ.get('SECRET_NAME')
client_id_sp_data_lake = os.environ.get('SP_ID_PRINCIPAL')
data_lake_name = os.environ.get('STORAGE_ACCOUNT_NAME')
file_system_name = os.environ.get('FILE_SYSTEM_NAME')
airbnb_dir_name = os.environ.get('AIRBNB_DIR_NAME')
hf_dir_name = os.environ.get('HUGGING_FACE_DIR_NAME')

# Authenticate with Key Vault
credential_sp_key_vault = ClientSecretCredential(tenant_id, client_id_sp_key_vault, client_secret_sp_key_vault)
client_key_vault = SecretClient(vault_url=key_vault_url, credential=credential_sp_key_vault)

# Get secret value
client_secret_sp_datalake = client_key_vault.get_secret(secret_name)._value

# Authenticate with Azure Storage
credential_sp_data_lake = ClientSecretCredential(tenant_id, client_id_sp_data_lake, client_secret_sp_datalake)
dl_service_client = DataLakeServiceClient(
    account_url=f"https://{data_lake_name}.dfs.core.windows.net/",
    credential=credential_sp_data_lake
)

# SAS Token generation
start_time = datetime.now(timezone.utc)
expiry_time = start_time + timedelta(hours=6)
user_delegation_key = dl_service_client.get_user_delegation_key(start_time, expiry_time)

sas_token = generate_directory_sas(
    account_name=data_lake_name,
    file_system_name=file_system_name,
    directory_name=airbnb_dir_name,
    credential=user_delegation_key,
    start=start_time,
    expiry=expiry_time,
    permission=DirectorySasPermissions(read=True,write=True),
)

# Ensure the SAS token is passed in for the DataLakeDirectoryClient
dl_client_sas = DataLakeDirectoryClient(
    account_url=f"https://{data_lake_name}.dfs.core.windows.net/",
    file_system_name=file_system_name,
    directory_name=airbnb_dir_name,
    credential=sas_token  
)

# Get the DataLakeFileClient for the specific file
file_name = "reviews5.csv"
file_client = dl_client_sas.get_file_client(airbnb_dir_name+"/" +file_name)

# Upload the file with proper headers
with open(file_name, 'rb') as file_data:
    file_client.upload_data(file_data, overwrite=True)
