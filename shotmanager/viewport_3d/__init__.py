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
To do: module description here.
"""

import bpy

from . import viewport_hud
from . import timeline_draw

# from .ui import vsm_ui


# classes = (
#     ,
# )


def register():
    print("       - Registering Viewport 3D Package")
    # for cls in classes:
    #     bpy.utils.register_class(cls)

    viewport_hud.register()
    timeline_draw.register ( )


def unregister():
    viewport_hud.unregister()
    timeline_draw.unregister()

    # for cls in reversed(classes):
    #     bpy.utils.unregister_class(cls)
