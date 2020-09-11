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
        self.applyRenderQualitySettings()

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

    def applyRenderQualitySettings(self, renderWithOpengl=True):
        # wkip les Quality Settings devraient etre globales au fichier
        # wkip faire une distinction avec le moteur courant pour l'application des settings
        props = bpy.context.scene.UAS_shot_manager_props
        bpy.context.space_data.overlay.show_overlays = props.useOverlays

        if "LOW" == self.renderQuality:
            # eevee
            bpy.context.scene.eevee.taa_render_samples = 6
            bpy.context.scene.eevee.taa_samples = 2

            # workbench
            bpy.context.scene.render_aa = "FXAA"
            bpy.context.scene.viewport_aa = "OFF"

            # cycles
            bpy.context.scene.cycles.samples = 6
            bpy.context.scene.cycles.preview_samples = 2

        elif "MEDIUM" == self.renderQuality:
            # eevee
            bpy.context.scene.eevee.taa_render_samples = 64
            bpy.context.scene.eevee.taa_samples = 16

            # workbench
            bpy.context.scene.render_aa = "5"
            bpy.context.scene.viewport_aa = "FXAA"

            # cycles
            bpy.context.scene.cycles.samples = 64
            bpy.context.scene.cycles.preview_samples = 16

        elif "HIGH" == self.renderQuality:
            # eevee
            bpy.context.scene.eevee.taa_render_samples = 128
            bpy.context.scene.eevee.taa_samples = 32

            # workbench
            bpy.context.scene.render_aa = "16"
            bpy.context.scene.viewport_aa = "5"

            # cycles
            bpy.context.scene.cycles.samples = 128
            bpy.context.scene.cycles.preview_samples = 32

        # CUSTOM
        else:
            # we use the scene settings
            pass

        return


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

    renderWithHandles: BoolProperty(name="Render With Handles", default=False)

    writeToDisk: BoolProperty(name="Write to Disk", default=False)

    renderOtioFile: BoolProperty(name="Render EDL File", default=False)

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
