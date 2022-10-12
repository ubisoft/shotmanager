.. |br| raw:: html
   
  <br/>


.. _si-features:

Features and limitations
========================


Information categories
----------------------

* :ref:`Time and frames information <time-and-frame-info>`
* :ref:`Shot and camera information <shot-and-camera-info>`
* :ref:`Metadata information <metadata-info>`

.. toctree::
   :maxdepth: 4
   :hidden:
   :caption: Stamp Info
  
   /rendering/stampinfo/time-and-frame-info


.. _final-resolution:

Setting up the final resolution
-------------------------------

The Final Resolution Mode defines how the metadata will be arranged over the rendered image.

* **Over Rendered images:** 

In this mode the black bands on which metadata text will be written directly on the image. It
will then hide a part of it at the top and bottom. The final image still have the same resolution
than the rendering output image.

..  image:: /img/rendering/StampInfoModes_Over.jpg
    :align: center


|br|
* **Outside Rendered images:**

In this second mode the metadata are written outside the rendering output image, making the final composited
image higher than the resolution specified in the Blender Rendering panel.

..  image:: /img/rendering/StampInfoModes_Outside.jpg
    :align: center


|br|
Both have advantages and inconvenients. We suggest to use the mode "Outside Rendered Images" when in a production context,
it saves rendering time while preserving the same aspect ratio for the cameras in the viewports.

For a more detailed description of these values watch `this part of the video tutorial <https://youtu.be/Sj2GyYhxFX4?t=272>`__.


Text and layout
---------------

How information is organised on the rendered frame.


Limitations
-----------

The layout for the text and information stamped on the framed image is currenly better fitted for 16:9 ratio.
Other ratios may produce unpredictable results. We have consideration for that issue for the future.

