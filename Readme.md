# Intelligent Customer Self-Service System

An AWS-based conversational customer-service system that automates common customer inquiries using **Amazon Lex, AWS Lambda, and Amazon DynamoDB**, with **Amazon Connect** designed as the contact-center and human-agent fallback layer.

![Architecture Diagram](architecture/architectre.png)

---

## Overview

The **Intelligent Customer Self-Service System** is a conversational customer-service solution designed to automate common support requests and reduce the need for manual agent involvement.

The implemented prototype uses **Amazon Lex** to understand customer requests and collect required information, **AWS Lambda** to process requests and apply backend logic, and **Amazon DynamoDB** to store and retrieve customer information.

The architecture also includes **Amazon Connect** as the planned contact-center integration layer. Connect would manage customer calls, contact flows, routing, and transfer unresolved requests to human support agents.

The current implementation focuses on the complete self-service processing flow:

```text
Amazon Lex
     ↓
AWS Lambda
     ↓
Amazon DynamoDB
     ↓
AWS Lambda
     ↓
Amazon Lex
     ↓
Customer Response
```

Amazon Connect is documented as the planned integration for the customer-contact and agent-fallback portion.

---

# Architecture

```text
                         Customer
                            |
                            v
                  +-------------------+
                  |  Amazon Connect   |
                  |  Contact Center   |
                  +---------+---------+
                            |
                            v
                  +-------------------+
                  |    Amazon Lex     |
                  | Conversational AI |
                  +---------+---------+
                            |
                     Intent + Slots
                            |
                            v
                  +-------------------+
                  |    AWS Lambda     |
                  | Backend Processing|
                  +---------+---------+
                            |
                            v
                  +-------------------+
                  |    DynamoDB       |
                  | Customer Records  |
                  +---------+---------+
                            |
                     Customer Data
                            |
                            v
                  +-------------------+
                  |  Lambda Response  |
                  +---------+---------+
                            |
                            v
                       Amazon Lex
                            |
                            v
                         Customer
```

### Architecture Note

Amazon Connect represents the **planned contact-center integration**.

The implemented prototype focuses on:

* Amazon Lex
* AWS Lambda
* Amazon DynamoDB

The Amazon Connect and human-agent fallback components are designed but were not implemented in this prototype because of service availability limitations in the target environment.

---

# System Workflow

The implemented self-service workflow follows these steps.

### 1. Customer Request

The customer submits a request through the conversational interface.

Example:

```text
"I want to check my account."
```

### 2. Intent Detection

Amazon Lex identifies the customer's intent.

```text
Customer Request
       |
       v
CheckAccount Intent
```

### 3. Information Collection

Lex collects the information required to process the request.

Example:

```text
Bot:
Please provide your customer ID.

Customer:
CUST1001
```

The customer ID is collected as a Lex slot.

### 4. Lambda Processing

Once the required information has been collected, the request is passed to AWS Lambda.

```text
Amazon Lex
     |
     | customerId
     v
AWS Lambda
```

Lambda extracts and validates the customer ID.

### 5. DynamoDB Lookup

Lambda queries the DynamoDB `Customers` table.

```text
AWS Lambda
     |
     | GetItem(customerId)
     v
Amazon DynamoDB
```

### 6. Customer Data Retrieval

DynamoDB returns the corresponding customer record.

Example:

```json
{
  "customerId": "CUST1001",
  "customerName": "John Doe",
  "accountNumber": "ACC1001",
  "accountStatus": "Active",
  "serviceType": "Premium"
}
```

### 7. Response Generation

Lambda processes the retrieved information and creates a response.

Example:

```text
Hello John Doe. Your account status is Active.
```

### 8. Response to Customer

The response is returned to the conversational workflow.

```text
DynamoDB
    |
    v
AWS Lambda
    |
    v
Amazon Lex
    |
    v
Customer
```

---

# AWS Services

| AWS Service         | Purpose                                         | Status        |
| ------------------- | ----------------------------------------------- | ------------- |
| **Amazon Lex**      | Intent detection and conversational interaction | ✅ Implemented |
| **AWS Lambda**      | Backend processing and business logic           | ✅ Implemented |
| **Amazon DynamoDB** | Customer data storage and retrieval             | ✅ Implemented |
| **Amazon Connect**  | Contact center and agent fallback               | ⚠️ Designed   |

---

# Amazon Lex

Amazon Lex provides the conversational interface for the system.

It identifies customer intent and collects the information required to process requests.

## Implemented Intent: CheckAccount

The `CheckAccount` intent handles requests related to customer account information.

### Example Utterances

```text
I want to check my account
Can you check my account?
Show me my account information
I need my account status
Can you look up my account?
```

### Required Slot

```text
customerId
```

### Example Conversation

```text
Customer:
I want to check my account.

Bot:
Sure. Please provide your customer ID.

Customer:
CUST1001

Bot:
Let me check your account information.
```

The customer ID is then passed to the backend processing layer.

---

## Additional Designed Intents

The system also defines conversational designs for additional customer-service scenarios.

### RequestInformation

Used for general service-information requests.

Example:

```text
I need information about your services
What services do you provide?
Tell me about the available services
```

Possible slots:

```text
serviceType
requestType
```

