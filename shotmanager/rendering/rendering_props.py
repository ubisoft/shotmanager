import bpy
from bpy.types import PropertyGroup
from bpy.props import StringProperty, BoolProperty, EnumProperty


class UAS_ShotManager_RenderGlobalContext(PropertyGroup):
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
        props = bpy.context.scene.UAS_shot_manager_props
        bpy.context.space_data.overlay.show_overlays = props.useOverlays

        if "LOW" == self.renderQuality:
            # eevee
            bpy.context.scene.eevee.taa_render_samples = 6
            bpy.context.scene.eevee.taa_samples = 2

        elif "MEDIUM" == self.renderQuality:
            # eevee
            bpy.context.scene.eevee.taa_render_samples = 64
            bpy.context.scene.eevee.taa_samples = 16

        elif "HIGH" == self.renderQuality:
            # eevee
            bpy.context.scene.eevee.taa_render_samples = 128
            bpy.context.scene.eevee.taa_samples = 32

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
