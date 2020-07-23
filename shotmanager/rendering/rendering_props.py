from bpy.types import PropertyGroup
from bpy.props import StringProperty, BoolProperty, EnumProperty


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

    renderOtioFile: BoolProperty(name="Render Otio File", default=False)

    otioFileType: EnumProperty(
        name="File Type",
        description="Export the edit either in an OpenTimelineIO file format or a standard XML",
        items=(("OTIO", "Otio", ""), ("XML", "Xml", "")),
        default="XML",
    )

    # file format
    # image_settings_file_format = 'FFMPEG'
    # scene.render.ffmpeg.format = 'MPEG4'
