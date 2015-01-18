vella
=====

vella is a life logging system I want to use to pull events/timelines/data
streams from various SaaS services as well as any other sources that are
storing my data right now. This project also aims to be a single source of
any event which might be captured by different sources over a period of time.
For example, you might switch your run tracking apps over time, but individual
runs will be stored in a standardized format in vella.

Main Concepts
-------------

### Kind

A log you want to record should have a kind, for example, `browser.tab.open`
, `facebook.post.comment` or `activity.run`. I haven't thought much of it but
right now I am using a dotted representation to denote `kind` of a log record which makes future grouping easier. These could however be "source-independent", hence instead
of `facebook.post.comment` we can use `social.post.comment`.

### Source

This can be used to denote the source of this log, it could be the actual
app from which this log was captured, or the API consumer which created the
log.

### Timelines

Logs can have timelines where a log record can have multiple events within
that timeline. For example, a log record can have `activity.run.lap_start`
and `activity.run.lap_end` events recorded in its timeline. These events also
have timestamps with them as well as you can add other information to these
events also.
Its not always necessary that all logs will have timelines. You can mark an
event as inactive if there won't be any more additions to its timeline.


TODO:
-----

 * Browser extension which sends tab / browsing information.
 * Implement plugin interface, web server interface.
 * Move Mongo implementation to MongoAlchemy.
 * Build a querying abstraction for plugins to be able to query information.
 * Build dashboards.
