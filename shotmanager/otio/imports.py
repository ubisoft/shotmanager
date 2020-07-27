from pathlib import Path

import bpy
import opentimelineio

from ..utils.utils import getSceneVSE


def importOtio(
    scene,
    otioFile,
    importAtFrame=0,
    reformatShotNames=False,
    createCameras=True,
    useMediaAsCameraBG=False,
    mediaHaveHandles=False,
    mediaHandlesDuration=0,
):
    # filePath="", fileName=""):

    print("Import Otio File: ", otioFile)

    props = context.scene.UAS_shot_manager_props
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
                            clipName = context.scene.UAS_shot_manager_props.new_shot_prefix + match.group(1)

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
                context.scene.frame_start = importAtFrame
                context.scene.frame_end = (
                    opentimelineio.opentime.to_frames(clip.range_in_parent().end_time_inclusive()) + importAtFrame
                )

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
    print("Son")

    # creation VSE si existe pas
    getSceneVSE(scene.name)

    # ajout par pistes
