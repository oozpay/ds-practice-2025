## System Architecture

The project follows the **Orchestrator Pattern**. Instead of services talking to each other in a messy web, they all report to the **Orchestrator**, which manages the workflow and aggregates the results.

### Service Breakdown

| Service | Port | Protocol | Responsibility |
| --- | --- | --- | --- |
| **Frontend** | 8080 | HTTP | User interface |
| **Orchestrator** | 8081 | REST/gRPC | Coordinates the checkout logic and service calls |
| **Fraud Detection** | 50051 | gRPC | Analyzes card numbers and amounts for risk |
| **Transaction Verification** | 50052 | gRPC | Validates data integrity and credit card formats |
| **Suggestions** | 50053 | gRPC | Recommends new reads based on the catalog |

---

## Data Flow: The Checkout Lifecycle

When a user clicks "Submit Order," the following sequence occurs:

1. **Frontend** sends a POST request with JSON data to the **Orchestrator**.
2. **Orchestrator** initializes a `ThreadPoolExecutor` to trigger three concurrent gRPC calls.
3. **Fraud Detection** checks if the order amount is suspiciously high or if the card starts with a shady prefix (currently dummy logic is applied)
4. **Transaction Verification** ensures the cart isn't empty and the user didn't forget their email (currently dummy logic is applied)
5. **Suggestions** suggests additional books based on what's purchased (currently dummy logic is applied)
6. **Orchestrator** gathers these results. If both "Fraud" and "Verification" give the green light, the order is approved.

---

## Testing the Logic

* **To trigger a Fraud Denial:** Attempt a checkout with an order amount over $1000 or a credit card starting with `999`.
* **To trigger a Verification Error:** Modify the frontend to send an empty `items` list or empty `user` fields.
* **To see the parallel magic:** Check the timestamps in the Orchestrator logs; you'll notice all three services are called at almost the exact same millisecond.

---

## Project Structure

```text
├── frontend/                   # Nginx server & HTML/Tailwind source
├── orchestrator/               # Flask API & Service Coordinator
├── fraud_detection/            # gRPC Fraud Analysis Service
├── transaction_verification/   # gRPC Data Validation Service
├── suggestions/                # gRPC Recommendation Engine
├── utils/                      # Shared Protobuf definitions & generated stubs
└── docker-compose.yaml
```
---

## Architecture
![System Architecture](./docs/diagrams/system_architecture.png)