.. _panel-features:

Panel features
==============

Panel features are a set of modules that can be triggered in order to extend the capabilities of Shot Manager.
When activated a module and its related graphics components will become visible in the main panel, at various places
according to its way of working.

**Modules are not enabled by default because they can add a significant complexity to the genereal interface of Shot Manager.
It is then strongly advised to activate only the ones you need, at the time you need. You can reactivate them at will.**

**Modules are just UI components. Disabling a module will not change anything in the scene or in the current configuration of Shot Manager.**


Opening the Features dialog box
-------------------------------

There are 2 ways to open the Features dialog box:

- Click on the panel Settings button to open the Settings menu and choose *Features*:

..  image:: /img/features-advanced/SM_Features_OpenFromSettings.png
    :align: center
    :scale: 100%

- Or directly click on the *Features* button.
  
    This button offers a quick access to the Features dialog box, which you may find convenient when you often toggle some features in order
    to keep the UI light.

..  image:: /img/features-advanced/SM_Features_OpenFromButton.png
    :align: center
    :scale: 100%

The Features dialog box gets opened. It allows the listed featuers to be toggled by a simple click on they associated button.

..  image:: /img/features-advanced/SM_Features_DialogBox.png
    :align: center
    :scale: 100%



Available features
------------------

The following features add their UI control components into the Take and the Shots panels:

- :ref:`Shot and take notes <shot-and-take-notes>`: Add notes on shots and takes to better manage your scene content.
- :ref:`Camera backgrounds <camera-backgrounds>`: Use and toggle camera backgrounds.


Retimer is a tool on its own. When turned on a new panel named *Retimer* will appear below the Shots panel.

- :ref:`Retimer <retimer>`: Insert, delete or scale time globally or on selected entities of the scene.



.. toctree::
    :maxdepth: 3
    :hidden:
    :caption: Advanced Features
 
    camerabg
    notes
    retimer


 