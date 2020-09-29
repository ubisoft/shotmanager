import bpy
from bpy.types import PropertyGroup
from bpy.props import StringProperty, BoolProperty, EnumProperty


# def list_available_render_engines(self, context):
#     engineList = list()

#     engineList.append(("EEVEE", "Eevee", "", 0))
#     engineList.append(("WORKBENCH", "Workbench", "", 1))
#     if "ENGINE_ANIM" == self.renderComputationMode or "ENGINE_LOOP" == self.renderComputationMode:
#         engineList.append(("CYCLES", "Cycles", "", 2))
#     return engineList


class UAS_ShotManager_RenderGlobalContext(PropertyGroup):

    renderComputationMode: EnumProperty(
        name="Render Mode",
        description="Use the specified render engine or the playblast mode",
        items=(
            ("PLAYBLAST_ANIM", "Playblast Anim.", "Use opengl render playblast (animation mode)"),
            ("PLAYBLAST_LOOP", "Playblast Loop", "Use opengl render playblast, images are computed in a custom loop"),
            ("ENGINE_ANIM", "Engine Anim", "Use specified renderer (animation mode)"),
            ("ENGINE_LOOP", "Engine Loop", "Use specified renderer, images are computed in a custom loop"),
        ),
        default="PLAYBLAST_ANIM",
        options=set(),
    )

    def _update_renderEngine(self, context):
        pass

    renderEngine: EnumProperty(
        name="Render Engine",
        description="Set the Render Engine to use for the rendering",
        items=(
            ("BLENDER_EEVEE", "Eevee", ""),
            ("BLENDER_WORKBENCH", "Workbench", ""),
            ("CYCLES", "Cycles", ""),
            ("CUSTOM", "Custom", "Use the settings present in the scene. No other settings are applied"),
        ),
        default="BLENDER_EEVEE",
        update=_update_renderEngine,
    )

    renderEngineOpengl: EnumProperty(
        name="Render Engine Opengl",
        description="Set the Render Engine to use for the playblast rendering",
        items=(
            ("BLENDER_EEVEE", "Eevee", ""),
            ("BLENDER_WORKBENCH", "Workbench", ""),
            ("CUSTOM", "Custom", "Use the settings present in the scene. No other settings are applied"),
        ),
        default="BLENDER_EEVEE",
        # update=_update_renderEngine,
    )

    def _update_renderQuality(self, context):
        self.applyRenderQualitySettings(context)

    renderQuality: EnumProperty(
        name="Render Quality",
        description="Set the Render Quality settings to use for the rendering.\nSettings are applied immediatly.",
        items=(
            ("LOW", "Low (faster)", ""),
            ("MEDIUM", "Medium", ""),
            ("HIGH", "High (slower)", ""),
            ("CUSTOM", "Custom", "Use the settings present in the scene. No other settings are applied"),
        ),
        default="LOW",
        update=_update_renderQuality,
    )

    def applyRenderQualitySettings(self, context, renderWithOpengl=True):
        # wkip les Quality Settings devraient etre globales au fichier
        # wkip faire une distinction avec le moteur courant pour l'application des settings
        props = context.scene.UAS_shot_manager_props
        #  bpy.context.space_data.overlay.show_overlays = props.useOverlays

        if "LOW" == self.renderQuality:
            # eevee
            context.scene.eevee.taa_render_samples = 6
            context.scene.eevee.taa_samples = 2

            # workbench
            # if "BLENDER_WORKBENCH" == bpy.context.scene.render.engine:
            context.scene.display.render_aa = "FXAA"
            context.scene.display.viewport_aa = "OFF"

            # cycles
            context.scene.cycles.samples = 6
            context.scene.cycles.preview_samples = 2

        elif "MEDIUM" == self.renderQuality:
            # eevee
            context.scene.eevee.taa_render_samples = 32  # 64
            context.scene.eevee.taa_samples = 6  # 16

            # workbench
            # if "BLENDER_WORKBENCH" == bpy.context.scene.render.engine:
            context.scene.display.render_aa = "5"
            context.scene.display.viewport_aa = "FXAA"

            # cycles
            context.scene.cycles.samples = 64
            context.scene.cycles.preview_samples = 16

        elif "HIGH" == self.renderQuality:
            # eevee
            context.scene.eevee.taa_render_samples = 64  # 128
            context.scene.eevee.taa_samples = 12  # 32

            # workbench
            #            if "BLENDER_WORKBENCH" == bpy.context.scene.render.engine:
            context.scene.display.render_aa = "16"
            context.scene.display.viewport_aa = "5"

            # cycles
            context.scene.cycles.samples = 128
            context.scene.cycles.preview_samples = 32

        # CUSTOM
        else:
            # we use the scene settings
            pass

        return

    useOverlays: BoolProperty(
        name="With Overlays",
        description="Also render overlays when the rendering is a playblast",
        default=False,
        options=set(),
    )


class UAS_ShotManager_RenderSettings(PropertyGroup):

    name: StringProperty(name="Name", default="Render Settings")

    renderMode: EnumProperty(
        name="Render Mode",
        description="Render Mode",
        items=(("STILL", "Still", ""), ("ANIMATION", "Animation", ""), ("ALL", "All Edits", ""), ("OTIO", "Otio", ""),),
        default="STILL",
    )

    # properties are initialized according to their use in the function props.createRenderSettings()

    renderAllTakes: BoolProperty(name="Render All Takes", default=False)

    renderAllShots: BoolProperty(name="Render All Shots", default=True)

    renderAlsoDisabled: BoolProperty(name="Render Also Disabled", default=False)

    renderHandles: BoolProperty(name="Render With Handles", default=False)

    writeToDisk: BoolProperty(name="Write to Disk", default=False)

    renderOtioFile: BoolProperty(name="Render EDL File", default=False)

    rerenderExistingShotVideos: BoolProperty(name="Re-render Exisiting Shot Videos", default=True)

    bypass_rendering_project_settings: BoolProperty(
        name="Bypass Project Settings",
        description="When Project Settings are used this allows the use of custom rendering settings",
        default=False,
        options=set(),
    )

    generateEditVideo: BoolProperty(
        name="Generate Edit Video(s)",
        description="Generate the edit video of the take with all the specified shot videos",
        default=False,
    )

    otioFileType: EnumProperty(
        name="File Type",
        description="Export the edit either in an OpenTimelineIO file format or a standard XML",
        items=(("OTIO", "Otio", ""), ("XML", "Xml", "")),
        default="XML",
    )

    # file format
    # image_settings_file_format = 'FFMPEG'
    # scene.render.ffmpeg.format = 'MPEG4'
