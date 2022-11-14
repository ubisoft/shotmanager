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
Grease pencil viewport overlay draw functions
"""

from shotmanager.utils.utils_operators_overlays import getOverlaysPropertyState

from shotmanager.config import config


def draw_overlays_global_settings(context, layout, mode="SHOT"):
    """Used for storyboard frames and grease pencil shots in the Shot Manager storyboard panel,
    and by the 2.5D grease pencil panel
    Args:
        mode:   can be "STORYBOARD", "GP", "SHOT"
    """

    props = config.getAddonProps(context.scene)
    prefs = config.getAddonPrefs()
    splitFactor = 0.16

    applyToAllViewports = "ALL" == props.shotsGlobalSettings.stb_overlaysViewportMode

    overlaysChecked = getOverlaysPropertyState(context, "show_overlays")
    onionSkinIsActive = getOverlaysPropertyState(context, "use_gpencil_onion_skin")
    useGrid = getOverlaysPropertyState(context, "use_gpencil_grid")
    gridIsinFront = getOverlaysPropertyState(context, "use_gpencil_canvas_xray")
    useFadeLayers = getOverlaysPropertyState(context, "use_gpencil_fade_layers")

    # onionSkinIsActive = False
    # useGrid = False
    # gridIsinFront = False
    # useFadeLayers = False
    # if applyToAllViewports:
    #     onionSkinIsActive = getOverlaysPropertyState(context, "use_gpencil_onion_skin")
    #     useGrid = getOverlaysPropertyState(context, "use_gpencil_grid")
    #     gridIsinFront = getOverlaysPropertyState(context, "use_gpencil_canvas_xray")
    #     useFadeLayers = getOverlaysPropertyState(context, "use_gpencil_fade_layers")
    # else:
    #     spaceDataViewport = props.getValidTargetViewportSpaceData(context)
    #     if spaceDataViewport is not None:
    #         onionSkinIsActive = spaceDataViewport.overlay.use_gpencil_onion_skin
    #         useGrid = spaceDataViewport.overlay.use_gpencil_grid
    #         gridIsinFront = spaceDataViewport.overlay.use_gpencil_canvas_xray
    #         useFadeLayers = spaceDataViewport.overlay.use_gpencil_fade_layers

    titleRow = layout.row(align=False)
    titleRow.label(text="Overlays: ")
    titleRowRight = titleRow.row(align=False)
    titleRowRight.alignment = "RIGHT"
    titleRowRight.label(text="Apply to:")
    titleRowRight.prop(props.shotsGlobalSettings, "stb_overlaysViewportMode", text="")

    layout.separator(factor=0.5)

    box = layout.box()
    row = box.row(align=False)

    leftRow = row.row()
    # leftRow.prop(spaceDataViewport.overlay, "show_overlays", text="Ok", icon="OVERLAY")
    # leftRow.operator(
    #     "uas_shot_manager.overlays_toggleoverlays", text="", icon="OVERLAY", depress=overlaysChecked
    # ).allViewports = applyToAllViewports
    leftRow.prop(prefs, "overlays_toggleoverlays_ui", text="", icon="OVERLAY")

    rightRow = row.row()
    rightRow.enabled = overlaysChecked
    overlayCol = rightRow.column()

    overlaySplit = overlayCol.split(factor=splitFactor)
    overlayLeftRow = overlaySplit.row()
    overlayLeftRow.label(text=" ")
    # overlayLeftRow.label(text="Overlays: ")

    if mode in ["GP", "STORYBOARD"]:
        # row = overlayCol.row(align=False)
        # overlaySplit = row.split(factor=splitFactor)
        # overlaySplit.separator()
        overlayRighRow = overlaySplit.row()
        # overlayRighRow.operator(
        #     "uas_shot_manager.overlays_toggleonionskin", depress=onionSkinIsActive
        # ).allViewports = applyToAllViewports
        overlayRighRow.prop(prefs, "overlays_toggleonionskin_ui", text="")
        overlayRighRow.label(text="Onion Skin")

        row = overlayCol.row(align=False)
        overlaySplit = row.split(factor=splitFactor)
        overlaySplit.separator()
        overlayRighRow = overlaySplit.row()
        # overlayRighRow.operator(
        #     "uas_shot_manager.overlays_togglegrid", depress=useGrid
        # ).allViewports = applyToAllViewports
        overlayRighRow.prop(prefs, "overlays_togglegrid_ui", text="")
        subOverlayRighRow = overlayRighRow.row(align=True)
        subOverlayRighRow.enabled = useGrid
        subOverlayRighRow.prop(prefs, "stb_overlay_grid_opacity", text="Canvas", slider=True)
        # subOverlayRighRow.operator(
        #     "uas_shot_manager.overlays_togglegridtofront", text="", icon="XRAY", depress=gridIsinFront
        # ).allViewports = applyToAllViewports
        subOverlayRighRow.prop(prefs, "overlays_togglegridtofront_ui", text="", icon="XRAY")

        row = overlayCol.row(align=False)
        overlaySplit = row.split(factor=splitFactor)
        overlaySplit.separator()
        overlayRighRow = overlaySplit.row()
        # overlayRighRow.prop(spaceDataViewport.overlay, "use_gpencil_fade_layers", text="")
        # overlayRighRow.operator(
        #     "uas_shot_manager.overlays_togglefadelayers", text="", depress=onionSkinIsActive
        # ).allViewports = applyToAllViewports
        overlayRighRow.prop(prefs, "overlays_togglefadelayers_ui", text="")
        subOverlayRighRow = overlayRighRow.row()
        subOverlayRighRow.enabled = useFadeLayers
        subOverlayRighRow.prop(prefs, "stb_overlay_layers_opacity", text="Fade Layers", slider=True)

    # if mode in ["STORYBOARD", "SHOT"]:
    #     overlayRighRow = overlaySplit.row()
    #     subOverlayRighRow = overlayRighRow.row()
    #     subOverlayRighRow.prop(props.shotsGlobalSettings, "stb_show_passepartout", text="", slider=True)
    #     subsubOverlayRighRow = subOverlayRighRow.row()
    #     subsubOverlayRighRow.enabled = props.shotsGlobalSettings.stb_show_passepartout
    #     subsubOverlayRighRow.prop(props.shotsGlobalSettings, "stb_passepartout_alpha", text="Passepartout", slider=True)
