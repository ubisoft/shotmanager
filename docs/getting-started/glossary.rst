.. _glossary:

Glossary
========

.. [Handles]
    The handles are the amount of spare images let at the start and end of the shot when the shot is rendered.
    They are quite helpful for the artist doing the movie edit since she can get more time before or after
    each shot to polish the cuts and transitions.

    Handles are not played in the viewport playback since they are not really part of the edit.

    Unless you are in a production context the duration of the handles is usualy left to 0.

.. [Project]
    A project is a set of settings defining the configuration of your production, such as the project name, image
    output resolution, aspect ratio, framerate, sequences naming convention...
    
    These settings can be entered manually in the Project Settings dialog box of the Shot Manager panel, in which
    case they are set only for the current scene.
    In production these settings would be set by a custom script, written speifically for your own pipeline and 
    automatically run when the Blender file is opened.

    For a local use of Shot Manager it is not necessary to define a project. The settings of the scene will then
    be used.

.. [Shot]
    A shot is the basic entity manipulated by the Shot Manager user interface. As for a live footage it is made of a
    point of view, thanks to a camera, and a "record duration", defined by a start time and an end time.
    
    A shot has one and one only camera. When it is not associated to a camera, or if this camera is missing, the shot
    is considered as invalid and cannot be used in the [Take]_.

.. [Take]
    A take is an ordered list of shots. Basicaly **a take is an edit** where shots are played one after the other, in the order
    set in the take and independently from the time at which they start in the time of the 3D scene.
    
    In practice - or in a production context - a take would generaly refert to what is commonly called a sequence, that's to say
    a small edit of shots that are tied together in the narration.
    
    In order to preserve the parallel with live shooting the take entity could probably have been named edit or sequence.
    The term take fits quite well nonetheless since, as for live shots, we can easily create variations of the edits, this so as
    to compare several ideas in the direction without having to "break" the setttings. Duplicating takes and switching from
    one to another is one of the major strenghts of Shot Manager to explore the narrative possibilities of the scene and offer
    to the director a lot of flexibility to find her final cut.

