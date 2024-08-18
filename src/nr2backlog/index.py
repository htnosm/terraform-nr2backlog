#!/usr/bin/env python

import os
import http.client
import urllib.parse
import json
import logging

import boto3
from botocore.config import Config
from datetime import datetime, timedelta, timezone

logger = logging.getLogger()

SECRET_NAME = os.environ['SECRET_NAME']

config = Config(
    retries={
        'max_attempts': 5,
        'mode': 'standard'
    },
)
session = boto3.Session()
client = session.client('secretsmanager', config=config)


def get_secret_values():
    """Retrieve secret values from AWS Secrets Manager."""
    try:
        values = client.get_secret_value(SecretId=SECRET_NAME)['SecretString']
        return json.loads(values)
    except Exception as e:
        logger.error(f"Unexpected {e=}, {type(e)=}")
        raise


class BacklogClient:
    """Client for interacting with Backlog API."""

    def __init__(self):
        self.secret_values = get_secret_values()
        self.connection = http.client.HTTPSConnection(
            self.secret_values['BACKLOG_DOMAIN'])
        self.params = urllib.parse.urlencode({
            'apiKey': self.secret_values['BACKLOG_API_KEY'],
        })

    def parse_datetime(self, timestamp_ms: int, offset_hours: int = 9) -> str:
        """Parses timestamp to formatted datetime string."""
        try:
            timestamp_s = timestamp_ms / 1000.0
            tz = timezone(timedelta(hours=offset_hours))
            datetime_utc = datetime.fromtimestamp(timestamp_s, tz=timezone.utc)
            datetime_with_tz = datetime_utc.astimezone(tz)
            formatted_datetime = datetime_with_tz.strftime('%Y-%m-%d %H:%M:%S')
            return formatted_datetime
        except Exception as e:
            logger.warning(f"Unexpected {e=}, {type(e)=}")
            return str(timestamp_ms)

    # https://developer.nulab.com/ja/docs/backlog/api/2/get-issue-list/
    def search_issues(self, issue_type_ids: list[str] = [], keyword: str = ""):
        """Returns list of issues.
        Args:
            issue_type_ids (list[str]): List of issue type IDs to filter.
            keyword (str): Keyword to search in issues.
        Returns:
            List of issues matching the criteria.
        """
        search_params = urllib.parse.urlencode({
            'projectId[]': self.secret_values['BACKLOG_PROJECT_ID'],
            'sort': 'created',
            'order': 'desc',
            'count': 100,
        })
        search_list_params = []
        search_list_params.extend(
            [("issueTypeId[]", issue_type_id) for issue_type_id in issue_type_ids])
        search_list_params.extend([("keyword", keyword)])
        search_list_params = urllib.parse.urlencode(search_list_params)
        logger.info(f"{search_params=}, {search_list_params=}")

        self.connection.request(
            'GET', f'/api/v2/issues?{self.params}&{search_params}&{search_list_params}')
        response = self.connection.getresponse()
        return json.loads(response.read().decode())

    # https://developer.nulab.com/ja/docs/backlog/api/2/add-issue/
    def create_issue(self, keyword: str, project_id: str, issue_type_id: str, priority_id: str, event_details: dict[any], assignee_id: str = "", notified_user_ids: list[int] = []):
        """Adds new issue.
        Args:
            keyword (str): The keyword used when update.
            issue_type_id (str): The ID of the issue type.
            priority_id (str): The ID of the priority.
            event_details (dict): Dictionary containing issue details.
            assignee_id (str): The ID of the assignee.
            notified_user_ids (list[str]): List of user IDs to notify.

        Returns:
            Response from Backlog API.
        """
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        summary = f"[{event_details['state']}] {event_details['title']}"

        descriptions: list[str] = [f"{keyword}\n(Auto-updated)\n"]
        descriptions.append(f"\n# {event_details['title']}\n")

        if 'createdAt' in event_details:
            descriptions.append(
                f"created at: {self.parse_datetime(event_details['createdAt'])}")
        if 'updatedAt' in event_details:
            descriptions.append(
                f"updated at: {self.parse_datetime(event_details['updatedAt'])}")

        if 'issueUrl' in event_details:
            descriptions.append(
                f"[Go to issue]({event_details['issueUrl']})\n")

        if 'state' in event_details:
            descriptions.append(f"state: {event_details['state']}")
        if 'trigger' in event_details:
            descriptions.append(f"trigger: {event_details['trigger']}")
        if 'priority' in event_details:
            descriptions.append(f"priority: {event_details['priority']}")
        if 'totalIncidents' in event_details:
            descriptions.append(
                f"total incidents: {event_details['totalIncidents']}\n")
        if 'violationChartUrl' in event_details:
            descriptions.append(
                f"\n![violationChartUrl]({event_details['violationChartUrl']})\n")

        if 'impactedEntities' in event_details:
            descriptions.append(
                f"\nimpacted entity: {event_details['impactedEntities']}\n")
        if 'alertPolicyNames' in event_details:
            descriptions.append(
                f"alert policy: {event_details['alertPolicyNames']}\n")
        if 'alertConditionNames' in event_details:
            descriptions.append(
                f"alert condition: {event_details['alertConditionNames']}\n")
        if 'isCorrelated' in event_details:
            descriptions.append(
                f"is correlated: {event_details['isCorrelated']}\n")
        if 'workflowName' in event_details:
            descriptions.append(
                f"workflow: {event_details['workflowName']}\n")

        descriptions.append("---\n\nraw event details:\n\n```")
        descriptions.append(json.dumps(
            event_details, ensure_ascii=False, indent=2))
        descriptions.append("```\n")
        description: str = "\n".join(descriptions)

        create_issue_params = {
            # Requires
            'projectId': project_id,
            'summary': summary,
            'issueTypeId': issue_type_id,
            'priorityId': priority_id,
            # Optionals
            'description': description,
        }
        if assignee_id:
            create_issue_params['assigneeId'] = assignee_id
        if notified_user_ids:
            create_issue_params['notifiedUserId[]'] = notified_user_ids

        body = urllib.parse.urlencode(create_issue_params, doseq=True)
        logger.info(f"{body=}")
        self.connection.request(
            'POST', f'/api/v2/issues?{self.params}', body, headers)
        response = self.connection.getresponse()
        return response.read().decode()

    # https://developer.nulab.com/ja/docs/backlog/api/2/update-issue/
    def update_issue(self, issue_id: str, close_status_id: str, event_details: dict[any], notified_user_ids: list[int] = []):
        """Updates information about issue.
        Args:
            issue_id (str): The ID of the issue to update.
            status_id (str): The ID of the status to update.
            event_details (dict): Dictionary containing updated issue details.
            notified_user_ids (list[str]): List of user IDs to notify.

        Returns:
            Response from Backlog API.
        """
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        comments: list[str] = ["(Auto-updated)"]
        if 'updatedAt' in event_details:
            comments.append(
                f"updated at: {self.parse_datetime(event_details['updatedAt'])}")
        if 'state' in event_details:
            comments.append(f"state: {event_details['state']}")
        if 'trigger' in event_details:
            comments.append(f"trigger: {event_details['trigger']}")
        if 'priority' in event_details:
            comments.append(f"priority: {event_details['priority']}")
        comment: str = "\n".join(comments)

        update_issue_params = {
            'comment': comment,
        }
        if event_details.get('state') == 'CLOSED':
            update_issue_params['statusId'] = close_status_id
        if notified_user_ids:
            update_issue_params['notifiedUserId[]'] = notified_user_ids

        body = urllib.parse.urlencode(update_issue_params, doseq=True)
        logger.info(f"{body=}")
        self.connection.request(
            'PATCH', f'/api/v2/issues/{issue_id}?{self.params}', body, headers)
        response = self.connection.getresponse()
        return response.read().decode()


