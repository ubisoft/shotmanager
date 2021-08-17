![](doc/images/Logo_90_A.png)
# Shot Manager - Blender Add-on
Shot Manager is a Blender add-on that introduces a true shot entity in Blender scenes, as well as a wide and powerful set of tools to build and edit sequences in real-time directly in the 3D context.

**Disclaimer**
>**This tool is currently supported for LTS version of Blender 2.83 and up to Blender 2.92**
>
>**At the moment it is NOT compatible with Blender version 2.93 because there is currently no OpenTimelineIO package for Python 3.9**
>
>It was initialy developed for an animated TV series production in 2020 on Blender 2.83. It has the features that were needed at the time but it
may not be considered as feature complete for a more generic purpose. In spite of all our efforts to make it reliable some troubles may occur in use cases we have not faced.
>
><br />

Note that development is on Windows 10. Please report issues and submit PRs for other OSs.

## Purpose

Manages the shots of a Blender scene. It offers a realtime editing directly on
the data of a 3D scene.
Shot Manager is very versatile and can be useful in many cases.
The main usecase is this: A continuous action is set in a scene, then some cameras
are put at the appropriate places in the world and a shot is created for each one of
them in order to record the right segment of time.
This is very convenient for previz and 3D layout.

<br />
<img src="docs/img/ShotManager_screen.png" alt="ShotManager Screen" width="70%"/>
<br /><br />

For installation, features, FAQ, user help please check the documentation here: [https://ubisoft-shotmanager.readthedocs.io](https://ubisoft-shotmanager.readthedocs.io)

## Dev notes

Various development notes related to the add-on itself, to the Git project or to the installation are available here: [Dev Notes](./doc/devnotes.md)
This add-on requires the OpenTimelineIO Python wheel. This library is automaticaly downloaded and deployed on the
Blender instance when the add-on is installed.

>The addon must be installed in Administrator mode so that the OpenTimelineIO Python wheel can
>be downloaded and deployed correctly. Also be sure that your firewall doesn't block the download (or use OpenVPN or equivalent).

## History
[Change Log](./CHANGELOG.md)

# Support

The active support repository is on the [StampInfo Github repository](https://github.com/ubisoft/shotmanager) which is part of the [Ubisoft open source](https://github.com/ubisoft) projects group.


# License and copyright

The original code is Copyright (C) 2021 Ubisoft.

All code of the `shotmanager` package is under the GPLv3 license.
