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


## 2026-11-15

Added support for topics in discussion posts.

Notable stuffs:
 * I've had to employ `# pyrefly: ignore` in a few places.  It's not currently
   clear to me if I'm doing something silly, but the code works, so it can't be
   that silly.  But it'd be good if I could figure out something better, or
   otherwise confirm that it's a bug.
 * I'm now seeing more instances of the following when running the unit tests:

       ResourceWarning: unclosed database in <sqlite3.Connection object at ...>

   I'm ignoring it for now, but I'd definitely like to eliminate them at some
   point.

### AI

Encountered Gemini (or whatever it is that serves the _AI Overview_ on
google.com) while searching for the reason that my attempted capture of
already_injected in test_init_encounters_SQLAlchemyError wasn't working.


## 2026-11-16

Added support for adding comments to discussion posts.

The addition of associated unit tests such as test_add_discussion_post_comment
uncovered a bit of a bug that took me while to track down:

    E               fastapi.exceptions.ResponseValidationError: 1 validation error:
    E                 {'type': 'missing', 'loc': ('response', 'topics'), 'msg': 'Field required', 'input': <modules.discussions.models.DiscussionPost object at 0x7dbcd20e4910>}
    E
    E                 File "/home/jhorns01/Uni/BBK/DataAnalyticsAndAI/AdvancedCloudComputing/piazza/modules/discussions/routes.py", line 19, in create_discussion_post
    E                   POST /posts

Eventually I figured out that this was due to the TopicsRegistry singleton
being initialized for every test, but not reset, so it was only populating the
discussion_topics table for the first test's test database.  Oops.

Part of the reason that this took me so long to track down was due to the fact
that the foreign key constraints weren't firing, which would have made the
problem clearer.  Hence the introduction of `pragma foreign_keys=on`.

Other notable stuffs:
 * Noticed that the existing models' columns with foreign key constraints were
   nullable.  Terribad.
 * Added missing types for a couple of the relationship-based model members.

### AI

Not used.


## 2026-11-17

Added support for being able to react to (i.e., like or dislike) discussion
posts.

### AI

Not used.


### 2026-11-21

Added support for getting an individual discussion post, and plumbed in comments
and likes and dislikes.

One thing I'm not entirely happy about is that get_discussion_post takes a
current_user parameter to enforce bearer authentication, but it's not actually
used in the function body.  I wonder if there's a better way...

### AI

Not used.
