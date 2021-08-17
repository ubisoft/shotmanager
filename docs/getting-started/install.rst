Installation
============

Supported versions
------------------

Shot Manager is developed and actively tested on Windows 10. Community users reported successful usage on Linux platform. 

The currently supported Blender version is 2.92.0. Shot Manager also loads successfully and should work on 2.83 LTS, 2.91.2.

**Shot Manager is currently not working on Blender 2.93 because no OpenTimelineIO package is available at the moment for Python 3.9.
This will be fixed as soon as possible**

.. _download:

Download
--------

Open the `latest release <https://github.com/ubisoft/shotmanager/releases/latest>`__  page from the Shot Manager Gihub `releases page <https://github.com/ubisoft/shotmanager/releases>`_.
Download the zip file listed in **Assets** that has the package icon: |package-icon|.

.. |package-icon| image:: /img/package-icon.png

.. _installing:

Install
-------

**The addon must be installed in Administrator mode so that the OpenTimelineIO Python library can
be downloaded and deployed correctly. Also be sure that your firewall doesn't block the download (or use OpenVPN or equivalent).**

Launch Blender, open the **Preferences** panel and go to the **Add-ons** section.
Press the **Install** button located at the top of the panel. A dialog box opens, pick the Shot Manager
zip file you previously downloaded and validate.
The add-on will be installed. Click on the checkbox at the left side of its name to enable it.

Once the addon is enabled, a Shot Manager tab is displayed in the 3D viewport N-Panel.

