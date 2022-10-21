.. _storyboard-detach:

Storyboard - Detach
===================


When a storyboard frame is detached from a shot of type Storyboard here is what happens:

  
- the grease pencil object used for the storyboard frame gets unparented from the camera hierarchy
  (technically speaking it is in fact parented to an Empty object that is itself parented to the camera),
  
- the transformation animation of the storyboard frame is cleared. This is because now the grease pencil
  is part of the 3D world.

- the shot type is changed to "Camera Shot" because now it is shooting content from the 3D world.
