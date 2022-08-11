.. _shots:

Shots
=====

As defined in the :ref:`Glossary <glossary>`, a [Shot]_ is the basic entity manipulated by the Shot Manager user interface. As for a live footage it is made of a
point of view, thanks to a camera, and a "record duration", defined by a start time and an end time.

A shot has one and one only camera. When it is not associated to a camera, or if this camera is missing, the shot
is considered as invalid and cannot be used in the [Take]_.


Since Shot Manager V 2.0 we make the disctinction between shots that are used purely for a 2D purpose, the :ref:`Storyboard Shots <storyboard-shot>`, from thoses associated to a 3D
camera, the :ref:`Camera Shots <camera-shot>`. Because their purpose is different we also treat them differently in the UI.


.. _shot_type:

Shot type
---------

A shot can be of one of the following types. The type defines how the shot - and in particular
its storyboard frame if it has one - will behave in the scene.
The type can be changed in the Properties panel of the selected shot, it is identified by a specific icon.

.. _storyboard-shot:

Storyboard Shot
+++++++++++++++

This shot is a 2D shot, meaning it contains only 2D drawings and objects such as text.

It is treated as part of the shots belonging to the storyboard shots grid.
Its camera location and orientation will then be changed to place the camera in the grid everytime the grid is updated. 

All the shots created when the Storyboard layout is active are of type Storyboard Shot.

.. _camera-shot:

Camera Shot
+++++++++++

This shot is a "3D" shot, meaning that either the camera is moving or it records an action taking place into the scene.

It is the type of shot to use everytime the camera is shooting content from the 3D space - which is most of the cases basically.

All the shots created when the Previz layout is active are of type Camera Shot.



See also :ref:`Frame Visibility <storyboard-frames-visibility>`
