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

#############################################
# RRS Package
#############################################

import bpy

from .ui_rrs import UAS_PT_ShotManager_RRS_Debug
from .operators_rrs import UAS_InitializeRRSProject, UAS_LaunchRRSRender, UAS_FixEntitiesParent

_classes = (
    UAS_InitializeRRSProject,
    UAS_LaunchRRSRender,
    UAS_PT_ShotManager_RRS_Debug,
    UAS_FixEntitiesParent,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
