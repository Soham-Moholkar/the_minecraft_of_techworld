# Security, Cybersecurity and DevSecOps Specification

Security is both:
1. a dedicated learning domain,
2. a cross-cutting requirement for every major feature.

The learning emphasis is defensive and engineering-oriented:
**identify → understand → remediate → test → monitor**.

Security labs must target only local/owned/authorized systems.

# 1. Security foundations

- CIA triad
- threat, vulnerability, risk
- assets
- attack surface
- trust boundaries
- least privilege
- defense in depth
- zero-trust principles
- secure defaults
- fail-safe behavior
- security controls
- threat modeling
- risk assessment
- security requirements

# 2. Cryptography

Teach concepts and safe library use:
- hashes
- password hashing
- salts
- MAC/HMAC
- symmetric encryption
- asymmetric encryption
- key exchange concepts
- digital signatures
- certificates
- PKI
- TLS
- key rotation
- key management
- randomness
- nonce/IV concepts

Clearly distinguish educational primitives from production-safe APIs.
Do not encourage designing custom cryptography.

# 3. Identity and access

- passwords
- MFA
- sessions
- secure cookies
- JWT
- OAuth 2
- OIDC
- SSO
- API keys
- service identities
- RBAC
- ABAC
- policy evaluation
- least privilege
- privilege boundaries
- secret storage
- rotation
- account lifecycle
- audit trails

Build interactive flow visualizers.

# 4. Application security

Teach major OWASP-style classes through local vulnerable/secure pairs:

- injection
- SQL injection
- command injection
- XSS
- CSRF
- SSRF
- path traversal
- insecure file upload
- unsafe deserialization concepts
- broken access control
- authentication failures
- session weaknesses
- misconfiguration
- dependency risk
- sensitive-data exposure
- insecure error handling
- mass assignment concepts
- rate-limit failures
- business-logic abuse
- request smuggling concepts where safe and appropriate
- CORS mistakes
- security headers
- CSP

Every vulnerable example requires:
- explanation,
- secure implementation,
- regression test.

# 5. API security

- authentication
- authorization
- object-level access checks
- input validation
- schemas
- pagination limits
- rate limits
- idempotency
- abuse controls
- replay concerns
- signing where appropriate
- webhook verification
- API gateways
- error sanitization
- audit logs

# 6. Browser/frontend security

- XSS
- DOM sinks
- CSP
- CSRF
- cookies
- SameSite
- storage choices
- clickjacking defense
- iframe policy
- dependency risks
- supply-chain risks
- source maps/secrets
- server/client boundaries
- secure handling of auth state.

# 7. Database security

- parameterized queries
- roles
- grants
- row-level security
- encryption
- credential rotation
- network isolation
- backups
- audit logs
- injection regression tests
- least-privileged service users.

# 8. Network security

- segmentation
- firewall concepts
- WAF
- VPN
- TLS
- DNS security concepts
- proxies
- IDS/IPS concepts
- packet analysis in controlled labs
- secure service-to-service communication
- network policy
- zero-trust network ideas.

# 9. Cloud security

Across AWS/Azure/GCP teach:
- IAM
- roles/service identities
- organization/account/project boundaries
- network segmentation
- security groups/firewalls
- secrets
- key management
- storage permissions
- logging/auditing
- public exposure
- metadata/service identity concepts
- managed database security
- container security
- common misconfigurations
- cost abuse protections.

# 10. Container and Kubernetes security

- image provenance
- minimal images
- non-root users
- capabilities
- filesystem permissions
- secrets
- image scanning
- SBOM
- Kubernetes RBAC
- namespaces
- NetworkPolicy
- admission controls
- security contexts
- resource limits
- runtime monitoring
- audit logs.

# 11. Software supply chain

- dependency inventory
- lockfiles
- integrity
- vulnerability scanning
- malicious/compromised package risks
- SBOM
- provenance
- signing
- artifact integrity
- CI permissions
- dependency pinning/update policy
- license scanning
- secret scanning.

# 12. DevSecOps pipeline

Target pipeline:

```text
commit
  ↓
format/lint/typecheck
  ↓
unit tests
  ↓
SAST
  ↓
secret scan
  ↓
dependency/SCA scan
  ↓
build
  ↓
SBOM
  ↓
container/IaC scan
  ↓
integration/contract tests
  ↓
deploy isolated staging
  ↓
DAST / security regression
  ↓
E2E / performance smoke
  ↓
promotion gate
```

Critical findings may block promotion based on policy.

# 13. Security tooling

Use representative free/open tooling where appropriate:
- Semgrep
- Bandit
- Ruff security-relevant linting where applicable
- dependency scanners
- Trivy
- Grype
- Syft/SBOM concepts
- Gitleaks-style secret scanning
- OWASP ZAP
- JMeter for load/security-adjacent testing where applicable
- container/IaC scanners
- browser security tooling

Verify current project status before adopting.

# 14. Detection and security operations

Teach:
- logs
- audit events
- normalization
- detection logic
- severity
- alert triage
- false positives
- correlation
- SIEM concepts
- anomaly detection concepts
- response playbooks.

Build a Security Operations dashboard with:
- auth failures,
- rate limits,
- blocked requests,
- suspicious events,
- findings,
- service posture,
- incident timeline.

# 15. Incident response

Teach:
- preparation
- identification
- containment
- eradication
- recovery
- lessons learned
- evidence handling concepts
- communication
- postmortems.

Local incident scenarios:
- leaked development secret
- compromised test credential
- vulnerable dependency
- public-storage misconfiguration simulation
- suspicious auth behavior
- malicious input causing application alert
- unauthorized tool request from an AI agent.

# 16. Threat modeling

Every large system-design case should have:
- assets
- actors
- entry points
- data flows
- trust boundaries
- STRIDE-style analysis
- mitigations
- residual risks.

Frontend needs a threat-model canvas.

# 17. AI/agent security

This is mandatory for AI engineering.

Cover:
- prompt injection
- indirect prompt injection
- RAG poisoning
- untrusted tool output
- data leakage
- unsafe tool invocation
- confused-deputy risks
- over-privileged agent
- cross-tenant context leakage
- unsafe code execution
- sensitive logging
- output validation
- human approvals
- sandboxing
- rate limits
- audit trails
- allowlists
- scoped credentials
- tool contracts.

Example policy:

```text
Agent
  └── Tool Gateway
      ├── file.read             allowed in workspace
      ├── file.write            approval or scoped
      ├── db.select             allowed
      ├── db.mutate             restricted
      ├── cloud.read            allowed in lab account
      └── cloud.deploy          explicit approval
```

# 18. Vulnerable-vs-secure pattern

For selected topics:

```text
labs/security/sql-injection/
├── vulnerable/
├── secure/
├── tests/
├── threat-model.md
└── remediation.md
```

The vulnerable version must not expose arbitrary public targets.

# 19. Security acceptance criteria

For each major app:
- secrets absent from source,
- authn/authz boundaries documented,
- validation present,
- relevant security headers,
- dependency scan,
- container scan if containerized,
- security regression tests for known lab vulnerabilities,
- audit events for sensitive actions,
- threat model,
- safe error handling,
- least-privileged service configuration where practical.
