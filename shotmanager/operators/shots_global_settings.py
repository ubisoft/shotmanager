import bpy
from bpy.types import Operator, PropertyGroup
from bpy.props import IntProperty, StringProperty, EnumProperty, BoolProperty, FloatProperty, PointerProperty


class UAS_ShotManager_ShotsGlobalSettings(PropertyGroup):
    def _update_backgroundAlpha(self, context):
        bpy.ops.uas_shots_settings.background_alpha(alpha=self.backgroundAlpha)

    backgroundAlpha: FloatProperty(
        name="Background Images Alpha",
        description="Change the opacity of the camera backgrounds",
        soft_min=0.0,
        min=0.0,
        soft_max=1.0,
        max=1.0,
        step=0.1,
        update=_update_backgroundAlpha,
        default=0.7,
    )


class UAS_ShotsSettings_UseBackground(Operator):
    bl_idname = "uas_shots_settings.use_background"
    bl_label = "Use Background Images"
    bl_description = "Enable or disable the background images for the shot cameras"
    bl_options = {"INTERNAL", "REGISTER", "UNDO"}

    useBackground: BoolProperty(default=False)

    def execute(self, context):
        props = context.scene.UAS_shot_manager_props

        take = props.getCurrentTake()
        shotList = take.getShotList(ignoreDisabled=False)

        for shot in shotList:
            if shot.camera is not None:
                shot.camera.data.show_background_images = self.useBackground

        return {"FINISHED"}


class UAS_ShotsSettings_BackgroundAlpha(Operator):
    bl_idname = "uas_shots_settings.background_alpha"
    bl_label = "Set Background Opacity"
    bl_description = "Change the background images opacity for the shot cameras"
    bl_options = {"INTERNAL", "REGISTER", "UNDO"}

    alpha: FloatProperty(default=0.75)

    def execute(self, context):
        props = context.scene.UAS_shot_manager_props
        # globalSettings = bpy.types.WindowManager.UAS_shot_manager_shotsGlobalSettings

        take = props.getCurrentTake()
        shotList = take.getShotList(ignoreDisabled=False)

        for shot in shotList:
            if shot.camera is not None and len(shot.camera.data.background_images):
                shot.camera.data.background_images[0].alpha = self.alpha  # globalSettings.backgroundAlpha

        return {"FINISHED"}


_classes = (
    UAS_ShotManager_ShotsGlobalSettings,
    UAS_ShotsSettings_UseBackground,
    UAS_ShotsSettings_BackgroundAlpha,
)



def register():
    for cls in _classes:
        bpy.utils.register_class(cls)

    # declaration of properties that will not be saved in the scene

    bpy.types.WindowManager.UAS_shot_manager_shotsGlobalSettings = PointerProperty(
        type=UAS_ShotManager_ShotsGlobalSettings
    )


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
