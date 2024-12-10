variable "endpoint" {
  description = "OpenNebula RPC2 endpoint"
  type        = string
}

variable "flow_endpoint" {
  description = "OpenNebula flow endpoint"
  type        = string
}

variable "username" {
  description = "Username for OpenNebula"
  type        = string
}

variable "password" {
  description = "Password for OpenNebula"
  type        = string
  sensitive   = true
}

variable "template_id" {
  description = "ID of the VM template"
  type        = number
  nullable    = false
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "op_group" {
  description = "Deployment group"
  type        = string
}