def lambda_handler(event, context):
    """AWS Lambda handler for processing events."""
    logger.info(f"{event=}")

    bc = BacklogClient()
    event_details: dict[any] = event.get('detail', {})

    # Setup keyword for searching issues
    keyword: str = f"<issueId:{event_details['id']}>" if event_details.get(
        'id', "") else ""
    logger.info(f"{keyword=}")

    # Parse notified user IDs from secrets
    notified_user_ids: list[int] = []
    for v in bc.secret_values['BACKLOG_ISSUE_NOTIFIED_USER_IDS'].split(","):
        try:
            notified_user_ids.append(int(v))
        except ValueError:
            pass
    logger.info(f"{notified_user_ids=}")

    # Search issues by keyword
    try:
        issues: list[dict[any]] = bc.search_issues(
            issue_type_ids=[bc.secret_values['BACKLOG_ISSUE_TYPE_ID']],
            keyword=keyword,
        )
        logger.info(f"search_issues: {len(issues)=}")
    except Exception as e:
        logger.error(f"Unexpected {e=}, {type(e)=}")
        raise

    # Update issue if exists
    for issue in issues:
        if issue.get('description', '').startswith(keyword):
            try:
                result = bc.update_issue(
                    issue_id=issue['id'],
                    close_status_id=bc.secret_values['BACKLOG_ISSUE_CLOSE_STATUS_ID'],
                    event_details=event_details,
                    notified_user_ids=notified_user_ids,
                )
                logger.info(f"update_issue: {result=}")
                return result
            except Exception as e:
                logger.error(f"Unexpected {e=}, {type(e)=}")
                raise

    # Create issue if not exists
    try:
        result = bc.create_issue(
            keyword=keyword,
            project_id=bc.secret_values['BACKLOG_PROJECT_ID'],
            issue_type_id=bc.secret_values['BACKLOG_ISSUE_TYPE_ID'],
            priority_id=bc.secret_values['BACKLOG_ISSUE_PRIORITY_ID'],
            event_details=event_details,
            assignee_id=bc.secret_values['BACKLOG_ISSUE_ASSIGNEE_ID'],
            notified_user_ids=notified_user_ids,
        )
        logger.info(f"create_issue: {result=}")
    except Exception as e:
        logger.error(f"Unexpected {e=}, {type(e)=}")
        raise

    return result
