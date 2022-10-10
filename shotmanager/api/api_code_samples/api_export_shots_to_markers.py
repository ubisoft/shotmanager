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
Shot Manager API Sample - Exporting shots as camera bound markers
"""

import bpy

from shotmanager.api import shot_manager
from shotmanager.api import shot
from shotmanager.utils.utils_markers import addMarkerAtFrame


# Get the shot manager instance of the scene
sm_props = shot_manager.get_shot_manager(bpy.context.scene)

# Initialyse shot manager instance to create, amonst other things, a default take
shot_manager.initialize_shot_manager(sm_props)

# Get the list of all the enabled shots
shots = shot_manager.get_shots_list(sm_props, ignore_disabled=True)
print("\nEnabled shots number: ", len(shots))
for s in shots:
    print("  - ", s.name)

    if shot.is_camera_valid(s):
        # marker_name = s.name
        marker_name = shot.get_name(s)
        m = addMarkerAtFrame(bpy.context.scene, shot.get_start(s), marker_name)
        m.camera = shot.get_camera(s)
    else:
        print(f"*** Shot {s.name} has an invalid camera - No marker created")
