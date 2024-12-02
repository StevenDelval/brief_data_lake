resource "azurerm_resource_group" "rg" {
  location = var.resource_group_location
  name     = var.resource_group_name
}

resource "azurerm_storage_account" "data_lake" {
  name                     = var.data_lake_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  is_hns_enabled           = "true"
}

resource "azurerm_storage_data_lake_gen2_filesystem" "dl_filesystem" {
  name               = var.dl_filesystem_name
  storage_account_id = azurerm_storage_account.data_lake.id
}

resource "azurerm_storage_data_lake_gen2_path" "Airbnb_csv" {
  path               = "Airbnb_csv"
  filesystem_name    = azurerm_storage_data_lake_gen2_filesystem.dl_filesystem.name
  storage_account_id = azurerm_storage_account.data_lake.id
  resource           = "directory"
}

resource "azurerm_storage_data_lake_gen2_path" "Hugging_Face_parquet" {
  path               = "Hugging_Face_parquet"
  filesystem_name    = azurerm_storage_data_lake_gen2_filesystem.dl_filesystem.name
  storage_account_id = azurerm_storage_account.data_lake.id
  resource           = "directory"
}