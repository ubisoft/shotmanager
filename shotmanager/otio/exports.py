from pathlib import Path

import bpy
import opentimelineio

from xml.dom.minidom import parse

from shotmanager.utils import utils_xml

import logging

_logger = logging.getLogger(__name__)


def exportShotManagerEditToOtio(
    scene,
    takeIndex=-1,
    filePath="",
    fileName="",
    addTakeNameToPath=True,
    fps=-1,
    fileListOnly=False,
    montageCharacteristics=None,
):
    """ Create an OpenTimelineIO XML file for the specified take
        Return the file path of the created file
        If file_name is left to default then the rendered file will be a .xml
        seqCharacteristics and videoCharacteristics are dictionaries from the Montage_Otio
    """

    def _addEditCharacteristicsToXML(xml_filename, montageCharacteristics):

        if montageCharacteristics is None:
            print("  *** Exporting edit XML: _addEditCharacteristicsToXML: No characteristics found for the montage")
            return ()

        filename = xml_filename

        dom1 = parse(filename)

        seq = dom1.getElementsByTagName("sequence")[0]

        seqMedia = None
        seqMediaVideo = None

        seqMedia = utils_xml.getFirstChildWithName(seq, "media")
        if seqMedia is not None:
            seqMediaVideo = utils_xml.getFirstChildWithName(seqMedia, "video")
            print(f"seqMediaVideo: {seqMediaVideo}")

            # sequence characteristics
            newNodeFormat = dom1.createElement("format")
            newNodeCharact = dom1.createElement("samplecharacteristics")
            newNodeFormat.appendChild(newNodeCharact)

            newNodeRate = dom1.createElement("rate")

            newNodeTimebase = dom1.createElement("timebase")
            nodeText = dom1.createTextNode(str(montageCharacteristics["framerate"]))
            newNodeTimebase.appendChild(nodeText)
            newNodeRate.appendChild(newNodeTimebase)
            newNodeNtsc = dom1.createElement("ntsc")
            nodeText = dom1.createTextNode("FALSE")
            newNodeNtsc.appendChild(nodeText)
            newNodeRate.appendChild(newNodeNtsc)

            newNodeCharact.appendChild(newNodeRate)

            # video characteristics
            newNode = dom1.createElement("width")
            nodeText = dom1.createTextNode(str(montageCharacteristics["resolution_x"]))
            newNode.appendChild(nodeText)
            newNodeCharact.appendChild(newNode)

            newNode = dom1.createElement("height")
            nodeText = dom1.createTextNode(str(montageCharacteristics["resolution_y"]))
            newNode.appendChild(nodeText)
            newNodeCharact.appendChild(newNode)

            newNode = dom1.createElement("anamorphic")
            nodeText = dom1.createTextNode("FALSE")
            newNode.appendChild(nodeText)
            newNodeCharact.appendChild(newNode)

            newNode = dom1.createElement("pixelaspectratio")
            nodeText = dom1.createTextNode("square")
            newNode.appendChild(nodeText)
            newNodeCharact.appendChild(newNode)

            newNode = dom1.createElement("fielddominance")
            nodeText = dom1.createTextNode("none")
            newNode.appendChild(nodeText)
            newNodeCharact.appendChild(newNode)

            newNode = dom1.createElement("colordepth")
            nodeText = dom1.createTextNode("24")
            newNode.appendChild(nodeText)
            newNodeCharact.appendChild(newNode)

            seqMediaVideo.insertBefore(newNodeFormat, seqMediaVideo.firstChild)

        # print(f"dom1.toxml(): {dom1.toprettyxml()}")
        print(f"dom1.toxml(): {dom1.toxml()}")

        file_handle = open(filename, "w")

        dom1.writexml(file_handle)
        # # print(f"dom1.toxml(): {dom1.toxml()}")
        # # file_handle.write(dom1.toxml())

        file_handle.close()
        dom1.unlink()

        return ()

    print("  ** -- ** exportShotManagerEditToOtio from exports.py, fileListOnly: ", fileListOnly)
    props = scene.UAS_shot_manager_props
    sceneFps = fps if fps != -1 else scene.render.fps
    #   import opentimelineio as opentimelineio

    montageCharacteristics = props.get_montage_characteristics()

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
    timeline.metadata["exported_with"] = "UAS Shot Manager V. " + props.version()[0]
    from datetime import datetime

    now = datetime.now()
    timeline.metadata["exported_date"] = f"{now.strftime('%b-%d-%Y')}  -  {now.strftime('%H:%M:%S')}"
    timeline.metadata["source_file"] = bpy.data.filepath

    # track 2
    # for some reason video track MUST be set first otherwise the pathurl is set at the second occurence of the media in the
    # xml file, not the first, and at import time file is not found...
    videoTrack = opentimelineio.schema.Track()
    videoTrack.name = "Video Track"
    videoTrack.kind = "Video"  # is the default
    timeline.tracks.append(videoTrack)

    # track 1
    audioTrack = opentimelineio.schema.Track()
    audioTrack.name = "Audio Track"
    audioTrack.kind = "Audio"
    timeline.tracks.append(audioTrack)

    # opentimelineio.schema.videoTrack.TrackKind.Audio = "Video"
    # print(f"videoTrack.kind: {videoTrack.kind}")
    # print(f"type(videoTrack.kind): {type(videoTrack.kind)}")
    # print(f"videoTrack.TrackKind(): {videoTrack.TrackKind()}")
    # myClass = opentimelineio.schema.videoTrack.kind
    # for i in myClass.__dict__.keys():
    #     # if i[:1] != '_'
    #     print("i: ", i)
    # print("myClass.__doc__: ", myClass.__doc__)

    videoClips = list()
    audioClips = list()
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

            # shotFileName = shot.getOutputFileName(fullPath=False)  # + ".mp4"  # wkip attention can be .png!!!

            # shotFileFullPath = f"{renderPath}"
            # _logger.info(f" renderPath: {renderPath}")
            # if not (shotFileFullPath.endswith("/") or shotFileFullPath.endswith("\\")):
            #     shotFileFullPath += "\\"
            # shotFileFullPath += f"{take_name}\\{shotFileName}"

            # shotFileFullPath = shot.getCompositedMediaPath(renderPath)
            shotFileFullPath = shot.getOutputMediaPath(rootPath=renderPath)
            print(" Export otio - shotFileFullPath: ", shotFileFullPath)
            shotFileName = Path(shotFileFullPath).name

            _logger.info(f" Adding shot: {shotFileFullPath}")
            if not Path(shotFileFullPath).exists():
                _logger.info(f"     *** File not found *** ")

            media_reference_video = opentimelineio.schema.ExternalReference(
                target_url=shotFileFullPath, available_range=available_range
            )
            media_reference_audio = opentimelineio.schema.ExternalReference(
                target_url=shotFileFullPath, available_range=available_range
            )

            # clip
            clip_start_time, clip_end_time_exclusive = (
                opentimelineio.opentime.from_frames(props.handles, sceneFps),
                opentimelineio.opentime.from_frames(shot.end - shot.start + 1 + props.handles, sceneFps),
            )
            source_range = opentimelineio.opentime.range_from_start_end_time(clip_start_time, clip_end_time_exclusive)

            newVideoClip = opentimelineio.schema.Clip(
                name=shotFileName, source_range=source_range, media_reference=media_reference_video
            )
            newVideoClip.metadata["clip_name"] = shot.name
            newVideoClip.metadata["camera_name"] = shot["camera"].name_full
            videoClips.append(newVideoClip)

            newAudioClip = opentimelineio.schema.Clip(
                name=shotFileName + "_audio", source_range=source_range, media_reference=media_reference_audio
            )
            newAudioClip.metadata["clip_name"] = shot.name + "_audio"
            newAudioClip.metadata["camera_name"] = shot["camera"].name_full
            audioClips.append(newAudioClip)

            playhead += media_duration

    videoTrack.extend(videoClips)
    audioTrack.extend(audioClips)

    Path(otioRenderPath).parent.mkdir(parents=True, exist_ok=True)
    print("Ici")
    if otioRenderPath.endswith(".xml"):
        print("Ici 02 ")
        opentimelineio.adapters.write_to_file(timeline, otioRenderPath, adapter_name="fcp_xml")

        print("Ici 03 ")
        montageCharacteristics = props.get_montage_characteristics()
        _addEditCharacteristicsToXML(otioRenderPath, montageCharacteristics)

        print("Ici 04 ")
    else:
        opentimelineio.adapters.write_to_file(timeline, otioRenderPath)

    return otioRenderPath
