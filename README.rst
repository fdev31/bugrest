BugRest
#######

Friendly tool to keep track of list of things.
It uses a plain text file (*ReStructuredText* compatible) as database, making it easy to share using version control systems. Can also run a web server to publish things to do.

See some generated `Bug file`__

__ https://raw.githubusercontent.com/fdev31/loof/master/bugs.rst

Screenshot
==========

.. image:: https://github.com/fdev31/bugrest/blob/master/shot.png

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

    br html > bugs.html

Start a web server on port 5555::

    br serve

Change priority of item #66 (using ``bugid`` instead of item position)::

    br set #66 priority 10

