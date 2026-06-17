import json
import os


def handler(event, context):
    """Simple health handler for D1 Terraform demo service."""
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(
            {
                "status": "UP",
                "environment": os.environ.get("ENVIRONMENT", "unknown"),
                "bucket": os.environ.get("BUCKET_NAME", "unknown"),
            }
        ),
    }
