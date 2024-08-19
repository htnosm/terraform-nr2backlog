# terraform-nr2backlog

This module is for sending New Relic issues to Backlog.

- As a prerequisite, the partner event source from New Relic must be associated with EventBridge.

## 概要

New Relic の Alert(Issue) を Backlog に送信するためのリソース群をAWS上に作成します。

## Usage

- 1) New Relic 上で Workflow を作成、 Notification Channel に EventBridge を設定
    - 参考: [example/newrelic](./example/newrelic/main.tf)
- 2) AWSマネジメントコンソール上で、追加されたパートナーイベントソースを Associate
- 3) AWS 上で Event rule を作成 (本モジュール)
    - 参考: [example/aws](./example/aws/main.tf)
    - Backlog の APIキーが必要 (管理者権限は不要)

## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.9 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 5.0 |
| <a name="requirement_http"></a> [http](#requirement\_http) | >= 3.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | >= 5.0 |
| <a name="provider_http"></a> [http](#provider\_http) | >= 3.0 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_lambda_function"></a> [lambda\_function](#module\_lambda\_function) | terraform-aws-modules/lambda/aws | 7.7.1 |

## Resources

| Name | Type |
|------|------|
| [aws_cloudwatch_event_rule.this](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_rule) | resource |
| [aws_cloudwatch_event_target.this](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_target) | resource |
| [aws_secretsmanager_secret.this](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret) | resource |
| [aws_secretsmanager_secret_version.this](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret_version) | resource |
| [aws_cloudwatch_event_bus.this](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/cloudwatch_event_bus) | data source |
| [aws_iam_policy_document.this_lambda_function](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [http_http.backlog_issue_types](https://registry.terraform.io/providers/hashicorp/http/latest/docs/data-sources/http) | data source |
| [http_http.backlog_priorities](https://registry.terraform.io/providers/hashicorp/http/latest/docs/data-sources/http) | data source |
| [http_http.backlog_project](https://registry.terraform.io/providers/hashicorp/http/latest/docs/data-sources/http) | data source |
| [http_http.backlog_project_users](https://registry.terraform.io/providers/hashicorp/http/latest/docs/data-sources/http) | data source |
| [http_http.backlog_statuses](https://registry.terraform.io/providers/hashicorp/http/latest/docs/data-sources/http) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_backlog"></a> [backlog](#input\_backlog) | Backlog parameters | <pre>object({<br>    DOMAIN             = string<br>    API_KEY            = string<br>    PROJECT_KEY        = string<br>    ISSUE_TYPE         = string<br>    ISSUE_CLOSE_STATUS = string<br>    ISSUE_PRIORITY     = string<br>  })</pre> | n/a | yes |
| <a name="input_backlog_optional"></a> [backlog\_optional](#input\_backlog\_optional) | Backlog optional parameters | <pre>object({<br>    ISSUE_ASSIGNEE       = optional(string, "")<br>    ISSUE_NOTIFIED_USERS = optional(list(string), [])<br>  })</pre> | `{}` | no |
| <a name="input_event_bus_name"></a> [event\_bus\_name](#input\_event\_bus\_name) | The name of the new event bus. | `string` | n/a | yes |
| <a name="input_resource_prefix"></a> [resource\_prefix](#input\_resource\_prefix) | The prefix to use for all resources. | `string` | `"nr2backlog"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_backlog"></a> [backlog](#output\_backlog) | n/a |
