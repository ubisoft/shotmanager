def buildSequenceVideo(self, mediaFiles, outputFile, handles, fps):
    previousScene = bpy.context.window.scene

    sequenceScene = None
    if "VSE_SequenceRenderScene" in bpy.data.scenes:
        sequenceScene = bpy.data.scenes["VSE_SequenceRenderScene"]
        bpy.data.scenes.remove(sequenceScene, do_unlink=True)
    sequenceScene = bpy.data.scenes.new(name="VSE_SequenceRenderScene")

    sequenceScene = utils.getSceneVSE(sequenceScene.name, createVseTab=False)  # config.devDebug)

    bpy.context.window.scene = sequenceScene

    sequenceScene.render.fps = fps  # projectFps
    # wkipwkipwkip
    sequenceScene.render.resolution_x = 1580
    sequenceScene.render.resolution_y = 960
    sequenceScene.frame_start = 0
    # sequenceScene.frame_end = props.getEditDuration() - 1
    sequenceScene.render.image_settings.file_format = "FFMPEG"
    sequenceScene.render.ffmpeg.format = "MPEG4"
    sequenceScene.render.ffmpeg.constant_rate_factor = "PERC_LOSSLESS"  # "PERC_LOSSLESS"
    sequenceScene.render.ffmpeg.gopsize = 5  # keyframe interval
    sequenceScene.render.ffmpeg.audio_codec = "AAC"
    sequenceScene.render.filepath = outputFile

    # change color tone mode to prevent washout bug with "filmic" rendered image mode
    sequenceScene.view_settings.view_transform = "Raw"

    for mediaPath in mediaFiles:
        # sequenceScene.sequence_editor
        frameToPaste = self.get_frame_end_from_content(sequenceScene)
        print("\n---- Importing video ----")
        print(f"  frametopaste: {frameToPaste}")
        # video clip
        self.createNewClip(
            sequenceScene,
            mediaPath,
            0,
            frameToPaste - handles,  # shot.getEditStart() - handles,
            offsetStart=handles,
            offsetEnd=handles,
            importVideo=True,
            importAudio=False,
        )

        # audio clip
        self.createNewClip(
            sequenceScene,
            mediaPath,
            1,
            frameToPaste - handles,  # shot.getEditStart() - handles,
            offsetStart=handles,
            offsetEnd=handles,
            importVideo=False,
            importAudio=True,
        )

    sequenceScene.frame_end = self.get_frame_end_from_content(sequenceScene) - 1

    bpy.ops.render.opengl(animation=True, sequencer=True, write_still=False)

    # cleaning current file from temp scenes
    if not config.devDebug_keepVSEContent:
        # current scene is sequenceScene
        bpy.ops.scene.delete()
        pass

    bpy.context.window.scene = previousScene

