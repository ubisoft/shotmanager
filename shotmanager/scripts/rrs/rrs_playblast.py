from pathlib import Path

import bpy

from shotmanager.utils import utils
from shotmanager.config import config

from shotmanager.rrs_specific.montage.montage_otio import MontageOtio


def rrs_animatic_to_vsm(editVideoFile=None, otioFile=None, montageOtio=None, importMarkers=True):
    scene = utils.getSceneVSE("RRS_CheckSequence", createVseTab=True)
    bpy.context.window.workspace = bpy.data.workspaces["Video Editing"]

    vse_render = bpy.context.window_manager.UAS_vse_render
    props = scene.UAS_shot_manager_props
    vsm_props = scene.UAS_vsm_props

    editVideoFile = editVideoFile
    if editVideoFile is None:
        editVideoFile = r"C:\_UAS_ROOT\RRSpecial\05_Acts\Act01\_Montage\Act01_Edit_Previz.mp4"
    if otioFile is None:
        otioFile = r"C:\_UAS_ROOT\RRSpecial\05_Acts\Act01\_Montage\Act01_Edit_Previz.xml"
    importMarkers = importMarkers

    # if config.uasDebug:
    #        importMarkers = False

    # vsm_props.updateTracksList(scene)

    #    bpy.context.space_data.show_seconds = False
    scene.frame_start = 0
    scene.frame_end = 40000
    if props.use_project_settings:
        # scene.render.image_settings.file_format = props.project_images_output_format
        scene.render.fps = props.project_fps
        scene.render.resolution_x = props.project_resolution_framed_x
        scene.render.resolution_y = props.project_resolution_framed_y

    scene.render.fps = 25
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960

    # projectFps = scene.render.fps
    # sequenceFileName = props.renderShotPrefix() + takeName
    # scene.use_preview_range = False
    # renderResolution = [scene.render.resolution_x, scene.render.resolution_y]
    # renderResolutionFramed = [scene.render.resolution_x, scene.render.resolution_y]

    # # override local variables with project settings
    # if props.use_project_settings:
    #     props.applyProjectSettings()
    #     scene.render.image_settings.file_format = props.project_images_output_format
    #     projectFps = scene.render.fps
    #     sequenceFileName = props.renderShotPrefix()
    #     renderResolution = [props.project_resolution_x, props.project_resolution_y]
    #     renderResolutionFramed = [props.project_resolution_framed_x, props.project_resolution_framed_y]

    # clear all
    # vsm_props.clear_all()
    # wkip a remplacer par des fonctions
    bpy.ops.uas_video_shot_manager.clear_markers()
    bpy.ops.uas_video_shot_manager.clear_clips()
    bpy.ops.uas_video_shot_manager.remove_multiple_tracks(action="ALL")

    # video
    channelInd = 2
    editVideoClip = vse_render.createNewClip(scene, editVideoFile, channelInd=channelInd, atFrame=0, importAudio=False)
    # vsm_props.addTrack(atIndex=1, trackType="STANDARD", name="Previz_Edit (video)", color=(0.1, 0.2, 0.8, 1))
    vsm_props.updateTracksList(scene)
    vsm_props.setTrackInfo(channelInd, trackType="VIDEO", name="Previz_Edit (video)")

    # audio
    channelInd = 1
    editAudioClip = vse_render.createNewClip(
        scene, editVideoFile, channelInd=channelInd, atFrame=0, importVideo=False, importAudio=True
    )
    # vsm_props.addTrack(atIndex=2, trackType="STANDARD", name="Previz_Edit (audio)", color=(0.1, 0.5, 0.2, 1))
    vsm_props.updateTracksList(scene)
    vsm_props.setTrackInfo(channelInd, trackType="AUDIO", name="Previz_Edit (audio)")

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
            # config.gMontageOtio
            config.gMontageOtio = None
            if importMarkers and "" != otioFile and Path(otioFile).exists():
                config.gMontageOtio = MontageOtio()
                config.gMontageOtio.fillMontageInfoFromOtioFile(
                    otioFile=otioFile, refVideoTrackInd=1, verboseInfo=False
                )

                config.gSeqEnumList = list()
                print(f"config.gMontageOtio name: {config.gMontageOtio.get_name()}")
                for i, seq in enumerate(config.gMontageOtio.sequencesList):
                    print(f"- seqList: i:{i}, seq: {seq.get_name()}")
                    config.gSeqEnumList.append((str(i), seq.get_name(), f"Import sequence {seq.get_name()}", i + 1))
            montageOtio = config.gMontageOtio

        for i, seq in enumerate(montageOtio.get_sequences()):
            print(f"seq name: {seq.get_name()}")
            for j, sh in enumerate(seq.getEditShots()):
                print(
                    f"    shot name: {sh.get_name()}, starts at: {sh.get_frame_final_start()}"
                )  # , from media {sh.get_med}
                marker_name = Path(sh.get_name()).stem
                scene.timeline_markers.new(marker_name, frame=sh.get_frame_final_start())

                # last marker
                if len(montageOtio.get_sequences()) - 1 == i and len(seq.getEditShots()) - 1 == j:
                    scene.timeline_markers.new("Edit End", frame=sh.get_frame_final_end())


def rrs_playblast_to_vsm(playblastInfo=None, editVideoFile=None, otioFile=None, montageOtio=None, importMarkers=True):
    print("\n ********************** \n rrs_playblast_to_vsm\n")

    if playblastInfo is not None:
        print(f"playblastInfo dict:")
        for k, v in playblastInfo.items():
            print(f"  {k}: {v}")

    scene = utils.getSceneVSE("RRS_CheckSequence", createVseTab=True)
    bpy.context.window.workspace = bpy.data.workspaces["Video Editing"]

    vse_render = bpy.context.window_manager.UAS_vse_render
    props = scene.UAS_shot_manager_props
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
    firstShotMarker = utils.getMarkerbyName(scene, playblastInfo["startShotName"])
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

        channelInd = 2

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
                channelInd_audio, trackType="AUDIO", name=playblast_AudioTrack_name, color=(0.1, 0.5, 0.2, 1),
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
            channelInd_video, trackType="VIDEO", name=playblast_VideoTrack_name, color=(0.6, 0.3, 0.3, 1),
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
    # bpy.ops.sequencer.view_selected()

    ################
    # create tracks
    ################
    #  self.addTrack(trackType="STANDARD",)

    ################
    # update
    ################
    #      vsm_props.updateTracksList(scene)

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

    # scene.render.resolution_percentage = 75.0

    return

