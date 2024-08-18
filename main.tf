/**
 * # nr2backlog
 *
 * This module is for sending New Relic issues to Backlog.
 *
 * - As a prerequisite, the partner event source from New Relic must be associated with EventBridge.
 *
 */

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

data "aws_cloudwatch_event_bus" "this" {
  name = var.event_bus_name
}

resource "aws_cloudwatch_event_rule" "this" {
  event_bus_name = data.aws_cloudwatch_event_bus.this.name
  name           = var.resource_prefix
  description    = "Capture each New Relic issues"
  state          = "ENABLED"

  event_pattern = jsonencode({
    "source" : [{
      "prefix" : "aws.partner/newrelic.com"
    }]
  })

  tags = {
    Name = var.resource_prefix
  }
}

module "lambda_function" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.7.1"

  source_path = [
    {
      path = "${path.module}/src/nr2backlog/index.py"
    },
  ]
  artifacts_dir                = "builds"
  recreate_missing_package     = false
  trigger_on_package_timestamp = false

  function_name = var.resource_prefix
  description   = "Send New Relic issues to Backlog"
  handler       = "index.lambda_handler"
  runtime       = "python3.12"
  architectures = ["arm64"]
  memory_size   = 128
  timeout       = 60
  publish       = true

  logging_log_format                = "JSON"
  logging_application_log_level     = "INFO"
  logging_system_log_level          = "INFO"
  cloudwatch_logs_retention_in_days = 7

  allowed_triggers = {
    EventBridge = {
      principal  = "events.amazonaws.com"
      source_arn = aws_cloudwatch_event_rule.this.arn
    }
  }

  environment_variables = {
    "SECRET_NAME" = aws_secretsmanager_secret.this.name
  }

  attach_policy_json = true
  policy_json        = data.aws_iam_policy_document.this_lambda_function.json

  tags = {
    Name = var.resource_prefix
  }
}

data "aws_iam_policy_document" "this_lambda_function" {
  statement {
    effect  = "Allow"
    actions = ["secretsmanager:GetSecretValue"]
    resources = [
      aws_secretsmanager_secret.this.arn
    ]
  }
}

resource "aws_cloudwatch_event_target" "this" {
  event_bus_name = aws_cloudwatch_event_rule.this.event_bus_name
  rule           = aws_cloudwatch_event_rule.this.name
  arn            = module.lambda_function.lambda_function_arn
}

resource "aws_secretsmanager_secret" "this" {
  name = var.resource_prefix
}

resource "aws_secretsmanager_secret_version" "this" {
  secret_id = aws_secretsmanager_secret.this.id
  secret_string = jsonencode({
    BACKLOG_DOMAIN                  = var.backlog["DOMAIN"]
    BACKLOG_API_KEY                 = var.backlog["API_KEY"]
    BACKLOG_PROJECT_KEY             = var.backlog["PROJECT_KEY"]
    BACKLOG_PROJECT_ID              = local.BACKLOG_PROJECT_ID
    BACKLOG_ISSUE_TYPE              = var.backlog["ISSUE_TYPE"]
    BACKLOG_ISSUE_TYPE_ID           = local.BACKLOG_ISSUE_TYPE_ID
    BACKLOG_ISSUE_PRIORITY          = var.backlog["ISSUE_PRIORITY"]
    BACKLOG_ISSUE_PRIORITY_ID       = local.BACKLOG_PRIORITY_ID
    BACKLOG_ISSUE_CLOSE_STATUS      = var.backlog["ISSUE_CLOSE_STATUS"]
    BACKLOG_ISSUE_CLOSE_STATUS_ID   = local.BACKLOG_CLOSE_STATUS_ID
    BACKLOG_ISSUE_ASSIGNEE          = var.backlog_optional["ISSUE_ASSIGNEE"]
    BACKLOG_ISSUE_ASSIGNEE_ID       = local.BACKLOG_ISSUE_ASSIGNEE_ID
    BACKLOG_ISSUE_NOTIFIED_USERS    = local.ISSUE_NOTIFIED_USERS
    BACKLOG_ISSUE_NOTIFIED_USER_IDS = local.ISSUE_NOTIFIED_USER_IDS
  })
}
