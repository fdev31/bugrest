BugRest
#######

Friendly and very light weight tool to keep track of list of things.
Designed with bugs/tickets/GTD in mind

See some generated `Bug file`__

__ https://github.com/fdev31/loof/blob/master/bugs.rst

Even though single list management is possible, this tool is intended to be used from many places at a time.
By default each folder with a SCM repository is candidate to be a storage.
The idea is to manage a list of topics grouped by folders, which "just works" with your projects under version control.
In case you are using empty folders you will just need to `git init` or `hg init` once - you may also want to commit from time to time to keep history.

Screenshot
==========

.. image:: https://github.com/fdev31/bugrest/raw/master/shot.png


Key features
============

- **CLI** (works in a terminal)
- Simple text file used as storage (**ReStructuredText**)
    - **SCM friendly**, support provided for git, mercurial and svn
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
- Supports plugins, provided examples:
   - Jira interaction
   - Impress output (interactive slides)
- **No database**, only the ``.rst`` file is used for storage

Usage
=====

The command line tool is `br` and works in the current directory.
If you don't like this, feel free to edit `br` file and change the following lines to absolute paths::

    BUGFILE = '/home/john/tickets.rst'
    DONEFILE = '/home/john/done.rst'
    SOURCE_MGR=False


Edit the configuration::

   br cfg

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

Tag ticket #3 as "feature"::

   br tag #3 feature


List tickets tagged as "feature"::

   br tag feature
   

Advanced usages
===============

Display tickets containing "comm"::

   br show $(br -q grep comm)

Same with filter::

   br show $(br -q filter 'text=.*comm')


Search only the title::

   br show $(br -q filter 'title=.*comm')

any attribute can be used with `filter` (cf **set** command).
Eg, listing tickets created in 2016::

   br filter created=2016

Mark done/remove the bugs tagged "old"::

   br rm $(br -q tag old)

List tickets due today (if a *due* attribute is set)::

   br filter due=$(date -I)

List tickets created this month::

   br filter created=${$(date -I)%-*}

Plugins
=======

impress
-------

generate an html5 presentation from the tickets::

   br impress

generate an html5 presentation from a presentation file following similar format, saving under ``index.html``::

   br presentation.rst impress > index.html

Make the 7 first slides go from right to left::

   for n in $(seq 0 6);
      do br README.rst set $n x -2000;
   done

