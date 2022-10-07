-----
## 2.1.23 (2022-10-01)
- Added a button to set the time range to shot or take range in the Frame Range toolbar
- Improved the Storyborad Frame Editing Mode button
- Improved the API (documentation, samples, code)

-----
## 2.1.22 (2022-10-01)
- Fixed keymap for draw mode to work when the mouve is over the add-on panel

-----
## 2.1.21 (2022-09-30)
- Revamped the UI of the Animated Frame Transformation to minimize UI ambiguities

-----
## 2.1.20 (2022-09-29)
- Several fixes related to the continuous draw mode
- Fixed storyboard frame that was not duplicated following to a take duplication
- Added shot name in the Render panel, near Current Shot label
- Refactored the Duplicate Shot dialog box and added a checkbox for color variation
- Added a key map for activating the draw mode on a current shot

-----
## 2.1.5 (2022-09-27)
- Fixed a crash on Storyboard Grid because of Python 3.10 code

-----
## 2.1.4 (2022-09-14)
### Interactive Shots Stack
- Added an info component
- Added mode and scale keyframe changes when a shot clip is manipulated

### Code
- Added a sample widget to the gpu components library

-----
## 2.1.3 (2022-09-12)
- Fixed regression bug on Convert Camera Binding
- Fixed the detached grease pencil transform lock state
- Added a function to get the canvas frame when missing

-----
## 2.1.2 (2022-09-12)
- Fixed the type of shot that was set to Storyboard when a storyboard frame was added

-----
## 2.1.1 (2022-09-12)
**Beta Release**
### Keymaps
- Separated key mappings per category
- Added a Preferences parameter to toggle the vertical arrows used to navigate from shot to shot
- Made the up arrow go to next shots by default instead of previous ones

### Shots Stack UI
- Added a Preferences setting to make the shots stack starts at the specified lane
- Set the first lane to 1 instead of 0 to see the keys of the Summany lane

-----
## 2.0.226 (2022-09-12)
### Shots Stack UI
- Added a user preference to automaticaly detect the sceen display factor (Windows only)

-----
## 2.0.224 (2022-08-24)
**Pre-Release**
### Retimer, markers
- Retimer UI and structure refactored and simplified
- Added support for markers in Retimer

- Fixed header title display when add-on has a warning

-----
## 2.0.223 (2022-08-24)
### Markers
- Integrated the tool Markers Nav Bar from the add-on Ubisoft Video Tracks

-----
## 2.0.222 (2022-08-23)
- Fixed error message at install time when internet connection is not available

-----
## 2.0.221 (2022-08-22)
### UX/UI
- In the Shots Global Settings the Passepartout has been moved out of the Overlays box since it is not an overlay property
- Improved the message displayed in the 3D views to identify the target viewport
- Added a dropdown property to be able to change the Overlays for every viewport, not only the target one

### Code
- Big refactor in files to introduce a function to get the add-on preferences

- Fixed Overlays Layer Opacity that wasn't working every time
- Fixed error message when material was not available for the drawing preset

-----
## 2.0.220 (2022-08-11)
- Small fix on the storyboard shot type icon

-----
## 2.0.214 (2022-08-10)
**Release**

-----
## 2.0.210 (2022-08-09)
- Changed the name of the add-on in the bl_info to "Ubisoft Shot Manager"

-----
## 2.0.206 (2022-08-04)
### Storyboard
- Major fix on the materials associated to layers. They are now correctly set when the layer is changed
- Fixed animation clearing when a storyboard frame is detached

-----
## 2.0.205 (2022-08-04)
### Storyboard
- Added a feature to detach a storyboard frame from a shot
- Refactored collection names for empties and storyboard frames to support multiple scenes

- Added the Passepartout controls to the Shots Global Control panel

- Fixed GP tool not set when entering in Draw mode

-----
## 2.0.204 (2022-08-03)
### UX/UI
- Added notion of "layout" to have a different and customizable UI when in Storyboard and in Previz mode
- Added a patch to support this feature

### Project Settings
- Added a new parameter to specify a camera to be used as a template for new shots, picked from a Blender file

- Fixed overlay state that wasn't restored correctly
- Fixed Sequence Timeline that wasn't interactive anymore when the overlay was off
- Fixed the orientation of the Storyboard Shots cameras to match the grid direction
- Fixed visibility of storyboard frames throughout takes
- Fixed hide cameras for Storyboard Shots

-----
## 2.0.202 (2022-07-29)
- Fixed visibility of storyboard frames: the frames belonging to a "storyboard" shot are kept visible
  even if not current, whereas the frames from "camera" shots are hidden when those shots are not current. See documentation "Storyboard Frames Visibility"
