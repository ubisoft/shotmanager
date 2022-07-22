# GPLv3 License
#
# Copyright (C) 2022 Ubisoft
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
Draw the names of the libraries and add-ons required by this add-on
"""

import bpy


def drawDependencies(context, layout: bpy.types.UILayout, **kwargs):

    box = layout.box()
    row = box.row()
    row.label(text="Dependencies:")
    row = box.row()
    row.separator()
    splitFactor = 0.45

    # Pillow
    ####################
    split = row.split(factor=splitFactor)
    split.label(text="- PIL (Python Imaging Library):")

    try:
        import PIL as pillow

        pillowVersion = pillow.__version__
        split.label(text=f"V. {pillowVersion}")
    except Exception:
        subRow = split.row()
        subRow.alert = True
        subRow.label(text="Module not found  - Add-on cannot run normally")

    box.separator(factor=0.2)
