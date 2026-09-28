# Amazon Lex Intent Design

## Overview

Amazon Lex is responsible for understanding customer requests and collecting the information required to process them.

The conversational design uses intents to represent different types of customer requests and slots to collect information from the customer.

---

## 1. CheckAccount Intent

### Purpose

The `CheckAccount` intent handles requests where a customer wants to check their account information.

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

### Processing Flow

```text
Customer Request
       |
       v
CheckAccount Intent
       |
       v
Collect customerId
       |
       v
AWS Lambda
       |
       v
DynamoDB
       |
       v
Customer Information
       |
       v
Response
```

---

## 2. RequestInformation Intent

### Purpose

The `RequestInformation` intent handles general requests for information about available services.

### Example Utterances

```text
I need information about your services
What services do you provide?
Tell me about the available services
I want service information
What options are available?
```

### Possible Slots

```text
serviceType
requestType
```

### Example Conversation

```text
Customer:
I need information about your services.

Bot:
Sure. Which service are you interested in?

Customer:
Premium support.

Bot:
I can provide information about the Premium Support service.
```

---

## 3. ServiceAssistance Intent

### Purpose

The `ServiceAssistance` intent handles requests where a customer needs help with a specific service.

### Example Utterances

```text
I need help with my service
I am having a problem with my service
Can you help me with my account?
I have an issue with my service
I need assistance
```

### Possible Slots

```text
customerId
serviceType
issueType
```

### Example Conversation

```text
Customer:
I need help with my service.

Bot:
Sure. Please provide your customer ID.

Customer:
CUST1001

Bot:
What type of issue are you experiencing?

Customer:
Service access problem.

Bot:
Let me check the available information.
```

---

## 4. Fallback Intent

### Purpose

The fallback mechanism handles requests that cannot be matched to the supported intents.

### Example

```text
Customer:
Can you help me book a flight to London?

Bot:
I'm unable to handle that request through self-service.
```

The system can then use the planned Amazon Connect integration to transfer the customer to a human support agent.

### Fallback Flow

```text
Customer Request
       |
       v
Amazon Lex
       |
       | Unable to understand
       v
Fallback
       |
       v
Amazon Connect
       |
       v
Agent Queue
       |
       v
Support Agent
```

---

# Slot Design

Slots represent information that the conversational system needs to collect from the customer.

| Slot            | Purpose                              | Example          |
| --------------- | ------------------------------------ | ---------------- |
| `customerId`    | Identifies the customer              | `CUST1001`       |
| `accountNumber` | Identifies an account                | `ACC1001`        |
| `serviceType`   | Identifies the requested service     | `Premium`        |
| `issueType`     | Identifies the customer's problem    | `Service Access` |
| `requestType`   | Identifies the requested information | `Account Status` |

---

# Intent-to-Backend Mapping

Not every intent requires a database lookup.

| Intent               | Lambda   | DynamoDB |
| -------------------- | -------- | -------- |
| `CheckAccount`       | Yes      | Yes      |
| `RequestInformation` | Optional | Optional |
| `ServiceAssistance`  | Yes      | Yes      |
| Fallback             | No       | No       |

The `CheckAccount` intent is the primary example of backend integration.

---

# CheckAccount End-to-End Flow

```text
Customer
   |
   v
Amazon Lex
   |
   | Detect CheckAccount
   |
   v
Collect customerId
   |
   v
AWS Lambda
   |
   | Query DynamoDB
   |
   v
Customer Record
   |
   v
Lambda Response
   |
   v
Amazon Lex
   |
   v
Customer
```

---

# Design Goals

The conversational design aims to:

1. Understand common customer requests.
2. Minimize the amount of information requested from the customer.
3. Collect only the information required to process a request.
4. Provide automated responses where possible.
5. Handle unsupported requests gracefully.
6. Provide a fallback path to human support.

---

# Future Intent Expansion

Additional intents could be added to support:

* Order status
* Appointment scheduling
* Password assistance
* Service cancellation
* Billing inquiries
* Complaint registration
* Ticket status
* Contact information updates