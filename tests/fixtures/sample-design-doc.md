---
title: "Order Fulfillment System: Technical Design"
author: Platform Engineering Team
date: 2026-01-15
status: Draft
---

# Order Fulfillment System: Technical Design

## Executive Summary

This document provides a technical design for the **Order Fulfillment System**, a new
service that automates warehouse operations for ShopFlow's e-commerce platform. The
system replaces manual order routing with an *automated pipeline* that matches orders
to optimal fulfillment centers based on inventory, proximity, and cost.

**Target Audience:** Engineers familiar with distributed systems and event-driven architecture.

---

## Architecture Overview

The system follows an event-driven architecture with three main layers:

1. **Ingestion Layer**
   - Consumes order events from the message broker
   - Validates order schema and enriches with customer data
   - Publishes to the routing topic
2. **Routing Layer**
   - Evaluates fulfillment rules per warehouse
   - Considers inventory levels, shipping distance, and SLAs
   - Produces fulfillment assignments
3. **Execution Layer**
   - Dispatches pick-pack-ship instructions to warehouses
   - Tracks fulfillment status via state machine
   - Handles exceptions (stockouts, split shipments)

## Technology Comparison

| Component | Current State | Future State | Risk | LOE |
|-----------|--------------|--------------|------|-----|
| Order routing | Manual assignment | Rule-based engine | Medium | 3 weeks |
| Inventory sync | Batch (hourly) | Real-time CDC | High | 4 weeks |
| Warehouse API | REST polling | Event-driven | Low | 2 weeks |
| Monitoring | Basic logs | Structured metrics | Low | 1 week |

## Data Model

Key entities and their relationships:

```sql
CREATE TABLE orders (
    order_id    BIGINT PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    status      VARCHAR(32) NOT NULL DEFAULT 'pending',
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10, 2) NOT NULL
);

CREATE TABLE fulfillment_assignments (
    assignment_id BIGINT PRIMARY KEY,
    order_id      BIGINT REFERENCES orders(order_id),
    warehouse_id  BIGINT NOT NULL,
    assigned_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    shipped_at    TIMESTAMP,
    status        VARCHAR(32) NOT NULL DEFAULT 'assigned'
);
```

## Fulfillment State Machine

Orders move through the following states:

- **Pending** → order received, awaiting routing
- **Assigned** → matched to a fulfillment center
  - Split orders create multiple assignments
- **Picking** → warehouse has begun pick-pack
- **Shipped** → carrier has the package
  - Tracking number available
- **Delivered** → confirmed delivery
- **Exception** → requires manual intervention
  - Stockout, address issue, or carrier failure

## Success Criteria

- 99.5% of orders routed within 30 seconds
- Zero data loss during warehouse failover
- Fulfillment cost reduction of 15% vs manual routing
- Test coverage: 90% of routing engine logic

> **Note:** The `routing_engine` module and `assignment_service` are the two
> highest-risk components and should be reviewed carefully.

---

*Last updated: 2026-01-15 | Status: Draft*
