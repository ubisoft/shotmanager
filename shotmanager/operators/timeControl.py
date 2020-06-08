import bpy
from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import IntProperty, EnumProperty, BoolProperty, FloatProperty, StringProperty

from ..tools import retimer


##########
# Retimer
##########


class UAS_Retimer_Properties(PropertyGroup):

    mode: EnumProperty(
        name="Time Mode",
        items=(
            (
                "INSERT",
                "Insert Time",
                "Insert the given time, in number of frames, after the specified frame.\nKeyframes after the range are just offset.",
            ),
            (
                "DELETE",
                "Delete Time",
                "Remove the frames after the start one up to the one specified for the end (included).\nKeyframes after the range are just offset.",
            ),
            (
                "RESCALE",
                "Scale Time !!! Not debugged yet !!!",
                "Change the scale of the specified time range.\nKeyframes after the end of the range are just offset.",
            ),
            (
                "CLEAR_ANIM",
                "Clear Animation",
                "Clear the animation on the specified time range.\nNo keyframes are offset.",
            ),
        ),
        options=set(),
    )

    def _get_start_frame(self):
        val = self.get("start_frame", True)
        return val

    def _set_start_frame(self, value):
        if value >= self.end_frame:
            self.end_frame = value + 1
        self["start_frame"] = value

    # def _update_start_frame(self, context):
    #     if self.start_frame >= self.end_frame:
    #         self.end_frame = self.start_frame + 1

    start_frame: IntProperty(
        name="Start Frame",
        description="Start frame for the time operation",
        get=_get_start_frame,
        set=_set_start_frame,
        # update=_update_start_frame,
        default=1,
        options=set(),
    )

    def _get_end_frame(self):
        val = self.get("end_frame", True)
        return val

    def _set_end_frame(self, value):
        if value <= self.start_frame:
            self.start_frame = value - 1
        self["end_frame"] = value

    # def _update_end_frame(self, context):
    #     if self.start_frame >= self.end_frame:
    #         self.start_frame = self.end_frame - 1

    end_frame: IntProperty(
        name="End Frame",
        description="End frame for the time operation",
        get=_get_end_frame,
        set=_set_end_frame,
        # update=_update_end_frame,
        default=10,
        options=set(),
    )

    move_current_frame: BoolProperty(
        "Move Current Frame", default=False, options=set(),
    )

    # Insert specific
    insert_duration: IntProperty(
        name="Insert Duration",
        description="Number of frames to insert after the specified one",
        default=10,
        soft_min=1,
        options=set(),
    )

    # Remove specific
    gap: BoolProperty(
        name="Remove Gap", default=True, options=set(),
    )

    # Rescale specific
    factor: FloatProperty(
        name="Factor", default=1, min=0, max=10, options=set(),
    )
    pivot: IntProperty(
        name="Pivot", options=set(),
    )

    onlyOnSelection: BoolProperty(
        name="Apply on Selection", default=False, options=set(),
    )

    applyToShots: BoolProperty(
        name="Shots", default=True, options=set(),
    )

    applyToObjects: BoolProperty(
        name="Objects", default=True, options=set(),
    )
    applyToShapeKeys: BoolProperty(
        name="Shape Keys", default=True, options=set(),
    )
    applytToGreasePencil: BoolProperty(
        name="Grease Pencil", default=True, options=set(),
    )


