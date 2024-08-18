variable "newrelic_account_id" {
  description = "Your New Relic account ID."
  type        = number
}

variable "newrelic_api_key" {
  description = "Your New Relic User API key (usually prefixed with NRAK)."
  type        = string
}

variable "resource_prefix" {
  description = "The prefix to use for all resources."
  type        = string
  default     = "nr2backlog"
}

variable "default_tags" {
  description = "The tags that will be associated with the entity."
  type = list(object({
    key    = string
    values = list(string)
  }))
  default = [
    {
      key    = "managedBy"
      values = ["terraform"]
    },
  ]
}

variable "aws_account_id" {
  description = "EVENT_BRIDGE: The account id to integrate to."
  type        = string
}

variable "aws_region" {
  description = "EVENT_BRIDGE: The AWS region this account is in."
  type        = string
}

variable "aws_account_name" {
  description = "EVENT_BRIDGE: The account name to integrate to."
  type        = string
  default     = null
}
