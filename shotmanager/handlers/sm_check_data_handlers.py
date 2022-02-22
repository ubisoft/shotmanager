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
Shot Manager Init for check data handlers
"""

import bpy
from bpy.app.handlers import persistent

from shotmanager.utils import utils

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


@persistent
def shotMngHandler_load_post_checkDataVersion(self, context):
    loadedFileName = bpy.path.basename(bpy.context.blend_data.filepath)
    print("\n\n-------------------------------------------------------")
    if "" == loadedFileName:
        print("\nNew file loaded")
    else:
        print("\nExisting file loaded: ", bpy.path.basename(bpy.context.blend_data.filepath))
        _logger.info("  - Shot Manager is checking the version used to create the loaded scene data...")

        latestVersionToPatch = 1003061

        numScenesToUpgrade = 0
        lowerSceneVersion = -1
        for scn in bpy.data.scenes:

            # if "UAS_shot_manager_props" in scn:
            #  if getattr(bpy.context.scene, "UAS_shot_manager_props", None) is not None:
            if getattr(scn, "UAS_shot_manager_props", None) is not None:
                #   print("\n   Shot Manager instance found in scene " + scn.name)
                props = scn.UAS_shot_manager_props

                _logger.debug_ext(f"Scene: {scn.name}, props.dataVersion: {props.dataVersion}", col="RED")

                # # Dirty hack to avoid accidental move of the cameras
                # try:
                #     print("ici")
                #     if bpy.context.space_data is not None:
                #         print("ici 02")
                #         if props.useLockCameraView:
                #             print("ici 03")
                #             bpy.context.space_data.lock_camera = False
                # except Exception as e:
                #     print("ici error")
                #     _logger.error("** bpy.context.space_data.lock_camera had an error **")
                #     pass

                #   print("     Data version: ", props.dataVersion)
                #   print("     Shot Manager version: ", bpy.context.window_manager.UAS_shot_manager_version)
                # if props.dataVersion <= 0 or props.dataVersion < bpy.context.window_manager.UAS_shot_manager_version:
                # if props.dataVersion <= 0 or props.dataVersion < props.version()[1]:

                if props.dataVersion <= 0:
                    props.dataVersion = props.version()[1]
                    _logger.info(
                        f"   *** Scene {scn.name}: The version of the Shot Manager data was not set - It has been fixed and is now {utils.convertVersionIntToStr(props.dataVersion)}"
                    )
                elif props.dataVersion < latestVersionToPatch:  # <= ???
                    _logger.info(
                        f"   *** Scene {scn.name}: The version of the Shot Manager data is lower than the latest patch version - Need patching ***"
                        f"\n     Data Version: {utils.convertVersionIntToStr(props.dataVersion)}, latest version to patch: {utils.convertVersionIntToStr(latestVersionToPatch)}"
                    )
                    numScenesToUpgrade += 1
                    if -1 == lowerSceneVersion or props.dataVersion < lowerSceneVersion:
                        lowerSceneVersion = props.dataVersion
                else:
                    if props.dataVersion < props.version()[1]:
                        props.dataVersion = props.version()[1]
                    # set right data version
                    # props.dataVersion = bpy.context.window_manager.UAS_shot_manager_version
                    # print("       Data upgraded to version V. ", props.dataVersion)

        if numScenesToUpgrade:
            print("\nUpgrading Shot Manager data with latest patches...")
            # apply patch and apply new data version
            # wkip patch strategy to re-think. Collect the data versions and apply the respective patches?

            patchVersion = 1002026
            if lowerSceneVersion < patchVersion:
                from shotmanager.data_patches.data_patch_to_v1_2_25 import data_patch_to_v1_2_25

                print(f"       Applying data patch to file: upgrade to {patchVersion}")
                data_patch_to_v1_2_25()
                lowerSceneVersion = patchVersion

            patchVersion = 1003016
            if lowerSceneVersion < patchVersion:
                from shotmanager.data_patches.data_patch_to_v1_3_16 import data_patch_to_v1_3_16

                print(f"       Applying data patch to file: upgrade to {patchVersion}")
                data_patch_to_v1_3_16()
                lowerSceneVersion = patchVersion

            patchVersion = 1003061
            if lowerSceneVersion < patchVersion:
                from shotmanager.data_patches.data_patch_to_v1_3_61 import data_patch_to_v1_3_61

                print(f"       Applying data patch to file: upgrade to {patchVersion}")
                data_patch_to_v1_3_61()
                lowerSceneVersion = patchVersion

            # current version, no patch required but data version is updated
            if lowerSceneVersion < props.version()[1]:
                props.dataVersion = props.version()[1]


# wkip doesn t work!!! Property values changed right before the save are not saved in the file!
# @persistent
# def checkDataVersion_save_pre_handler(self, context):
#     print("\nFile saved - Shot Manager is writing its data version in the scene")
#     for scn in bpy.data.scenes:
#         if "UAS_shot_manager_props" in scn:
#             print("\n   Shot Manager instance found in scene, writing data version: " + scn.name)
#             props.dataVersion = bpy.context.window_manager.UAS_shot_manager_version
#             print("   props.dataVersion: ", props.dataVersion)