class UAS_PT_ShotManagerRetimer(Panel):
    bl_label = "Retimer"
    bl_idname = "UAS_PT_ShotManagerRetimerPanel"
    bl_description = "Manage the global timing of the action in the scene and the shots"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UAS Shot Man"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        retimerProps = context.scene.UAS_shot_manager_props.retimer

        layout = self.layout
        layout.prop(retimerProps, "mode")

        box = layout.box()

        row = box.row()
        row.separator(factor=0.1)
        # row = box.row()
        # row.separator(factor=1)
        # row.prop(retimerProps, "start_frame", text="Move Frame")
        # row.prop(retimerProps, "end_frame", text="To")

        # row.operator("uas_shot_manager.gettimerange", text="", icon="SEQ_STRIP_META")
        # row.separator(factor=1)

        if retimerProps.mode == "INSERT":
            row = box.row(align=True)
            row.separator(factor=1)

            row.prop(retimerProps, "start_frame", text="Insert After")
            row.operator(
                "uas_shot_manager.getcurrentframefor", text="", icon="TRIA_UP_BAR"
            ).propertyToUpdate = "start_frame"
            row.separator()

            row.prop(retimerProps, "insert_duration", text="Duration")
            row.separator(factor=1)

            # apply ###
            row = box.row()
            row.separator(factor=0.1)
            compo = layout.row()
            compo.separator(factor=2)
            compo.scale_y = 1.2
            compo.operator("uas_shot_manager.retimerapply", text="Insert")
            compo.separator(factor=2)

        elif retimerProps.mode == "DELETE":
            row = box.row(align=True)
            row.separator(factor=1)
            row.prop(retimerProps, "start_frame", text="Delete After")
            row.operator(
                "uas_shot_manager.getcurrentframefor", text="", icon="TRIA_UP_BAR"
            ).propertyToUpdate = "start_frame"
            row.separator()

            row.prop(retimerProps, "end_frame", text="Up To (incl.)")
            row.operator(
                "uas_shot_manager.getcurrentframefor", text="", icon="TRIA_UP_BAR"
            ).propertyToUpdate = "end_frame"
            row.separator()

            #            row.operator("uas_shot_manager.gettimerange", text="", icon="SEQ_STRIP_META")
            row.separator(factor=1)

            # apply ###
            row = box.row()
            row.separator(factor=0.1)
            compo = layout.row()
            compo.separator(factor=2)
            compo.scale_y = 1.2
            compo.operator("uas_shot_manager.retimerapply", text="Delete")
            compo.separator(factor=2)

        elif retimerProps.mode == "RESCALE":
            row = box.row()
            row.separator(factor=1)
            row.prop(retimerProps, "start_frame", text="From")
            row.prop(retimerProps, "end_frame", text="To")

            row.operator("uas_shot_manager.gettimerange", text="", icon="SEQ_STRIP_META")
            row.separator(factor=1)

            row = box.row()
            row.use_property_split = True

            row.prop(retimerProps, "factor")
            row.prop(retimerProps, "pivot")

            # apply ###
            row = box.row()
            row.separator(factor=0.1)
            compo = layout.row()
            compo.separator(factor=2)
            compo.scale_y = 1.2
            compo.operator("uas_shot_manager.retimerapply", text="Rescale")
            compo.separator(factor=2)

        elif retimerProps.mode == "CLEAR_ANIM":
            row = box.row(align=True)
            row.separator(factor=1)
            row.prop(retimerProps, "start_frame", text="From")
            row.operator(
                "uas_shot_manager.getcurrentframefor", text="", icon="TRIA_UP_BAR"
            ).propertyToUpdate = "start_frame"
            row.separator()

            row.prop(retimerProps, "end_frame", text="To")
            row.operator(
                "uas_shot_manager.getcurrentframefor", text="", icon="TRIA_UP_BAR"
            ).propertyToUpdate = "end_frame"
            row.separator()

            #            row.operator("uas_shot_manager.gettimerange", text="", icon="SEQ_STRIP_META")
            row.separator(factor=1)

            # apply ###
            row = box.row()
            row.separator(factor=0.1)
            compo = layout.row()
            compo.separator(factor=2)
            compo.scale_y = 1.2
            compo.operator("uas_shot_manager.retimerapply", text="Clear Animation")
            compo.separator(factor=2)

        elif retimerProps.mode == "MOVE":
            row = box.row()
            row.separator(factor=1)
            row.prop(retimerProps, "start_frame", text="Move Frame")
            row.prop(retimerProps, "end_frame", text="To")

            row.operator("uas_shot_manager.gettimerange", text="", icon="SEQ_STRIP_META")
            row.separator(factor=1)

            # apply ###
            row = box.row()
            row.separator(factor=0.1)
            compo = layout.row()
            compo.separator(factor=2)
            compo.scale_y = 1.2
            compo.operator("uas_shot_manager.retimerapply", text="Move")
            compo.separator(factor=2)

        else:
            pass


class UAS_PT_ShotManagerRetimer_Settings(Panel):
    bl_label = "Apply to"
    bl_idname = "UAS_PT_ShotManagerRetimer_SettingsPanel"
    bl_description = "Manage the global timing of the action in the scene and the shots"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UAS Shot Man"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "UAS_PT_ShotManagerRetimerPanel"

    def draw(self, context):
        retimerProps = context.scene.UAS_shot_manager_props.retimer

        layout = self.layout

        row = layout.row()
        row.prop(retimerProps, "onlyOnSelection", text="Selection Only")

        box = layout.box()
        box.use_property_split = True
        col = box.column()
        row = col.row(align=True)
        row.prop(retimerProps, "applyToShots")

        row = col.row(align=True)
        row.prop(retimerProps, "applyToObjects")
        row.prop(retimerProps, "applyToShapeKeys")
        row.prop(retimerProps, "applytToGreasePencil")


