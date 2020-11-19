from pathlib import Path

import bpy

from shotmanager.utils import utils
from shotmanager.config import config

from shotmanager.rrs_specific.montage.montage_otio import MontageOtio


def rrs_playblast_to_vsm(playblastInfo=None, editVideoFile=None, otioFile=None, montageOtio=None, importMarkers=True):
    print("\n ********************** \n rrs_playblast_to_vsm\n")

    if playblastInfo is not None:
        print(f"playblastInfo dict:")
        for k, v in playblastInfo.items():
            print(f"  {k}: {v}")

    scene = utils.getSceneVSE("VideoShotManger", createVseTab=True)
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

    importMarkers = False
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
    vsm_props.setTrackInfo(channelInd, trackType="STANDARD", name="Previz_Edit (video)", color=(0.1, 0.2, 0.8, 1))

    # audio
    channelInd = 1
    editAudioClip = vse_render.createNewClip(
        scene, editVideoFile, channelInd=channelInd, atFrame=0, importVideo=False, importAudio=True
    )
    # vsm_props.addTrack(atIndex=2, trackType="STANDARD", name="Previz_Edit (audio)", color=(0.1, 0.5, 0.2, 1))
    vsm_props.updateTracksList(scene)
    vsm_props.setTrackInfo(channelInd, trackType="STANDARD", name="Previz_Edit (audio)", color=(0.1, 0.5, 0.2, 1))

    # if self.useOverlayFrame:
    #     overlayClip = vse_render.createNewClip(scene, self.overlayFile, 2, 0, offsetEnd=-60000)
    #     scene.sequence_editor.sequences_all[overlayClip.name].blend_type = "ALPHA_OVER"

    # playblast
    playblastClip = None
    # filePath = props.renderRootPath
    # if not filePath.endswith("\\") and not filePath.endswith("/"):
    #     filePath += "\\"
    # filePath += f"_playblast_.{props.getOutputFileFormat()}"
    # filePath = bpy.path.abspath(filePath)

    filePath = playblastInfo["outputFullPath"]
    importPlayblastAtFrame = playblastInfo["startFrameInEdit"]

    print(f"Playblast filepath: {filePath}")
    if not Path(filePath).exists():
        print("Playblast Clip not found")
    else:
        channelInd = 3
        playblastClip = vse_render.createNewClip(
            scene,
            filePath,
            channelInd=channelInd,
            atFrame=importPlayblastAtFrame,
            importAudio=False,
            clipName=f'Playblast {playblastInfo["scene"]}',
        )

        if playblastClip is not None:
            playblastClip.use_crop = True
            playblastClip.crop.min_x = -1 * int((1280 - playblastInfo["resolution_x"]) / 2)
            playblastClip.crop.max_x = playblastClip.crop.min_x
            playblastClip.crop.min_y = -1 * int((960 - playblastInfo["resolution_y"]) / 2)
            playblastClip.crop.max_y = playblastClip.crop.min_y

        # vsm_props.addTrack(atIndex=3, trackType="STANDARD", name="Playblast", color=(0.5, 0.4, 0.6, 1))
        vsm_props.updateTracksList(scene)
        vsm_props.setTrackInfo(channelInd, trackType="STANDARD", name="Playblast", color=(0.5, 0.4, 0.6, 1))
        vsm_props.setSelectedTrackByIndex(channelInd)

    # works on selection
    bpy.ops.sequencer.set_range_to_strips(preview=False)

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

