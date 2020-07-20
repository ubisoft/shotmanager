import os
import importlib
import subprocess
import platform

import bpy


try:
    import opentimelineio as otio

    # wkip type de comparaison qui ne marche pas tout le temps!!! ex: "2.12.1"<"11.12.1"  is False !!!
    if otio.__version__ < "0.12.1" and platform.system() == "Windows":
        print("Upgrading OpentimelineIO to 0.12.1")
        subprocess.run(
            [
                bpy.app.binary_path_python,
                "-m",
                "pip",
                "install",
                os.path.join(os.path.dirname(__file__), "OpenTimelineIO-0.12.1-cp37-cp37m-win_amd64.whl"),
            ]
        )
        importlib.reload(otio)  # Need to be tested.
except ModuleNotFoundError:
    if platform.system() == platform.system() == "Windows":
        subprocess.run(
            [
                bpy.app.binary_path_python,
                "-m",
                "pip",
                "install",
                os.path.join(os.path.dirname(__file__), "OpenTimelineIO-0.12.1-cp37-cp37m-win_amd64.whl"),
            ]
        )
    else:
        subprocess.run([bpy.app.binary_path_python, "-m", "pip", "install", "opentimelineio"])
    import opentimelineio as otio

from . import operators

from pathlib import Path


def exportOtio(scene, takeIndex=-1, filePath="", fileName="", addTakeNameToPath=True, fps=-1):
    """ Create an OpenTimelineIO XML file for the specified take
        Return the file path of the created file
        If file_name is left to default then the rendered file will be a .xml
    """
    print("  ** -- ** exportOtio")
    props = scene.UAS_shot_manager_props

    sceneFps = fps if fps != -1 else scene.render.fps
    print("exportOtio: sceneFps:", sceneFps)
    #   import opentimelineio as otio

    take = props.getCurrentTake() if -1 == takeIndex else props.getTakeByIndex(takeIndex)
    shotList = take.getShotList(ignoreDisabled=True)

    take_name = take.getName_PathCompliant()

    # wkip note: scene.frame_start probablement à remplacer par start du premier shot enabled!!!
    startFrame = 0
    timeline = otio.schema.Timeline(
        name=scene.name + "_" + take_name, global_start_time=otio.opentime.from_frames(startFrame, sceneFps)
    )
    track = otio.schema.Track()
    timeline.tracks.append(track)

    renderPath = filePath if "" != filePath else props.renderRootPath
    otioRenderPath = renderPath + "\\"
    if addTakeNameToPath:
        otioRenderPath += take_name + "\\"
    if "" == fileName:
        otioRenderPath += take_name + ".xml"
    else:
        otioRenderPath += fileName
        if Path(fileName).suffix == "":
            otioRenderPath += ".otio"

    print("   OTIO otioRenderPath:", otioRenderPath)

    clips = list()
    playhead = 0
    for shot in shotList:
        if shot.enabled:

            # media
            media_duration = shot.end - shot.start + 1 + 2 * props.handles
            start_time, end_time_exclusive = (
                otio.opentime.from_frames(0, sceneFps),
                otio.opentime.from_frames(media_duration, sceneFps),
            )

            available_range = otio.opentime.range_from_start_end_time(start_time, end_time_exclusive)

            # shotFilePath = shot.getOutputFileName(fullPath=True, rootFilePath=renderPath)

            shotFileName = shot.getOutputFileName(fullPath=False)
            shotFilePath = f"{renderPath}\\{take_name}\\{shotFileName}"
            print("    shotFilePath: ", shotFilePath, shotFileName)

            media_reference = otio.schema.ExternalReference(target_url=shotFilePath, available_range=available_range)

            # clip
            clip_start_time, clip_end_time_exclusive = (
                otio.opentime.from_frames(props.handles, sceneFps),
                otio.opentime.from_frames(shot.end - shot.start + 1 + props.handles, sceneFps),
            )
            source_range = otio.opentime.range_from_start_end_time(clip_start_time, clip_end_time_exclusive)
            newClip = otio.schema.Clip(name=shotFileName, source_range=source_range, media_reference=media_reference)
            # newClip.metadata = {"clip_name": shot["name"], "camera_name": shot["camera"].name_full}
            newClip.metadata["clip_name"] = shot.name
            newClip.metadata["camera_name"] = shot["camera"].name_full

            clips.append(newClip)
            playhead += media_duration

    track.extend(clips)

    Path(otioRenderPath).parent.mkdir(parents=True, exist_ok=True)
    if otioRenderPath.endswith(".xml"):
        otio.adapters.write_to_file(timeline, otioRenderPath, adapter_name="fcp_xml")
    else:
        otio.adapters.write_to_file(timeline, otioRenderPath)

    return otioRenderPath


# classes = (
#     ,
# )


def register():
    print("       - Registering OTIO Package")
    # for cls in classes:
    #     bpy.utils.register_class(cls)

    operators.register()


def unregister():
    operators.unregister()

    # for cls in reversed(classes):
    #     bpy.utils.unregister_class(cls)

