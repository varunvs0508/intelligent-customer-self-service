# AWS Lambda Processing Flow

## Overview

AWS Lambda acts as the backend processing layer between Amazon Lex and Amazon DynamoDB.

When Amazon Lex collects the required customer information, the information is passed to Lambda. Lambda validates the input, retrieves the corresponding customer record from DynamoDB, and returns a response to the conversational interface.

---

## End-to-End Flow

```text
Customer
   |
   | "Check my account"
   v
Amazon Lex
   |
   | Detect CheckAccount intent
   |
   | Collect customerId
   v
AWS Lambda
   |
   | Validate customerId
   |
   v
Amazon DynamoDB
   |
   | Get customer record
   v
AWS Lambda
   |
   | Build response
   v
Amazon Lex
   |
   v
Customer
```

---

## 1. Amazon Lex Collects Customer Information

The customer begins with a request such as:

```text
"I want to check my account."
```

Amazon Lex identifies the `CheckAccount` intent.

Lex then asks for the required `customerId` slot:

```text
"Please provide your customer ID."
```

The customer responds:

```text
"CUST1001"
```

The customer ID becomes part of the Lex session data.

---

## 2. Lex Invokes Lambda

After the required information has been collected, Lex can invoke the configured Lambda function.

The Lambda event contains the detected intent and slot values.

A simplified Lex V2 event looks like:

```json
{
  "sessionState": {
    "intent": {
      "name": "CheckAccount",
      "slots": {
        "customerId": {
          "value": {
            "interpretedValue": "CUST1001"
          }
        }
      }
    }
  }
}
```

The Lambda function extracts the customer ID from this event.

---

## 3. Lambda Extracts the Customer ID

The Python function uses the Lex session state to retrieve the slot value.

Example:

```python
session_state = event.get("sessionState", {})
intent = session_state.get("intent", {})
slots = intent.get("slots", {})

customer_id_slot = slots.get("customerId")

value = customer_id_slot.get("value", {})

customer_id = value.get("interpretedValue")
```

For the example request:

```text
customer_id = CUST1001
```

---

## 4. Lambda Queries DynamoDB

The Lambda function connects to the DynamoDB table using the AWS SDK for Python (`boto3`).

The customer ID is used as the DynamoDB partition key.

```python
response = table.get_item(
    Key={
        "customerId": customer_id
    }
)
```

DynamoDB searches the `Customers` table for the corresponding record.

---

## 5. DynamoDB Returns the Customer Record

For example, DynamoDB could return:

```json
{
  "customerId": "CUST1001",
  "customerName": "John Doe",
  "accountNumber": "ACC1001",
  "accountStatus": "Active",
  "serviceType": "Premium"
}
```

Lambda retrieves the relevant information from the returned item.

---

## 6. Lambda Creates the Response

Lambda processes the customer information and creates a conversational response.

Example:

```python
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
```

The resulting response could be:

```text
Hello John Doe. Your account status is Active.
```

---

## 7. Lambda Returns the Response to Lex

Lambda returns an Amazon Lex-compatible response.

Example:

```python
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
```

Lex can then present the response to the customer.

---

# Error Handling

The Lambda function should handle several possible failure conditions.

## Customer Not Found

If DynamoDB does not contain the requested customer:

```text
I could not find an account for the provided customer ID.
```

## Missing Customer ID

If the required slot is missing:

```text
Please provide a valid customer ID.
```

## DynamoDB Error

If the database operation fails:

```text
I'm unable to retrieve your account information right now.
```

## Unexpected Error

Unexpected exceptions are caught and logged:

```python
except Exception as error:
    print(f"Unexpected error: {error}")
```

The customer receives a generic error message instead of an internal error.

---

# Lambda Environment Variable

The Lambda function uses an environment variable to define the DynamoDB table name.

```text
CUSTOMER_TABLE=Customers
```

The code reads the value using:

```python
table_name = os.environ.get(
    "CUSTOMER_TABLE",
    "Customers"
)
```

This avoids hard-coding the table name throughout the application.

---

# IAM Permissions

In an actual AWS deployment, the Lambda execution role would require permission to read from the DynamoDB table.

A minimal conceptual permission would allow:

```text
dynamodb:GetItem
```

on the `Customers` table.

The Lambda function should not receive unnecessary permissions.

---

# Processing Summary

```text
1. Customer sends request
          |
          v
2. Lex detects intent
          |
          v
3. Lex collects customerId
          |
          v
4. Lambda receives event
          |
          v
5. Lambda extracts customerId
          |
          v
6. Lambda queries DynamoDB
          |
          v
7. DynamoDB returns customer data
          |
          v
8. Lambda builds response
          |
          v
9. Lex returns response
          |
          v
10. Customer receives result
```

---

# Design Goal

The Lambda layer keeps backend processing separate from the conversational interface.

Amazon Lex focuses on understanding the customer, while Lambda handles business logic and DynamoDB access.

This separation makes the architecture easier to extend with additional customer-service operations in the future.