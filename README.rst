BugReST
#######

Basic bugtracker that uses a plain text file (*ReStructuredText* compatible) as database.

In theory it should run everywhere with Python2 or Python3 available.

See some generated `Bug file <bugrest/files/tip/bugs.rst>`_

Usage
=====

The command line tool is `br` and works in the current directory.
If you don't like this, feel free to edit `br` file and change the following lines to absolute paths::

    BUGFILE = 'bugs.rst'
    DONEFILE = 'fixed_bugs.rst'


List bugs::

    br

Add new bug::

    br new

Delete bug number 4::

    br rm 4

Add one comment::

    br add 3

Show full description of current bugs::

    br show

Show description of some specific bug::

    br show 42

Produce an html report::

    br show | rst2html > bugs.html

