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
  username      = var.username
  password      = var.password

  default_tags {
    tags = {
      environment     = var.environment
      deployment_mode = "terraform"
    }
  }
}

