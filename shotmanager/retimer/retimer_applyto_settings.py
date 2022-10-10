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
Retimer ApplyTo settings
"""

from bpy.types import PropertyGroup
from bpy.props import BoolProperty, StringProperty

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


class UAS_Retimer_ApplyToSettings(PropertyGroup):
    """Contextual settings to define to which entitites the retiming will be applied to"""

    id: StringProperty(name="ID", default="DEFAULT")
    name: StringProperty(name="Name", default="Retimer ApplyTo Default Settings")

    onlyOnSelection: BoolProperty(
        name="Apply Only on Selection",
        description="Apply time change only to objects selected in the scene",
        default=False,
        options=set(),
    )
    includeLockAnim: BoolProperty(
        name="Apply Also on Locked Anim",
        description="Apply time change even if animation curves or action are locked",
        default=True,
        options=set(),
    )
    snapKeysToFrames: BoolProperty(
        name="Snap Keys to Frames",
        description="Snap the retime keys to the nearest frame value",
        default=True,
        options=set(),
    )

    applyToObjects: BoolProperty(
        name="Objects",
        description="Apply time change to objects in the scene.\nGrease Pencil objects are ignored",
        default=True,
        options=set(),
    )
    applyToShapeKeys: BoolProperty(
        name="Shape Keys",
        description="Apply time change to objects with shape keys",
        default=True,
        options=set(),
    )
    applytToGreasePencil: BoolProperty(
        name="Grease Pencil",
        description="Apply time change to Grease Pencil objects",
        default=True,
        options=set(),
    )

    applyToMarkers: BoolProperty(
        name="Markers",
        description="Apply time change to markers",
        default=True,
        options=set(),
    )

    applyToCameraShotRanges: BoolProperty(
        name="Camera Shot Ranges",
        description="Apply time change to the range (but not the shot content) of the shots of type Camera (*** NOT to Storyboard shots ! ***",
        default=True,
        options=set(),
    )
    applyToStoryboardShotRanges: BoolProperty(
        name="Storyboard Shot Ranges",
        description="Apply time change to the range (but not the shot content) of the shots of type Storyboard (*** NOT to Camera shots ! ***",
        default=False,
        options=set(),
    )

    applyToVSE: BoolProperty(
        name="VSE",
        description="Apply time change to the content of the VSE",
        default=True,
        options=set(),
    )

    # moved to add-on preferences
    applyToTimeCursor: BoolProperty(
        name="Apply to Time Cursor",
        description="Apply retime operation to the time cursor",
        default=True,
        options=set(),
    )
    applyToSceneRange: BoolProperty(
        name="Apply to Scene Range",
        description="Apply retime operation to the animation start and end of the scene",
        default=True,
        options=set(),
    )

    def initialize(self, applyToMode):
        """
        Args:
            applyToMode: the mode of the applyTo settings. Can be SCENE, SELECTED_OBJECTS, LEGACY
                         Internaly if can also be: STB_SHOT_CLIP
        """
        _logger.debug_ext(f"initialize Retimer ApplyTo Settings {applyToMode}", col="GREEN", tag="RETIMER")

        # common values
        # -

        # Scene
        if "SCENE" == applyToMode:
            self.id = applyToMode
            self.name = "Apply to Scene Preset"

            self.onlyOnSelection = False
            self.includeLockAnim = True
            self.snapKeysToFrames = True

            self.applyToObjects = True
            self.applyToShapeKeys = True
            self.applytToGreasePencil = True

            self.applyToMarkers = True

            self.applyToCameraShotRanges = True
            self.applyToStoryboardShotRanges = False

            self.applyToVSE = True

            self.applyToTimeCursor = True
            self.applyToSceneRange = True

        # Selected objects
        if "SELECTED_OBJECTS" == applyToMode:
            self.id = applyToMode
            self.name = "Apply to Selected Objects Preset"

            self.onlyOnSelection = False
            self.includeLockAnim = True
            self.snapKeysToFrames = True

            # NOTE: a camera from a shot is an object belonging to the scene
            self.applyToObjects = True
            self.applyToShapeKeys = True
            self.applytToGreasePencil = True

            self.applyToMarkers = False

            self.applyToCameraShotRanges = False
            self.applyToStoryboardShotRanges = False

            self.applyToVSE = False

            self.applyToTimeCursor = False
            self.applyToSceneRange = False

        # Storyboard shot clip - for shot stack clip manipulations
        ########################
        if "STB_SHOT_CLIP" == applyToMode:
            self.id = applyToMode
            self.name = "Apply to Storyboard Shot Clips"

            self.onlyOnSelection = False
            self.includeLockAnim = True
            self.snapKeysToFrames = True

            self.applyToObjects = True
            self.applyToShapeKeys = True
            self.applytToGreasePencil = True

            self.applyToMarkers = False

            self.applyToCameraShotRanges = False
            self.applyToStoryboardShotRanges = False

            self.applyToVSE = False

            self.applyToTimeCursor = False
            self.applyToSceneRange = False

        # Camera (or previz) shot clip - for shot stack clip manipulations
        ########################
        if "PVZ_SHOT_CLIP" == applyToMode:
            self.id = applyToMode
            self.name = "Apply to Camera Shot Clips"

            self.onlyOnSelection = False
            self.includeLockAnim = True
            self.snapKeysToFrames = True

            self.applyToObjects = True
            self.applyToShapeKeys = True
            self.applytToGreasePencil = True

            self.applyToMarkers = False

            self.applyToCameraShotRanges = False
            self.applyToStoryboardShotRanges = False

            self.applyToVSE = False

            self.applyToTimeCursor = False
            self.applyToSceneRange = False

        # Legacy
        if "LEGACY" == applyToMode:
            self.id = applyToMode
            self.name = "Apply to Legacy Preset"

    def getQuickHelp(self, topic):
        """Args:
        topic:  Can be APPLYTO_STORYBOARDSHOTS"""

        docPath = "https://ubisoft-shotmanager.readthedocs.io/en/latest/feature-toggles/retimer.html"

        if "APPLYTO_STORYBOARDSHOTS" == topic:
            title = "Storyboard Shots"
            text = "Except if you have some very specific needs, it is usually not necessary to"
            text += "\napply the Scene Retiming to the Storyboard shots since they do not"
            text += "\nreally depends on the scene content."
            # TODO wkip add doc anchor to each path
            docPath += ""
        # elif "INSERT_BEFORE" == topic:
        #     text += ""
        # elif "INSERT_AFTER" == topic:
        #     text += ""
        # elif "DELETE_RANGE" == topic:
        #     text += ""
        # elif "RESCALE" == topic:
        #     text += ""
        # elif "CLEAR_ANIM" == topic:
        #     text += ""
        else:
            title = "description"
            text = "text"

        tooltip = "Quick tips about " + title
        return (tooltip, title, text, docPath)
