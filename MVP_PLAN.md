# Calendar MCP — MVP Plan / Requirements
# Stack: FastAPI + SQLAlchemy (PostgreSQL on Neon) + python-mcp SDK
# Auth: JWT (simple, extensible to multi-user/multi-calendar)
# Input: ICS file ingestion endpoint
# Ground truth: PostgreSQL via Neon connection string
# Consumers: 525600minutes.com site, scanning agents (re-opt)

# MVP (current build): one user / one calendar / login + auth + ICS ingest + basic read
# Post-MVP (deferred): multi-calendar per user, scanning/re-optimization endpoint, ICS export, family/business split
