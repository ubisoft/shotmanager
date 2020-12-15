import bpy
from bpy.types import Operator, PropertyGroup
from bpy.props import EnumProperty, BoolProperty, FloatProperty

from shotmanager.utils import utils


class UAS_ShotManager_ShotsGlobalSettings(PropertyGroup):

    alsoApplyToDisabledShots: BoolProperty(
        name="Also Apply to Disabled Shots",
        description="Apply Global Settings changes to disabled shots as well as to enabled ones",
        default=True,
    )

    #########################
    # Camera BG
    #########################

    def _update_backgroundAlpha(self, context):
        props = context.scene.UAS_shot_manager_props
        take = props.getCurrentTake()
        shotList = take.getShotList(ignoreDisabled=False)

        for shot in shotList:
            if shot.enabled or props.shotsGlobalSettings.alsoApplyToDisabledShots:
                if shot.camera is not None and len(shot.camera.data.background_images):
                    # shot.camera.data.background_images[0].alpha = self.backgroundAlpha
                    gamma = 2.2
                    shot.camera.data.background_images[0].alpha = pow(self.backgroundAlpha, gamma)

    backgroundAlpha: FloatProperty(
        name="Background Images Alpha",
        description="Change the opacity of the camera backgrounds",
        soft_min=0.0,
        min=0.0,
        soft_max=1.0,
        max=1.0,
        step=0.1,
        update=_update_backgroundAlpha,
        default=0.9,
    )

    def _update_proxyRenderSize(self, context):
        take = context.scene.UAS_shot_manager_props.getCurrentTake()
        shotList = take.getShotList(ignoreDisabled=False)

        for shot in shotList:
            if shot.enabled or props.shotsGlobalSettings.alsoApplyToDisabledShots:
                if shot.camera is not None and len(shot.camera.data.background_images):
                    shot.camera.data.background_images[0].clip_user.proxy_render_size = self.proxyRenderSize

    proxyRenderSize: EnumProperty(
        name="Proxy Render Size",
        description="Draw preview using full resolution or different proxy resolution",
        items=(
            ("PROXY_25", "25%", ""),
            ("PROXY_50", "50%", ""),
            ("PROXY_75", "75%", ""),
            ("PROXY_100", "100%", ""),
            ("FULL", "None, Full render", ""),
        ),
        update=_update_proxyRenderSize,
        # default="PROXY_50",
        default="FULL",
    )

    #########################
    # Sound
    #########################

    def _update_backgroundVolume(self, context):
        props = context.scene.UAS_shot_manager_props
        take = props.getCurrentTake()
        shotList = take.getShotList(ignoreDisabled=False)

        for shot in shotList:
            if shot.enabled or props.shotsGlobalSettings.alsoApplyToDisabledShots:
                if shot.camera is not None and len(shot.camera.data.background_images):
                    # shot.camera.data.background_images[0].alpha = self.backgroundAlpha
                    #   gamma = 2.2
                    #   shot.camera.data.background_images[0].alpha = pow(self.backgroundAlpha, gamma)
                    pass

    backgroundVolume: FloatProperty(
        name="Background Volume",
        description="Change the volume of the camera backgrounds sound",
        soft_min=0.0,
        min=0.0,
        soft_max=3.0,
        max=30.0,
        step=0.1,
        update=_update_backgroundVolume,
        default=1.0,
    )

    #########################
    # Grease Pencil
    #########################

    def _update_greasepencilAlpha(self, context):
        props = context.scene.UAS_shot_manager_props
        take = props.getCurrentTake()
        shotList = take.getShotList(ignoreDisabled=False)

        for shot in shotList:
            if shot.enabled or props.shotsGlobalSettings.alsoApplyToDisabledShots:
                if shot.camera is not None and len(shot.camera.data.background_images):
                    # shot.camera.data.background_images[0].alpha = self.backgroundAlpha
                    gamma = 2.2
                    shot.camera.data.background_images[0].alpha = pow(self.backgroundAlpha, gamma)

    greasepencilAlpha: FloatProperty(
        name="Grease Pencil Alpha",
        description="Change the opacity of the grease pencils",
        soft_min=0.0,
        min=0.0,
        soft_max=1.0,
        max=1.0,
        step=0.1,
        update=_update_greasepencilAlpha,
        default=0.9,
    )


#####################################################################################
# Operators
#####################################################################################


