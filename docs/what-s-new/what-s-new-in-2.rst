.. _what-s-new-in-2:

What's New in 2.0
=================


    - :ref:`Concept changes <concepts>`
    - :ref:`Installation <installation>`
    - :ref:`Storyboarding <storyboarding>`
    - :ref:`UX/UI <ux-ui>`
    - :ref:`Project settings <project-settings>`
    - :ref:`Bug fixes <bug-fixes>`
    - :ref:`Code and architecture <code-and-archi>`


.. _concepts:

Concept changes
---------------

With the introduction of storyboarding in Shot Manager the notion of shot and its relationship to
the content of the 3D scene evolved a bit.

A property **Type** has been added to the shots to differenciate the shots that are containing purely 2D content -
they are called the :ref:`Storyboard Shots <storyboard-shot>` -
from those that are shooting 3D elements or are associated to a camera that is moving in space - they are called :ref:`Camera Shots <camera-shot>`.

More here: :ref:`Shot Type <shot-type>`

On the workflow side we introduced a notion of "layout" to distinguish the context for creating a storyboard from the one to do the previz.
Indeed in the first one most of the work lays in drawing the frames reprensenting what will be shot later in the process. In the previz context
though we need to create the interactions thenselves between the cameras and the action (or in other words we place the cameras to shoot the
action as we would like).

It is then now possible to switch from one layout to the other according to what we want to achieve in the scene.


.. _installation:

Installation
------------

As usual, and since the code relies on some external Python dependencies, it is necessary to run Blender in Administator mode to install it
(** but just for the install !**). It is also required to be connected to Internet.

But with Shot Manager V2 it is not needed anymore to install the add-on named Ubisoft Stamp Info. This add-on was handeling the writting of
the metadata information directly onto the rendered images. It has now been completely integrated into Shot Manager.

A visual feedback has also been added at the top right side of the main panel to inform the user of a new available version.


.. _storyboarding:

Storyboarding
-------------

A whole new world here to express your creativity! Just draw and play the sequence and you will see your movie becoming a reality!


    - Added a feature to detach a storyboard frame from a shot in order to create a free 3D object
    - Continuous drawing mode while changing storyboard frames
    - Added a frame grid to order the storyboard frames in space
    - and many more...

See more here: :ref:`Storyboard <storyboard>`

.. _ux-ui:

UX/UI
-----

A lot of improvements here since version 1.7:

    - Previz and Storyboard layouts
    - Interactive Shots Stack completely rewritten: faster, more intuitive, pleasant to use
    - More settings exposed in the add-on Preferences panel
    - Added a warning and reset button for pixel aspect, fps, resolution
    - Added a Reset to Default button for all the usage presets
    - Turned off the Use Best Play Performances mode by default
    - Added a button to disable the Blender metadata burning in the warnings
    - Added a Shift modifier key on shot creation and deletion to skip the dialog box
    - Added an add-on preference to store the Delete Cameras of the Remove Shots operator
    - Added a button in Features to toggle the display of Stamp Info in the 3D view tab list
    - Added a Resolution Percentage parameter for each render preset
    - Added an Open in Player button for Render Current
    - Moved the render warning UI component below in the panel to make it more visible
    - Display the shots names over the storyboard frames when the camera is hidden
    - ...


.. _project-settings:

Project settings
----------------

The "projects settings" are a set of properties defining the configuration of your project. This is really handy to ensure
some settings such as the render resolution, framerate, output directories... are not changed by error during the manipulations
done in the scene.

Although this feature is not new (it was introduced with the very first version of Shot Manager because it is just a life-saver
when in production), it has been improved in this release.

    - More flexible support for production naming conventions
    - Template to use for the cameras created with new shots


.. _bug-fixes:

Bug fixes
---------

A lot of work here too. See the `change log <https://github.com/ubisoft/shotmanager/blob/main/CHANGELOG.md>`_ on GitHub for an exhaustive list.

    - Fixed overlay state that wasn't restored correctly
    - Fixed Sequence Timeline that wasn't interactive anymore when the overlay was off
    - Fixed bug on Render Playblast, intermediate files are now deleted
    - Fixed issue in the offset of camera background video
    - ...


.. _code-and-archi:

Code and architecture
---------------------

    - Changed the name of the add-on in the bl_info from "Shot Manager" to "Ubisoft Shot Manager":
      This was done to allow another Blender add-on - also named Shot Manager and currently available on the market -
      to be installed in the same Blender instance.

    - Support for Blender 3.1 and Python 3.10