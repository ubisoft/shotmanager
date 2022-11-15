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
Data check functions
"""

from shotmanager.config import config


def check_shotmanager_file_data(verbose=True):
    """Return a string with all the scene information"""
    import bpy

    def _isAddonLoaded(addon_name):
        try:
            bpy.context.preferences.addons[addon_name]
            isLoaded = True
        except Exception:
            isLoaded = False
        return isLoaded

    def _sceneHasShotManagerData(scene):
        """Return True if the scene contains Shot Manager data"""
        try:
            propGrp = scene["UAS_shot_manager_props"]
            propGrp = True
        except Exception:
            propGrp = False
        return propGrp

    def _getPropValue(prop_ower, prop_name):
        """Return a string with the value of prop_name, the string 'Not found' otherwise"""
        if prop_name in prop_ower:
            # this is not forcing the value to None
            prop_value_str = getattr(prop_ower, prop_name, None)
        return str(prop_ower)

    spacer = "\n"
    checkStr = ""
    checkStr += "\n---------------------------------------------------------------\n"
    checkStr += f"{spacer}Num scenes in file: {len(bpy.data.scenes)}"

    sm_addon_is_loaded = _isAddonLoaded("shotmanager")
    checkStr += f"{spacer}Ubisoft Shot Manager add-on is loaded: {sm_addon_is_loaded}"

    for scene in bpy.data.scenes:
        spacer = "\n  "
        checkStr += f"\n{spacer}- Scene: {scene.name}"
        spacer += "  "

        props = None
        sm_data_in_scene = _sceneHasShotManagerData(scene)
        checkStr += f"{spacer}Contains Ubisoft Shot Manager data: {sm_data_in_scene}"

        if getattr(scene, "UAS_shot_manager_props", None) is not None:
            props = config.getAddonProps(scene)

        checkStr += f"{spacer}props: {props}"
        spacer += "  "

        if not sm_data_in_scene:
            pass

        elif sm_addon_is_loaded:
            # here props should not be None
            if True or props is not None:
                checkStr += f"{spacer}SM Data version: {props.dataVersion}, SM version: {bpy.context.window_manager.UAS_shot_manager_version}"

                # properties introduced in SM V. 2.0.5
                # checkStr += f"\n{spacer}New properties introduced in SM V. 2.0.5"
                # spacer += "  "
                # checkStr += f"{spacer}props.{'project_naming_project_format'}: {getattr(props, 'project_naming_project_format', 'Not Set')}"
                # checkStr += f"{spacer}props.{'project_naming_sequence_format'}: {getattr(props, 'project_naming_sequence_format', 'Not Set')}"
                # checkStr += f"{spacer}props.{'project_naming_shot_format'}: {getattr(props, 'project_naming_shot_format', 'Not Set')}"
                # checkStr += f"{spacer}props.{'project_naming_separator_char'}: {getattr(props, 'project_naming_separator_char', 'Not Set')}"
                # checkStr += f"{spacer}props.{'project_naming_project_index'}: {getattr(props, 'project_naming_project_index', 'Not Set')}"
                # checkStr += f"{spacer}props.{'project_naming_sequence_index'}: {getattr(props, 'project_naming_sequence_index', 'Not Set')}"

                # check issue found on some old scenes
                if (
                    "Render Settings" == props.renderSettingsStill.name
                    or "Render Settings" == props.renderSettingsAnim.name
                    or "Render Settings" == props.renderSettingsAll.name
                    or "Render Settings" == props.renderSettingsOtio.name
                    or "Render Settings" == props.renderSettingsPlayblast.name
                ):
                    # props.reset_render_properties()
                    checkStr += f"{spacer}Some render settings presets are not correctly initialized"

        else:
            props_dict = scene["UAS_shot_manager_props"].to_dict()

            checkStr += f"{spacer}*** SM group properties converted to dictionary ***"
            # checkStr += f"{spacer}SM name: {}")
            checkStr += f"{spacer}SM Data Version in scene: {'Not defined' if 'dataVersion' not in props_dict else props_dict['dataVersion']}"

    checkStr += "\n"

    if verbose:
        print(checkStr)

    return checkStr
