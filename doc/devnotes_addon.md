# Dev Notes for Shot Manager

- [Installation](#installation)
- [Dependencies](#dependencies)
- [Widgets and components](#widgets-and-components)
- [Important points in Shot Manager](#important-points-in-shot-manager)


</br>

## Installation
The addon must be installed in Administrator mode so that the OpenTimelineIO Python library can
be downloaded and deployed correctly. Also be sure that your firewall doesn't block the download (or use OpenVPN or equivalent).


</br>

## Dependencies
Shot Manager requires the following packages and add-ons to run at its best:

- **OpenTimelineIO Python wheel:** This Python package is automatically installed all along with Shot Manager.

- **Stamp Info:** This add-on has been developed by Ubisoft Animation Studio at the same time than Shot Manager.
    Its purpose is to write information on the rendered images.

    It is NOT mandatory, Shot Manager can run without it but some features will then not be available.

    It has to be installed manually, it can be downloaded here: [https://github.com/ubisoft/stampinfo](https://github.com/ubisoft/stampinfo)


</br>

## Widgets and components

- [Interactive Shots Stack](../shotmanager/overlay_tools/interact_shots_stack/doc/interac_shots_stack.md)
- [Doc GPU Library](../shotmanager/gpu/gpu_2d/doc_gpu_2d_components.md)


</br>

## Important points in Shot Manager

### 3D:
- Camera markers are NOT compatible with Shot Manager. They prevent the shot play to work correctly.
Shot Manager will then not allow their use by freezint its user interface.

- Negative frames are not supported. When starting the action prepare a start time zone between 0 and the
start of the first shot (including the lenght of the handles).

- The end frame of a shot is included in the shot and rendered.
The duration of a shot (ie. the total number of frames) is then equal to end - start + 1

### 3D Edit:
- By default first frame of the edit is 0, as most editing applications, but this is a preference and it can
be set to 1, or event to an arbitrary (positive) number (so that the sequence and exported xml can be added
at the end of another one)

### Media:
- First frame of the exported videos gets the number 0 (and not 1)
- Hence the last frame of a media is equal to duration - 1
- Rendered media and exports are done in the specified Root directory. Path relative to the current project are
supported.


### Naming:
- Shot: Association of a period of time in the 3D scene, given by a start and a end, and a point of view, given
by the camera held by the shot.


</br>

## Props, the main properties class
Terminology:
    We distinguish the "selected shot", which is the one selected in the shots list, from the "current shot",
    which is the shot actualy displayed in the viewport and identified in the shots list with an orange icon
    in the first column.

</br>

## Shot select, set current, set to Draw Mode

The manipulation behaviors are defined in the Shot Manipulations rollout of the add-on Preferences.
They are all part of the add-on preferences settings, so any change is applied to every scenes.

Key functions and operators to manage those manipulations are:

### When a shot becomes selected
- *In props.py:* The update() function of selected_shot_index: IntProperty holds all the actions done when
  a shot is selected

- The fact that a shot that has just been selected should be made as the current one is defined by the
  function props.selectedShotShouldBecomeCurrent()

### When a shot becomes current
- *In shots.py:* The operator uas_shot_manager.set_current_shot holds all the actions done when a shot is
  made current
- In props.setCurrentShotByIndex()

### When a shot has to be set to Draw mode
- To set the draw mode of a shot, when in Continuous mode: uas_shot_manager.greasepencil_select_and_draw
