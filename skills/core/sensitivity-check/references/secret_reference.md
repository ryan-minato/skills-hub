# Secret Severity Reference

Use these tiers to classify every secret or credential finding. Severity
describes the blast radius if the value is (or was) exposed.

## Critical — full compromise of a system or identity

- Private keys of any kind: TLS/SSL, SSH, PGP, code-signing, blockchain
  wallets
- Cloud account root or organization-admin credentials
- Master or key-encryption keys (KMS CMKs, disk/backup encryption keys)
- Database administrator passwords for production systems

## High — significant access or spend under an attacker's control

- Third-party API keys with spend or data access (payment processors, LLM
  providers, communication platforms)
- OAuth client secrets and JWT signing secrets
- Personal access tokens (GitHub, GitLab, Bitbucket, Azure DevOps)
- CI/CD deploy keys, pipeline secrets, and webhook signing secrets
- SMTP and other messaging credentials

## Medium — scoped access inside a trust boundary

- Internal service credentials with limited scope
- Connection strings embedding non-admin users
- Session-signing keys and internal API tokens
- Encryption keys for non-production data

## Low — little to no live impact

- Values explicitly marked as test, demo, or sandbox credentials
- Keys that are demonstrably revoked or rotated
- Credentials that only work on a developer's local machine

## Applying the tiers

- **Entropy is a signal, not proof.** A high-entropy string next to a
  telling variable name is probably a secret; a high-entropy string in a
  hash column is probably data. Read the surrounding code.
- **Committed means compromised.** A secret that ever reached version
  control must be treated as exposed even if the line was later deleted;
  recommend rotation, not just removal.
- **Placeholders are informational.** `YOUR_API_KEY`, `${VAR}`, `<token>`,
  `changeme` show where a secret belongs, not that one leaked.
- **Hashes correlate across engines.** Both secret engines report
  `hashed_secret` as the SHA-1 of the raw value and never print the value;
  identical hashes from different engines are the same secret. Re-read the
  source at the reported line to review the actual value.
