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
Playblast
"""

from pathlib import Path

import bpy

from shotmanager.utils import utils
from shotmanager.utils import utils_markers
from shotmanager.utils import utils_vse
from shotmanager.utils.utils_os import module_can_be_imported
from shotmanager.config import config

# from shotmanager.otio.montage_otio import MontageOtio

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


def importShotMarkersFromMontage(scene, montageOtio, verbose=False):
    for i, seq in enumerate(montageOtio.get_sequences()):
        if verbose:
            print(f"seq name: {seq.get_name()}")
        for j, sh in enumerate(seq.getEditShots()):
            if verbose:
                print(
                    f"    shot name: {sh.get_name()}, starts at: {sh.get_frame_final_start()}"
                )  # , from media {sh.get_med}
            marker_name = Path(sh.get_name()).stem
            scene.timeline_markers.new(marker_name, frame=sh.get_frame_final_start())

            # last marker
            if len(montageOtio.get_sequences()) - 1 == i and len(seq.getEditShots()) - 1 == j:
                scene.timeline_markers.new("Edit End", frame=sh.get_frame_final_end())


def rrs_animatic_to_vsm(editVideoFile=None, otioFile=None, montageOtio=None, importMarkers=True):
    scene = utils.getSceneVSE("SM_CheckSequence", createVseTab=True)
    bpy.context.window.workspace = bpy.data.workspaces["Video Editing"]

    vse_render = bpy.context.window_manager.UAS_vse_render
    props = config.getAddonProps(scene)
    vsm_props = scene.UAS_vsm_props

    editVideoFile = editVideoFile
    if editVideoFile is None:
        editVideoFile = r"C:\_UAS_ROOT\RRSpecial\05_Acts\Act01\_Montage\Act01_Edit_Previz.mp4"
    if otioFile is None:
        otioFile = r"C:\_UAS_ROOT\RRSpecial\05_Acts\Act01\_Montage\Act01_Edit_Previz.xml"
    importMarkers = importMarkers

    # if config.devDebug:
    #        importMarkers = False

    vsm_props.updateTracksList(scene)

    #    bpy.context.space_data.show_seconds = False
    scene.frame_start = 0
    scene.frame_end = 40000
    if props.use_project_settings:
        # scene.render.image_settings.file_format = props.project_images_output_format
        utils.setSceneFps(scene, props.project_fps)
        scene.render.resolution_x = props.project_resolution_framed_x
        scene.render.resolution_y = props.project_resolution_framed_y
    else:
        utils.setSceneFps(scene, 25)
        scene.render.resolution_x = 1280
        scene.render.resolution_y = 960

    # projectFps = scene.render.fps
    # sequenceFileName = props.getRenderShotPrefix() + takeName
    # scene.use_preview_range = False
    # renderResolution = [scene.render.resolution_x, scene.render.resolution_y]
    # renderResolutionFramed = [scene.render.resolution_x, scene.render.resolution_y]

    # # override local variables with project settings
    # if props.use_project_settings:
    #     props.applyProjectSettings()
    #     scene.render.image_settings.file_format = props.project_images_output_format
    #     projectFps = scene.render.fps
    #     sequenceFileName = props.getRenderShotPrefix()
    #     renderResolution = [props.project_resolution_x, props.project_resolution_y]
    #     renderResolutionFramed = [props.project_resolution_framed_x, props.project_resolution_framed_y]

    # clear all
    # vsm_props.clear_all()
    # wkip a remplacer par des fonctions
    bpy.ops.uas_video_shot_manager.clear_markers()

    # bpy.ops.uas_video_shot_manager.clear_clips()
    vsm_props.getTrackByIndex(1).clearContent()
    vsm_props.getTrackByIndex(2).clearContent()
    # bpy.ops.uas_video_shot_manager.remove_multiple_tracks(action="ALL")

    vsm_props.updateTracksList(scene)

    # video
    channelInd = 2
    trackName = "Act01 Previz_Edit (video)"
    editVideoClip = vse_render.createNewClip(
        scene, editVideoFile, clipName=trackName, channelInd=channelInd, atFrame=0, importAudio=False
    )
    # vsm_props.addTrack(atIndex=1, trackType="STANDARD", name="Previz_Edit (video)", color=(0.1, 0.2, 0.8, 1))
    vsm_props.setTrackInfo(channelInd, trackType="VIDEO", name=trackName)

    # audio
    channelInd = 1
    trackName = "Act01 Previz_Edit (audio)"
    editAudioClip = vse_render.createNewClip(
        scene, editVideoFile, clipName=trackName, channelInd=channelInd, atFrame=0, importVideo=False, importAudio=True
    )
    # vsm_props.addTrack(atIndex=2, trackType="STANDARD", name="Previz_Edit (audio)", color=(0.1, 0.5, 0.2, 1))
    vsm_props.setTrackInfo(channelInd, trackType="AUDIO", name=trackName)

    # if self.useOverlayFrame:
    #     overlayClip = vse_render.createNewClip(scene, self.overlayFile, 2, 0, offsetEnd=-60000)
    #     scene.sequence_editor.sequences_all[overlayClip.name].blend_type = "ALPHA_OVER"

    # works on selection
    bpy.ops.sequencer.set_range_to_strips(preview=False)

    ################
    # import markers
    ################

    scene.timeline_markers.clear()
    if importMarkers:

        if montageOtio is None:
            if not module_can_be_imported("shotmanager.otio"):
                _logger.error("Otio module not available (no OpenTimelineIO): Cannot import markers")
            else:
                from shotmanager.otio.montage_otio import MontageOtio

                # config.gMontageOtio
                config.gMontageOtio = None
                if importMarkers and "" != otioFile and Path(otioFile).exists():
                    config.gMontageOtio = MontageOtio()
                    config.gMontageOtio.fillMontageInfoFromOtioFile(
                        otioFile=otioFile, refVideoTrackInd=0, verboseInfo=False
                    )

                    config.gSeqEnumList = list()
                    print(f"config.gMontageOtio name: {config.gMontageOtio.get_name()}")
                    for i, seq in enumerate(config.gMontageOtio.sequencesList):
                        #    print(f"- seqList: i:{i}, seq: {seq.get_name()}")
                        config.gSeqEnumList.append((str(i), seq.get_name(), f"Import sequence {seq.get_name()}", i + 1))
                montageOtio = config.gMontageOtio

        importShotMarkersFromMontage(scene, config.gMontageOtio)


def getSoundFilesForEachShot(montageOtio, seqName, otioFile):
    soundsDict = dict()
    if montageOtio is None:

        if not module_can_be_imported("shotmanager.otio"):
            _logger.error("Otio module not available (no OpenTimelineIO)")
            return soundsDict
        else:
            from shotmanager.otio.montage_otio import MontageOtio

            config.gMontageOtio = MontageOtio()
            config.gMontageOtio.fillMontageInfoFromOtioFile(otioFile=otioFile, refVideoTrackInd=0, verboseInfo=False)

    seq = config.gMontageOtio.get_sequence_by_name(seqName)
    if seq is not None:
        print(f" here seq sound name: {seq.get_name()}")
        shotSounds = dict()
        for s in seq.getEditShots():

            print(f"  shot sound name: {s.get_name()}")
            shotSounds[s.get_name()] = s.get_media_soundfiles()
            soundsDict.append(shotSounds)

    return soundsDict


def rrs_sequence_to_vsm(scene, sequenceName):
    """Import specified sequence video to the VSM"""
    vse_render = bpy.context.window_manager.UAS_vse_render
    props = config.getAddonProps(scene)
    vsm_props = scene.UAS_vsm_props

    # if not len(config.gMontageOtio.sequencesList):
    #     return {"CANCELLED"}

    # selSeq = config.gMontageOtio.sequencesList[int(self.sequenceList)]

    # selSeq.printInfo()

    sequenceClip = None
    # sequenceName = bpy.data.scenes[0].name
    # wkip mettre un RE match ici
    act = sequenceName[0:5]
    filePath = (
        r"C:\_UAS_ROOT\RRSpecial\05_Acts\\" + act + r"\\" + sequenceName + r"\Shots\Main_Take\\" + sequenceName + ".mp4"
    )

    print(f" *** Seq filePath: {filePath}")

    importSequenceAtFrame = 0

    # find if a marker exists with the name of the first shot
    markers = utils_markers.sortMarkers(scene.timeline_markers, sequenceName)
    if len(markers):
        # if firstShotMarker is not None:
        importSequenceAtFrame = markers[0].frame

    if not Path(filePath).exists():
        print(f" *** Sequence video file not found: {Path(filePath)}")
    else:
        sequence_AudioTrack_name = f"{sequenceName} (audio)"
        sequence_VideoTrack_name = f"{sequenceName} (video)"
        sequence_AudioTrack = None
        sequence_VideoTrack = None

        channelInd = 2

        sequence_AudioTrack = vsm_props.getTrackByName(sequence_AudioTrack_name)
        if sequence_AudioTrack is not None:
            sequence_AudioTrack.clearContent()
        sequence_VideoTrack = vsm_props.getTrackByName(sequence_VideoTrack_name)
        if sequence_VideoTrack is not None:
            sequence_VideoTrack.clearContent()

        channelInd_audio = channelInd + 1
        importSound = True
        if importSound:
            # create audio clip
            if sequence_AudioTrack is not None:
                channelInd_audio = vsm_props.getTrackIndex(sequence_AudioTrack)
            sequenceAudioClip = vse_render.createNewClip(
                scene,
                filePath,
                channelInd=channelInd_audio,
                atFrame=importSequenceAtFrame,
                importVideo=False,
                importAudio=True,
                clipName=sequence_AudioTrack_name,
            )
            vsm_props.updateTracksList(scene)
            sequence_AudioTrack = vsm_props.setTrackInfo(
                channelInd_audio,
                trackType="AUDIO",
                name=sequence_AudioTrack_name,
            )

        # create video clip
        channelInd_video = channelInd + 1
        if sequence_AudioTrack is not None:
            channelInd_video = channelInd_audio + 1

        if sequence_VideoTrack is not None:
            channelInd_video = vsm_props.getTrackIndex(sequence_VideoTrack)

        sequenceClip = vse_render.createNewClip(
            scene,
            filePath,
            channelInd=channelInd_video,
            atFrame=importSequenceAtFrame,
            importAudio=False,
            clipName=sequence_VideoTrack_name,
        )

        if sequenceClip is not None:
            res_x = 1280
            res_y = 960
            vse_render.cropClipToCanvas(
                res_x,
                res_y,
                sequenceClip,
                1280,
                960,
                mode="FIT_WIDTH",
            )

            scene.sequence_editor.active_strip = sequenceClip

        # vsm_props.addTrack(atIndex=3, trackType="STANDARD", name="Sequence", color=(0.5, 0.4, 0.6, 1))
        vsm_props.updateTracksList(scene)
        sequence_VideoTrack = vsm_props.setTrackInfo(
            channelInd_video,
            trackType="VIDEO",
            name=sequence_VideoTrack_name,
        )
        vsm_props.setSelectedTrackByIndex(channelInd_video)

    # works on selection
    #  bpy.ops.sequencer.set_range_to_strips(preview=False)

    bpy.ops.sequencer.select_all(action="DESELECT")

    if sequenceClip is not None:
        sequenceClip.select = True
    # scene.sequence_editor.sequences[2].select = Tru

    scene.frame_set(importSequenceAtFrame)

    # wkip works but applies the modifs on every sequence editor occurence of the file
    edSeqWksp = bpy.data.workspaces["Video Editing"]
    for screen in edSeqWksp.screens:
        #   print(f"Screen type: {screen.name}")
        for area in screen.areas:
            #      print(f"Area type: {area.type}")
            if area.type == "SEQUENCE_EDITOR":
                #         print("Area seq ed")
                override = bpy.context.copy()
                override["area"] = area
                override["region"] = area.regions[-1]

                bpy.ops.sequencer.view_selected(override)
                # bpy.context.space_data.show_seconds = False


def rrs_playblast_to_vsm(playblastInfo=None, editVideoFile=None, otioFile=None, montageOtio=None, importMarkers=True):
    print("\n ********************** \n rrs_playblast_to_vsm\n")

    if playblastInfo is not None:
        print(f"playblastInfo dict:")
        for k, v in playblastInfo.items():
            print(f"  {k}: {v}")

    scene = utils.getSceneVSE("SM_CheckSequence", createVseTab=True)
    bpy.context.window.workspace = bpy.data.workspaces["Video Editing"]

    vse_render = bpy.context.window_manager.UAS_vse_render
    props = config.getAddonProps(scene)
    vsm_props = scene.UAS_vsm_props

    editVideoFile = editVideoFile
    if editVideoFile is None:
        editVideoFile = r"C:\_UAS_ROOT\RRSpecial\05_Acts\Act01\_Montage\Act01_Edit_Previz.mp4"
    if otioFile is None:
        otioFile = r"C:\_UAS_ROOT\RRSpecial\05_Acts\Act01\_Montage\Act01_Edit_Previz.xml"
    importMarkers = importMarkers

    if vsm_props.getTrackByName("Previz_Edit (video)") is None:
        rrs_animatic_to_vsm(
            editVideoFile=editVideoFile, otioFile=otioFile, montageOtio=montageOtio, importMarkers=importMarkers
        )

    ############################################
    ############################################

    # playblast
    playblastClip = None
    # filePath = props.renderRootPath
    # if not filePath.endswith("\\") and not filePath.endswith("/"):
    #     filePath += "\\"
    # filePath += f"_playblast_.{props.getOutputFileFormat()}"
    # filePath = bpy.path.abspath(filePath)

    filePath = playblastInfo["outputFullPath"]
    importPlayblastAtFrame = playblastInfo["startFrameInEdit"]

    # find if a marker exists with the name of the first shot
    firstShotMarker = utils_markers.getMarkerbyName(scene, playblastInfo["startShotName"])
    if firstShotMarker is not None:
        importPlayblastAtFrame = firstShotMarker.frame

    print(f"Playblast filepath: {filePath}")
    if not Path(filePath).exists():
        print(f" *** Playblast video file not found: {Path(filePath)}")
    else:
        playblast_AudioTrack_name = f'Playblast {playblastInfo["scene"]} (audio)'
        playblast_VideoTrack_name = f'Playblast {playblastInfo["scene"]} (video)'
        playblast_AudioTrack = None
        playblast_VideoTrack = None

        channelInd = 4

        playblast_AudioTrack = vsm_props.getTrackByName(playblast_AudioTrack_name)
        if playblast_AudioTrack is not None:
            playblast_AudioTrack.clearContent()
        playblast_VideoTrack = vsm_props.getTrackByName(playblast_VideoTrack_name)
        if playblast_VideoTrack is not None:
            playblast_VideoTrack.clearContent()

        channelInd_audio = channelInd + 1
        if playblastInfo["renderSound"]:
            # create audio clip
            if playblast_AudioTrack is not None:
                channelInd_audio = vsm_props.getTrackIndex(playblast_AudioTrack)
            playblastAudioClip = vse_render.createNewClip(
                scene,
                filePath,
                channelInd=channelInd_audio,
                atFrame=importPlayblastAtFrame,
                importVideo=False,
                importAudio=True,
                clipName=playblast_AudioTrack_name,
            )
            vsm_props.updateTracksList(scene)
            playblast_AudioTrack = vsm_props.setTrackInfo(
                channelInd_audio,
                trackType="AUDIO",
                name=playblast_AudioTrack_name,
                color=(0.6, 0.4, 0.4, 1),
            )

        # create video clip
        channelInd_video = channelInd + 1
        if playblast_AudioTrack is not None:
            channelInd_video = channelInd_audio + 1

        if playblast_VideoTrack is not None:
            channelInd_video = vsm_props.getTrackIndex(playblast_VideoTrack)

        playblastClip = vse_render.createNewClip(
            scene,
            filePath,
            channelInd=channelInd_video,
            atFrame=importPlayblastAtFrame,
            importAudio=False,
            clipName=playblast_VideoTrack_name,
        )

        if playblastClip is not None:
            res_x = 1280
            res_y = 960
            vse_render.cropClipToCanvas(
                res_x,
                res_y,
                playblastClip,
                playblastInfo["resolution_x"],
                playblastInfo["resolution_y"],
                clipRenderPercentage=playblastInfo["render_percentage"],
                mode="FIT_WIDTH",
            )

            scene.sequence_editor.active_strip = playblastClip

        # vsm_props.addTrack(atIndex=3, trackType="STANDARD", name="Playblast", color=(0.5, 0.4, 0.6, 1))
        vsm_props.updateTracksList(scene)
        playblast_VideoTrack = vsm_props.setTrackInfo(
            channelInd_video,
            trackType="VIDEO",
            name=playblast_VideoTrack_name,
            color=(0.6, 0.3, 0.3, 1),
        )
        vsm_props.setSelectedTrackByIndex(channelInd_video)

    # works on selection
    #  bpy.ops.sequencer.set_range_to_strips(preview=False)

    bpy.ops.sequencer.select_all(action="DESELECT")

    if playblastClip is not None:
        playblastClip.select = True
    # scene.sequence_editor.sequences[2].select = Tru

    scene.frame_set(importPlayblastAtFrame)
    #  bpy.ops.sequencer.view_frame()
    # bpy.context.window.workspace = bpy.data.workspaces["Video Editing"]

    #    bpy.ops.workspace.append_activate(idname="Video Editing")

    #  utils_vse.showSecondsInVSE(False, workspace=bpy.context.workspace)
    utils_vse.showSecondsInVSE(False, workspace=bpy.data.workspaces["Video Editing"])

    # wkip works but applies the modifs on every sequence editor occurence of the file
    edSeqWksp = bpy.data.workspaces["Video Editing"]
    for screen in edSeqWksp.screens:
        #   print(f"Screen type: {screen.name}")
        for area in screen.areas:
            #      print(f"Area type: {area.type}")
            if area.type == "SEQUENCE_EDITOR":
                #         print("Area seq ed")
                override = bpy.context.copy()
                override["area"] = area
                override["region"] = area.regions[-1]

                bpy.ops.sequencer.view_selected(override)
                # bpy.context.space_data.show_seconds = False

    ################
    # video settings
    ################

    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.constant_rate_factor = "PERC_LOSSLESS"  # "PERC_LOSSLESS"
    scene.render.ffmpeg.gopsize = 5  # keyframe interval
    scene.render.ffmpeg.audio_codec = "AAC"

    #       scene.render.filepath = output_filepath
    scene.render.use_file_extension = False

    vsm_props.jumpToScene = bpy.data.scenes[playblastInfo["scene"]]

    # scene.render.resolution_percentage = 75

    return
