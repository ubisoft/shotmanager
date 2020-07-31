import logging

from pathlib import Path
from urllib.parse import unquote_plus, urlparse
import re

import bpy
import opentimelineio

from ..utils import utils

_logger = logging.getLogger(__name__)


def createShotsFromOtio(
    scene,
    otioFile,
    importAtFrame=0,
    reformatShotNames=False,
    createCameras=True,
    useMediaAsCameraBG=False,
    mediaHaveHandles=False,
    mediaHandlesDuration=0,
    importSoundInVSE=True,
):
    # filePath="", fileName=""):

    print("Import Otio File: ", otioFile)
    from random import uniform
    from math import radians

    props = scene.UAS_shot_manager_props
    if len(props.getCurrentTake().getShotList()) != 0:
        bpy.ops.uas_shot_manager.add_take(name=Path(otioFile).stem)

    try:
        timeline = opentimelineio.adapters.read_from_file(otioFile)
        if len(timeline.video_tracks()):
            track = timeline.video_tracks()[0]  # Assume the first one contains the shots.

            cam = None
            if not createCameras:  # Create Default Camera
                # bpy.ops.object.camera_add(location=[0, 0, 0], rotation=[0, 0, 0])  # doesn't return a cam...
                cam = bpy.data.cameras.new("Camera")
                cam_ob = bpy.data.objects.new(cam.name, cam)
                bpy.context.collection.objects.link(cam_ob)
                bpy.data.cameras[cam.name].lens = 40
                cam_ob.location = (0.0, 0.0, 0.0)
                cam_ob.rotation_euler = (radians(90), 0.0, radians(90))

            shot_re = re.compile(r"sh_?(\d+)", re.IGNORECASE)
            for i, clip in enumerate(track.each_clip()):
                clipName = clip.name
                if createCameras:
                    if reformatShotNames:
                        match = shot_re.search(clipName)
                        if match:
                            clipName = scene.UAS_shot_manager_props.new_shot_prefix + match.group(1)

                    cam = bpy.data.cameras.new("Cam_" + clipName)
                    cam_ob = bpy.data.objects.new(cam.name, cam)
                    bpy.context.collection.objects.link(cam_ob)
                    bpy.data.cameras[cam.name].lens = 40
                    cam_ob.color = [uniform(0, 1), uniform(0, 1), uniform(0, 1), 1]
                    cam_ob.location = (0.0, i, 0.0)
                    cam_ob.rotation_euler = (radians(90), 0.0, radians(90))

                    # add media as camera background
                    if useMediaAsCameraBG:
                        print("Import Otio clip.media_reference.target_url: ", clip.media_reference.target_url)
                        media_path = Path(utils.file_path_from_uri(clip.media_reference.target_url))
                        print("Import Otio media_path: ", media_path)
                        if not media_path.exists():
                            # Lets find it inside next to the xml
                            media_path = Path(otioFile).parent.joinpath(media_path.name)
                            print("** not found, so Path(self.otioFile).parent: ", Path(otioFile).parent)
                            print("   and new media_path: ", media_path)

                        handlesDuration = 0
                        if mediaHaveHandles:
                            handlesDuration = mediaHandlesDuration

                        # start frame of the background video is not set here since it will be linked to the shot start frame
                        utils.add_background_video_to_cam(
                            cam, str(media_path), 0, alpha=props.shotsGlobalSettings.backgroundAlpha
                        )

                shot = props.addShot(
                    name=clipName,
                    start=opentimelineio.opentime.to_frames(clip.range_in_parent().start_time) + importAtFrame,
                    end=opentimelineio.opentime.to_frames(clip.range_in_parent().end_time_inclusive()) + importAtFrame,
                    camera=cam_ob,
                    color=cam_ob.color,  # (cam_ob.color[0], cam_ob.color[1], cam_ob.color[2]),
                )
                # bpy.ops.uas_shot_manager.add_shot(
                #     name=clipName,
                #     start=opentimelineio.opentime.to_frames(clip.range_in_parent().start_time) + importAtFrame,
                #     end=opentimelineio.opentime.to_frames(clip.range_in_parent().end_time_inclusive()) + importAtFrame,
                #     cameraName=cam.name,
                #     color=(cam_ob.color[0], cam_ob.color[1], cam_ob.color[2]),
                # )
                shot.bgImages_linkToShotStart = True
                shot.bgImages_offset = -1 * handlesDuration

                # wkip maybe to remove
                scene.frame_start = importAtFrame
                scene.frame_end = (
                    opentimelineio.opentime.to_frames(clip.range_in_parent().end_time_inclusive()) + importAtFrame
                )

            if importSoundInVSE:
                # creation VSE si existe pas
                vse = utils.getSceneVSE(scene.name)
                # bpy.context.space_data.show_seconds = False
                bpy.context.window.workspace = bpy.data.workspaces["Video Editing"]
                importOtioToVSE(otioFile, vse, importAtFrame=importAtFrame, importVideoTracks=False)

    except opentimelineio.exceptions.NoKnownAdapterForExtensionError:
        from ..utils.utils import ShowMessageBox

        ShowMessageBox("File not recognized", f"{otioFile} could not be understood by Opentimelineio", "ERROR")


