import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty, EnumProperty

from ..config import config


class UAS_ShotManager_AddonPrefs(AddonPreferences):
    """
        Use this to get these prefs:
        prefs = context.preferences.addons["shotmanager"].preferences
    """

    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package
    bl_idname = "shotmanager"

    ##################
    # general ###
    ##################

    new_shot_duration: IntProperty(
        min=0, default=50,
    )

    take_properties_extended: BoolProperty(
        name="Extend Take Properties", default=False,
    )
    take_notes_extended: BoolProperty(
        name="Extend Take Notes", default=False,
    )

    shot_properties_extended: BoolProperty(
        name="Extend Shot Properties", default=True,
    )
    shot_notes_extended: BoolProperty(
        name="Extend Shot Notes", default=False,
    )
    shot_cameraBG_extended: BoolProperty(
        name="Extend Shot Camera BG", default=False,
    )
    shot_greasepencil_extended: BoolProperty(
        name="Extend Shot Grease Pencil", default=False,
    )

    current_shot_changes_current_time: BoolProperty(
        name="Set Current Frame To Shot Start When Current Shot Is Changed", description="", default=True,
    )
    current_shot_changes_time_range: BoolProperty(
        name="Set Time Range To Shot Range When Current Shot Is Changed", description="", default=False,
    )

    playblastFileName: StringProperty(name="Temporary Playblast File", default="toto.mp4")

    # def _get_useLockCameraView(self):
    #     # Can also use area.spaces.active to get the space assoc. with the area
    #     for area in bpy.context.screen.areas:
    #         if area.type == "VIEW_3D":
    #             for space in area.spaces:
    #                 if space.type == "VIEW_3D":
    #                     realVal = space.lock_camera

    #     # not used, normal it's the fake property
    #     self.get("useLockCameraView", realVal)

    #     return realVal

    # def _set_useLockCameraView(self, value):
    #     self["useLockCameraView"] = value
    #     for area in bpy.context.screen.areas:
    #         if area.type == "VIEW_3D":
    #             for space in area.spaces:
    #                 if space.type == "VIEW_3D":
    #                     space.lock_camera = value

    # # fake property: value never used in itself, its purpose is to update ofher properties
    # useLockCameraView: BoolProperty(
    #     name="Lock Cameras to View",
    #     description="Enable view navigation within the camera view",
    #     get=_get_useLockCameraView,
    #     set=_set_useLockCameraView,
    #     # update=_update_useLockCameraView,
    #     options=set(),
    # )

    ##################
    # rendering ui   ###
    ##################
    renderMode: EnumProperty(
        name="Display Shot Properties Mode",
        description="Update the content of the Shot Properties panel either on the current shot\nor on the shot seleted in the shots list",
        items=(
            ("STILL", "Still", ""),
            ("ANIMATION", "Animation", ""),
            ("ALL", "All Edits", ""),
            ("OTIO", "OTIO", ""),
            ("PLAYBLAST", "PLAYBLAST", ""),
        ),
        default="STILL",
    )

    ##################
    # tools ui     ###
    ##################
    toggleShotsEnabledState: BoolProperty(name=" ", default=False)

    ##################
    # shots features #
    ##################
    toggleCamsBG: BoolProperty(name=" ", default=False)
    toggleCamsSoundBG: BoolProperty(name=" ", default=False)
    toggleGreasePencil: BoolProperty(name=" ", default=False)

    ##################
    # ui helpers   ###
    ##################

    # used for example as a placehoder in VSM to have a text field when no strip is selected
    emptyField: StringProperty(name=" ")
    emptyBool: BoolProperty(name=" ", default=False)

    ##################
    # add new shot ###
    ##################

    def _get_addShot_start(self):
        val = self.get("addShot_start", 25)
        return val

    # *** behavior here must match the one of start and end of shot properties ***
    def _set_addShot_start(self, value):
        self["addShot_start"] = value
        # increase end value if start is superior to end
        # if self.addShot_start > self.addShot_end:
        #     self["addShot_end"] = self.addShot_start

        # prevent start to go above end (more user error proof)
        if self.addShot_start > self.addShot_end:
            self["addShot_start"] = self.addShot_end

    addShot_start: IntProperty(
        name="Add Shot Start UI Only", soft_min=0, get=_get_addShot_start, set=_set_addShot_start, default=25,
    )

    def _get_addShot_end(self):
        val = self.get("addShot_end", 30)
        return val

    # *** behavior here must match the one of start and end of shot properties ***
    def _set_addShot_end(self, value):
        self["addShot_end"] = value
        # reduce start value if end is lowr than start
        # if self.addShot_start > self.addShot_end:
        #    self["addShot_start"] = self.addShot_end

        # prevent end to go below start (more user error proof)
        if self.addShot_start > self.addShot_end:
            self["addShot_end"] = self.addShot_start

    addShot_end: IntProperty(
        name="Add Shot End UI Only", soft_min=0, get=_get_addShot_end, set=_set_addShot_end, default=50,
    )

    ##################
    # global temps values   ###
    ##################

    # Playblast
    ####################

    ##################################################################################
    # Draw
    ##################################################################################
    def draw(self, context):
        layout = self.layout
        prefs = context.preferences.addons["shotmanager"].preferences

        box = layout.box()
        box.use_property_decorate = False
        col = box.column()
        col.use_property_split = True
        col.prop(prefs, "new_shot_duration", text="Default Shot Length")
        #    col.prop(prefs, "useLockCameraView", text="Use Lock Camera View")

        layout.label(
            text="Temporary preference values (for dialogs for instance) are only visible when global variable uasDebug is True."
        )

        if config.uasDebug:
            layout.label(text="Add New Shot Dialog:")
            box = layout.box()
            col = box.column(align=False)
            col.prop(self, "addShot_start")
            col.prop(self, "addShot_end")

    ##################
    # markers ###
    ##################

    mnavbar_use_filter: BoolProperty(
        name="Filter Markers", default=False,
    )

    mnavbar_filter_text: StringProperty(
        name="Filter Text", default="",
    )


_classes = (UAS_ShotManager_AddonPrefs,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)

