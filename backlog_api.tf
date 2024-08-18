locals {
  BACKLOG_URL = "https://${var.backlog["DOMAIN"]}/api/v2"
}

# https://developer.nulab.com/ja/docs/backlog/api/2/get-project/
data "http" "backlog_project" {
  url = "${local.BACKLOG_URL}/projects/${var.backlog["PROJECT_KEY"]}?apiKey=${var.backlog["API_KEY"]}"
  request_headers = {
    Accept = "application/json"
  }
}

# https://developer.nulab.com/ja/docs/backlog/api/2/get-issue-type-list/
data "http" "backlog_issue_types" {
  url = "${local.BACKLOG_URL}/projects/${local.BACKLOG_PROJECT_ID}/issueTypes?apiKey=${var.backlog["API_KEY"]}"
  request_headers = {
    Accept = "application/json"
  }
}

# https://developer.nulab.com/ja/docs/backlog/api/2/get-priority-list/
data "http" "backlog_priorities" {
  url = "${local.BACKLOG_URL}/priorities?apiKey=${var.backlog["API_KEY"]}"
  request_headers = {
    Accept = "application/json"
  }
}

# https://developer.nulab.com/ja/docs/backlog/api/2/get-status-list-of-project/
data "http" "backlog_statuses" {
  url = "${local.BACKLOG_URL}/projects/${local.BACKLOG_PROJECT_ID}/statuses?apiKey=${var.backlog["API_KEY"]}"
  request_headers = {
    Accept = "application/json"
  }
}

# https://developer.nulab.com/ja/docs/backlog/api/2/get-project-user-list/
data "http" "backlog_project_users" {
  url = "${local.BACKLOG_URL}/projects/${local.BACKLOG_PROJECT_ID}/users?apiKey=${var.backlog["API_KEY"]}"
  request_headers = {
    Accept = "application/json"
  }
}

locals {
  BACKLOG_PROJECT_ID      = jsondecode(data.http.backlog_project.response_body).id
  BACKLOG_ISSUE_TYPES     = jsondecode(data.http.backlog_issue_types.response_body)
  BACKLOG_ISSUE_TYPE_ID   = one([for issue_type in local.BACKLOG_ISSUE_TYPES : issue_type.id if issue_type.name == var.backlog["ISSUE_TYPE"]])
  BACKLOG_PRIORITIES      = jsondecode(data.http.backlog_priorities.response_body)
  BACKLOG_PRIORITY_ID     = one([for priority in local.BACKLOG_PRIORITIES : priority.id if priority.name == var.backlog["ISSUE_PRIORITY"]])
  BACKLOG_STATUSES        = jsondecode(data.http.backlog_statuses.response_body)
  BACKLOG_CLOSE_STATUS_ID = one([for status in local.BACKLOG_STATUSES : status.id if status.name == var.backlog["ISSUE_CLOSE_STATUS"]])

  BACKLOG_PROJECT_USERS      = jsondecode(data.http.backlog_project_users.response_body)
  _BACKLOG_ISSUE_ASSIGNEE_ID = one([for user in local.BACKLOG_PROJECT_USERS : user.id if user.name == var.backlog_optional["ISSUE_ASSIGNEE"]])
  BACKLOG_ISSUE_ASSIGNEE_ID  = local._BACKLOG_ISSUE_ASSIGNEE_ID == null ? "" : local._BACKLOG_ISSUE_ASSIGNEE_ID
  ISSUE_NOTIFIED_USERS       = join(",", var.backlog_optional["ISSUE_NOTIFIED_USERS"])
  ISSUE_NOTIFIED_USER_IDS    = join(",", [for user in local.BACKLOG_PROJECT_USERS : user.id if contains(var.backlog_optional["ISSUE_NOTIFIED_USERS"], user.name)])
}