class UAS_ShotsSettings_UseBackground(Operator):
    bl_idname = "uas_shots_settings.use_background"
    bl_label = "Use Background Images"
    bl_description = "Enable or disable the background images for the shot cameras"
    bl_options = {"INTERNAL", "UNDO"}

    useBackground: BoolProperty(default=False)

    def execute(self, context):
        props = context.scene.UAS_shot_manager_props

        take = props.getCurrentTake()
        shotList = take.getShotList(ignoreDisabled=False)

        for shot in shotList:
            if shot.enabled or props.shotsGlobalSettings.alsoApplyToDisabledShots:
                if shot.camera is not None:
                    shot.camera.data.show_background_images = self.useBackground

        return {"FINISHED"}


class UAS_ShotsSettings_UseBackgroundSound(Operator):
    bl_idname = "uas_shots_settings.use_background_sound"
    bl_label = "Use Background Sound"
    bl_description = "Enable or disable the background sound for the shot cameras"
    bl_options = {"INTERNAL", "UNDO"}

    useBackgroundSound: BoolProperty(default=False)

    def execute(self, context):
        props = context.scene.UAS_shot_manager_props

        props.useBGSounds = self.useBackgroundSound
        # if self.useBackgroundSound:
        props.enableBGSoundForShot(True, props.getCurrentShot())
        # else:
        #     props.enableBGSoundForShot(False, None)

        return {"FINISHED"}


class UAS_ShotsSettings_UseGreasePencil(Operator):
    bl_idname = "uas_shots_settings.use_greasepencil"
    bl_label = "Use Grease Pencil"
    bl_description = "Enable or disable the grease pencil for the shot cameras"
    bl_options = {"INTERNAL", "UNDO"}

    useGreasepencil: BoolProperty(default=False)

    def execute(self, context):
        props = context.scene.UAS_shot_manager_props

        take = props.getCurrentTake()
        shotList = take.getShotList(ignoreDisabled=False)

        for shot in shotList:
            if shot.enabled or props.shotsGlobalSettings.alsoApplyToDisabledShots:
                if shot.camera is not None:
                    gp_child = utils.get_greasepencil_child(shot.camera)
                    if gp_child is not None:
                        gp_child.hide_viewport = self.useGreasepencil
                        gp_child.hide_render = self.useGreasepencil

        return {"FINISHED"}


# class UAS_ShotsSettings_BackgroundAlpha(Operator):
#     bl_idname = "uas_shots_settings.background_alpha"
#     bl_label = "Set Background Opacity"
#     bl_description = "Change the background images opacity for the shot cameras"
#     bl_options = {"INTERNAL", "UNDO"}

#     alpha: FloatProperty(default=0.75)

#     def execute(self, context):
#         props = context.scene.UAS_shot_manager_props
#         take = props.getCurrentTake()
#         shotList = take.getShotList(ignoreDisabled=False)

#         for shot in shotList:
#             if shot.camera is not None and len(shot.camera.data.background_images):
#                 shot.camera.data.background_images[0].alpha = self.alpha  # globalSettings.backgroundAlpha

#         return {"FINISHED"}


# class UAS_ShotsSettings_BackgroundProxyRenderSize(Operator):
#     bl_idname = "uas_shots_settings.bg_proxy_render_size"
#     bl_label = "proxy Render Size"
#     bl_description = "proxy Render Size"
#     bl_options = {"INTERNAL", "UNDO"}

#     proxyRenderSize: bpy.props.EnumProperty(
#         name="Proxy Render Size",
#         description="Draw preview using full resolution or different proxy resolution",
#         items=(
#             ("PROXY_25", "25%", ""),
#             ("PROXY_50", "50%", ""),
#             ("PROXY_75", "75%", ""),
#             ("PROXY_100", "100%", ""),
#             ("FULL", "None, Full render", ""),
#         ),
#         default="PROXY_50",
#     )

#     def execute(self, context):
#         props = context.scene.UAS_shot_manager_props
#         take = props.getCurrentTake()
#         shotList = take.getShotList(ignoreDisabled=False)

#         for shot in shotList:
#             if shot.camera is not None and len(shot.camera.data.background_images):
#                 shot.camera.data.background_images[0].clip_user.proxy_render_size = self.proxyRenderSize

#         return {"FINISHED"}


_classes = (
    UAS_ShotManager_ShotsGlobalSettings,
    UAS_ShotsSettings_UseBackground,
    UAS_ShotsSettings_UseBackgroundSound,
    UAS_ShotsSettings_UseGreasePencil,
    # UAS_ShotsSettings_BackgroundAlpha,
    # UAS_ShotsSettings_BackgroundProxyRenderSize,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
