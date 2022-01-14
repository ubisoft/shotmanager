    
    
    def buildSequenceVideoFromMedia(self, outputFile, handles, fps, mediaDictArr=None, mediaFiles=None):
        previousScene = bpy.context.window.scene

        sequenceScene = None
        if "VSE_SequenceRenderScene" in bpy.data.scenes:
            sequenceScene = bpy.data.scenes["VSE_SequenceRenderScene"]
            bpy.data.scenes.remove(sequenceScene, do_unlink=True)
        sequenceScene = bpy.data.scenes.new(name="VSE_SequenceRenderScene")

        createVseTab = False  # config.devDebug
        sequenceScene = utils.getSceneVSE(sequenceScene.name, createVseTab=createVseTab)  # config.devDebug)
        bpy.context.window.scene = sequenceScene

        if createVseTab:
            bpy.context.window.workspace = bpy.data.workspaces["Video Editing"]

        #     for area in bpy.context.screen.areas:
        #         print(f"area type: {area.type}")
        #         if area.type == "SEQUENCE_EDITOR":
        #             area.spaces.items()[0][1].show_seconds = True

        sequenceScene.render.fps = fps  # projectFps

        if mediaDictArr is not None:
            sequenceScene.render.resolution_x = mediaDictArr[0]["bg_resolution"][0]
            sequenceScene.render.resolution_y = mediaDictArr[0]["bg_resolution"][1]
            inputOverResolution = mediaDictArr[0]["image_sequence_resolution"]
        else:
            # mediaFiles is not None
            # wkipwkipwkip
            sequenceScene.render.resolution_x = 1580
            sequenceScene.render.resolution_y = 960        

        sequenceScene.frame_start = 0
        # sequenceScene.frame_end = props.getEditDuration() - 1
        sequenceScene.render.image_settings.file_format = "FFMPEG"
        sequenceScene.render.ffmpeg.format = "MPEG4"
        sequenceScene.render.ffmpeg.constant_rate_factor = "PERC_LOSSLESS"  # "PERC_LOSSLESS"
        sequenceScene.render.ffmpeg.gopsize = 5  # keyframe interval, 2?
        sequenceScene.render.ffmpeg.audio_codec = "AAC"
        sequenceScene.render.filepath = outputFile

        # change color tone mode to prevent washout bug with "filmic" rendered image mode
        sequenceScene.view_settings.view_transform = "Raw"

        if mediaDictArr is not None:
            atFrame = 0
            for i, mediaDict in enumerate(mediaDictArr):
                # sequenceScene.sequence_editor
                frameToPaste = self.get_frame_end_from_content(sequenceScene)
                print("\n---- Importing image sequences ----")
                print(f"  frametopaste: {frameToPaste}")

                bgClip = None
                if "bg" in mediaDict and mediaDict["bg"] is not None:
                    try:
                        print(f"self.inputBGMediaPath: {mediaDict['bg']}")
                        bgClip = self.createNewClip(sequenceScene, mediaDict["bg"], 2, atFrame)
                        print("BG Media OK")
                    except Exception:
                        print(f" *** Rendered shot not found: {mediaDict['bg']}")

                    # bgClip = None
                    # if os.path.exists(self.inputBGMediaPath):
                    #     bgClip = self.createNewClip(vse_scene, self.inputBGMediaPath, 1, 1)
                    # else:
                    #     print(f" *** Rendered shot not found: {self.inputBGMediaPath}")

                #    print(f"self.inputBGMediaPath: {self.inputOverMediaPath}")

                shotDuration = 0
                if "image_sequence" in mediaDict and mediaDict["image_sequence"] is not None:
                    overClip = None
                    try:
                        overClip = self.createNewClip(sequenceScene, mediaDict["image_sequence"], 3, atFrame)
                        print("Over Media OK")
                    except Exception:
                        print(f" *** Rendered shot not found: {mediaDict['image_sequence']}")
                    # overClip = None
                    # if os.path.exists(self.inputOverMediaPath):
                    #     overClip = self.createNewClip(vse_scene, self.inputOverMediaPath, 2, 1)
                    # else:
                    #     print(f" *** Rendered shot not found: {self.inputOverMediaPath}")

                    if overClip is not None:
                        res_x = mediaDictArr[0]["bg_resolution"][0]
                        res_y = mediaDictArr[0]["bg_resolution"][1]
                        clip_x = inputOverResolution[0]
                        clip_y = inputOverResolution[1]
                        self.cropClipToCanvas(
                            res_x, res_y, overClip, clip_x, clip_y, mode="FIT_WIDTH",
                        )
                        # overClip.use_crop = True
                        # overClip.crop.min_x = -1 * int((mediaDictArr[0]["bg_resolution"][0] - inputOverResolution[0]) / 2)
                        # overClip.crop.max_x = overClip.crop.min_x
                        # overClip.crop.min_y = -1 * int((mediaDictArr[0]["bg_resolution"][1] - inputOverResolution[1]) / 2)
                        # overClip.crop.max_y = overClip.crop.min_y

                        overClip.blend_type = "OVER_DROP"
                        shotDuration = overClip.frame_final_duration

                if "sound" in mediaDict and mediaDict["sound"] is not None:
                    audioClip = None
                    if os.path.exists(mediaDict["sound"]):
                        audioClip = self.createNewClip(
                            sequenceScene, mediaDict["sound"], 1, atFrame, final_duration=shotDuration
                        )
                        audioClip = self.createNewClipFromRange(sequenceScene, mediaDict["sound"], 1,)
                    else:
                        print(f" *** Rendered shot not found: {mediaDict['sound']}")

                # bpy.context.scene.sequence_editor.sequences
                # get res of video: bpy.context.scene.sequence_editor.sequences[1].elements[0].orig_width
                # ne marche que sur vidéos

                # sequenceScene.frame_end = self.get_frame_end_from_content(sequenceScene) - 1
                # print(f"sequenceScene.frame_end: {sequenceScene.frame_end}")
                atFrame += shotDuration
                print(f"atFrame: {atFrame}")

            # Make "My New Scene" the active one
            # bpy.context.window.scene = vse_scene

            sequenceScene.frame_end = atFrame - 1

            # fix to get even resolution values:
            # print(
            #     f"Render W: {sequenceScene.render.resolution_x} and H: {sequenceScene.render.resolution_y}, %: {sequenceScene.render.resolution_percentage}"
            # )
            if 100 != sequenceScene.render.resolution_percentage:
                sequenceScene.render.resolution_x = int(
                    sequenceScene.render.resolution_x * sequenceScene.render.resolution_percentage / 100.0
                )
                sequenceScene.render.resolution_y = int(
                    sequenceScene.render.resolution_y * sequenceScene.render.resolution_percentage / 100.0
                )
                sequenceScene.render.resolution_percentage = 100

            if 1 == sequenceScene.render.resolution_x % 2:
                sequenceScene.render.resolution_x += 1
            if 1 == sequenceScene.render.resolution_y % 2:
                sequenceScene.render.resolution_y += 1

            # print(
            #     f"Render New W: {sequenceScene.render.resolution_x} and H: {sequenceScene.render.resolution_y}, %: {sequenceScene.render.resolution_percentage}"
            # )

        else:
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

        # wkip changer ca fait que le time range n'est pas pris en compte...
        # if not config.devDebug:
        bpy.context.window.scene = previousScene
        # if config.devDebug:
        #     bpy.context.window.scene = sequenceScene