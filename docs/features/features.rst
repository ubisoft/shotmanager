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
- EDL import and export based on OpenTimelineIO
- Grease pencil sketching per shot (experimental)
- Edit forth and back with VSE (experimental)
- ...


Limitations
-----------

.. warning::
    - Blender 2.93: Some features (EDL imports and exports) are NOT YET SUPPORTED ONT THIS VERSION because there is currently no OpenTimelineIO package for Python 3.9

    - Shot Manager is not compatible with camera binding. Indeed the *Shot Play Mode* overrides the standant play mode and has its own
      way of changing the viewport camera. Good news is this mode is far more powerfull than the camera binding approach :)

    - Actions are not supported by the Retimer tool.

