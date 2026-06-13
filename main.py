import asyncio
from fastapi import FastAPI
from api.routes.document import router as document_router
from api.routes.projects import router as project_router
from api.routes.reviews import router as review_router
from worker.document_processing import DocumentProcessing
from worker.agentic_review import AgenticReview
from contextlib import asynccontextmanager
import uvicorn

document_worker = DocumentProcessing(queue_name="document-processing")
agentic_review = AgenticReview(queue_name="reviews-processing")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("STARTUP")
    task = asyncio.create_task(document_worker.start())
    task = asyncio.create_task(agentic_review.start())
    yield
    print("SHUTDOWN")
    task.cancel()


app = FastAPI(title="Enterprise Architecture Advisor", lifespan=lifespan)

app.include_router(document_router, prefix="/api", tags=["documents"])
app.include_router(project_router, prefix="/api", tags=["projects"])
app.include_router(review_router, prefix="/api", tags=["reviews"])


if __name__ == "__main__":
    uvicorn.run(app=app, host="127.0.0.1", port=8080)


# if env.get("UI_DEBUG"):
#     serve(entities=[workflow()], auth_enabled=False)


# async def process(message: str) -> None:
#     w = workflow()

#     async for event in w.run(message=message, stream=True):
#         if event.type in ("intermediate", "output"):
#             data = event.data
#             if isinstance(data, AgentResponseUpdate):
#                 created_at = data.created_at
#                 executor_id = data.author_name
#                 if created_at:
#                     print(f"response at {created_at} by {executor_id}")

#             elif event.type == "output":
#                 outputs = cast(list[Message], event.data)
#         else:
#             print(f"event ==> {event.type} : {event.executor_id}")
#             if "completed" in event.type:
#                 print(f"State for {event.executor_id}: {event.data}")


# asyncio.run(process(
#     """
# # Drug Inventory Management System (DIMS)
# Version: 2.4
# Last Updated: 2026-04-15

# ## Overview

# The Drug Inventory Management System (DIMS) is a cloud-native application designed to manage pharmaceutical inventory across multiple warehouses, hospitals, and retail pharmacies.

# The platform provides capabilities for inventory tracking, drug dispensing, stock replenishment, supplier integration, regulatory compliance reporting, and expiration monitoring.

# The system serves approximately 12,000 concurrent users across North America and Europe.

# ---

# ## Business Requirements

# ### Functional Requirements

# 1. Track inventory quantities for all pharmaceutical products.
# 2. Support controlled substances management.
# 3. Allow pharmacists to reserve inventory for prescriptions.
# 4. Generate expiration alerts 90, 60, and 30 days before drug expiration.
# 5. Integrate with supplier systems for automated purchase orders.
# 6. Support barcode and QR code scanning.
# 7. Maintain complete audit trails for inventory modifications.
# 8. Generate compliance reports for FDA and EMA regulations.
# 9. Provide role-based access control.
# 10. Support multi-warehouse inventory visibility.

# ### Non-Functional Requirements

# 1. System availability must be 99.95%.
# 2. Recovery Point Objective (RPO) must be less than 15 minutes.
# 3. Recovery Time Objective (RTO) must be less than 1 hour.
# 4. Support up to 50 million inventory records.
# 5. All customer data must be encrypted at rest and in transit.
# 6. Average API response time should remain below 300 ms.
# 7. System must support deployment in multiple regions.

# ---

# ## High-Level Architecture

# The solution follows a microservices architecture.

# ### Core Services

# #### Inventory Service

# Responsibilities:
# - Maintain current inventory levels.
# - Process stock adjustments.
# - Track batch numbers.
# - Track expiration dates.

# Technology:
# - .NET 9
# - PostgreSQL

# #### Dispensing Service

# Responsibilities:
# - Process medication dispensing requests.
# - Validate prescription allocations.
# - Update inventory reservations.

# Technology:
# - Java Spring Boot
# - PostgreSQL

