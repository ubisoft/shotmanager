.. _what-s-new-in-2-1:

What's New in 2.1
=================


    - :ref:`Shots Stack <shots-stack-2-1>`
    - :ref:`UX/UI <ux-ui-2-1>`
    - :ref:`Rendering <rendering-2-1>`
    - :ref:`Bug fixes <bug-fixes-2-1>`
    - :ref:`Code and architecture <code-and-archi-2-1>`


.. _shots-stack-2-1:

Shots Stack UI
--------------

Added a new manipulation mode for the shot clips: the keys of the camera and of the Storyboard Frames
can now be offset when the clip is moved and scaled when a clip handle is manipulated with the 
modifier key Shift pressed.

    - Added an info component
    - Added a Preferences setting to make the shots stack starts at the specified lane
    - Set the first lane to 1 instead of 0 to see the keys of the Summary lane


.. _ux-ui-2-1:

UX/UI
-----

    - Improvements on the Continuous Draw Mode
    - Revamped the UI of the Animated Frame Transformation to minimize UI ambiguities
    - Added shot name in the Render panel, near Current Shot label
    - Refactored the Duplicate Shot dialog box and added a checkbox for color variation
    - Added a button to set the time range to shot or take range in the Frame Range toolbar
    - Improved the Storyboard Frame Editing Mode button

    - Separated key mappings per category
    - Added a Preferences parameter to toggle the vertical arrows used to navigate from shot to shot
    - Made the up arrow go to next shots by default instead of previous ones
    - Added a key map for activating the draw mode on a current shot


.. _rendering-2-1:

Rendering
---------

    - Made the playblast temp directories different from the rendering directories


.. _bug-fixes-2-1:

Bug fixes
---------

See the `change log <https://github.com/ubisoft/shotmanager/blob/main/CHANGELOG.md>`_ on GitHub for an exhaustive list.


- Fixed occasional bug in duplicate cameras and duplicate takes

- Fixed rendering issues on Mac OS due to backslash character conflicts in path names:
    - Shot videos where not rendered
    - Playblast was all black
    - Open in File Explorer buttons were not working


.. _code-and-archi-2-1:

Code and architecture
---------------------

    - Improvement of the API code, samples and documentation