def importSound(
    scene,
    otioFile,
    importAtFrame=0,
    reformatShotNames=False,
    createCameras=True,
    useMediaAsCameraBG=False,
    mediaHaveHandles=False,
    mediaHandlesDuration=0,
):
    print("Son ************* Deprecated to delete")

    # creation VSE si existe pas
    vse = utils.getSceneVSE(scene.name)
    # bpy.context.space_data.show_seconds = False
    bpy.context.window.workspace = bpy.data.workspaces["Video Editing"]
    # bpy.context.window.space_data.show_seconds = False

    importOtioToVSE(otioFile, vse, importAtFrame=50, importVideoTracks=True, importAudioTracks=True)

    # ajout par pistes


def importOtioToVSE(otioFile, vse, importAtFrame=0, importVideoTracks=True, importAudioTracks=True):
    print("Import Otio File to VSE: ", importOtioToVSE)

    import opentimelineio

    def importAudioTrack(track, trackInd, importAtFrame):
        for i, clip in enumerate(track.each_clip()):
            clipName = clip.name
            print("   Clip name: ", clipName)
            print("   Clip ind: ", i)

            print("Import Otio clip.media_reference.target_url: ", clip.media_reference.target_url)
            media_path = Path(utils.file_path_from_uri(clip.media_reference.target_url))
            print("Import Otio media_path: ", media_path)
            print("  Import at frame: ", importAtFrame)
            if not media_path.exists():
                # Lets find it inside next to the xml
                media_path = Path(otioFile).parent.joinpath(media_path.name)
                print("** not found, so Path(self.otioFile).parent: ", Path(otioFile).parent)
                print("   and new media_path: ", media_path)

            if media_path.exists():
                media_path = str(media_path)

                # local clip infos:

                _logger.info("Logger info")
                _logger.warning(f"logger warning")
                _logger.error("logger error")

                start = opentimelineio.opentime.to_frames(clip.range_in_parent().start_time) + importAtFrame
                end = opentimelineio.opentime.to_frames(clip.range_in_parent().end_time_inclusive()) + importAtFrame
                duration = opentimelineio.opentime.to_frames(clip.available_range().end_time_inclusive())

                # local clip infos:
                otio_clipSourceRange = clip.source_range
                # clip cut in in local clip time ref (= relatively to clip start)
                otio_clipLocalCutStart = opentimelineio.opentime.to_frames(clip.source_range.start_time)
                # clip cut out in local clip time ref (= relatively to clip start)
                otio_clipLocalCutEnd = None  # opentimelineio.opentime.to_frames(clip.source_range.end_time())
                otio_clipLocalCutEndInclus = opentimelineio.opentime.to_frames(clip.source_range.end_time_inclusive())
                print(
                    f"\n   otio_clipSourceRange: {otio_clipSourceRange}, otio_clipLocalCutStart: {otio_clipLocalCutStart}, otio_clipLocalCutEnd: {otio_clipLocalCutEnd}, otio_clipLocalCutEndInclus: {otio_clipLocalCutEndInclus}"
                )

                trucSourceRangeEnd = opentimelineio.opentime.to_frames(clip.source_range.end_time_inclusive())
                trimmedClipDuration = opentimelineio.opentime.to_frames(clip.duration())
                print(
                    f"   start: {start}, end: {end}, duration: {duration}, trimmedClipDuration: {trimmedClipDuration}, otio_clipSourceRange: {otio_clipSourceRange}, trucSourceRangeEnd: {trucSourceRangeEnd}"
                )
                print("otio_clipSourceRange[0][0]: ", otio_clipSourceRange.start_time)
                print(
                    "otio_clipSourceRange[0][0]: ", opentimelineio.opentime.to_frames(otio_clipSourceRange.start_time)
                )
                # print(f"   range_from_start_end_time: {clip.range_in_parent().range_from_start_end_time()}")
                bpy.context.window_manager.UAS_vse_render.createNewClip(
                    bpy.context.scene,
                    media_path,
                    trackInd,
                    start - otio_clipLocalCutStart,
                    offsetStart=otio_clipLocalCutStart,
                    trimmedClipDuration=trimmedClipDuration,
                )

        pass

    #        try:
    timeline = opentimelineio.adapters.read_from_file(otioFile)
    # if len(timeline.video_tracks()):
    #     track = timeline.video_tracks()[0]  # Assume the first one contains the shots.

    # audio
    if importAudioTracks:
        for trackInd, editTrack in enumerate(timeline.audio_tracks()):
            print(f"\nChannel Name: {editTrack.name}, {trackInd}")
            importAudioTrack(editTrack, trackInd + 1, importAtFrame)


