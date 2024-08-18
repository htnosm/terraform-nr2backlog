variable "event_bus_name" {
  description = "The name of the new event bus."
  type        = string
}

variable "resource_prefix" {
  description = "The prefix to use for all resources."
  type        = string
  default     = "nr2backlog"
}

variable "backlog" {
  description = "Backlog parameters"
  type = object({
    DOMAIN             = string
    API_KEY            = string
    PROJECT_KEY        = string
    ISSUE_TYPE         = string
    ISSUE_CLOSE_STATUS = string
    ISSUE_PRIORITY     = string
  })
}

variable "backlog_optional" {
  description = "Backlog optional parameters"
  type = object({
    ISSUE_ASSIGNEE       = optional(string, "")
    ISSUE_NOTIFIED_USERS = optional(list(string), [])
  })
  default = {}
}
