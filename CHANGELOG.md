# 1.7.15 (2022-03-30)

## Project:

- Improve support for sequence names when using the project settings
   In the Project Settings panel the shot name template has been replaced by 3 identifiers,
   one for the project or act, one for the sequence and one for the shot.

   In the main panel the name of the sequence, when the project settings are used, is now
   set thanks to a dedicated dialog box.

## Tools:

- Improve the shot tool named Create Specified Number of Shots

## OTIO:

- Improve support for custom sequence names
- Clean code for otio and xml exporters

## Fixed:

- FPS variable issue when rendering and when exporting and importing edit file
- Issue in rendered sequence video name: the name of the take was not added
- Issue in OTIO export: the exported take was not the current one
- Issue in Reset Render Settings: initial values were not all restored

## Doc:

- New page for naming of entities

## Dev:

- Improved output messages with logger
- Added patch V1.7.15 to ensure the data compatibility
- Refactored the Render Settings properties initialization
# 1.7.12 (2022-03-23)

- Integration of a Windows wheel for OpenTimelineIO for Python 3.10.
This package will be installed on the user Blender Python environment if no
wheel can be downloaded from the network.

# 1.7.11 (2022-03-22)

- Support for Blender 3.1 and Python 3.10

## Fixed:

- Fixed implicit conversions from float to integer for some Blender parameters because this is not
supported anymore with Python 3.10

- Fixed float framerate values: now non-integer framerates such as 29.97 are supported thanks to a
new set of functions in utils.py: convertFramerateToSceneFPS, setSceneFps, getSceneEffectiveFps


# 1.7.10 (2022-03-03)

## Fixed:

- Popup property panels appearing for several operators
- Shots Play Mode was wrong in Blender 3.x


# 1.7.08 (2022-03-04)

## Rendering:

- Fixed rendering in Playblast mode

## UI:

- "Render Shot Prefix" parameter was renamed Render Sequence Prefix

## Code:

- Cleaned the debug folder to make it a well-integrated package
- render_sequence_prefix renamed to render_sequence_prefix


# 1.7.1 (2022-02-11)

## Fixed:

- Image output were left in the rendering folder

## Edit Files and OpenTimelineIO:

- Fixed several bugs in Edit List File import and export
- Improved the Import dialog window
- Imported edit framerate and resolution can now be used to update the scene
- Added a global and project value to control the index of the first frame in the output file names
- Added a global and project value to control the number of digits in the output file names

## Rendering:

- Added the ability to render image sequences for shots instead or in addition to the videos
- Added a checkbox in the render panel to choose to keep the intermediate rendered images
- Added a Reset Render Properties button

## Grease Pencil:
- Fixed bug when painting on hidden objects

## UI:

- Added button to take range
- Added information for output render
- Added the main panel items menu in the Render Panel

## Code:

- Code cleaning to match Flake8 rules
- Refactor code for output media
***Warning: temp directory names have changed ***

## Debug
- Added debug function to fix entities parent in old blender files

Debug
Added debug function to fix entities parent in old blender files

# 1.6.9 (2021-12-04)

## UX

- Improved performances during animation play
- Fixed crashes on undo and redo with the overlay tools
- Improved warning messages
- Exposed a render param to preserve rendered images
- Added a button to convert camera binding to shots

## Fixes

- Fixed Make All Cameras Unique script

## Preferences and user settings

- Can show or hide overlay tools

## Overlay tools

- Added controls for the Interactive Shots Stack in a toolbar in the Timeline editor

- Exposed preferences to display disabled shots in the timeline and shots stack
- Exposed a Compact mode for the shots stack in the settings

- Refactored code for the handlers
- Improved the look and feel of the Interactive Shots Stack
- Improved the look and feel of the Sequence Timeline

## UI

- Re-vamped all the Settings panels

- Added a viewport target to specify which view will receive the camera and sequence timeline
- Added a node sheet target to specify which timeline or node sheet editor will receive the interactive
shots stack

- Added a button to toggle the scene sound

- Fixed the Frame Time Range button in the Timeline
- improved behaviors when clicking on Set Current shot with modifier keys

