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
Shot Manager debug operators
"""

import bpy
from bpy.types import Operator


class UAS_compositeVideoInVSE(Operator):
    bl_idname = "vse.compositevideoinvse"
    bl_label = "CreateSceneAndAddClips"
    bl_description = ""

    def execute(self, context):
        """UAS_VSETruc"""
        print("Op compositeVideoInVSE")
        #   vse_render = context.window_manager.UAS_vse_render
        #   scene = context.scene

        context.window_manager.UAS_vse_render.compositeVideoInVSE(
            bpy.context.scene.render.fps, 1, 20, "c:\\tmp\\MyVSEOutput.mp4"
        )

        return {"FINISHED"}


class UAS_PrintDebugTextColor(Operator):
    bl_idname = "uas.debug_print_text_color"
    bl_label = "Print Text Color"
    bl_description = "Print text in various colors in the output terminal"

    # https://stackoverflow.com/questions/39473297/how-do-i-print-colored-output-with-python-3
    def execute(self, context):
        # 1; :bold
        colors = {
            "BLUE": "\33[34m",
            "BLUE_LIGHT": "\33[1;34m",
            "GREEN": "\33[32m",
            "GREEN_LIGHT": "\33[1;32m",
            "GRAY": "\33[1;30m",
            "YELLOW": "\33[33m",
            "YELLOW_LIGHT": "\33[1;33m",
            "ORANGE": "\33[1;31m",
            "RED": "\33[31m",
            "REDBG": "\33[41m",
            "PURPLE": "\33[35m",
            "PURPULE_LIGHT": "\33[1;35m",
            "TURQUOISE": "\33[36m",
            "TURQUOISE_LIGHT": "\33[1;36m",
            "WHITE": "\33[37m",
            "TEST": "\33[31m",
            "TEST2": "\33[32m",
            "TEST3": "\33[208m",
        }

        _ENDCOLOR = "\033[0m"

        def colored(r, g, b, text):
            return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(r, g, b, text)

        text = "Hello, World"
        colored_text = colored(255, 165, 0, text)
        print(colored_text)

        text = "Hello, World utils"
        from ..utils.utils_python import asciiColor

        colored_text = asciiColor(205, 165, 80)
        print(f"{colored_text}{text}{_ENDCOLOR}")

        for key, val in colors.items():
            print(f"{val}{key}: {val}{_ENDCOLOR}")

        for i in range(1, 60):
            val = "\33[" + str(i) + "m"
            print(f"{val}{key}: {i}{_ENDCOLOR}")

        return {"FINISHED"}


_classes = (UAS_compositeVideoInVSE, UAS_PrintDebugTextColor)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    from shotmanager.config import config

    config.devDebug = False
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
