from pathlib import Path

import bpy
import opentimelineio

import logging

_logger = logging.getLogger(__name__)


def exportOtio(scene, takeIndex=-1, filePath="", fileName="", addTakeNameToPath=True, fps=-1, fileListOnly=False):
    """ Create an OpenTimelineIO XML file for the specified take
        Return the file path of the created file
        If file_name is left to default then the rendered file will be a .xml
    """
    # print("  ** -- ** exportOtio, fileListOnly: ", fileListOnly)
    props = scene.UAS_shot_manager_props

    sceneFps = fps if fps != -1 else scene.render.fps
    #   import opentimelineio as opentimelineio

    take = props.getCurrentTake() if -1 == takeIndex else props.getTakeByIndex(takeIndex)
    shotList = take.getShotList(ignoreDisabled=True)
    take_name = take.getName_PathCompliant()

    renderPath = filePath if "" != filePath else props.renderRootPath
    renderPath = bpy.path.abspath(renderPath)
    otioRenderPath = renderPath
    if otioRenderPath.startswith("//"):
        otioRenderPath = bpy.path.abspath(otioRenderPath)

    # print(f" otion export - avant - otioRenderPath: {otioRenderPath}")
    if not (otioRenderPath.endswith("/") or otioRenderPath.endswith("\\")):
        otioRenderPath += "\\"
        # print(f" otion export - apres - otioRenderPath: {otioRenderPath}")
    if addTakeNameToPath:
        otioRenderPath += take_name + "\\"
    if "" == fileName:
        otioRenderPath += take_name + ".xml"
    else:
        otioRenderPath += fileName
        if Path(fileName).suffix == "":
            otioRenderPath += ".otio"

    print("\n--- --- --- --- --- --- --- --- --- ---")
    print(f"\nExporting EDL: {otioRenderPath}\n")

    if fileListOnly:
        return otioRenderPath

    # wkip note: scene.frame_start probablement à remplacer par start du premier shot enabled!!!
    startFrame = 0
    timeline = opentimelineio.schema.Timeline(
        name=scene.name + "_" + take_name, global_start_time=opentimelineio.opentime.from_frames(startFrame, sceneFps)
    )
    track = opentimelineio.schema.Track()
    timeline.tracks.append(track)
    # opentimelineio.schema.track.TrackKind.Audio = "Video"
    myClass = opentimelineio.schema.track.TrackKind.audio
    print(f"track.TrackKind(): {opentimelineio.schema.track.TrackKind}")
    for i in myClass.__dict__.keys():
        # if i[:1] != '_'
        print("i: ", i)
    print("myClass.__doc__: ", myClass.__doc__)

    clips = list()
    playhead = 0
    for shot in shotList:
        if shot.enabled:

            # media
            media_duration = shot.end - shot.start + 1 + 2 * props.handles
            start_time, end_time_exclusive = (
                opentimelineio.opentime.from_frames(0, sceneFps),
                opentimelineio.opentime.from_frames(media_duration, sceneFps),
            )

            available_range = opentimelineio.opentime.range_from_start_end_time(start_time, end_time_exclusive)

            # shotFileFullPath = shot.getOutputFileName(fullPath=True, rootFilePath=renderPath)

            shotFileName = shot.getOutputFileName(fullPath=False) + ".mp4"  # wkip attention can be .png!!!

            shotFileFullPath = f"{renderPath}"
            _logger.info(f" renderPath: {renderPath}")
            if not (shotFileFullPath.endswith("/") or shotFileFullPath.endswith("\\")):
                shotFileFullPath += "\\"
            shotFileFullPath += f"{take_name}\\{shotFileName}"

            _logger.info(f" Adding shot: {shotFileFullPath}")
            if not Path(shotFileFullPath).exists():
                _logger.info(f"     *** File not found *** ")

            media_reference = opentimelineio.schema.ExternalReference(
                target_url=shotFileFullPath, available_range=available_range
            )

            # clip
            clip_start_time, clip_end_time_exclusive = (
                opentimelineio.opentime.from_frames(props.handles, sceneFps),
                opentimelineio.opentime.from_frames(shot.end - shot.start + 1 + props.handles, sceneFps),
            )
            source_range = opentimelineio.opentime.range_from_start_end_time(clip_start_time, clip_end_time_exclusive)
            newClip = opentimelineio.schema.Clip(
                name=shotFileName, source_range=source_range, media_reference=media_reference
            )
            # newClip.metadata = {"clip_name": shot["name"], "camera_name": shot["camera"].name_full}
            newClip.metadata["clip_name"] = shot.name
            newClip.metadata["camera_name"] = shot["camera"].name_full

            clips.append(newClip)
            playhead += media_duration

    track.extend(clips)

    Path(otioRenderPath).parent.mkdir(parents=True, exist_ok=True)
    if otioRenderPath.endswith(".xml"):
        opentimelineio.adapters.write_to_file(timeline, otioRenderPath, adapter_name="fcp_xml")
    else:
        opentimelineio.adapters.write_to_file(timeline, otioRenderPath)

    return otioRenderPath
