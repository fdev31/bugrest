BetterRest *impress*
====================

--------------------------------------

Integrated
==========

:class: slide

Say you have slides separated using `----------` in a **presentation.rst** file, you can run in a terminal:

.. code::

   Shell> br presentation.rst impress > index.html
   Shell> xdg-open index.html

But before that you will need to edit the configuration file (you can use "``br cfg``"):

.. code::

   PLUGINS=['jira', 'impress']

Ensure **impress** is part of the plugin array !


--------------------------------------

Code support
============


.. code::

   #!/bin/sh
   foo="baz"

--------------------

Code (again)
============

:class: slide
:x: 0
:y: 1000

.. code::
   :number-lines:


   #!/bin/python
   for i in range(10): print(i)


-- Imagine a full tutorial this way !

I prefer not to.

.. note:: this could be awesome !

---------------

Note
====

:notitle:

.. warning:: Are you ready ?

---------------

Images
======

.. image:: https://images.presentationgo.com/2018/03/Infinity-Symbol-Diagram-PowerPoint.png
   :width: 100%

--------------------


Diagrams support
================

:notitle:

:x: 0
:z: -500
:rot_y: 70

.. x :z: -500
.. x :rot_y: 180


.. raw:: html

   <div class="mermaid">
       %% This is a comment in mermaid markup
        graph LR
          A(Support for<br />diagrams)
          B[Provided by<br />mermaid.js]
          C{Already<br />know<br />mermaid?}
          D(<a href=&quot;http://knsv.github.io/mermaid/index.html#usage&quot;>Tutorial</a>)
          E(Great, hope you enjoy!)
          A-->B
          B-->C
          C--No-->D
          C--Yes-->E
          classDef startEnd fill:#fcc,stroke:#353,stroke-width:2px;
          class A,D,E startEnd;
   </div>



---------------


That's all folks!
=================


:z: 5000
:x: -2500
:y: -1000
:rot_y: 0
