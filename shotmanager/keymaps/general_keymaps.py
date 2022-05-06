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
Key mappings for all the operators of the add-on

Eg here: https://blender.stackexchange.com/questions/196483/create-keyboard-shortcut-for-an-operator-using-python
"""

import bpy

from shotmanager import config

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


def registerKeymaps():
    # Add the hotkey
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        ###############################
        # General
        ###############################

        # shots_play_mode operator
        ###############################

        # VIEW_3D works also for timeline
        km = wm.keyconfigs.addon.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new("uas_shot_manager.shots_play_mode", type="SPACE", value="PRESS", alt=True)
        config.gAddonKeymaps.append((km, kmi))

        km = wm.keyconfigs.addon.keymaps.new(name="Dopesheet", space_type="DOPESHEET_EDITOR")
        kmi = km.keymap_items.new("uas_shot_manager.shots_play_mode", type="SPACE", value="PRESS", alt=True)
        config.gAddonKeymaps.append((km, kmi))

        km = wm.keyconfigs.addon.keymaps.new(name="Graph Editor", space_type="GRAPH_EDITOR")
        kmi = km.keymap_items.new("uas_shot_manager.shots_play_mode", type="SPACE", value="PRESS", alt=True)
        config.gAddonKeymaps.append((km, kmi))

        # NOTE: Does not exist anymore on 2.83+, use VIEW_3D instead
        # km = wm.keyconfigs.addon.keymaps.new(name="Timeline", space_type="TIMELINE")
        # kmi = km.keymap_items.new("uas_shot_manager.shots_play_mode", type="SPACE", value="PRESS", alt=True)
        # config.gAddonKeymaps.append((km, kmi))

        # display_overlay_tools operator
        ###############################

        km = wm.keyconfigs.addon.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new("uas_shot_manager.display_overlay_tools", type="NONE", value="PRESS")
        config.gAddonKeymaps.append((km, kmi))

        # km = wm.keyconfigs.addon.keymaps.new(name="Dopesheet", space_type="DOPESHEET_EDITOR")
        # kmi = km.keymap_items.new("uas_shot_manager.display_overlay_tools", type="NONE", value="PRESS")
        # config.gAddonKeymaps.append((km, kmi))

        # km = wm.keyconfigs.addon.keymaps.new(name="Graph Editor", space_type="GRAPH_EDITOR")
        # kmi = km.keymap_items.new("uas_shot_manager.display_overlay_tools", type="NONE", value="PRESS")
        # config.gAddonKeymaps.append((km, kmi))
