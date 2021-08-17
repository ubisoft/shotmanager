# Dev Notes for Shot Manager

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