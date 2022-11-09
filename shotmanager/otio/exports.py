# GPLv3 License
#
# Copyright (C) 2021 Ubisoft
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Otion exports
"""

from pathlib import Path

import bpy
import opentimelineio

from xml.dom.minidom import parse

from ..utils import utils
from ..utils import utils_xml

from ..config import sm_logging

_logger = sm_logging.getLogger(__name__)


def addEditCharacteristicsToXML(xml_filename, montageCharacteristics):

    if montageCharacteristics is None:
        print("  *** Exporting edit XML: addEditCharacteristicsToXML: No characteristics found for the montage")
        return ()

    filename = xml_filename

    dom1 = parse(filename)

    seq = dom1.getElementsByTagName("sequence")[0]

    seqMedia = None
    seqMediaVideo = None

    seqMedia = utils_xml.getFirstChildWithName(seq, "media")
    if seqMedia is not None:
        seqMediaVideo = utils_xml.getFirstChildWithName(seqMedia, "video")

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
    # use this:
    # print(f"dom1.toxml(): {dom1.toxml()}")

    file_handle = open(filename, "w")

    dom1.writexml(file_handle)
    # # print(f"dom1.toxml(): {dom1.toxml()}")
    # # file_handle.write(dom1.toxml())

    file_handle.close()
    dom1.unlink()

    return ()


def fillEditFile(scene, props, take, sceneFps, output_media_mode, rootPath):
    seq_name = props.getSequenceName("FULL", addSeparator=True)
    take_name = take.getName_PathCompliant()
    shotList = take.getShotList(ignoreDisabled=True)

    # wkip note: scene.frame_start probablement à remplacer par start du premier shot enabled!!!
    startFrame = 0
    timeline = opentimelineio.schema.Timeline(
        name=f"{seq_name}{take_name}",
        global_start_time=opentimelineio.opentime.from_frames(startFrame, sceneFps),
    )
    timeline.metadata["exported_with"] = "Ubisoft Shot Manager V. " + props.version()[0]
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
            media_duration = shot.end - shot.start + 1 + 2 * props.getHandlesDuration()
            start_time, end_time_exclusive = (
                opentimelineio.opentime.from_frames(0, sceneFps),
                opentimelineio.opentime.from_frames(media_duration, sceneFps),
            )

            available_range = opentimelineio.opentime.range_from_start_end_time(start_time, end_time_exclusive)

            shotFileFullPath = shot.getOutputMediaPath(
                "SH_" + output_media_mode, rootPath=rootPath, insertSeqPrefix=True
            )
            # print(" Export otio - shotFileFullPath: ", shotFileFullPath)
            # shotFileName = Path(shotFileFullPath).name
            shotFileName = shot.getName_PathCompliant(withPrefix=True)

            _logger.debug_ext(f" Adding shot to Edit file: {shotFileFullPath}", tag="EDIT_IO")
            if not Path(shotFileFullPath).exists():
                _logger.warning_ext("    File not found ! ")

            media_reference_video = opentimelineio.schema.ExternalReference(
                target_url=shotFileFullPath, available_range=available_range
            )
            media_reference_audio = opentimelineio.schema.ExternalReference(
                target_url=shotFileFullPath, available_range=available_range
            )

            # clip
            clip_start_time, clip_end_time_exclusive = (
                opentimelineio.opentime.from_frames(props.getHandlesDuration(), sceneFps),
                opentimelineio.opentime.from_frames(shot.end - shot.start + 1 + props.getHandlesDuration(), sceneFps),
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

    return timeline


def exportTakeEditToOtio(
    scene,
    take,
    rootPath,
    output_filepath="",
    fps=-1,
    fileListOnly=False,
    output_media_mode="VIDEO",
):
    """Create an OpenTimelineIO XML file for the specified take
    Return the file path of the created file
    If file_name is left to default then the rendered file will be a .xml
    seqCharacteristics and videoCharacteristics are dictionaries from the Montage_Otio
    output_media_mode: can be "IMAGE_SEQ", "VIDEO", "IMAGE_SEQ_AND_VIDEO". Specify the file format of the rendered
    media.
    """
    props = config.getAddonProps(scene)
    sceneFps = fps if fps != -1 else utils.getSceneEffectiveFps(scene)
    #   import opentimelineio as opentimelineio

    infoStr = "\n--- --- --- --- --- --- --- --- --- ---"
    infoStr += "\n   Exporting edit file"
    infoStr += "\n--- --- --- --- --- --- --- --- --- ---"
    infoStr += f"\n\n    File: {output_filepath}\n"
    _logger.info_ext(infoStr, col="GREEN")

    if fileListOnly:
        return output_filepath

    timeline = fillEditFile(scene, props, take, sceneFps, output_media_mode, rootPath)

    Path(output_filepath).parent.mkdir(parents=True, exist_ok=True)
    if output_filepath.endswith(".xml"):
        opentimelineio.adapters.write_to_file(timeline, output_filepath, adapter_name="fcp_xml")

        montageCharacteristics = props.get_montage_characteristics()
        addEditCharacteristicsToXML(output_filepath, montageCharacteristics)

    else:
        opentimelineio.adapters.write_to_file(timeline, output_filepath)

    return output_filepath


def exportShotManagerEditToOtio(
    scene,
    takeIndex=-1,
    filePath="",
    fileName="",
    addTakeNameToPath=True,
    fps=-1,
    fileListOnly=False,
    montageCharacteristics=None,
    output_media_mode="VIDEO",
):
    """Create an OpenTimelineIO XML file for the specified take
    Return the file path of the created file
    If file_name is left to default then the rendered file will be a .xml
    seqCharacteristics and videoCharacteristics are dictionaries from the Montage_Otio
    """
    _logger.debug_ext(f"exportShotManagerEditToOtio from exports.py, fileListOnly: {fileListOnly}", tag="DEPRECATED")

    props = config.getAddonProps(scene)
    sceneFps = fps if fps != -1 else utils.getSceneEffectiveFps(scene)
    #   import opentimelineio as opentimelineio

    take = props.getCurrentTake() if -1 == takeIndex else props.getTakeByIndex(takeIndex)
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
    print(f"\nExporting Edit file: {otioRenderPath}\n")

    if fileListOnly:
        return otioRenderPath

    otioRenderPath = exportTakeEditToOtio(
        scene, take, renderPath, otioRenderPath, sceneFps, fileListOnly, output_media_mode
    )

    return otioRenderPath
