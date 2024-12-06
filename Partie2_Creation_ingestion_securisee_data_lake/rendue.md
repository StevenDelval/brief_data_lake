

Pour créer les ressources :
```
terraform init 
terraform apply -var-file="terraform.tfvars"
```

Dans le fichier terraform.tfvars :
```
resource_group_name     = "RG_SDELVAL"
resource_group_location = "francecentral"
data_lake_name          = "sdelvaldatalake"
dl_filesystem_name      = "sddatastorage"
```

Dans le fichier .env :
```
SP_ID_SECONDARY="YOUR SP_ID_SECONDARY"
SP_SECONDARY_PASSWORD="YOUR SP_SECONDARY_SECRET"
SP_ID_PRINCIPAL="YOUR SP_ID_PRINCIPAL"
TENANT_ID="YOUR TENANT_ID"
KEYVAULT_URL="YOUR KEYVAULT_URL"
SECRET_NAME="YOUR SECRET_NAME"
STORAGE_ACCOUNT_NAME="sdelvaldatalake"
FILE_SYSTEM_NAME="sddatastorage"
AIRBNB_DIR_NAME="Airbnb_csv"
HUGGING_FACE_DIR_NAME="Hugging_Face_parquet"
```

Capture d'écran du Data Lake après l'exécution du script :
![image](img/resultal.script_import.png)