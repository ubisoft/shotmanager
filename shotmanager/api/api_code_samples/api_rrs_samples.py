# GPLv3 License
#
# Copyright (C) 2021 Ubisoft
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Shot Manager API samples - RRS examples

Documentation and general concepts: https://github.com/ubisoft/shotmanager/blob/main/doc/shot_manager_api.md
"""

import bpy
import os

from shotmanager.api import rrs

# This should work with any scene where a Shot Manager instance has been instanced and where
# there are several shots
# In case a scene is required you can use this one from the GitLab:
# https://gitlab-ncsa.ubisoft.org/animation-studio/blender/shotmanager-addon/-/blob/master/fixtures/shots_sceneRunningRabbid/shots_sceneRunningRabbid.blend


# Get current file path
current_file = bpy.data.filepath
current_dir = os.path.dirname(current_file)

if "" == current_file:
    print("*** Save the scene first ***")


# Initialize the shot manager of the current scene with the project environment variables
rrs.initialize_for_rrs(override_existing=True, verbose=True)

# launch the rendering process of the shots from the current take and get a dictionary of
# the rendered and failed files
# The dictionary have the following entries: rendered_files, failed_files, otio_file
files_dico = rrs.publishRRS(current_dir, take_index=-1, verbose=True, use_cache=False)

print("\nRendered files: ", len(files_dico["rendered_files"]))
for f in files_dico["rendered_files"]:
    print("   - ", f)

print("\nFailed files: ", len(files_dico["failed_files"]))
for f in files_dico["failed_files"]:
    print("   - ", f)

print("\Otio files: ", len(files_dico["otio_file"]))
for f in files_dico["otio_file"]:
    print("   - ", f)
