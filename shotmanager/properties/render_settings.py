from bpy.types import PropertyGroup
from bpy.props import StringProperty, BoolProperty, EnumProperty


class UAS_ShotManager_RenderSettings(PropertyGroup):

    name: StringProperty(name="Name", default="Render Settings")

    renderMode: EnumProperty(
        name="Render Mode",
        description="Render Mode",
        items=(("STILL", "Still", ""), ("ANIMATION", "Animation", ""), ("PROJECT", "Project", "")),
        default="STILL",
    )

    renderAllTakes: BoolProperty(name="Render All Takes", default=False)

    renderAllShots: BoolProperty(name="Render All Shots", default=False)

    renderAlsoDisabled: BoolProperty(name="Render Also Disabled", default=False)

    renderWithHandles: BoolProperty(name="Render With Handles", default=False)

    writeToDisk: BoolProperty(name="Write to Disk", default=False)

    # file format
    # image_settings_file_format = 'FFMPEG'
    # scene.render.ffmpeg.format = 'MPEG4'
