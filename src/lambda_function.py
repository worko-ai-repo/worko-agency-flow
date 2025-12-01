import json
import os
import requests

def lambda_handler(event, context):
    """Simple test handler for the agency-test Lambda.

    Returns basic metadata and echoes query string parameters.
    """
    env = os.environ.get("ENVIRONMENT", "dev")
    region = os.environ.get("AWS_REGION", "")

    body = {
        "message": "Worko Agency Test Lambda",
        "environment": env,
        "region": region,
        "path": event.get("path"),
        "method": event.get("httpMethod"),
        "queryStringParameters": event.get("queryStringParameters"),
    }

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }
