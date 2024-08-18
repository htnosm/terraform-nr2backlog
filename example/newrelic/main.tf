terraform {
  required_version = ">= 1.9"

  required_providers {
    newrelic = {
      source  = "newrelic/newrelic"
      version = ">= 3.0"
    }
  }
}

provider "newrelic" {
  account_id = var.newrelic_account_id
  api_key    = var.newrelic_api_key
  region     = "US"
}

/*
Destination
*/
locals {
  aws_account_name = var.aws_account_name != null ? var.aws_account_name : var.aws_account_id
}

resource "newrelic_notification_destination" "event_bridge" {
  name = "${var.resource_prefix}-${local.aws_account_name}-${var.aws_region}"
  type = "EVENT_BRIDGE"

  property {
    key   = "AWSAccountId"
    value = var.aws_account_id
  }
  property {
    key   = "AWSRegion"
    value = var.aws_region
  }
}

resource "newrelic_entity_tags" "notification_destination_event_bridge" {
  guid = newrelic_notification_destination.event_bridge.guid

  dynamic "tag" {
    for_each = var.default_tags
    content {
      key    = tag.value.key
      values = tag.value.values
    }
  }
}

/*
Notification Channel
*/
resource "newrelic_notification_channel" "event_bridge" {
  name           = newrelic_notification_destination.event_bridge.name
  type           = "EVENT_BRIDGE"
  destination_id = newrelic_notification_destination.event_bridge.id
  product        = "IINT"

  property {
    key   = "eventSource"
    value = "aws.partner/newrelic.com/${var.newrelic_account_id}/${newrelic_notification_destination.event_bridge.name}"
  }

  // must be valid json
  property {
    key   = "eventContent"
    value = <<-EOT
    {
        "id": {{ json issueId }},
        "issueUrl": {{ json issuePageUrl }},
        "title": {{ json annotations.title.[0] }},
        "priority": {{ json priority }},
        "impactedEntities": {{json entitiesData.names}},
        "totalIncidents": {{json totalIncidents}},
        "state": {{ json state }},
        "trigger": {{ json triggerEvent }},
        "isCorrelated": {{ json isCorrelated }},
        "createdAt": {{ createdAt }},
        "updatedAt": {{ updatedAt }},
        "sources": {{ json accumulations.source }},
        "alertPolicyNames": {{ json accumulations.policyName }},
        "alertConditionNames": {{ json accumulations.conditionName }},
        "workflowName": {{ json workflowName }},
        "violationChartUrl": {{ json violationChartUrl }}
    }
    EOT
  }
}

/*
Workflow
*/
resource "newrelic_workflow" "event_bridge" {
  name                  = var.resource_prefix
  muting_rules_handling = "NOTIFY_ALL_ISSUES"

  issues_filter {
    name = "filter-name"
    type = "FILTER"

    predicate {
      attribute = "priority"
      operator  = "EQUAL"
      values = [
        "CRITICAL",
        "HIGH",
        "MEDIUM",
        "LOW",
      ]
    }
  }

  destination {
    channel_id = newrelic_notification_channel.event_bridge.id
    notification_triggers = [
      "ACTIVATED", // EventBridge Default
      "ACKNOWLEDGED",
      "PRIORITY_CHANGED", // EventBridge Default
      "CLOSED",           // EventBridge Default
      "OTHER_UPDATES",
    ]
  }
}

resource "newrelic_entity_tags" "workflow_event_bridge" {
  guid = newrelic_workflow.event_bridge.guid

  dynamic "tag" {
    for_each = var.default_tags
    content {
      key    = tag.value.key
      values = tag.value.values
    }
  }
}
