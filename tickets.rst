*BugReST* tickets
=================

:total-count: 20

--------------------------------------------------------------------------------

More tests would be nice
========================

:bugid: 9
:created: 2017-05-05T21:20:33
:priority: 0
:x: -2000

There is clearly a defficiency in the coverage

Make some "shell" runs instead of API for the given commands:

- filter
- grep
-  (un)tag
- html
- (un)set

- serve ?


less important / more tested:

- list
- show

--------------------------------------------------------------------------------

Batch commands
==============

:bugid: 12
:created: 2017-11-16T23:00:05
:priority: 0
:x: -2000

One should be able to pass a list of bugids for any command
Two options proposed:

- compatible, passing multiple bugids, space-separated, in the same cmdline argument
- changing bugid position in cmdline, before the command when bugid needed
    - implies detection of number of bugids passed, quite easy since list of commands is known...

--------------------------------------------------------------------------------

Add dropdown to change bugs order in serve view
===============================================

:bugid: 14
:created: 2017-11-16T23:02:00
:priority: 0
:x: -2000

--------------------------------------------------------------------------------

Plugins improvement
===================

:bugid: 18
:created: 2019-03-27T21:45:09
:priority: 0
:x: -2000


Impress
-------

- Better template / more tests
- Support custom css & js files
- Integrate images (base64 ?)

- Allow setting default class(es) for the slides
- Allow injecting Rest macros commands / plugins ?

--------------------------------------------------------------------------------

Impress plugin: refactor
========================

:bugid: 19
:created: 2019-03-27T23:57:01
:priority: 0
:x: -2000

Use the same system for position & rotation

- would allow standard usage (with keep transforms being the default)
- also allows "reset" for instance to position the final slide close to the first one

--------------------------------------------------------------------------------

Allow set to have a list of tickets
===================================

:bugid: 20
:created: 2024-02-14T00:09:56
:priority: 2
:x: -2000

Make the following command work::
  br set $(br filter priority=0 -q) priority 10