# #### Supplier Integration Service

# Responsibilities:
# - Communicate with external suppliers.
# - Generate purchase orders.
# - Receive shipment notifications.

# Technology:
# - Python FastAPI

# #### Compliance Service

# Responsibilities:
# - Generate regulatory reports.
# - Maintain audit logs.

# Technology:
# - Node.js

# #### Notification Service

# Responsibilities:
# - Send email, SMS, and push notifications.

# Technology:
# - C#

# ---

# ## Data Architecture

# ### Inventory Database

# Database Engine:
# PostgreSQL 16

# Key Tables:

# InventoryItem
# - ItemId
# - DrugCode
# - WarehouseId
# - Quantity
# - ExpirationDate
# - BatchNumber

# DrugCatalog
# - DrugCode
# - DrugName
# - Manufacturer
# - ControlledSubstanceFlag

# AuditLog
# - AuditId
# - Timestamp
# - UserId
# - Action
# - EntityType

# ### Data Retention

# - Inventory records retained indefinitely.
# - Audit records retained for 10 years.
# - Compliance reports retained for 15 years.

# ---

# ## Security Architecture

# Authentication:
# - Microsoft Entra ID

# Authorization:
# - Role-Based Access Control (RBAC)

# Roles:
# - Pharmacist
# - PharmacyManager
# - ComplianceOfficer
# - WarehouseOperator
# - SystemAdministrator

# Encryption:
# - TLS 1.3
# - AES-256

# Secrets Management:
# - Azure Key Vault

# Network Security:
# - Private Endpoints
# - Web Application Firewall

# ---

# ## Integration Architecture

# ### External Systems

# 1. Supplier ERP Systems
#    Protocol: HTTPS REST APIs

# 2. Hospital EHR Systems
#    Protocol: HL7 FHIR

# 3. Government Compliance Portal
#    Protocol: SFTP

# 4. Payment Gateway
#    Protocol: REST

# ---

# ## Messaging Architecture

# Message Broker:
# Apache Kafka

# Topics:

# inventory-updated
# prescription-dispensed
# purchase-order-created
# shipment-received
# compliance-report-generated

# Expected Throughput:
# 50,000 messages per minute

# Retention:
# 7 days

# ---

# ## Infrastructure Architecture

# Cloud Provider:
# Microsoft Azure

# Regions:
# - East US
# - Central US
# - West Europe

# Compute:
# - Azure Kubernetes Service (AKS)

# Container Registry:
# - Azure Container Registry

# API Gateway:
# - Azure API Management

# Monitoring:
# - Azure Monitor
# - Application Insights

# Logging:
# - Log Analytics Workspace

# CI/CD:
# - GitHub Actions

# Infrastructure as Code:
# - Terraform

# ---

# ## Disaster Recovery

# Primary Region:
# East US

# Secondary Region:
# Central US

# Database Replication:
# Asynchronous

# Backup Schedule:
# - Daily Full Backup
# - Hourly Incremental Backup

# Failover:
# Manual approval required

# ---

# ## Known Constraints

# 1. Legacy supplier systems support only TLS 1.2.
# 2. Some hospital systems support only HL7 v2.
# 3. Inventory updates may arrive out of order.
# 4. Barcode scanners may operate offline for up to 8 hours.
# 5. Controlled substance transactions require dual approval.

# ---

# ## Open Questions

# 1. Should inventory reservations be eventually consistent or strongly consistent?
# 2. Is multi-region active-active required?
# 3. What is the maximum acceptable data loss during regional failover?
# 4. Should compliance reports be generated synchronously or asynchronously?
# 5. Are supplier integrations allowed to use public internet connectivity?

# ---

# ## Risks

# 1. Inventory overselling due to concurrent reservations.
# 2. Supplier API rate limiting.
# 3. Regional outage impacting dispensing operations.
# 4. Inconsistent inventory counts caused by offline scanners.
# 5. Regulatory penalties due to missing audit records.

# """
# ))
