# DynamoDB Design

## Overview

Amazon DynamoDB is used as the proposed customer-data store for the self-service system.

The database contains customer records that can be retrieved by AWS Lambda when Amazon Lex collects a customer ID.

## Table Design

### Table Name

```text
Customers
```

### Primary Key

```text
customerId
```

The `customerId` attribute is used as the partition key.

## Data Model

| Attribute       | Type   | Description                |
| --------------- | ------ | -------------------------- |
| `customerId`    | String | Unique customer identifier |
| `customerName`  | String | Customer name              |
| `accountNumber` | String | Customer account number    |
| `accountStatus` | String | Current account status     |
| `serviceType`   | String | Customer service type      |

## Example Record

```json
{
  "customerId": "CUST1001",
  "customerName": "John Doe",
  "accountNumber": "ACC1001",
  "accountStatus": "Active",
  "serviceType": "Premium"
}
```

## Data Access Flow

The customer ID collected by Amazon Lex is passed to AWS Lambda.

Lambda uses the customer ID as the DynamoDB partition key.

```text
Amazon Lex
     |
     | customerId
     v
AWS Lambda
     |
     | GetItem(customerId)
     v
DynamoDB
     |
     | Customer record
     v
AWS Lambda
     |
     v
Amazon Lex
```

## Example Query

The Lambda function performs a DynamoDB `GetItem` operation using the customer ID.

Conceptually:

```python
response = table.get_item(
    Key={
        "customerId": customer_id
    }
)
```

The returned record can then be used to construct a conversational response.

## Example Response

If DynamoDB returns:

```json
{
  "customerId": "CUST1001",
  "customerName": "John Doe",
  "accountStatus": "Active"
}
```

The conversational system can generate:

```text
Hello John Doe. Your account status is Active.
```

## Error Handling

The backend should handle situations such as:

* Customer ID not found
* Invalid customer ID
* DynamoDB service errors
* Missing customer information
* Unexpected backend errors

For an unknown customer:

```text
I could not find an account for the provided customer ID.
```

For a backend failure:

```text
I'm unable to retrieve your account information right now.
```

## Security Considerations

A production DynamoDB implementation should:

* Use IAM permissions with least privilege.
* Avoid storing unnecessary sensitive information.
* Enable encryption where appropriate.
* Restrict table access to authorized resources.
* Avoid placing real customer data in the GitHub repository.

The sample data in this repository is fictional and intended only for demonstration.
