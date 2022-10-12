.. _si-general-philosophy:

.. |br| raw:: html

  <br/>


Stamp Info general philosophy
=============================


**Before starting to use Stamp Info it worths understanding what this add-on is about and
what you will be able to achieve with it.**

The aim of Stamp Info is to write information onto the rendered images. Those pieces of information
can be:

- **elements from the scene content:** the name of the scene, of the camera, the output resolution...
- **information related to the use of the image:** frame number, sequence range, custom notes...
- **information related to the edit:** sequence and shot names...
- **information about your project:** name, logo...
- **metadata:** user name, date of rendering, file path...

All this is very useful in production to understand the context of creation of any image and to track
the related Blender files used to generate it.


How it works
------------

When a rendering is done with Stamp Info the stamped information is collected and written on an image
that is saved on disk and then composited with the actual rendered image from the scene in a custom
post-process step to create the final output. Technicaly speaking this blending is done is the Video
Sequence Editor of the same Blender file as the one opened for the rendering. Temporary scene and
files are then cleaned in order to make all that as transparent as possible for the user.

A previous implementation was based on the Compositing editor but the approach appeared to be not
very reliable and complex to maintain in the case where a post-process compositing graph was already
used in the scene.

Currently no information is visible in real-time directly in the viewport. This may be a good
possible improvement for the add-on.


Features and settings
---------------------

Stamping the output images is pretty simple: check the "Use Stamp Info" checkbox to enable it, check
the metadata you want to print on the image and press the Render button located at the top of the
panel. The images are then computed, composited and displayed (for a still image).

If the "Use Stamp Info" checkbox is not checked then the Blender usual rendering process is launched.

Printable data are sorted in several panels, gathered by theme. The list is available in the
:ref:`Stamp Info Features page <features>` 


One setting is very different from the others though, it is the :ref:`Final Resolution Mode <final-resolution>`.
Basically it allows you to define if you want the data to be written over the rendered image,
hidding a part of it at the top and bottom, or outside the rendered image, making the final composited
image higher than the rendered output.
Both have advantages and inconvenients. We suggest to use the mode "Outside Rendered Images" when in a production context,
it saves rendering time while preserving the same aspect ratio for the cameras in the viewports.


Help and feedback
-----------------

If you have any question or feedback please enter an issue on `the add-on GitHub <https://github.com/ubisoft/stampinfo/issues>`_.
