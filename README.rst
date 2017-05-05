BugRest
#######

Friendly and very light weight tool to keep track of list of things.
Designed with bugs/tickets/GTD in mind

See some generated `Bug file`__

__ https://raw.githubusercontent.com/fdev31/loof/master/bugs.rst

Screenshot
==========

.. image:: https://github.com/fdev31/bugrest/raw/master/shot.png


Key features
============

- **CLI** (works in a terminal)
- Simple text file used as storage (**ReStructuredText**)
    - **Git, Mercurial** & co friendly
    - **Colorized** in the terminal
    - No need to edit the text file by hand
- Automatically detects the "root" folder to use by finding  .hg, .svn or other version manager folder in parent directories
- More advanced features not getting in your way if you don't need them:
    - Priorities
    - Tags
    - Attributes
    - Time tracker (counts the time spent on a given task)
- Web Server allowing **real-time read only sharing** of the list
- HTML export
- Search tool (``grep``-like)

On the technical side
---------------------

- Pure **Python**, no dependency required (Ok... ``docutils``, but misses it ? ;)
- Simple *one file* design, keeping things short
- **No database**, only the ``.rst`` file is used for storage



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