class UAS_ShotManager_GetTimeRange(Operator):
    bl_idname = "uas_shot_manager.gettimerange"
    bl_label = "Get Time Range"
    bl_description = "Get current time range and use it for the time changes"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        retimerProps = context.scene.UAS_shot_manager_props.retimer
        scene = context.scene

        if scene.use_preview_range:
            retimerProps.start_frame = scene.frame_preview_start
            retimerProps.end_frame = scene.frame_preview_end
        else:
            retimerProps.start_frame = scene.frame_start
            retimerProps.end_frame = scene.frame_end

        return {"FINISHED"}


class UAS_ShotManager_GetCurrentFrameFor(Operator):
    bl_idname = "uas_shot_manager.getcurrentframefor"
    bl_label = "Get Current Frame"
    bl_description = "Use the current frame for the specifed component"
    bl_options = {"INTERNAL"}

    propertyToUpdate: StringProperty()

    def execute(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props
        retimerProps = props.retimer

        currentFrame = scene.frame_current

        if "start_frame" == self.propertyToUpdate:
            retimerProps.start_frame = currentFrame
        elif "end_frame" == self.propertyToUpdate:
            retimerProps.end_frame = currentFrame
        else:
            retimerProps[self.propertyToUpdate] = currentFrame

        return {"FINISHED"}


class UAS_ShotManager_RetimerApply(Operator):
    bl_idname = "uas_shot_manager.retimerapply"
    bl_label = "Apply Retime"
    bl_description = "Apply retime"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        retimerProps = context.scene.UAS_shot_manager_props.retimer

        if retimerProps.onlyOnSelection:
            obj_list = context.selected_objects
        else:
            obj_list = context.scene.objects

        startFrame = retimerProps.start_frame
        endFrame = retimerProps.end_frame

        # wkip travail en cours
        if "INSERT" == retimerProps.mode:

            print(" start frame for Insert: ", startFrame)

            retimer.retimeScene(
                context.scene,
                retimerProps.mode,
                obj_list,
                startFrame,
                retimerProps.insert_duration,
                retimerProps.gap,
                retimerProps.factor,
                retimerProps.pivot,
                retimerProps.applyToObjects,
                retimerProps.applyToShapeKeys,
                retimerProps.applytToGreasePencil,
                retimerProps.applyToShots,
            )
        elif "DELETE" == retimerProps.mode:
            retimer.retimeScene(
                context.scene,
                retimerProps.mode,
                obj_list,
                startFrame + 1,
                endFrame - startFrame,
                True,
                retimerProps.factor,
                retimerProps.pivot,
                retimerProps.applyToObjects,
                retimerProps.applyToShapeKeys,
                retimerProps.applytToGreasePencil,
                retimerProps.applyToShots,
            )
        elif "CLEAR_ANIM" == retimerProps.mode:
            retimer.retimeScene(
                context.scene,
                retimerProps.mode,
                obj_list,
                startFrame,
                endFrame - startFrame,
                False,
                retimerProps.factor,
                retimerProps.pivot,
                retimerProps.applyToObjects,
                retimerProps.applyToShapeKeys,
                retimerProps.applytToGreasePencil,
                False,
            )
        else:
            retimer.retimer(
                context.scene,
                retimerProps.mode,
                obj_list,
                startFrame,
                endFrame,
                retimerProps.gap,
                retimerProps.factor,
                retimerProps.pivot,
                retimerProps.applyToObjects,
                retimerProps.applyToShapeKeys,
                retimerProps.applytToGreasePencil,
                retimerProps.applyToShots,
            )

        context.area.tag_redraw()
        # context.region.tag_redraw()
        bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP", iterations=1)

        if retimerProps.move_current_frame:
            if retimerProps.mode == "INSERT":
                context.scene.frame_current = context.scene.frame_current + (
                    retimerProps.end_frame - retimerProps.start_frame
                )

        return {"FINISHED"}


_classes = (
    UAS_PT_ShotManagerRetimer,
    UAS_Retimer_Properties,
    UAS_PT_ShotManagerRetimer_Settings,
    UAS_ShotManager_GetTimeRange,
    UAS_ShotManager_GetCurrentFrameFor,
    UAS_ShotManager_RetimerApply,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)

    # bpy.types.WindowManager.UAS_Retimer = PointerProperty(type=UAS_Retimer_Properties)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)

    # del bpy.types.WindowManager.UAS_Retimer
