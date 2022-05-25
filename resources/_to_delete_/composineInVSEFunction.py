# NOTE: This function is NOT called by the render functions of SM so far...
    def compositeMedia(
        self,
        scene,
        fps=None,
        bg_file=None,
        bg_res=None,
        fg_file=None,
        fg_res=None,
        audio_file=None,
        output_file=None,
        frame_start=None,
        frame_end=None,
        postfix_scene_name="",
        output_resolution=None,
        import_at_frame=1,
        clean_temp_scene=True,
    ):
        """High level function used to create a media from a background and foreground media and a sound

        This function will set the internal bg and fg media of the vse_render class and will call compositeVideoInVSE()
        Not set values are taken from scene

        This function is NOT used !!!

        Args:
            output_resolution: array [width, height]
        """
        self.clearMedia()

        if bg_file is not None:
            self.inputBGMediaPath = bg_file
        if bg_res is not None:
            self.inputBGResolution = bg_res

        if fg_file is not None:
            self.inputOverMediaPath = fg_file
        if fg_res is not None:
            self.inputOverResolution = fg_res

        if audio_file is not None:
            self.inputAudioMediaPath = audio_file

        self.compositeVideoInVSE(
            # scene.render.fps if fps is None else fps,
            utils.getSceneEffectiveFps(scene) if fps is None else fps,
            scene.frame_start if frame_start is None else frame_start,
            scene.frame_end if frame_end is None else frame_end,
            output_file,
            postfixSceneName=postfix_scene_name,
            output_resolution=output_resolution,
            importAtFrame=import_at_frame,
        )

        if clean_temp_scene:
            scenesToDelete = [
                s
                for s in bpy.data.scenes
                if (s.name.startswith("Tmp_VSE_RenderScene") or s.name.startswith("VSE_SequenceRenderScene"))
            ]
            for s in scenesToDelete:
                bpy.data.scenes.remove(s, do_unlink=True)

