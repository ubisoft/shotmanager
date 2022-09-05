.. _features-and-limitations:

Features and limitations
========================


Overview
--------

- Creation of shots from scene cameras and of sequences from those shots
- Non-linear real-time play of the sequences
- :ref:`Action and edit global retime <how-to-retimetheeditortheaction>`
- Global control on camera video backgrounds
- Global control on camera sound backgrounds
- Sequence batch rendering, with Eevee, Cycle and custom playblast
- Edit file import and export based on OpenTimelineIO
- Grease pencil sketching per shot (experimental)
- Edit forth and back with VSE (experimental)
- ...


Limitations
-----------

.. warning::
    - Shot Manager is not compatible with camera binding. Indeed the *Shots Play Mode* overrides the standant play mode and has its own
      way of changing the viewport camera. Good news is this mode is far more powerfull than the camera binding approach :)
      
      Use the convertion tools available in the Warning area of the add-on panel to convert the bound markers to shots.


    - Actions are not supported by the Retimer tool.

