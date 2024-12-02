variable "resource_group_location" {
  type        = string
  default     = "francecentral"
  description = "Location of the resource group."
}

variable "resource_group_name" {
  type        = string
  description = "The resource group name."
}

variable "data_lake_name" {
  type        = string
  description = "The data lake resource name."
}

