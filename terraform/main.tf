terraform {
  required_providers {
    opennebula = {
      source  = "OpenNebula/opennebula"
      version = "~> 1.4"
    }
  }
}

provider "opennebula" {
  endpoint      = var.endpoint
  flow_endpoint = var.flow_endpoint
  username      = var.username
  password      = var.password
  insecure      = true

  default_tags {
    tags = {
      environment     = var.environment
      deployment_mode = "terraform"
    }
  }
}

