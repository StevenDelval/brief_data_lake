import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobServiceClient, generate_container_sas,BlobSasPermissions

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
container_name = os.environ.get('CONTAINER_NAME')
airbnb_dir_name = os.environ.get('AIRBNB_DIR_NAME')
hf_dir_name = os.environ.get('HUGGING_FACE_DIR_NAME')

# Authenticate with Key Vault
credential_sp_key_vault = ClientSecretCredential(tenant_id, client_id_sp_key_vault, client_secret_sp_key_vault)
client_key_vault = SecretClient(vault_url=key_vault_url, credential=credential_sp_key_vault)

# Get secret value
client_secret_sp_datalake = client_key_vault.get_secret(secret_name)._value

# Authenticate with Azure Storage
credential_sp_data_lake = ClientSecretCredential(tenant_id, client_id_sp_data_lake, client_secret_sp_datalake)
blob_service_client = BlobServiceClient(
    account_url=f"https://{data_lake_name}.blob.core.windows.net/",
    credential=credential_sp_data_lake
)

# SAS Token generation
start_time = datetime.now()
expiry_time = start_time + timedelta(minutes=10)
user_delegation_key = blob_service_client.get_user_delegation_key(start_time, expiry_time)

sas_token = generate_container_sas(
    account_name=data_lake_name,
    container_name=f"{container_name}/{airbnb_dir_name}",
    user_delegation_key=user_delegation_key,  # Pass the UserDelegationKey here
    expiry=expiry_time,
    permission=BlobSasPermissions(read=True,write=True)
)


# Upload the CSV file
local_csv_path = "reviews.csv"
client_with_sas = BlobServiceClient(
            account_url=f"https://{data_lake_name}.blob.core.windows.net/",
            credential=sas_token
            )

container_client = client_with_sas.get_container_client(container_name)
with open(local_csv_path, "rb") as data:
    container_client.upload_blob(local_csv_path,data, overwrite=True)