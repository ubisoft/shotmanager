.. _use-in-production:

How to use in production
========================

Shot Manager was designed by the production, for the production. It can be used from the scale of a simple scene
to the one of a feature film, splited in many files.

Project settings
----------------

For large-scale productions it is important that each instance of Shot Manager, in every scene of every file, use
the same settings, that those settings cannot be modified by mistake by a user and that they all come from the
same source so that any change is propataged all over the production easily.

To do so Shot Manager has a notion of "Project", in other words a set of settings covering the shot naming conventions,
output resolution, file formats... All that can be also set by a production tool when a scene is opened for example.


API
---

Shot Manager also has its own API. This would allow you to integrate it into your pipeline, or to pilot it from
another add-on, by calling functions that will not change even if the architecture of the add-on is modified for
whatever reason.