## Add-on preferences

- Added a Frame Shot in Timeline option to change the timeline zoom when a shot is selected
- Added a render parameter in the Render Prefs panel to allow the generated files to be kept on disk

## Documentation

- Updated online documentation

## Dev

- Import OpentimelineIO 0.14 from pip
- Refactored Logger integration


# 1.5.77 (2021-11-05)

## Tools

- Removed Camera tools (Create Camera From Viewport and Move Selected Camera to Viewport)
and introduced a button in the Shots section instead
- Made the number of occurrences of each camera appear in red when the camera is used
by several shots

## UI

- Introduced some new icons (Overlay Tools, Retimer, Camera to Viewport...)
- Changed some custom icons, moved some buttons, improved responsive design
- Exposed key mapping for:
   - Shots Play Mode: Alt + Space
   - Toggle Overlay Tools: Not defined


# 1.5.75 (2021-11-05)

- Improved warnings display
- Add a button tp convert camera bound markers to shots
- Fixed bugs in the Best Play Performance mode
- Fixed a bug in the play of the sequence timeline


# 1.5.74 (2021-11-04)

Due to heavy framerate drops when playing the animation with the timelines visible
this version received a deep refactor on the opengl tools:

- Code refactor and cleaning of the opengl features, leading to a new tools category
named Overlay Tools with the followings features:

   - the Sequence Timeline in the 3D viewport
   - the Cameras HUD in the 3D viewport
   - the Interactive Shots Stack in the Timeline editor
   - the start of an opengl graphics components library in utils_ogl.py

- Added a Best Play Performance toggle button near the Display Overlay Tools
to prevent these tools to be drawn at play time in order to increase performances
- Added settings to control which overlay tools should be disabled at play time


# 1.5.73 (2021-09-19)

- Integrated OpenTimelineIO for Blender 2.93 and higher (Windows only)
- Small integration fixes


# 1.5.70 (2021-10-19)

## Features

Added 2 new tools for cameras in the Shots Tools panel:
- New Camera from View: Create a new camera from the current 3D view and put it in the viewport
- Selected Camera to View: Make the selected camera match the the current 3D view

New Shot dialog box:
- Added an option to make the new camera match the current viewport
- Improved the UI
- Added a label to indicate the number of shots using the selected camera

# 1.5.69 (2021-10-15)

## Retimer Tool

Many improvements / bug fixes / code cleaning on the Retimer:

- Bug fix: Grease Pencil wasn't updated after a time change

New features:
- Introduction of an Offset Time mode
- checkbox to force time change on locked animation channels
- doc (in the tooltips)
- time cursor and time range are also affected by retiming (with an option to avoid it)
- display of the retimer is a user pref, not a scene pref anymore
- more stability when the shots are displayed in the timeline

Code:
- deep code refactoring and cleaning

<br><br>

# 1.5.66 (2021-09-23)

## UI and Installation

- Cleaned user feedback at install time in case of errors
- Added a warning when scene contains camera binding and a Clear operator


<br><br>

# 1.5.65 (2021-09-20)

**Shot Manager now works on Blender 2.93!! (with OpenTimelineIO features turn off though :S )**

## UI and Installation

- Better user feedback in case of installation errors

## Documentation

- Improved online documentation


<br><br>

# 1.5.62 (2021-09-02)

## UI

- Added a warning section at the top of the panel to display issues from the scene
- Placed the debug mode toggle in the addon preferences

## Fix

- Debug mode is set to off by default
- Take resolution override has been refactored and fixed
- Scene resolution is now updated correctly from Shot Manager settings

## Code

- Renamed the debug var from UASdebug to DevDebug


<br><br>

# 1.5.60 (2021-08-23)

## Features

- Added a project settings for the default take name

## Fix

- Default resolution for new takes is now the same as the scene resolution


<br><br>

# 1.5.31 (2021-05-16)

## Documentation:

- Updated documentation


<br><br>

# 1.5.10 (2021/01/30)

- First version cleaned from production specific code and with major structural fixes.


<br><br>

--------

# 1.1.X - Production versions



