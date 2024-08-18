import json
import logging
import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.parametrize(
    "event, mock_search_result, mock_create_result, mock_update_result",
    [
        (
            {
                'detail-type': 'NewRelicEvent',
                'detail': {
                    'id': '550e8400-e29b-41d4-a716-446655440000',
                    'issueUrl': 'https://radar-api.service.newrelic.com/accounts/1234567/issues/550e8400-e29b-41d4-a716-446655440000',
                    'title': 'Sample Issue',
                    'priority': 'CRITICAL',
                    'impactedEntities': ['entity1'],
                    'totalIncidents': '1',
                    'state': 'ACTIVATED',
                    'trigger': 'STATE_CHANGE',
                    'isCorrelated': 'false',
                    'createdAt': 1723972836888,
                    'updatedAt': 1723972836889,
                    'sources': ['newrelic'],
                    'alertPolicyNames': ['sample_policy'],
                    'alertConditionNames': ['sample_condition'],
                    'workflowName': 'sample_workflow',
                    'violationChartUrl': 'https://gorgon.nr-assets.net/image/550e8400-e29b-41d4-a716-446655440000'
                }
            },
            [],
            {'id': '12345678', 'summary': '[ACTIVATED] Sample Issue', "status": {"name": "未対応"}, "description": "<issueId:550e8400-e29b-41d4-a716-446655440000>\n(Auto-created)"},
            {},
        ),
        (
            {
                'detail-type': 'NewRelicEvent',
                'detail': {
                    'id': '550e8400-e29b-41d4-a716-446655440000',
                    'issueUrl': 'https://radar-api.service.newrelic.com/accounts/1234567/issues/550e8400-e29b-41d4-a716-446655440000',
                    'title': 'Sample Issue',
                    'priority': 'CRITICAL',
                    'impactedEntities': ['entity1'],
                    'totalIncidents': '1',
                    'state': 'CLOSED',
                    'trigger': 'INCIDENT_CLOSED',
                    'isCorrelated': 'false',
                    'createdAt': 1723972836888,
                    'updatedAt': 1723972043189,
                    'sources': ['newrelic'],
                    'alertPolicyNames': ['sample_policy'],
                    'alertConditionNames': ['sample_condition'],
                    'workflowName': 'sample_workflow',
                    'violationChartUrl': 'Not Available'
                }
            },
            [{'id': '12345678', 'summary': '[ACTIVATED] Sample Issue', "description": "<issueId:550e8400-e29b-41d4-a716-446655440000>\n(Auto-updated)"}],
            {},
            {'id': '12345678', 'summary': '[ACTIVATED] Sample Issue', "status": {"name": "処理済み"}, "description": "<issueId:550e8400-e29b-41d4-a716-446655440000>\n(Auto-created)"},
        ),
        (
            {
                'detail-type': 'NewRelicEvent',
                'detail': {
                    'id': '550e8400-e29b-41d4-a716-446655449999',
                    'title': 'Sample Issue',
                    'state': 'CLOSED',
                }
            },
            [],
            {'id': '12345678', 'summary': '[CLOSED] Sample Issue', "status": {"name": "未対応"}, "description": "<issueId:550e8400-e29b-41d4-a716-446655449999>\n(Auto-created)"},
            {},
        )
    ]
)
@patch('http.client.HTTPSConnection')
def test_lambda_handler_create_issue(mock_https, secretsmanager_client, caplog, event, mock_search_result, mock_create_result, mock_update_result):
    from nr2backlog.index import lambda_handler
    # ^^ Importing here ensures that the mock has been established.

    # Enable logging capture
    caplog.set_level(logging.INFO)

    # Mock https connection
    mock_conn = MagicMock()
    mock_https.return_value = mock_conn

    def mock_getresponse(request):
        method = request[0]
        url = request[1]
        if method == 'GET' and url.startswith('/api/v2/issues?'):
            return json.dumps(mock_search_result).encode()
        elif method == 'POST' and url.startswith('/api/v2/issues?'):
            return json.dumps(mock_create_result).encode()
        elif method == 'PATCH' and url.startswith('/api/v2/issues/'):
            return json.dumps(mock_update_result).encode()
        else:
            return b"{}"
    mock_conn.getresponse.return_value.read.side_effect = lambda: mock_getresponse(mock_conn.request.call_args[0])

    # Call the lambda handler
    result = lambda_handler(event, None)

    for record in caplog.records:
        print(record)  # Print all logs for debugging

    if len(mock_search_result) == 0:
        assert json.loads(result) == mock_create_result
    else:
        assert json.loads(result) == mock_update_result
