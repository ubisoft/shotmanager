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
Data patch
"""

import bpy
from ..utils import utils
from shotmanager.config import config


# Patch to upgrade the shot manager data created with a shot manager version older than V.1.2.25

# v1_2_25: 1002025
def data_patch_to_v1_2_25():
    for scene in bpy.data.scenes:
        # if "UAS_shot_manager_props" in scene:
        if getattr(bpy.context.scene, "UAS_shot_manager_props", None) is not None:
            #  print("\n   Shot Manager instance found in scene " + scene.name)
            props = config.getAddonProps(scene)

            # print("     Data version: ", props.dataVersion)
            # print("     Shot Manager version: ", bpy.context.window_manager.UAS_shot_manager_version)
            if props.dataVersion <= 0 or props.dataVersion < bpy.context.window_manager.UAS_shot_manager_version:

                # apply patch and apply new data version
                #   print("       Applying data patch data_patch_to_v1_2_25 to scenes")
                takes = props.getTakes()
                for take in takes:
                    take.getParentScene()
                    shots = props.getShotsList()
                    for shot in shots:
                        shot.getParentScene()

                # set right data version
                # props.dataVersion = bpy.context.window_manager.UAS_shot_manager_version
                props.dataVersion = 1002025
                print(
                    f"       {scene.name}: Data upgraded to version V.{utils.convertVersionIntToStr(props.dataVersion)}"
                )
