import json
import os
import boto3
from botocore.exceptions import ClientError

# DynamoDB configuration
dynamodb = boto3.resource("dynamodb")
table_name = os.environ.get("CUSTOMER_TABLE", "Customers")
table = dynamodb.Table(table_name)


def lambda_handler(event, context):
    """
    AWS Lambda function used by the customer self-service system.

    Expected customer ID:
        CUST1001

    The function retrieves the corresponding customer
    record from DynamoDB and returns a response.
    """

    try:
        # Get customer ID from Lex event
        customer_id = get_customer_id(event)

        if not customer_id:
            return build_response(
                "Please provide a valid customer ID."
            )

        # Retrieve customer information
        response = table.get_item(
            Key={
                "customerId": customer_id
            }
        )

        customer = response.get("Item")

        if not customer:
            return build_response(
                f"I could not find an account for customer ID {customer_id}."
            )

        # Build customer response
        customer_name = customer.get(
            "customerName",
            "customer"
        )

        account_status = customer.get(
            "accountStatus",
            "unknown"
        )

        message = (
            f"Hello {customer_name}. "
            f"Your account status is {account_status}."
        )

        return build_response(message)

    except ClientError as error:
        print(f"DynamoDB error: {error}")

        return build_response(
            "I'm unable to retrieve your account information right now."
        )

    except Exception as error:
        print(f"Unexpected error: {error}")

        return build_response(
            "Something went wrong while processing your request."
        )


def get_customer_id(event):
    """
    Extract customerId from an Amazon Lex V2 event.
    """

    session_state = event.get("sessionState", {})
    intent = session_state.get("intent", {})
    slots = intent.get("slots", {})

    customer_id_slot = slots.get("customerId")

    if not customer_id_slot:
        return None

    value = customer_id_slot.get("value", {})

    return value.get("interpretedValue")


def build_response(message):
    """
    Build an Amazon Lex V2 compatible response.
    """

    return {
        "sessionState": {
            "dialogAction": {
                "type": "Close"
            },
            "intent": {
                "name": "CheckAccount",
                "state": "Fulfilled"
            }
        },
        "messages": [
            {
                "contentType": "PlainText",
                "content": message
            }
        ]
    }