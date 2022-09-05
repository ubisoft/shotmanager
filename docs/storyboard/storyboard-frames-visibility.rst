.. _storyboard-frames-visibility:

Storyboard Frames Visibility
============================


Here are the rules for the display of the storyboard frame of a shot.

**Hidden:** The storyboard frame is never visible

**Auto:**
    - For shots of type **Camera shot**: Storyboard frame is automaticaly hidden if the shot is not the current one
    - For shots of type **Storyboard shot**: Storyboard frame is visible even if the shot is not the current one

**Visible:** The storyboard frame is "always visible" in the viewport. It will not be displayed in the rendering of other
shots though.

See :ref:`Shot Type <shot-type>`

In the viewport
---------------

The storyboard frame of the **current shot** is displayed in the viewport if its visibility
is set to Auto or Visible.

For the other storyboard frames:
- The storyboard frame of a shot of type **Camera shot** is visible in the viewport only if set to **Visible**.
Hidding the storyboard frames of the other camera shots avoid to see things that belongs to another shot 
when cameras have overlapping fields of view. 

- The storyboard frame of a shot of type **Storyboard shot** is visible in the viewport if set to **Visible or to Auto**.
  This allows the other storyboard shots to stay visible all the time and to compare shots.


At render time
--------------

The storyboard frame of the **rendered shot** is displayed in the rendered picture if its visibility
is set to Auto or Visible.
All the other storyboard frames are hidden.


Tips: When to use what
----------------------

- When a shot is purely a 2D drawing, with no 3D visible over or behind it:
    - it should be of type "Storyboard Shot"
    - its storyboard frame visibility should be "Auto"

    Eg: Any storyboard drawing

- When a shot has to display 3D objects from the scene:
    - it should be of type "Camera Shot"
    - its storyboard frame visibility should be "Auto"

    Eg: The storyboard frame displays a drawn character and the background is made of a terrain, or a custom plate
    Eg 2: The camera of the shot is moving into the scene



