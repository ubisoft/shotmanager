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
Grease pencil functions specific to Shot Manager
"""

import bpy

from shotmanager.utils import utils
from shotmanager.utils import utils_greasepencil


def setInkLayerReadyToDraw(gpencil: bpy.types.GreasePencil):
    inkLayer = None
    if gpencil.data.layers["Lines"] is not None:
        inkLayer = gpencil.data.layers["Lines"]

    gpencil.data.layers.active = inkLayer

    # create frame
    bpy.ops.gpencil.blank_frame_add(all_layers=False)