def import_otio(scene, filepath, old_dir, new_dir):
    old_dir = old_dir.replace("\\", "/")
    new_dir = new_dir.replace("\\", "/")
    if not scene.sequence_editor:
        scene.sequence_editor_create()
    seq_editor = scene.sequence_editor

    timeline = opentimelineio.adapters.read_from_file(filepath)
    bad_file_uri_check = re.compile(
        r"^/\S:.*"
    )  # file uri parsing on windows can result in a leading / in front of the drive letter.

    for i, track in enumerate(timeline.tracks):
        track_kind = track.kind

        for clip in track.each_clip():
            media_path = unquote_plus(urlparse(clip.media_reference.target_url).path).replace("\\", "//")

            head, tail = os.path.split(media_path)
            media_path = new_dir + tail
            print("media_path: ", media_path)

            # if bad_file_uri_check.match(media_path):  # Remove leading /
            #     media_path = media_path[1:]
            # media_path = media_path.replace(old_dir, new_dir)

            # print("media_path: ", media_path)
            # media_path = Path(media_path)
            if not Path(media_path).exists():
                print(f"Could not be find {media_path}.")
            #     continue

            # if track_kind == "Video":
            #     c = seq_editor.sequences.new_movie(
            #         clip.name, str(media_path), i, opentimelineio.opentime.to_frames(clip.range_in_parent().start_time)
            #     )
            #     c.frame_final_duration = opentimelineio.opentime.to_frames(clip.duration())

            elif track_kind == "Audio":
                c = seq_editor.sequences.new_sound(
                    clip.name, str(media_path), i, opentimelineio.opentime.to_frames(clip.range_in_parent().start_time)
                )
                c.frame_final_duration = opentimelineio.opentime.to_frames(clip.duration())

