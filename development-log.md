# Piazza Development Log

## 2026-11-07

Today I mostly experimented with and decided upon the linters that I'm going to
use for Piazza.  But also this commit bootstraps the genesis structure of the
Piazza application.

Good luck evvybody! &%D

### AI

Installed Claude.


## 2026-11-10

Landed user-registration and JWT-based auth, the implementation of which was
largely lifted from Week 4's Auth API
[cf. https://github.com/se93jmh0/BBK-AdvancedCloudComputing--week4-auth-api].

One notable difference is that I had to adopt SQLAlchemy 2.1, else
`pyrefly check` complained:

    ERROR Argument `Column[str]` is not assignable to parameter `hashed_password` with type `str` in function `security.verify_password` [bad-argument-type]

### AI

Not used.
