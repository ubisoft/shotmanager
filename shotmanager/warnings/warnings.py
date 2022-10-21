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
Functions specific to Shot Manager props
"""

from stat import S_IMODE, S_IWRITE
from pathlib import Path

import bpy
from shotmanager.config import config
from shotmanager.utils import utils
from shotmanager.utils.utils_markers import sceneContainsCameraBinding


def getWarnings(props, scene):
    """Check if some warnings are to be mentioned to the user/
    A warning message can be on several lines when the separator \n is used.

    Return:
        An array of tupples made of:
            - the warning message
            - the warning index
            - the panel type, which can be 'ALL', 'MAIN' or 'RENDER'
        eg: [("Current file in Read-Only", 1, 'ALL'), ("Current scene fps and project fps are different !!", 2, 'MAIN')]
    """
    prefs = config.getAddonPrefs()
    warningList = []

    # check if the current file is saved and not read only
    ###########
    currentFilePath = bpy.path.abspath(bpy.data.filepath)
    if "" == currentFilePath:
        # warningList.append("Current file has to be saved")
        # wkip to remove ones warning mecanics are integrated in the settings
        pass
    else:
        stat = Path(currentFilePath).stat()
        # print(f"Blender file Stats: {stat.st_mode}")
        if S_IMODE(stat.st_mode) & S_IWRITE == 0:
            warningList.append(("Current file in Read-Only", 10, "ALL"))

    # check is the data version is compatible with the current version
    # wkip obsolete code due to post register data version check
    if config.devDebug:
        if props.dataVersion <= 0 or props.dataVersion < bpy.context.window_manager.UAS_shot_manager_version:
            # print("Warning: elf.dataVersion:", props.dataVersion)
            # print(
            #     "Warning: bpy.context.window_manager.UAS_shot_manager_version:",
            #     bpy.context.window_manager.UAS_shot_manager_version,
            # )

            warningList.append(("Debug: Data version is lower than SM version. Save and reload the file.", 50, "ALL"))

    # check if some camera markers bound to cameras are used in the scene
    ###########
    if sceneContainsCameraBinding(scene):
        warningList.append(
            (
                "Scene contains markers binded to cameras"
                "\n*** Shot Manager is NOT compatible with camera binding ***",
                60,
                "ALL",
            )
        )

    ##############################
    # rendering - 1xx
    ##############################

    # check rendering preset issue found on some old scenes
    ###########
    if (
        "Render Settings" == props.renderSettingsStill.name
        or "Render Settings" == props.renderSettingsAnim.name
        or "Render Settings" == props.renderSettingsAll.name
        or "Render Settings" == props.renderSettingsOtio.name
        or "Render Settings" == props.renderSettingsPlayblast.name
    ):
        # props.reset_render_properties()
        warningList.append(
            (
                "Wrong initialization of Render Settings Presets"
                "\n*** Reset the Render Presets (see in Render panel Tools menu) ***",
                110,
                "ALL",
            )
        )

    # check rendering path validity
    ###########
    # NOTE: see isRenderRootPathValid()

    if "" == props.renderRootPath:
        warningList.append(("Rendering path is not defined", 120, "RENDER"))

    elif not props.isRenderRootPathValid():
        warningList.append(("Rendering path is invalid", 121, "RENDER"))

    # check if the resolution render percentage is at 100%
    ###########
    if not props.use_project_settings and 100 != scene.render.resolution_percentage:
        warningList.append(("Render Resolution Percentage is not at 100%", 130, "ALL"))

    # check if the render resolution is the same as the one set in project settings
    ###########
    if props.use_project_settings:
        if (
            props.project_resolution_x != scene.render.resolution_x
            or props.project_resolution_y != scene.render.resolution_y
        ):
            warningList.append(
                (
                    "Scene Render Resolution is different from Project Settings Resolution\nStoryboard and Grease Pencil shots will not be displayed correctly",
                    131,
                    "ALL",
                )
            )

    # check if the resolution render uses multiples of 2
    ###########
    if not props.use_project_settings:
        if 0 != scene.render.resolution_x % 2 or 0 != scene.render.resolution_y % 2:
            warningList.append(("Render Resolution must use multiples of 2", 132, "ALL"))

    # check if the render pixel aspects X or Y are used
    ###########
    if 1.0 != scene.render.pixel_aspect_x or 1.0 != scene.render.pixel_aspect_y:
        warningList.append(
            (
                "Render Pixel Aspects should be 1.0\nIf not then Storyboard and Grease Pencil shots will not be displayed correctly",
                134,
                "ALL",
            )
        )

    # check if the current fps is valid according to the project settings
    ###########
    if props.use_project_settings:
        if utils.getSceneEffectiveFps(scene) != props.project_fps:
            warningList.append(("Current scene fps and project fps are different !!", 136, "ALL"))

    # scene metadata activated and they will be written on rendered images
    ###########
    if scene.render.use_stamp:
        warningList.append(
            ("Scene Metadata Burning Into Images is activated\nRendering will be affected", 140, "RENDER")
        )

    # check if a negative render frame may be rendered
    ###########
    shotList = props.get_shots()
    hasNegativeFrame = False
    shotInd = 0
    handlesDuration = props.getHandlesDuration()
    while shotInd < len(shotList) and not hasNegativeFrame:
        hasNegativeFrame = shotList[shotInd].start - handlesDuration < 0
        shotInd += 1
    if hasNegativeFrame:
        if props.areShotHandlesUsed():
            warningList.append(
                (
                    "Index of the output frame of a shot minus handle is negative !!"
                    "\nNegative time indicies are not supported by Shot Manager renderer.",
                    150,
                    "ALL",
                )
            )
        else:
            warningList.append(
                (
                    "At least one shot starts at a negative frame !!"
                    "\nNegative time indicies are not supported by Shot Manager renderer.",
                    151,
                    "ALL",
                )
            )

    ##############################
    # dependencies - 7x
    ##############################

    # check if the installed version of Stamp Info is supported
    ###########

    # stampInfoInstalledVersion = utils.addonVersion("Stamp Info")
    # if stampInfoInstalledVersion:
    #     stampInfoMinVersion = prefs.dependency_min_supported_version("Stamp Info")
    #     if stampInfoInstalledVersion[1] < stampInfoMinVersion[1]:
    #         warningList.append(
    #             (
    #                 f"Installed version of Stamp Info add-on is too old: {stampInfoInstalledVersion[0]}"
    #                 f"\nSupported version: {stampInfoMinVersion[0]}",
    #                 71,
    #                 "ALL",
    #             )
    #         )

    # if props.use_project_settings and "Scene" in scene.name:
    #     warningList.append("Scene Name is Invalid !!!")
    # c.label(text=" *************************************** ")
    # c.label(text=" *    SCENE NAME IS INVALID !!!    * ")
    # c.label(text=" *************************************** ")

    return warningList