- Shots can now be renamed by directly double-clicking on their name in the Shots list

### UI
- Added icons in the shot column and the Shots Stack for shots of type "storyboard"

-----
## 2.0.201 (2022-07-24)
- Full integration of Stamp Info inside Shot Manager: this add-on doesn't depend anymore
  on the Stamp Info add-on

-----
## 2.0.105 (2022-07-21)
### Interactive Shots Stack
- Completely rewrote the Shots Stack UI and graphics library: this was required for a long time
  to improve the UI and to fix some glitches and visual bugs. It also allowed to fix the
  events loop that didn't work anymore due to changes in the API in Blender 3.2
- Sequence Timeline is not hidden by default anymore when the viewport overlay tools display is
  turned off. This can be changed in the Sequence Timeline Preferences


-----
## 2.0.104 (2022-06-22)
- Installation of Stamp Info add-on during the installation of Shot Manager
- Fixed Logger path

-----
## 2.0.101 (2022-06-08)
#### Documentation
- Add Experimental page

#### Rendering
- Fixed bug on Render Playblast, intermediate files are now deleted

-----
## 2.0.35 (2022-06-07)
#### Warnings
- Add a warning and reset button for pixel aspect, fps, resolution

#### Grease pencil and Storyboard
- Fixed layers creation process
- Added a Reset to Default button for all the usage presets


-----
## 2.0.34 (2022-06-03)
#### UX
- Improve the grease pencil continuous editing workflow
- Turned off the Use Best Play Performances mode by default

#### UI
- Add an Overlay toggle button in the Global Settings of the storyboard panel


-----
## 2.0.33 (2022-06-03)
#### UI
- Added a button to better identify the current layout and easily toggle it

#### Rendering
- Added support for take note in the rendering of Stamp Info, when project settings are used
- Added a button to disable the Blender metadata burning in the warnings
- Fixes in rendering resolution, use of Stamp Info and display of grease pencil


-----
## 2.0.32 (2022-06-01)
#### General
- Added a Shift modifier key on shot creation and deletion to skip the dialog box
- Added an add-on preference to store the Delete Cameras of the Remove Shots operator
- Added a button in Features to toggle the display of Stamp Info in the 3D view tab list

#### Rendering
- Added a Resolution Percentage parameter for each render preset
- Added an Open in Player button for Render Current
- Moved the render warning UI component below in the panel to make it more visible


-----
## 2.0.31 (2022-06-01)
#### Storyboard
- Continuous drawing mode while changing storyboard frames


-----
## 2.0.30 (2022-05-30)
#### Bug fix:
- Shots Stack not working on Blender 3.0.x: Fixed an implicit Float to Int conversion
- Camera passepartout is now working for all the cameras, not only storyboard frames
- Fixed error message when render root path is invalid

#### Rendering
- Improve warnings and added a dialog box when render root path is invalid
- Fixed Stamp Info not rendered even when activated in the project settings


-----
## 2.0.28 (2022-05-25)
- Fix message for json test file


-----
## 2.0.27 (2022-05-25)
- Bug fixes on rendering

- Bug NOT FIXED: When the number of digits is inferior to the effective number of digits in the
  file name then the image or sequence are not recognized in the VSE Compositing function


-----
## 2.0.26 (2022-05-25)
- Added a new layer support in Storyboard Frames for perspective - May not be stable !!!


-----
## 2.0.25 (2022-05-24)
- Added the support for a minimal version of Stamp Info
- Fixed color issue to maintain the view_transform mode (Filmic, Standard...)
- Fixed issue with Keep Intermediate Rendering Images


- Improved the support of the project setting Video First Frame to allow the rendering images to
  use offset indices


- Fixed Interactive Shots Stack processor consumption
- Fixed issue in the offset of camera background video


-----
## 2.0.24 (2022-05-23)
- Fixed issue in the offset of camera background video


-----
## 2.0.21 (2022-05-10)
- Display the shots names over the storyboard frames when the camera is hidden


-----
## 2.0.20 (2022-05-06)
- Added key mapping for previous and next shots, previous and next grease pencil key frame
- Added a frame grid and a frame grid panel to update the way storyboard frames are placed in 3D space
- Added a passepartout global value on storyboard frames


-----
## 2.0.19 (2022-05-04)
- Added a UI information to inform the user of a new available version


-----
## 2.0.18 (2022-05-02)
#### Storyboard
- Fixed UI and storyboard frame behaviors
- Added buttons to add, duplicate or remove grease pencil key frames
- Changed the alternative behaviors of the storyboard frame action to toggle layer visibility

