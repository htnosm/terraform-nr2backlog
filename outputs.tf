output "backlog" {
  value = {
    PROJECT              = "${var.backlog["PROJECT_KEY"]} (${local.BACKLOG_PROJECT_ID})"
    ISSUE_TYPE           = "${var.backlog["ISSUE_TYPE"]} (${local.BACKLOG_ISSUE_TYPE_ID})"
    ISSUE_PRIORITY       = "${var.backlog["ISSUE_PRIORITY"]} (${local.BACKLOG_PRIORITY_ID})"
    ISSUE_CLOSE_STATUS   = "${var.backlog["ISSUE_CLOSE_STATUS"]} (${local.BACKLOG_CLOSE_STATUS_ID})"
    ISSUE_ASSIGNEE       = "${var.backlog_optional["ISSUE_ASSIGNEE"]} (${local.BACKLOG_ISSUE_ASSIGNEE_ID})"
    ISSUE_NOTIFIED_USERS = "${local.ISSUE_NOTIFIED_USERS} (${local.ISSUE_NOTIFIED_USER_IDS})"
  }
}
