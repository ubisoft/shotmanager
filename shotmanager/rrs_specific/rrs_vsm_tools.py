import os
from pathlib import Path
import shutil
from stat import S_IMODE, S_IWRITE


import bpy
from bpy.types import Operator, Panel
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty

from shotmanager.config import config
from shotmanager.utils import utils, utils_vse

from shotmanager.rrs_specific.montage.montage_otio import MontageOtio
from shotmanager.scripts.rrs import utils_rrs


from shotmanager.scripts.rrs.rrs_playblast import (
    rrs_playblast_to_vsm,
    rrs_animatic_to_vsm,
    rrs_sequence_to_vsm,
    getSoundFilesForEachShot,
    importShotMarkersFromMontage,
)

import logging

_logger = logging.getLogger(__name__)


######
# RRS VSE panel #
######


class UAS_PT_RRSVSMTools(Panel):
    bl_idname = "UAS_PT_RRSVSMTools"
    bl_label = "RR Special VSE Tools"
    bl_description = "RRS Options"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_category = "UAS Video Shot Man"
    #  bl_parent_id = "UAS_PT_Video_Shot_Manager"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        val = not (
            scene.name.startswith("Act01_Seq")
            or scene.name.startswith("Act02_Seq")
            or scene.name.startswith("Act03_Seq")
        )
        return val

    def draw(self, context):
        scene = context.scene
        vsm_props = scene.UAS_vsm_props
        layout = self.layout

        #########################################
        # RRS Specific
        #########################################

        layout.separator(factor=1)

        # wkip conditions dégueu
        if not (
            scene.name.startswith("Act01_Seq")
            or scene.name.startswith("Act02_Seq")
            or scene.name.startswith("Act03_Seq")
        ):
            layout.label(text="RR-Special: Visual Check:")
            box = layout.box()
            box.separator(factor=0.2)
            row = box.row()
            row.scale_y = 1
            row.operator("uas_video_shot_manager.rrs_check_sequence", text="Import Previz Montage Act 01")
            row.label(text="On Tracks 1 (audio) and 2 (video)")

            if (
                not (
                    bpy.data.scenes[0].name.startswith("Act01_Seq")
                    or bpy.data.scenes[0].name.startswith("Act02_Seq")
                    or bpy.data.scenes[0].name.startswith("Act03_Seq")
                )
                or "RRS_CheckSequence" == scene.name
            ):
                box.separator(factor=0.1)
                row = box.row()
                row.operator("uas_video_shot_manager.import_published_sequence")
                row.label(text="On Tracks 3 (audio) and 4 (video)")
                layout.separator()

            if (
                bpy.data.scenes[0].name.startswith("Act01_Seq")
                or bpy.data.scenes[0].name.startswith("Act02_Seq")
                or bpy.data.scenes[0].name.startswith("Act03_Seq")
            ) and bpy.data.scenes[0] is not scene:
                row = layout.row()
                row.scale_y = 1.4
                row.operator(
                    "uas_video_shot_manager.go_to_sequence_scene", text="Go to Sequence Scene", icon="SCENE_DATA"
                ).sceneName = bpy.data.scenes[0].name

            box.label(text="Playblast Tracks: 5 (audio) and 6 (video)")
            box.separator(factor=0.2)

        # layout.separator(factor=1)

        # act 2 and 3
        layout.label(text="Exports videos for Act 02 and Act 03:")
        box = layout.box()
        row = box.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"

        row = box.row()
        row.prop(vsm_props, "actToExport_Predec")
        row.operator("uas_video_shot_manager.open_export_doc_page")

        row = box.row()
        row.scale_y = 1
        row.operator(
            "uas_video_shot_manager.rrs_check_sequence", text="Import Predec Animatic"
        ).mode = vsm_props.actToExport_Predec
        row.label(text="On Tracks 1 (audio) and 2 (video)")
        box.separator(factor=0.2)

        row = box.row()
        row.operator(
            "uas_video_shot_manager.export_animatic_videos_and_publish", text="Export Predec Shots"
        ).mode = vsm_props.actToExport_Predec
        box.separator(factor=0.3)

        ##################
        row = box.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        #   row.operator("uas_video_shot_manager.rrs_export_sounds_per_shot")

        layout.label(text="For Montages and Confos:")
        box = layout.box()
        row = box.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator(
            "uas_video_shot_manager.export_content_between_markers", text="   Export Shots Between Markers..."
        ).outputDir = r"C:\_UAS_ROOT\RRSpecial\05_Acts\Act01\_Montage\_OutputShots"

        layout.separator(factor=1)