-----
## 2.0.17 (2022-04-29)
#### Storyboard
- Added a frame grid to order the storyboard frames in space


-----
## 2.0.16 (2022-04-26)
- Support for Blender 3.1 and Python 3.10


-----
## 2.0.15 (2022-04-20)
#### Storyboard
- Improved presets panel to support materials + fixes
- Fixed issue on current object material list


-----
## 2.0.13 (2022-04-20)
#### Storyboard
- Added a "storyboard" layout with a lightened UI for the shots items in the shot list
- Added a property "Type" to define the role of each shot (storyboard, previz...)


-----
## 2.0.12 (2022-04-15)
#### Storyboard
- Improvement of the storyboard frames entry to draw mode
- Added a Pin mode to maintain the selected grease pencil object referenced in the panel
- Added a panel to set up the usages and context of each layer, and support for up to 8 usage presets

#### General
- Patch to correctly update previous scenes with the usage template


-----
## 2.0.10 (2022-04-11)
- Added a checkbox to set the current shot camera to the viewport when a free grease pencil object enters into draw mode
- Added a dropdown to set the stroke placement and origin when a free grease pencil object enters into draw mode
- Modified the alternative behaviors for the Set Current Shot button in order to change the current shot
without changing the current viewport


-----
## 2.0.9 (2022-04-08)
- Introduction of an Empty object between the shot camera and the storyboard grease pencil in order to
allow animated frames


-----
## 2.0.5 (2022-04-05)
- Exposed the size of the shot names displayed over the cameras in the viewport
in the add-on Preferences panel as well as in the Features panel preferences
- Fix: The name of the shots is not displayed anymore for hidden cameras


-----
## 1.7.16 (2022-04-24)
#### Camera HUD:
- Exposed the size of the shot names displayed over the cameras in the viewport
in the add-on Preferences panel as well as in the Features panel preferences
- Fix: The name of the shots is not displayed anymore for hidden cameras


-----
## 1.7.15 (2022-03-30)
#### Project:
- Improve support for sequence names when using the project settings
   In the Project Settings panel the shot name template has been replaced by 3 identifiers,
   one for the project or act, one for the sequence and one for the shot.

   In the main panel the name of the sequence, when the project settings are used, is now
   set thanks to a dedicated dialog box.

#### Tools:
- Improve the shot tool named Create Specified Number of Shots

#### OTIO:
- Improve support for custom sequence names
- Clean code for otio and xml exporters

#### Fixed:
- FPS variable issue when rendering and when exporting and importing edit file
- Issue in rendered sequence video name: the name of the take was not added
- Issue in OTIO export: the exported take was not the current one
- Issue in Reset Render Settings: initial values were not all restored

#### Doc:
- New page for naming of entities

#### Dev:
- Improved output messages with logger
- Added patch V1.7.15 to ensure the data compatibility
- Refactored the Render Settings properties initialization


-----
## 1.7.12 (2022-04-24)
- Integration of a Windows wheel for OpenTimelineIO for Python 3.10.
This package will be installed on the user Blender Python environment if no
wheel can be downloaded from the network.


-----
## 1.7.11 (2022-03-22)
- Support for Blender 3.1 and Python 3.10

#### Fixed:
- Fixed implicit conversions from float to integer for some Blender parameters because this is not
supported anymore with Python 3.10
- Fixed float framerate values: now non-integer framerates such as 29.97 are supported thanks to a
new set of functions in utils.py: convertFramerateToSceneFPS, setSceneFps, getSceneEffectiveFps


-----
## 1.7.10 (2022-03-03)
#### Fixed:
- Popup property panels appearing for several operators
- Shots Play Mode was wrong in Blender 3.x


-----
## 1.7.08 (2022-03-04)

#### Rendering:
- Fixed rendering in Playblast mode

#### UI:
- "Render Shot Prefix" parameter was renamed Render Sequence Prefix

#### Code:
- Cleaned the debug folder to make it a well-integrated package
- render_sequence_prefix renamed to render_sequence_prefix


-----
## 1.7.1 (2022-02-11)

#### Fixed:
- Image output were left in the rendering folder

#### Edit Files and OpenTimelineIO:
- Fixed several bugs in Edit List File import and export
- Improved the Import dialog window
- Imported edit framerate and resolution can now be used to update the scene
- Added a global and project value to control the index of the first frame in the output file names
- Added a global and project value to control the number of digits in the output file names

