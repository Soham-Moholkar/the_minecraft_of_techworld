# ADR-0002: replaceable local authentication provider

- Status: accepted for local development only
- Date: 2026-08-27

Product routes require a bearer principal from their first implementation. Local
development uses a constant-time checked token held server-side by the web BFF.
The `require_principal` dependency is the provider seam for an OIDC validator.

The local provider must never be deployed to an internet-facing environment.
Phase 1 replaces it with signed sessions, organization claims, RBAC, rotation, and
audit events while retaining the same route dependency contract.