class UAS_VideoShotManager_OT_RRSExportAnimaticVideosAndPublish(Operator):
    bl_idname = "uas_video_shot_manager.export_animatic_videos_and_publish"
    bl_label = "Export Animatic Videos"
    bl_description = "Export all the segments defined by the markers as separated videos"
    bl_options = {"INTERNAL"}

    # can be ACT01_PREDEC, ACT02_PREDEC, ACT03_PREDEC
    mode: StringProperty(default="")

    start: IntProperty(name="Start", default=10)
    end: IntProperty(name="end", default=150)

    exportAnimatic: BoolProperty(
        name="Export Predec Animatic to 05_Acts/_Montage/Act0X_Edit_Previz.mp4",
        description="Export Predec Animatic to 05_Acts/_Montage/Act0X_Edit_Previz.mp4",
        default=True,
    )
    exportAsVideoFiles: BoolProperty(
        name="Export Shots Video Files to 05_Acts/Act0X/Act0X_Seq0---/Predec_Shots/Main_Take/", default=True
    )
    # 05_Acts/_Montage/Shots/

    exportVideosWithSound: BoolProperty(name="With Sound File", default=True)
    exportAsAudioFiles: BoolProperty(name="Export as Audio Files", default=False)
    exportEditSoundtracks: BoolProperty(
        name="Export Each Mixed Down Sound Track per Shot to 05_Acts/_Montage/_Exports/", default=True
    )
    exportToGattaca: BoolProperty(name="Export Shot Videos and Infos to Gattaca", default=True)

    def invoke(self, context, event):

        self.start = context.scene.frame_start
        self.end = context.scene.frame_end

        wm = context.window_manager
        wm.invoke_props_dialog(self, width=500)
        return {"RUNNING_MODAL"}

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "start")
        row.prop(self, "end")

        row = layout.row()
        row.prop(self, "exportAnimatic")

        row = layout.row()
        row.prop(self, "exportAsVideoFiles")
        #  row.prop(self, "exportVideosWithSound")
        # row = layout.row()
        # row.prop(self, "exportAsAudioFiles")
        row = layout.row()
        row.prop(self, "exportEditSoundtracks")

        layout.separator()
        row = layout.row()
        row.prop(self, "exportToGattaca")

    def execute(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props
        vsm_props = scene.UAS_vsm_props
        vse_render = bpy.context.window_manager.UAS_vse_render

        ActIndStr = self.mode[3:5]
        print(f"*** Act {ActIndStr}")

        allShotsOutput = f"C:/_UAS_ROOT/RRSpecial/05_Acts/Act{ActIndStr}/_Montage/Shots"

        ######
        # Export video
        # wkip: pour l'instant ca copie juste la vidéo, en attendant le hud
        if self.exportAnimatic:

            editVideoFile = f"C:/_UAS_ROOT/RRSpecial/04_ActsPredec/Act{ActIndStr}/Act{ActIndStr}_Predec.mp4"
            targetEditVideoFile = (
                f"C:/_UAS_ROOT/RRSpecial/05_Acts/Act{ActIndStr}/_Montage/Act{ActIndStr}_Edit_Previz.mp4"
            )

            shutil.copyfile(editVideoFile, targetEditVideoFile)

        ######
        # Export videos

        scene.render.image_settings.file_format = "FFMPEG"
        scene.render.ffmpeg.format = "MPEG4"
        scene.render.ffmpeg.constant_rate_factor = "PERC_LOSSLESS"  # "PERC_LOSSLESS"
        scene.render.ffmpeg.gopsize = 5  # keyframe interval
        scene.render.ffmpeg.audio_codec = "AAC" if self.exportVideosWithSound else "NONE"

        #       scene.render.filepath = output_filepath
        scene.render.use_file_extension = False

        markers = utils.sortMarkers(scene.timeline_markers)

        # print(f"markers: {markers}")
        if self.exportAsVideoFiles:
            print(f"\n * Exporting video files:")

            # turn off separated sound tracks
            vsm_props.getTrackByIndex(1).enabled = True
            vsm_props.getTrackByIndex(2).enabled = True
            vsm_props.getTrackByIndex(3).enabled = False
            vsm_props.getTrackByIndex(4).enabled = False
            vsm_props.getTrackByIndex(5).enabled = False
            vsm_props.getTrackByIndex(6).enabled = False

            for i, mrk in enumerate(markers):
                if self.start <= markers[i].frame <= self.end:
                    if i < len(markers) - 1:
                        if self.start <= markers[i + 1].frame <= self.end:
                            #    print(f"{i} Marker name: {mrk.name}")
                            scene.frame_start = markers[i].frame
                            scene.frame_end = markers[i + 1].frame - 1
                            scene.render.filepath = allShotsOutput + "/" + mrk.name + ".mp4"
                            bpy.ops.render.opengl(animation=True, sequencer=True)

                            seqName = mrk.name[0:13]
                            targetShotFile = f"C:/_UAS_ROOT/RRSpecial/05_Acts/Act{ActIndStr}/{seqName}/Predec_Shots/Main_Take/{mrk.name}.mp4"

                            targetShotFilePath = Path(targetShotFile).parent
                            if Path(targetShotFilePath).exists():
                                # print(f"Path Ok: {targetShotFilePath}")

                                if Path(targetShotFile).exists():
                                    stat = Path(targetShotFile).stat()
                                    #   print(f"Blender file Stats: {stat.st_mode}")
                                    fileIsReadOnly = S_IMODE(stat.st_mode) & S_IWRITE == 0
                                    if fileIsReadOnly:
                                        os.chmod(targetShotFile, 0o666)

                            else:
                                # print(f"Path not found: {targetShotFilePath}")
                                try:
                                    os.makedirs(targetShotFilePath)
                                except OSError:
                                    print("Creation of the directory %s failed" % targetShotFilePath)
                                else:
                                    # print("Successfully created the directory %s" % targetShotFilePath)
                                    pass

                            # copy shot video to the published video directory of the sequence
                            shutil.copyfile(scene.render.filepath, targetShotFile)

                            #### publish romain

        ######
        # Export audios

        if self.exportAsAudioFiles:
            for i, mrk in enumerate(markers):
                if self.start <= markers[i].frame <= self.end:
                    #   print(f"{i} if 01 - Marker name: {mrk.name}")
                    if i < len(markers) - 1:
                        #       print(f"{i} if 02 - Marker name: {mrk.name}, {self.start}, {markers[i + 1].frame}, {self.end}")
                        if self.start <= markers[i + 1].frame <= self.end:
                            #    print(f"{i} Marker name: {mrk.name}")
                            scene.frame_start = markers[i].frame
                            scene.frame_end = markers[i + 1].frame - 1
                            # https://blenderartists.org/t/scripterror-mixdown-operstor/548056/4
                            # bpy.ops.sound.mixdown(filepath=str(audioFilePath), relative_path=False, container="WAV", codec="PCM", bitrate=192)
                            audioFilePath = allShotsOutput + "/" + mrk.name + ".mp3"
                            bpy.ops.sound.mixdown(
                                filepath=audioFilePath, relative_path=False, container="MP3", codec="MP3"
                            )

        ######
        # Export Sound Tracks

        if self.exportEditSoundtracks:
            vsm_props = context.scene.UAS_vsm_props
            tracks = vsm_props.getTracks()
            for t in tracks:
                t.enabled = False

            for t in tracks:
                if (
                    t.get_name() == f"Act{ActIndStr} SFX"
                    or t.get_name() == f"Act{ActIndStr} Rabbids"
                    or t.get_name() == f"Act{ActIndStr} Humans_Rabbids"
                    or t.get_name() == f"Act{ActIndStr} Humans"
                ):
                    t.enabled = True

                    # print(f" Len markers: {len(markers)}")
                    for i, mrk in enumerate(markers):
                        if self.start <= markers[i].frame <= self.end:
                            #       print(f"{i} if 01 - Marker name: {mrk.name}")
                            if i < len(markers) - 1:
                                # print(
                                #     f"{i} if 02 - Marker name: {mrk.name}, {self.start}, {markers[i + 1].frame}, {self.end}"
                                # )
                                if self.start <= markers[i + 1].frame <= self.end + 1:
                                    #   print(f"{i} Marker 3 name: {mrk.name}")
                                    scene.frame_start = markers[i].frame
                                    scene.frame_end = markers[i + 1].frame - 1
                                    # https://blenderartists.org/t/scripterror-mixdown-operstor/548056/4
                                    # bpy.ops.sound.mixdown(filepath=str(audioFilePath), relative_path=False, container="WAV", codec="PCM", bitrate=192)
                                    seqName = mrk.name[0:13]
                                    audioFile = f"C:/_UAS_ROOT/RRSpecial/05_Acts/Act{ActIndStr}/{seqName}/_Exports/Sound/{mrk.name}_{(t.get_name())[6:]}.wav"

                                    audioFilePath = Path(audioFile).parent
                                    if Path(audioFilePath).exists():
                                        # print(f"Path Ok: {audioFilePath}")
                                        pass
                                        if Path(audioFile).exists():
                                            stat = Path(audioFile).stat()
                                            #   print(f"Blender file Stats: {stat.st_mode}")
                                            fileIsReadOnly = S_IMODE(stat.st_mode) & S_IWRITE == 0
                                            if fileIsReadOnly:
                                                os.chmod(audioFile, 0o666)

                                    else:
                                        # print(f"Path not found: {audioFilePath}")
                                        try:
                                            os.makedirs(audioFilePath)
                                        except OSError:
                                            print("Creation of the directory %s failed" % audioFilePath)
                                        else:
                                            # print("Successfully created the directory %s" % audioFilePath)
                                            pass

                                    print(f"Exporting audioFile: {audioFile}")

                                    bpy.ops.sound.mixdown(
                                        filepath=audioFile, relative_path=False, container="WAV",
                                    )

                    print("")
                    t.enabled = False

        context.scene.frame_start = self.start
        context.scene.frame_end = self.end
        print(f"\n * Export content between markers done\n")

        return {"FINISHED"}


class UAS_VideoShotManager_OT_RRS_CheckSequence(Operator):
    bl_idname = "uas_video_shot_manager.rrs_check_sequence"
    bl_label = "Check Sequence..."
    bl_description = "Import the animatic of the scpecified act into the VSE"
    bl_options = {"INTERNAL", "UNDO"}

    # can be ACT01_PREDEC, ACT02_PREDEC, ACT03_PREDEC
    mode: StringProperty(default="")

    overlayFile: StringProperty(default=r"C:\_UAS_ROOT\RRSpecial\00_Common\Images\RRS_EditPreviz_Overlay.png")

    editVideoFile: StringProperty(default=r"C:\_UAS_ROOT\RRSpecial\05_Acts\Act01\_Montage\Act01_Edit_Previz.mp4")
    otioFile: StringProperty(default=r"C:\_UAS_ROOT\RRSpecial\05_Acts\Act01\_Montage\Act01_Edit_Previz.xml")
    # editVideoFile: StringProperty(
    #     default=r"C:\_UAS_ROOT\RRSpecial\_Sandbox\Julien\Fixtures_Montage\PrevizAct01_Seq0060\Act01_Seq0060_Main_Take_ModifsRename.mp4"
    # )
    # otioFile: StringProperty(
    #     default=r"C:\_UAS_ROOT\RRSpecial\_Sandbox\Julien\Fixtures_Montage\PrevizAct01_Seq0060\Act01_Seq0060_Main_Take_ModifsRename.xml"
    # )
    useOverlayFrame: BoolProperty(name="Use Overlay Frame", default=False)
    importMarkers: BoolProperty(name="Import Markers", default=True)

    def invoke(self, context, event):
        wm = context.window_manager
        scene = context.scene
        props = scene.UAS_shot_manager_props

        openDialog = "" == self.mode

        if not openDialog:
            self.useOverlayFrame = True
            self.importMarkers = True

            ActIndStr = self.mode[3:5]
            print(f"*** Act {ActIndStr}")

            self.editVideoFile = f"C:/_UAS_ROOT/RRSpecial/04_ActsPredec/Act{ActIndStr}/Act{ActIndStr}_Predec.mp4"

            if "ACT01_PREDEC" == self.mode:
                self.otioFile = r"C:/_UAS_ROOT/RRSpecial/05_Acts/Act01/_Montage/Act01_Edit_Previz.xml"
            else:

                if "ACT02_PREDEC" == self.mode:
                    self.otioFile = f"C:/_UAS_ROOT/RRSpecial/04_ActsPredec/Act{ActIndStr}/Exports/RRSpecial_Act{ActIndStr}_AQ_XML/RRspecial_Act02_AQ_201007.xml"
                elif "ACT03_PREDEC" == self.mode:
                    self.otioFile = f"C:/_UAS_ROOT/RRSpecial/04_ActsPredec/Act{ActIndStr}/Exports/RRSpecial_Act{ActIndStr}_AQ_XML/RRspecial_Act02_AQ_201007.xml"

        # print
        print(f" - self.editVideoFile: {self.editVideoFile}")
        print("")

        config.gMontageOtio = None
        if self.importMarkers and "" != self.otioFile and Path(self.otioFile).exists():
            config.gMontageOtio = MontageOtio()
            config.gMontageOtio.fillMontageInfoFromOtioFile(
                otioFile=self.otioFile, refVideoTrackInd=0, verboseInfo=False
            )

            config.gSeqEnumList = list()
            print(f"config.gMontageOtio name: {config.gMontageOtio.get_name()}")
            for i, seq in enumerate(config.gMontageOtio.sequencesList):
                print(f"- seqList: i:{i}, seq: {seq.get_name()}")
                config.gSeqEnumList.append((str(i), seq.get_name(), f"Import sequence {seq.get_name()}", i + 1))

            self.sequenceList = config.gSeqEnumList[0][0]

        if openDialog:
            return {wm.invoke_props_dialog(self, width=500)}
            # return {"RUNNING_MODAL"}
        return self.execute(context)

    def draw(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props

        # selSeq = config.gMontageOtio.sequencesList[int(self.sequenceList)] if config.gMontageOtio is not None else None

        layout = self.layout
        row = layout.row(align=True)

        box = row.box()
        box.label(text="OTIO File")
        box.prop(self, "otioFile", text="")

        if "" == self.otioFile or not Path(self.otioFile).exists():
            row = box.row()
            row.alert = True
            row.label(text="Specified EDL file not found! - Verify your local depot")  # wkip rrs specific
            row.alert = False

        # box.prop(self, "useOverlayFrame")
        #  box.prop(self, "importMarkers")

        if config.gMontageOtio is not None:
            numVideoTracks = len(config.gMontageOtio.timeline.video_tracks())
            numAudioTracks = len(config.gMontageOtio.timeline.audio_tracks())

            row = box.row()
            row.label(text=f"Timeline: {config.gMontageOtio.timeline.name}")
            # row = box.row()
            row.label(text=f"Video Tracks: {numVideoTracks},  Audio Tracks: {numAudioTracks}")
            row = box.row()
            row.label(
                text=f"Duration: {config.gMontageOtio.get_frame_duration()} frames at {config.gMontageOtio.get_fps()} fps"
            )
            row.separator(factor=3)
            row.label(text=f"Num. Sequences: {len(config.gMontageOtio.sequencesList)}")

            row = box.row()
            if config.gMontageOtio.get_fps() != scene.render.fps:
                row.alert = True
                row.label(text=f"!! Scene has a different framerate: {scene.render.fps} fps !!")
                row.alert = False

        #     # if config.uasDebug:
        #     #     row.operator("uas_shot_manager.montage_sequences_to_json")  # uses config.gMontageOtio

        #     subRow = box.row()
        #     subRow.enabled = selSeq is not None
        #     row.operator("uasshotmanager.compare_otio_and_current_montage").sequenceName = selSeq.get_name()

        # row = layout.row(align=True)
        # box = row.box()
        # box.separator(factor=0.2)
        # box.prop(self, "sequenceList")

        # # print("self.sequenceList: ", self.sequenceList)
        # if selSeq is not None:
        #     labelText = f"Start: {selSeq.get_frame_start()}, End: {selSeq.get_frame_end()}, Duration: {selSeq.get_frame_duration()}, Num Shots: {len(selSeq.shotsList)}"

        #     # sm_montage.printInfo()

        # else:
        #     labelText = f"Start: {-1}, End: {-1}, Num Shots: {0}"

    def execute(self, context):
        scene = context.scene
        vse_render = bpy.context.window_manager.UAS_vse_render
        props = scene.UAS_shot_manager_props
        vsm_props = scene.UAS_vsm_props

        vse_render.clearAllChannels(scene)
        utils_vse.showSecondsInVSE(False)

        vsm_props.updateTracksList(scene)

        # animaticClip = rrs_animatic_to_vsm(
        #     scene=scene,
        #     editVideoFile=self.editVideoFile,
        #     montageOtio=config.gMontageOtio,
        #     importMarkers=self.importMarkers,
        # )

        scene.frame_start = 0
        scene.frame_end = 40000
        # if props.use_project_settings:
        #     # scene.render.image_settings.file_format = props.project_images_output_format
        #     scene.render.fps = props.project_fps
        #     scene.render.resolution_x = props.project_resolution_framed_x
        #     scene.render.resolution_y = props.project_resolution_framed_y

        scene.render.fps = 25
        scene.render.resolution_x = 1280
        scene.render.resolution_y = 720

        # video
        channelInd = 2
        trackName = "Act01 Previz_Edit (video)"
        editVideoClip = vse_render.createNewClip(
            scene, self.editVideoFile, clipName=trackName, channelInd=channelInd, atFrame=0, importAudio=False
        )
        # vsm_props.addTrack(atIndex=1, trackType="STANDARD", name="Previz_Edit (video)", color=(0.1, 0.2, 0.8, 1))
        vsm_props.setTrackInfo(channelInd, trackType="VIDEO", name=trackName)

        # audio
        channelInd = 1
        trackName = "Act01 Previz_Edit (audio)"
        editAudioClip = vse_render.createNewClip(
            scene,
            self.editVideoFile,
            clipName=trackName,
            channelInd=channelInd,
            atFrame=0,
            importVideo=False,
            importAudio=True,
        )
        # vsm_props.addTrack(atIndex=2, trackType="STANDARD", name="Previz_Edit (audio)", color=(0.1, 0.5, 0.2, 1))
        vsm_props.setTrackInfo(channelInd, trackType="AUDIO", name=trackName)

        bpy.ops.sequencer.set_range_to_strips(preview=False)

        ################
        # import markers
        ################

        scene.timeline_markers.clear()
        if self.importMarkers:

            if config.gMontageOtio is not None:
                # # config.gMontageOtio
                # config.gMontageOtio = None
                # if self.importMarkers and "" != otioFile and Path(otioFile).exists():
                #     config.gMontageOtio = MontageOtio()
                #     config.gMontageOtio.fillMontageInfoFromOtioFile(
                #         otioFile=otioFile, refVideoTrackInd=0, verboseInfo=False
                #     )

                config.gSeqEnumList = list()
                print(f"config.gMontageOtio name: {config.gMontageOtio.get_name()}")

                importShotMarkersFromMontage(scene, config.gMontageOtio)

        # if animaticClip is not None:
        #     res_x = 1280
        #     res_y = 960
        #     clip_x = 1280
        #     clip_y = 720
        #     vse_render.cropClipToCanvas(
        #         res_x, res_y, animaticClip, clip_x, clip_y, mode="FIT_WIDTH",
        #     )

        # import sounds
        if "" != self.mode:
            ActIndStr = self.mode[3:5]
            print(f"**** Import Act {ActIndStr}")

            ##### SFX
            channelInd = 3
            trackName = f"Act{ActIndStr} SFX"
            audioFile = (
                f"C:/_UAS_ROOT/RRSpecial/05_Acts/Act{ActIndStr}/_Montage/_Exports/Act{ActIndStr}_Soundtracks_SFX.mp3"
            )
            editAudioClip = vse_render.createNewClip(
                scene, audioFile, clipName=trackName, channelInd=channelInd, atFrame=0
            )
            #            print(f"   - Name 02: {editAudioClip.name}")
            vsm_props.setTrackInfo(channelInd, trackType="AUDIO", name=trackName)

            ##### Rabbids
            channelInd = 4
            trackName = f"Act{ActIndStr} Rabbids"
            audioFile = f"C:/_UAS_ROOT/RRSpecial/05_Acts/Act{ActIndStr}/_Montage/_Exports/Act{ActIndStr}_Soundtracks_Rabbids.mp3"
            editAudioClip = vse_render.createNewClip(
                scene, audioFile, clipName=trackName, channelInd=channelInd, atFrame=0
            )
            vsm_props.setTrackInfo(channelInd, trackType="AUDIO", name=trackName)

            ##### Humans_Rabbids
            channelInd = 5
            trackName = f"Act{ActIndStr} Humans_Rabbids"
            audioFile = f"C:/_UAS_ROOT/RRSpecial/05_Acts/Act{ActIndStr}/_Montage/_Exports/Act{ActIndStr}_Soundtracks_Humans_Rabbids.mp3"
            editAudioClip = vse_render.createNewClip(
                scene, audioFile, clipName=trackName, channelInd=channelInd, atFrame=0
            )
            vsm_props.setTrackInfo(channelInd, trackType="AUDIO", name=trackName)

            ##### Humans
            channelInd = 6
            trackName = f"Act{ActIndStr} Humans"
            audioFile = (
                f"C:/_UAS_ROOT/RRSpecial/05_Acts/Act{ActIndStr}/_Montage/_Exports/Act{ActIndStr}_Soundtracks_Humans.mp3"
            )
            editAudioClip = vse_render.createNewClip(
                scene, audioFile, clipName=trackName, channelInd=channelInd, atFrame=0
            )
            vsm_props.setTrackInfo(channelInd, trackType="AUDIO", name=trackName)

            # import
            # if "ACT01_PREDEC" == self.mode:

        #  bpy.ops.uas_video_shot_manager.zoom_view(zoomMode="SELECTEDCLIPS")

        return {"FINISHED"}


class UAS_VideoShotManager_OT_RRSExportAnimaticVideos(Operator):
    bl_idname = "uas_video_shot_manager.export_animatic_videos"
    bl_label = "Export Animatic Videos"
    bl_description = "Export all the segments defined by the markers as separated videos"
    bl_options = {"INTERNAL"}

    # can be ACT01_PREDEC, ACT02_PREDEC, ACT03_PREDEC
    mode: StringProperty(default="")

    outputDir: StringProperty(default=r"-- Copy Output Directory Here ---")

    start: IntProperty(name="Start", default=10)
    end: IntProperty(name="end", default=150)

    exportAsVideoFiles: BoolProperty(name="Export as Video Files", default=True)
    exportVideosWithSound: BoolProperty(name="With Sound", default=True)
    exportAsAudioFiles: BoolProperty(name="Export as Audio Files", default=True)
    exportEditSoundtracks: BoolProperty(name="Export Edit Sound Tracks", default=True)

    def invoke(self, context, event):

        self.start = context.scene.frame_start
        self.end = context.scene.frame_end

        wm = context.window_manager
        wm.invoke_props_dialog(self, width=500)
        return {"RUNNING_MODAL"}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "outputDir")
        row = layout.row()
        row.prop(self, "start")
        row.prop(self, "end")
        row = layout.row()
        row.prop(self, "exportAsVideoFiles")
        row.prop(self, "exportVideosWithSound")
        row = layout.row()
        row.prop(self, "exportAsAudioFiles")
        row = layout.row()
        row.prop(self, "exportEditSoundtracks")

    def execute(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props

        vse_render = bpy.context.window_manager.UAS_vse_render

        if not Path(self.outputDir).exists():
            print(f" *** Cannot export VSE content, path does not exist: {self.outputDir}")
            return {"FINISHED"}

        ######
        # Export videos

        scene.render.image_settings.file_format = "FFMPEG"
        scene.render.ffmpeg.format = "MPEG4"
        scene.render.ffmpeg.constant_rate_factor = "PERC_LOSSLESS"  # "PERC_LOSSLESS"
        scene.render.ffmpeg.gopsize = 5  # keyframe interval
        scene.render.ffmpeg.audio_codec = "AAC" if self.exportVideosWithSound else "NONE"

        #       scene.render.filepath = output_filepath
        scene.render.use_file_extension = False

        markers = utils.sortMarkers(scene.timeline_markers)

        # print(f"markers: {markers}")
        if self.exportAsVideoFiles:
            print(f"\n * Exporting video files:")
            for i, mrk in enumerate(markers):
                if self.start <= markers[i].frame <= self.end:
                    if i < len(markers) - 1:
                        if self.start <= markers[i + 1].frame <= self.end:
                            #    print(f"{i} Marker name: {mrk.name}")
                            scene.frame_start = markers[i].frame
                            scene.frame_end = markers[i + 1].frame - 1
                            scene.render.filepath = self.outputDir + "/" + mrk.name + ".mp4"
                            bpy.ops.render.opengl(animation=True, sequencer=True)

        ######
        # Export audios

        if self.exportAsAudioFiles:
            for i, mrk in enumerate(markers):
                if self.start <= markers[i].frame <= self.end:
                    #   print(f"{i} if 01 - Marker name: {mrk.name}")
                    if i < len(markers) - 1:
                        #       print(f"{i} if 02 - Marker name: {mrk.name}, {self.start}, {markers[i + 1].frame}, {self.end}")
                        if self.start <= markers[i + 1].frame <= self.end:
                            #    print(f"{i} Marker name: {mrk.name}")
                            scene.frame_start = markers[i].frame
                            scene.frame_end = markers[i + 1].frame - 1
                            # https://blenderartists.org/t/scripterror-mixdown-operstor/548056/4
                            # bpy.ops.sound.mixdown(filepath=str(audioFilePath), relative_path=False, container="WAV", codec="PCM", bitrate=192)
                            audioFilePath = self.outputDir + "/" + mrk.name + ".mp3"
                            bpy.ops.sound.mixdown(
                                filepath=audioFilePath, relative_path=False, container="MP3", codec="MP3"
                            )

        ######
        # Export Sound Tracks

        if self.exportEditSoundtracks:
            vsm_props = context.scene.UAS_vsm_props
            tracks = vsm_props.getTracks()
            for t in tracks:
                t.enabled = False

            for t in tracks:
                if (
                    t.get_name() == "SFX"
                    or t.get_name() == "Rabbids"
                    or t.get_name() == "Humans_Rabbids"
                    or t.get_name() == "Humans"
                ):
                    t.enabled = True

                    # print(f" Len markers: {len(markers)}")
                    for i, mrk in enumerate(markers):
                        if self.start <= markers[i].frame <= self.end:
                            #       print(f"{i} if 01 - Marker name: {mrk.name}")
                            if i < len(markers) - 1:
                                # print(
                                #     f"{i} if 02 - Marker name: {mrk.name}, {self.start}, {markers[i + 1].frame}, {self.end}"
                                # )
                                if self.start <= markers[i + 1].frame <= self.end + 1:
                                    #   print(f"{i} Marker 3 name: {mrk.name}")
                                    scene.frame_start = markers[i].frame
                                    scene.frame_end = markers[i + 1].frame - 1
                                    # https://blenderartists.org/t/scripterror-mixdown-operstor/548056/4
                                    # bpy.ops.sound.mixdown(filepath=str(audioFilePath), relative_path=False, container="WAV", codec="PCM", bitrate=192)
                                    seqName = mrk.name[0:13]
                                    audioFile = f"C:/_UAS_ROOT/RRSpecial/05_Acts/Act01/{seqName}/_Exports/Sound/{mrk.name}_{t.get_name()}.wav"

                                    audioFilePath = Path(audioFile).parent
                                    if Path(audioFilePath).exists():
                                        # print(f"Path Ok: {audioFilePath}")
                                        pass
                                        if Path(audioFile).exists():
                                            stat = Path(audioFile).stat()
                                            #   print(f"Blender file Stats: {stat.st_mode}")
                                            fileIsReadOnly = S_IMODE(stat.st_mode) & S_IWRITE == 0
                                            if fileIsReadOnly:
                                                os.chmod(audioFile, 0o666)

                                    else:
                                        # print(f"Path not found: {audioFilePath}")
                                        try:
                                            os.makedirs(audioFilePath)
                                        except OSError:
                                            print("Creation of the directory %s failed" % audioFilePath)
                                        else:
                                            # print("Successfully created the directory %s" % audioFilePath)
                                            pass

                                    print(f"Exporting audioFile: {audioFile}")

                                    bpy.ops.sound.mixdown(
                                        filepath=audioFile, relative_path=False, container="WAV",
                                    )

                    print("")
                    t.enabled = False

        context.scene.frame_start = self.start
        context.scene.frame_end = self.end
        print(f"\n * Export content between markers done to {self.outputDir}\n")

        return {"FINISHED"}


class UAS_VideoShotManager_GoToSequenceScene(Operator):
    bl_idname = "uas_video_shot_manager.go_to_sequence_scene"
    bl_label = "Go To Sequence Scene"
    bl_description = "Go to specified scene"
    bl_options = {"INTERNAL"}

    sceneName: StringProperty()

    def invoke(self, context, event):

        # print("trackName: ", self.trackName)
        # Make track scene the current one
        # bpy.context.window.scene = context.scene.UAS_vsm_props.tracks[self.trackName].shotManagerScene
        bpy.context.window.scene = bpy.data.scenes[self.sceneName]
        bpy.context.window.workspace = bpy.data.workspaces["Layout"]

        return {"FINISHED"}


class UAS_VideoShotManager_OpenExportDocPage(Operator):
    bl_idname = "uas_video_shot_manager.open_export_doc_page"
    bl_label = "Open Export Doc Page"
    bl_description = "Open Export Doc Page to see the details of the export operation for act 02 and act 03"
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        import webbrowser

        webbrowser.open("https://confluence.ubisoft.com/pages/viewpage.action?pageId=976948217")

        return {"FINISHED"}


def list_sequences_from_markers(self, context):
    res = config.gSeqEnumList
    # res = list()
    nothingList = list()
    nothingList.append(("NO_SEQ", "No Sequence Found", "No sequence found in the specified EDL file", 0))

    # seqList = getSequenceListFromOtioTimeline(config.gMontageOtio)
    # for i, item in enumerate(seqList):
    #     res.append((item, item, "My seq", i + 1))

    # res = getSequenceListFromOtio()
    # res.append(("NEW_CAMERA", "New Camera", "Create new camera", 0))
    # for i, cam in enumerate([c for c in context.scene.objects if c.type == "CAMERA"]):
    #     res.append(
    #         (cam.name, cam.name, 'Use the exising scene camera named "' + cam.name + '"\nfor the new shot', i + 1)
    #     )

    if res is None or 0 == len(res):
        res = nothingList
    return res


class UAS_VideoShotManager_ImportPublishedSequence(Operator):
    bl_idname = "uas_video_shot_manager.import_published_sequence"
    bl_label = "Import a Published Sequence"
    bl_description = "Import a specified sequence generated by the Publish"
    bl_options = {"INTERNAL", "UNDO"}

    sequenceList: EnumProperty(
        name="Sequence",
        description="Sequences available from the markers list",
        # items=(("NO_SEQ", "No Sequence Found", ""),),
        items=(list_sequences_from_markers),
    )

    def invoke(self, context, event):
        wm = context.window_manager
        scene = context.scene
        props = scene.UAS_shot_manager_props

        # parse the markers to get the shots list
        previzMarkers = scene.timeline_markers
        seqNames = list()
        currentSeqName = ""
        # if bpy.data.scenes[0].name.startswith("Act"):  # wkip re match
        if utils_rrs.start_with_act(bpy.data.scenes[0].name):  # wkip re match
            currentSeqName = (bpy.data.scenes[0].name)[6:13]
        print(f"Current seq name: {currentSeqName}")
        currentSeqIndex = -1
        seqInd = -1
        config.gSeqEnumList = list()
        for i, m in enumerate(previzMarkers):
            if utils_rrs.start_with_seq(m.name):
                seqName = m.name[0:13]
                seqNameShort = m.name[6:13]
                if seqName not in seqNames:
                    seqNames.append(seqName)
                    seqInd += 1
                    # config.gSeqEnumList.append((str(seqInd), seqName, f"Import sequence {seqName}", seqInd + 1))
                    config.gSeqEnumList.append((seqName, seqNameShort, f"Import sequence {seqName}", seqInd + 1))
                    if seqName == currentSeqName:
                        currentSeqIndex = seqInd
                        # strDebug += " - Is current sequence !"

        if not len(config.gSeqEnumList):
            config.gSeqEnumList.append(
                (str(0), " ** No Sequence in the markers list **", f"No sequence found in the markers list", 1)
            )

        if -1 != currentSeqIndex:
            self.sequenceList = config.gSeqEnumList[currentSeqIndex][0]
        else:
            self.sequenceList = config.gSeqEnumList[0][0]
        _logger.debug(f"self.sequenceList: {self.sequenceList}")

        return wm.invoke_props_dialog(self, width=500)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.UAS_shot_manager_props

        # selSeq = (
        #     config.gMontageOtio.sequencesList[int(self.sequenceList)]
        #     if config.gMontageOtio is not None and len(config.gMontageOtio.sequencesList)
        #     else None
        # )

        row = layout.row(align=True)
        box = row.box()
        box.separator(factor=0.2)
        box.prop(self, "sequenceList")

        # # print("self.sequenceList: ", self.sequenceList)
        # if selSeq is not None:
        #     labelText = f"Start: {selSeq.get_frame_start()}, End: {selSeq.get_frame_end()}, Duration: {selSeq.get_frame_duration()}, Num Shots: {len(selSeq.shotsList)}"

        #     # display the shots infos
        #     # sm_montage.printInfo()

        # else:
        #     labelText = f"Start: {-1}, End: {-1}, Num Shots: {0}"

    def execute(self, context):
        seqToImport = self.sequenceList
        # seqToImport = config.gSeqEnumList[self.sequenceList][1]
        print("seq list to import:", seqToImport)
        success = rrs_sequence_to_vsm(context.scene, seqToImport)
        if not success:
            utils.ShowMessageBox(f"Sequence {seqToImport} cannot be loaded", "Cannot load sequence", "ERROR")
            return {"CANCELLED"}
        return {"FINISHED"}


# class UAS_VideoShotManager_OT_RRS_ExportAllSoundsPerShot(Operator):
#     bl_idname = "uas_video_shot_manager.rrs_export_sounds_per_shot"
#     bl_label = "Export Sounds Per Shot"
#     bl_description = "Bla bla"
#     bl_options = {"INTERNAL", "UNDO"}

#     def execute(self, context):
#         soundsPerShot = getSoundFilesForEachShot(config.gMontageOtio, "Act01_Seq0100", otioFile)
#         print("soundsPerShot: ", soundsPerShot)

#         return {"FINISHED"}


_classes = (
    UAS_VideoShotManager_OT_RRSExportAnimaticVideosAndPublish,
    UAS_VideoShotManager_OT_RRSExportAnimaticVideos,
    UAS_VideoShotManager_OT_RRS_CheckSequence,
    UAS_VideoShotManager_GoToSequenceScene,
    UAS_VideoShotManager_ImportPublishedSequence,
    UAS_PT_RRSVSMTools,
    UAS_VideoShotManager_OpenExportDocPage,
    # UAS_VideoShotManager_OT_RRS_ExportAllSoundsPerShot,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
