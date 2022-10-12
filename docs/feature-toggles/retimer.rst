.. _retimer:

.. |br| raw:: html

  <br/>

Retimer
=======

See also :ref:`How to retime the edit or the action <how-to-retimetheeditortheaction>` for a practical use of the retiming tools.

**Retimer is a set of tools that can be used independently from the use of the shots in the scene.
This allows you to change the time of the action, either globaly or on selected objects, without
having to creaste a set of chots.**


The Retimer panel
-----------------

To display the Retimer panel open the :ref:`Feature Toggles panel <feature-toggles-panel>` and click on *Retimer*.

..  image:: /img/feature-toggles/SM_Features_Retimer.png
    :align: center
    :scale: 100%

|br|
The panel then appears below the Shot Manager main panel.

..  image:: /img/feature-toggles/SM_Retimer_Panel.png
    :align: center
    :scale: 80%

|br|

Insert, scale or delete time
----------------------------

In the Retimer panel choose the action you want to do by specifying it in the *Time Mode* dropdown component.

Then set the start time, either in the panel itself or by moving the Current Time main cursor and then pressing
on the up arrow near the time component.

A text line will inform you of the changes that are about to be made, anticipating the new time values.

Then press the button to apply the changes in the scene.

**For some reasons this may create several Undos in the Blender Undo stack. Be cautious when undoing things then.**


Working on the whole scene timing
---------------------------------

By default, or in other words if all the checkboxes of the panel *Apply to* are checked except the checkbox
*Selection Only*, time modifications affects the whole scene. This concerns every animated objects, materials,
entity having an animation track. It also concerns the Video Sequence Editor content (if you use sound clips for
example) and the Grease Pencil animations.

**Actions are not supported: If the scene contains some actions they will not be retimed as expected and it will
very likely break the animation**

Working of a selection of objects or on some entities only
----------------------------------------------------------

Expand the *Apply to...* panel to get access to the proerties to control the scope of the time change.

Selection only
++++++++++++++
    If checked only selected objects or entities will be affected by the change. This is very useful to modify the animation
    onto only some objects of the scene for example.

    If not checked then the change will concern all the entities of the scene, even if they are hidden. It will then be a global
    time change.


Filter checkboxes
*****************
    Each checkbox correspond to a category of entity on which the change will be applied to. It is then possible
    to change the animation only on shots, or on objects, on Grease Pencil...



Limitations
-----------

.. warning::
    - **Actions are not supported:** Changing time in the scene will not affect the Blender animation clips named "actions", if the scene contains some.
      This is because retiming these entities (as well as VSE clips by the way) is a difficult paradigm. It raises a lot of questions
      that we haven't tackled.

