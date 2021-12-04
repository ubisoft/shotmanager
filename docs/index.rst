.. |br| raw:: html

  <br/>

..  image:: /img/ubisoft_logo.png
    :align: center

Ubisoft Shot Manager: Creative narration and editing with Blender
=================================================================

**Manage the cameras and the editing of your scenes inside Blender in real time and with great simplicity.**

**Current version: 1.6. Compatible with Blender 2.93.x and 3.0.x**

..  image:: /img/ShotManager_screen.png
    :align: center
    :width: 80%


|br|
See how this tool was used in production: `User Stories - Blender and the Rabbids <https://www.blender.org/user-stories/blender-and-the-rabbids/?utm_source=www-homepage>`__.


Disclaimer
----------

Shot Manager is a pre-production tool that was initialy developed to support the previz of an animated TV series we did at Ubisoft between
January 2020 and February 2021. We believe it can be very interesting for the Blender community so we shared it as an open source project and we keep supporting it.

Since it was dedicated to our production needs some limitations may appear for a more general purpose. Quality of the code is also probably arguable.
In spite of all our efforts to make it reliable, it may in some circumstances corrupt you Blender scenes data.
Be aware that neither Ubisoft nor Ubisoft employees can be taken as responsible in such cases. Use it at your own risks.

**This said, we will do our best to listen to your feedback and improve this add-on accordingly in order to provide a robust and flexible production tool.
Have fun !**

.. warning::
   !! Blender 2.93: Some features (EDL imports and exports) are NOT YET SUPPORTED ONT THIS VERSION because there is currently no OpenTimelineIO package for Python 3.9 !!
   
   This will be fixed as soon as possible.

   
Getting started
---------------

**It is highly recommended to start by reading the** :ref:`Shot Manager General Philosophy <general-philosophy>` **to clearly understand the purpose of this tool !**

Then:

   * :ref:`Download <download>` the Shot Manager zip file,
   * :ref:`Install <installing>` Shot Manager as a Blender addon,
   * Mind the :ref:`features <features-and-limitations>` and the :ref:`vocabulary <glossary>`,
   * ...And at last :ref:`try out <first-steps>` your installation !


.. toctree::
   :maxdepth: 2
   :hidden:
   
   /getting-started/general-philosophy

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Getting started

   /getting-started/install
   /getting-started/features
   /getting-started/first-steps
   /getting-started/glossary
   
.. toctree::
   :maxdepth: 3
   :hidden:
   :caption: Features

   /features/features
   /features/main-panel
   /features-advanced/advanced-features
   
.. toctree::
   :maxdepth: 3
   :hidden:
   :caption: Settings
   
   /settings/add-on-preferences
   /settings/project
   /settings/keymap
   
.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: How to...

   /how-to/how-to
   /how-to/how-to-advanced
   /how-to/use-in-production
   /how-to/tips


.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Troubleshooting

   /troubleshoot/faq
   /troubleshoot/issue


.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: I want more

   /more/more-addons