### ServiceAssistance

Used when a customer requires assistance with a specific service.

Possible slots:

```text
customerId
serviceType
issueType
```

These intents can be extended with additional Lambda processing as the system grows.

---

# AWS Lambda

AWS Lambda provides the backend processing layer.

The Lambda implementation is written in **Python** and is designed to work with Amazon Lex V2 and DynamoDB.

### Lambda Responsibilities

The Lambda function:

1. Receives the Amazon Lex event.
2. Extracts the customer ID.
3. Validates the input.
4. Queries DynamoDB.
5. Handles missing customer records.
6. Handles database errors.
7. Builds the response.
8. Returns an Amazon Lex-compatible response.

### Processing Flow

```text
Amazon Lex
     |
     | Intent + Slot Values
     v
AWS Lambda
     |
     | Extract customerId
     v
DynamoDB
     |
     | Customer Record
     v
AWS Lambda
     |
     | Build Response
     v
Amazon Lex
```

---

# Lambda Implementation

The main Lambda function is located at:

```text
lambda/customer_lookup.py
```

The function uses the AWS SDK for Python (`boto3`) to communicate with DynamoDB.

Example database operation:

```python
response = table.get_item(
    Key={
        "customerId": customer_id
    }
)
```

The DynamoDB table name is configurable through the environment variable:

```text
CUSTOMER_TABLE=Customers
```

---

# DynamoDB

Amazon DynamoDB acts as the customer-data store.

## Table Configuration

```text
Table Name:
Customers

Partition Key:
customerId
```

## Data Model

| Attribute       | Type   | Description                |
| --------------- | ------ | -------------------------- |
| `customerId`    | String | Unique customer identifier |
| `customerName`  | String | Customer name              |
| `accountNumber` | String | Account identifier         |
| `accountStatus` | String | Current account status     |
| `serviceType`   | String | Customer service type      |

### Example Record

```json
{
  "customerId": "CUST1001",
  "customerName": "John Doe",
  "accountNumber": "ACC1001",
  "accountStatus": "Active",
  "serviceType": "Premium"
}
```

---

# End-to-End Example

The following example demonstrates the primary self-service workflow.

```text
Customer
   |
   | "I want to check my account."
   v
Amazon Lex
   |
   | Detect CheckAccount intent
   v
Lex Slot Collection
   |
   | customerId = CUST1001
   v
AWS Lambda
   |
   | Query customerId
   v
Amazon DynamoDB
   |
   | Customer record
   v
AWS Lambda
   |
   | Generate response
   v
Amazon Lex
   |
   v
Customer
```

Example final response:

```text
Hello John Doe. Your account status is Active.
```

---

# Amazon Connect Integration

Amazon Connect is included as the planned contact-center component.

The intended architecture is:

```text
Customer
    |
    v
Amazon Connect
    |
    v
Amazon Lex
    |
    +----------------------+
    |                      |
    v                      v
Resolved Request       Unresolved Request
    |                      |
    v                      v
Automated Response    Agent Queue
                           |
                           v
                      Support Agent
```

### Planned Responsibilities

Amazon Connect would be responsible for:

* Handling customer calls
* Managing contact flows
* Starting the conversational interaction
* Routing customer requests
* Managing agent queues
* Transferring unresolved requests to human agents

### Implementation Status

Amazon Connect was **not implemented** in the current prototype because of service availability limitations in the target environment.

The contact-center integration and human-agent fallback are documented as part of the system architecture.

---

# Repository Structure

```text
intelligent-customer-self-service/
│
├── README.md
│
├── architecture/
│   └── architecture.png
│
├── docs/
│   ├── lex-intents.md
│   ├── lambda-flow.md
│   └── dynamodb-design.md
│
├── lambda/
│   ├── customer_lookup.py
│   └── requirements.txt
│
└── sample-data/
    └── customer-record.json
```

---

# Technologies

### Cloud Platform

**Amazon Web Services (AWS)**

### AWS Services

* Amazon Lex
* AWS Lambda
* Amazon DynamoDB
* Amazon Connect

### Programming

* Python
* Boto3
* JSON

---

# Project Status

## Implemented

The following components have been implemented as part of the prototype:

* Amazon Lex conversational intent design
* Customer intent detection
* Slot-based information collection
* AWS Lambda backend processing
* DynamoDB customer lookup
* Customer data model
* Automated response generation
* Error handling
* Lex-to-Lambda-to-DynamoDB processing flow

## Designed but Not Implemented

* Amazon Connect contact-center integration
* Connect contact flows
* Live phone-based customer interaction
* Agent queue integration
* Human-agent fallback execution

The Amazon Connect component is documented as the planned extension to the implemented self-service workflow.

---

# Limitations

The current implementation is a prototype and is not intended for production customer-service operations.

Additional work would be required for:

* Production authentication
* Real customer databases
* Production monitoring
* Advanced authorization
* CRM integration
* Contact-center deployment
* Production security controls
* Scalability and performance testing

---

# Disclaimer

This project is an **AWS-based prototype developed for learning and demonstration purposes**.

The customer records included in this repository are fictional sample data and do not represent real customers.

Amazon Connect is documented as a planned integration layer and was not implemented in the current prototype due to service availability limitations in the target environment.