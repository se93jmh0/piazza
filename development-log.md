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


## 2026-11-13

Added simple smoketest.

### AI

Not used.


## 2026-11-14

Initial work on supporting discussion posts.  We can now create them, although
there's no support for topics, status, comments, or likes/dislikes.

One thing I'm not entirely happy about is that I'm manually having to restore
timezones at the SQLAlchemy model layer after doing a refresh.  Feels clumsy,
but using sqlalchemy.types.DateTime(timezone=True) doesn't appear to work with
SQLite.

### AI

Not used.