#### Rendering:
- Added the ability to render image sequences for shots instead or in addition to the videos
- Added a checkbox in the render panel to choose to keep the intermediate rendered images
- Added a Reset Render Properties button

#### Grease Pencil:
- Fixed bug when painting on hidden objects

#### UI:
- Added button to take range
- Added information for output render
- Added the main panel items menu in the Render Panel

#### Code:
- Code cleaning to match Flake8 rules
- Refactor code for output media
***Warning: temp directory names have changed ***

#### Debug
- Added debug function to fix entities parent in old blender files


-----
## 1.6.9 (2021-12-04)

#### UX
- Improved performances during animation play
- Fixed crashes on undo and redo with the overlay tools
- Improved warning messages
- Exposed a render param to preserve rendered images
- Added a button to convert camera binding to shots

#### Fixes
- Fixed Make All Cameras Unique script

#### Preferences and user settings
- Can show or hide overlay tools

#### Overlay tools
- Added controls for the Interactive Shots Stack in a toolbar in the Timeline editor


- Exposed preferences to display disabled shots in the timeline and shots stack
- Exposed a Compact mode for the shots stack in the settings


- Refactored code for the handlers
- Improved the look and feel of the Interactive Shots Stack
- Improved the look and feel of the Sequence Timeline

#### UI
- Re-vamped all the Settings panels


- Added a viewport target to specify which view will receive the camera and sequence timeline
- Added a node sheet target to specify which timeline or node sheet editor will receive the interactive
shots stack


- Added a button to toggle the scene sound


- Fixed the Frame Time Range button in the Timeline
- improved behaviors when clicking on Set Current shot with modifier keys

#### Add-on preferences
- Added a Frame Shot in Timeline option to change the timeline zoom when a shot is selected
- Added a render parameter in the Render Prefs panel to allow the generated files to be kept on disk

#### Documentation
- Updated online documentation

#### Dev
- Import OpentimelineIO 0.14 from pip
- Refactored Logger integration


-----
## 1.5.77 (2021-11-05)

#### Tools
- Removed Camera tools (Create Camera From Viewport and Move Selected Camera to Viewport)
and introduced a button in the Shots section instead
- Made the number of occurrences of each camera appear in red when the camera is used
by several shots

#### UI
- Introduced some new icons (Overlay Tools, Retimer, Camera to Viewport...)
- Changed some custom icons, moved some buttons, improved responsive design
- Exposed key mapping for:
   - Shots Play Mode: Alt + Space
   - Toggle Overlay Tools: Not defined


-----
## 1.5.75 (2021-11-05)

- Improved warnings display
- Add a button tp convert camera bound markers to shots
- Fixed bugs in the Best Play Performance mode
- Fixed a bug in the play of the sequence timeline


-----
## 1.5.74 (2021-11-04)

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


-----
## 1.5.73 (2021-09-19)

- Integrated OpenTimelineIO for Blender 2.93 and higher (Windows only)
- Small integration fixes


-----
## 1.5.70 (2021-10-19)

#### Features

Added 2 new tools for cameras in the Shots Tools panel:
- New Camera from View: Create a new camera from the current 3D view and put it in the viewport
- Selected Camera to View: Make the selected camera match the the current 3D view

New Shot dialog box:
- Added an option to make the new camera match the current viewport
- Improved the UI
- Added a label to indicate the number of shots using the selected camera


-----
## 1.5.69 (2021-10-15)

#### Retimer Tool
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


-----
## 1.5.66 (2021-09-23)

#### UI and Installation
- Cleaned user feedback at install time in case of errors
- Added a warning when scene contains camera binding and a Clear operator



-----
## 1.5.65 (2021-09-20)

**Shot Manager now works on Blender 2.93!! (with OpenTimelineIO features turn off though :S )**

#### UI and Installation
- Better user feedback in case of installation errors

#### Documentation
- Improved online documentation



-----
## 1.5.62 (2021-09-02)

#### UI
- Added a warning section at the top of the panel to display issues from the scene
- Placed the debug mode toggle in the addon preferences

#### Fix
- Debug mode is set to off by default
- Take resolution override has been refactored and fixed
- Scene resolution is now updated correctly from Shot Manager settings

#### Code
- Renamed the debug var from UASdebug to DevDebug


-----
## 1.5.60 (2021-08-23)

#### Features
- Added a project settings for the default take name

#### Fix
- Default resolution for new takes is now the same as the scene resolution



-----
## 1.5.31 (2021-05-16)

#### Documentation:
- Updated documentation


-----
## 1.5.10 (2021/01/30)

- First version cleaned from production specific code and with major structural fixes.



-----
## 1.1.X - Production versions



