Frequently asked questions
==========================

.. _faq:

General
-------

Why is Shot Manager still not working on Blender 2.93?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Several functionalities of Shot Manager rely on OpenTimelineIO, a Python framework developped
by Pixar and dedicated to the transfert of editings from one video application to another.

Currently this library is not available for Python 3.9, which is the version of Python supported
by Blender 2.93 and other future releases.

This should be fixed soon.


