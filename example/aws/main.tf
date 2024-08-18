terraform {
  required_version = ">= 1.9"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
    http = {
      source  = "hashicorp/http"
      version = ">= 3.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      "managedBy" = "terraform"
    }
  }
}

module "nr2backlog" {
  source = "../../"

  event_bus_name   = var.event_bus_name
  backlog          = var.backlog
  backlog_optional = var.backlog_optional
}
