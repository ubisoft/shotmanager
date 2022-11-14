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
from shotmanager.utils import utils_shot_manager
from shotmanager.data_patches.check_scene_data import check_shotmanager_file_data

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


@persistent
def shotMngHandler_load_post_checkDataVersion(self, context):
    loadedFileName = bpy.path.basename(bpy.context.blend_data.filepath)
    print("\n\n-------------------------------------------------------")

    _logger.debug_ext("shotMngHandler_load_post_checkDataVersion", col="PINK", tag="INIT_AND_DATA")

    if "" == loadedFileName:
        print("\nNew file loaded")
    else:
        _logger.info_ext(f"Existing file loaded: {bpy.path.basename(bpy.context.blend_data.filepath)}", col="GREEN")
        _logger.info_ext(
            "  - Shot Manager is checking the version used to create the loaded scene data...", col="GREEN"
        )

        latestVersionToPatch = 2000204
        infoTxt = f"Ubisoft Shot Manager Version: {utils.convertVersionIntToStr(latestVersionToPatch)}"
        # infoTxt = f"Ubisoft Shot Manager Version: {props.version()[0]}"
        _logger.info_ext(f"{infoTxt}", col="GREEN")

        checkStr = check_shotmanager_file_data(verbose=False)
        _logger.debug_ext("Before changes:", col="PINK")
        _logger.debug_ext(checkStr, col="PINK")

        numScenesToUpgrade = 0
        lowerSceneVersion = -1

        for scene in bpy.data.scenes:
            sm_data_in_scene = utils_shot_manager.sceneHasShotManagerData(scene)
            if not sm_data_in_scene:
                continue

            props = config.getAddonProps(scene)
            infoTxt = ""
            if config.devDebug:
                _logger.debug_ext(f"Scene: {scene.name}, props.dataVersion: {props.dataVersion}", col="RED")
                _logger.debug_ext(f"props.version: {props.version()[1]}", col="RED")
                _logger.debug_ext(
                    f"\n---------------\n   latestVersionToPatch: {latestVersionToPatch}\n---------------\n", col="RED"
                )

            infoTxt += f"Scene: {scene.name}  -  Data Version is {utils.convertVersionIntToStr(props.dataVersion)}"

            #   print("     Data version: ", props.dataVersion)
            #   print("     Shot Manager version: ", bpy.context.window_manager.UAS_shot_manager_version)
            # if props.dataVersion <= 0 or props.dataVersion < bpy.context.window_manager.UAS_shot_manager_version:
            # if props.dataVersion <= 0 or props.dataVersion < props.version()[1]:

            if props.dataVersion <= 0:
                # props.dataVersion = props.version()[1]
                # _logger.info(
                #     f"   *** Scene {scene.name}: The version of the Shot Manager data was not set - It has been fixed and is now {utils.convertVersionIntToStr(props.dataVersion)}"
                # )
                _logger.info_ext(
                    f"   *** Scene {scene.name}: The version of the Ubisoft Shot Manager data is not set - Scene will be patched ***",
                    col="RED",
                )

            if props.dataVersion < latestVersionToPatch:  # <= ???
                _logger.info(
                    f"   *** Scene {scene.name}: The version of the Ubisoft Shot Manager data is lower than the latest patch version - Need patching ***"
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

            # fixing issues "on the fly"
            if props.parentScene is None:
                props.getParentScene()
                _logger.info_ext(
                    f"Fixed Shot Manager parent scene issue in the following scene: {scene.name}", col="GREEN"
                )

            _logger.info_ext(f"{infoTxt}", col="GREEN")

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

            patchVersion = 1007015
            if lowerSceneVersion < patchVersion:
                from shotmanager.data_patches.data_patch_to_v1_7_15 import data_patch_to_v1_7_15

                print(f"       Applying data patch to file: upgrade to {patchVersion}")
                data_patch_to_v1_7_15()
                lowerSceneVersion = patchVersion

            patchVersion = 2000012
            if lowerSceneVersion < patchVersion:
                from shotmanager.data_patches.data_patch_to_v2_0_12 import data_patch_to_v2_0_12

                print(f"       Applying data patch to file: upgrade to {patchVersion}")
                data_patch_to_v2_0_12()
                lowerSceneVersion = patchVersion

            patchVersion = 2000204
            if lowerSceneVersion < patchVersion:
                from shotmanager.data_patches.data_patch_to_v2_0_204 import data_patch_to_v2_0_204

                print(f"       Applying data patch to file: upgrade to {patchVersion}")
                data_patch_to_v2_0_204()
                lowerSceneVersion = patchVersion

            # current version, no patch required but data version is updated
            if lowerSceneVersion < props.version()[1]:
                props.dataVersion = props.version()[1]

            checkStr = check_shotmanager_file_data(verbose=False)
            _logger.debug_ext("\n\nAfter changes:", col="PINK")
            _logger.debug_ext(checkStr, col="PINK")


# wkip doesn t work!!! Property values changed right before the save are not saved in the file!
# @persistent
# def checkDataVersion_save_pre_handler(self, context):
#     print("\nFile saved - Shot Manager is writing its data version in the scene")
#     for scene in bpy.data.scenes:
#         if "UAS_shot_manager_props" in scene:
#             print("\n   Shot Manager instance found in scene, writing data version: " + scene.name)
#             props.dataVersion = bpy.context.window_manager.UAS_shot_manager_version
#             print("   props.dataVersion: ", props.dataVersion)
