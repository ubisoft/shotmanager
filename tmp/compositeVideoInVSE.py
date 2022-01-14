

    def compositeVideoInVSE(
        self,
        fps,
        frame_start,
        frame_end,
        output_filepath,
        postfixSceneName="",
        output_resolution=None,
        importAtFrame=1,
    ):
        """Low level function that will use the bg and fg media already held by this vse_render class to generate
        a media
        
        Args:
            output_resolution: array [width, height]
        """

        self.printMedia()
        print(f" output_filepath: {output_filepath}")
        mediaStr = "VSE_Render  output_resolution:   "
        mediaStr += (
            "None" if output_resolution is None else f"{output_resolution[0]} x {output_resolution[1]}"
        ) + f"  {output_resolution}\n"
        print(mediaStr)

        specificFrame = None
        if frame_start == frame_end:
            specificFrame = frame_start

        previousScene = bpy.context.window.scene
        previousWorkspace = bpy.context.workspace.name
        print(f"Previous Workspace: {previousWorkspace}")
        previousScreen = bpy.context.window.screen.name
        print(f"Previous Screen: {previousScreen}")
        previousRenderView = None
        region = next(
            iter([area.spaces[0].region_3d for area in bpy.context.screen.areas if area.type == "VIEW_3D"]), None
        )
        if region:
            # print(f"current view: {region.view_perspective}")
            previousRenderView = region.view_perspective

        # Add new scene
        # vse_scene = bpy.data.scenes.new(name="Tmp_VSE_RenderScene" + postfixSceneName)
        vse_scene = utils.getSceneVSE("Tmp_VSE_RenderScene" + postfixSceneName, createVseTab=True)
        self.clearAllChannels(vse_scene)

        vse_scene.render.fps = fps
        # Make "My New Scene" the active one
        #    bpy.context.window.scene = vse_scene

        #    vse_scene = utils.getSceneVSE(vse_scene.name, createVseTab=config.devDebug)
        # if not vse_scene.sequence_editor:
        #     vse_scene.sequence_editor_create()

        # https://docs.blender.org/api/blender_python_api_2_77_0/bpy.types.Sequences.html
        # Path ( renderPath ).parent.mkdir ( parents = True, exist_ok = True )

        # resolution
        output_res = [vse_scene.render.resolution_x, vse_scene.render.resolution_y]
        if output_resolution is not None:
            output_res = output_resolution.copy()
        else:
            if "" != self.inputBGMediaPath:
                output_res = self.inputBGResolution.copy()
            elif "" != self.inputOverMediaPath:
                output_res = self.inputOverResolution.copy()

        vse_scene.render.resolution_x = output_res[0]
        vse_scene.render.resolution_y = output_res[1]
        # print(f"  * - * vse_scene.render.resolution: {vse_scene.render.resolution_x} x {vse_scene.render.resolution_y}")

        # add BG
        vse_scene.frame_start = frame_start
        vse_scene.frame_end = frame_end

        if specificFrame is None:
            # get output file format from specified output
            fileExt = str(Path(output_filepath).suffix).upper()

            if 0 < len(fileExt):
                if "." == fileExt[0]:
                    fileExt = fileExt[1:]

                if "PNG" == fileExt:
                    vse_scene.render.image_settings.file_format = "PNG"
                elif "JPG" == fileExt:
                    vse_scene.render.image_settings.file_format = "JPG"
                elif "MP4" == fileExt:
                    vse_scene.render.image_settings.file_format = "FFMPEG"
                    vse_scene.render.ffmpeg.format = "MPEG4"
                    vse_scene.render.ffmpeg.constant_rate_factor = "PERC_LOSSLESS"  # "PERC_LOSSLESS"
                    vse_scene.render.ffmpeg.gopsize = 5  # keyframe interval
                    vse_scene.render.ffmpeg.audio_codec = "AAC"
        else:
            vse_scene.render.image_settings.file_format = "PNG"  # wkipwkipwkip mettre project info

        vse_scene.render.filepath = output_filepath
        vse_scene.render.use_file_extension = False

        # change color tone mode to prevent washout bug (usually with "filmic" mode)
        vse_scene.view_settings.view_transform = "Filmic"  # "raw"

        bgClip = None
        if "" != self.inputBGMediaPath:
            try:
                #    print(f"self.inputBGMediaPath: {self.inputBGMediaPath}")
                bgClip = self.createNewClip(vse_scene, self.inputBGMediaPath, 1, atFrame=importAtFrame)
            #    print("BG Media OK")
            except Exception as e:
                print(f" *** Rendered shot not found: {self.inputBGMediaPath}")

            # bgClip = None
            # if os.path.exists(self.inputBGMediaPath):
            #     bgClip = self.createNewClip(vse_scene, self.inputBGMediaPath, 1, 1)
            # else:
            #     print(f" *** Rendered shot not found: {self.inputBGMediaPath}")

            #    print(f"self.inputBGMediaPath: {self.inputOverMediaPath}")

            if bgClip is not None:
                if output_res[0] < self.inputBGResolution[0] or output_res[1] < self.inputBGResolution[1]:
                    bgClip.use_crop = True
                    bgClip.crop.min_x = int((self.inputBGResolution[0] - output_res[0]) / 2)
                    bgClip.crop.max_x = bgClip.crop.min_x
                    bgClip.crop.min_y = int((self.inputBGResolution[1] - output_res[1]) / 2)
                    bgClip.crop.max_y = bgClip.crop.min_y

        if "" != self.inputOverMediaPath:
            overClip = None
            try:
                overClip = self.createNewClip(vse_scene, self.inputOverMediaPath, 2, atFrame=importAtFrame)
            #    print("Over Media OK")
            except Exception as e:
                print(f" *** Rendered shot not found: {self.inputOverMediaPath}")
            # overClip = None
            # if os.path.exists(self.inputOverMediaPath):
            #     overClip = self.createNewClip(vse_scene, self.inputOverMediaPath, 2, 1)
            # else:
            #     print(f" *** Rendered shot not found: {self.inputOverMediaPath}")

            if overClip is not None:
                # if output_res[0] < self.inputOverResolution[0] or output_res[1] < self.inputOverResolution[1]:
                if output_res[0] != self.inputOverResolution[0] or output_res[1] != self.inputOverResolution[1]:
                    overClip.use_crop = True
                    overClip.crop.min_x = int((self.inputOverResolution[0] - output_res[0]) / 2)
                    overClip.crop.max_x = overClip.crop.min_x
                    overClip.crop.min_y = int((self.inputOverResolution[1] - output_res[1]) / 2)
                    overClip.crop.max_y = overClip.crop.min_y
                    overClip.blend_type = "OVER_DROP"

        if self.inputAudioMediaPath is not None:
            if specificFrame is None:
                audioClip = None
                if os.path.exists(self.inputAudioMediaPath):
                    audioClip = self.createNewClip(vse_scene, self.inputAudioMediaPath, 3, atFrame=importAtFrame)
                else:
                    print(f" *** Rendered shot not found: {self.inputAudioMediaPath}")

        # bpy.context.scene.sequence_editor.sequences
        # get res of video: bpy.context.scene.sequence_editor.sequences[1].elements[0].orig_width
        # ne marche que sur vidéos

        # Make "My New Scene" the active one
        bpy.context.window.scene = vse_scene
        if specificFrame is None:
            bpy.ops.render.opengl(animation=True, sequencer=True)
        else:
            vse_scene.frame_set(specificFrame)
            # bpy.ops.render.render(write_still=True)
            bpy.ops.render.opengl(animation=False, sequencer=True, write_still=True)

        if not config.devDebug_keepVSEContent:
            bpy.ops.scene.delete()

        bpy.context.window.scene = previousScene

        # print(f" *** Current Workspace: {bpy.context.workspace.name}")

        # bpy.context.window.screen.name = previousScreen
        bpy.context.window.workspace = bpy.data.workspaces[previousWorkspace]
        # print(f" *** Current Workspace: {bpy.context.workspace.name}")

        bpy.context.window.screen = bpy.context.window_manager.windows[0].screen
        bpy.context.window.screen = bpy.data.screens[previousScreen]
        # bpy.context.window_manager.windows[1].screen = bpy.data.screens[previousScreen]

        if region and previousRenderView is not None:
            region.view_perspective = previousRenderView

        # testDir = "Z:\\UAS_ShotManager_Data\\"
        # bpy.ops.image.open(filepath="//Main_Take0010.png", directory=testDir, files=[{"name":"Main_Take0010.png", "name":"Main_Take0010.png"}],
        #   relative_path=True, show_multiview=False)
        # bpy.ops.image.open(
        #     filepath="//SceneRace_Sh0020_0079.png",
        #     directory="C:\\tmp02\\Main_Take\\",
        #     files=[{"name": "SceneRace_Sh0020_0079.png", "name": "SceneRace_Sh0020_0079.png"}],
        #     relative_path=True,
        #     show_multiview=False,
        # )

        # open rendered media in a player
        if specificFrame is not None:
            utils.openMedia(output_filepath, inExternalPlayer=False)
