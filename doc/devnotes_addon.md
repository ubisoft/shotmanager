# Dev Notes for Shot Manager

- [Installation](#installation)
- [dependencies](#dependencies)
- [Important points in Shot Manager](#important-points-in-shot-manager)


## Installation
The addon must be installed in Administrator mode so that the OpenTimelineIO Python library can
be downloaded and deployed correctly. Also be sure that your firewall doesn't block the download (or use OpenVPN or equivalent).

## Dependencies
Shot Manager requires the following packages and add-ons to run at its best:

- **OpenTimelineIO Python wheel:** This Python package is automatically installed all along with Shot Manager.

- **Stamp Info:** This add-on has been developed by Ubisoft Animation Studio at the same time than Shot Manager.
    Its purpose is to write information on the rendered images.

    It is NOT mandatory, Shot Manager can run without it but some features will then not be available.

    It has to be installed manually, it can be downloaded here: [https://github.com/ubisoft/stampinfo](https://github.com/ubisoft/stampinfo)

## Important points in Shot Manager

### 3D:
- Camera markers are NOT compatible with Shot Manager. They prevent the shot play to work correctlt.
Shot Manager will then not allow their use by freezint its user interface.

- Negative frames are not supported. When starting the action prepare a sate time zone between 0 and the
start of the first shot (including the lenght of the handles).

- The end frame of a shot is included in the shot and rendered.
The duration of a shot (ie the total number of frames) is then equal to end - start + 1

### 3D Edit:
- By default first frame of the edit is 0, as most edititng applications, but this is a preference and it can
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