.. _tips:

Tips
====

Markers, camera binding and shots
---------------------------------

Markers bound to cameras are not compatible with the way Shot Manager works. When such markers
are found in the scene most of the content of the add-on gets disabled and a warning appears, all
along with a button allowing the convertion of such markers to shots.


Tooltips and Quick Doc
----------------------

An important focus has been set to make the UI intuitive and the properties of the add-on
as predictable as possible. This reduce the need for documentation as well as the user memory load.

Tooltips are everywhere! When you are wondering what a parameter is about start by reading the tooltip.

Some special and more complete documentation has been introduced also at required places of the UI. They
look like buttons and their action is to open a message window with more detailed information than
usual tooltips could handle.


Shots and cameras
-----------------

A shot is an association of a point of view in space and a time range, defining when this point of view is used.
It is equivalent to a Record session for a video camera.

A shot can have one and only one camera. At the contrary a camera can be used by several shots. For example if 
you shoot a field against field sequence, 2 persons dialoging for example, you would use 2 cameras and create
a set of shots that would alternate between one and the other camera.

It is highly not advised to use the same camera for every shot. In fact Shot Manager has been developed to avoid
exactly that. Indeed when you do such an approach every modification of the camera affects every shots, changing
the animation must be done very carefuly to avoid breaking other shots and modifying the range of a shot requires
to change the animation of the camera as well as possibly to retime the whole scene after the considered shot end.

We recommend to use one camera per shot and to name it after the name of the shot. Not only this would make
every shots perfectly independent one from each other but it would also create a level of abstraction between the
action in the scene and the way it is shot, hence avoiding to retime the scene when a shot duration is extended.

We also recommend - in most of the cases - to use the duplicate option for the cameras when duplicating a take.
This will make takes completely independent and you will avoid breaking a take silently when modifying a shared camera
in another one.

The number of shots using a given camera is exposed in the UI, in the shot list as well as in the shot properties.
When a camera is shared by more than a single shot this information is highlighted in red.




