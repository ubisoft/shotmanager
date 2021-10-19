# 1.5.74 (2021-09---) (WIP)

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

Mainy improvements / bug fixes / code cleaning on the Retimer:

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



