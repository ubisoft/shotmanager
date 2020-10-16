import bpy


def jump_to_shot(scene):

    verbose = False

    def getPreviousShotIndex(shots, current_index):
        previous_index = (current_shot_index - 1) % len(shots)
        while current_index != previous_index:
            if shots[previous_index].enabled:
                return previous_index
            previous_index = (previous_index - 1) % len(shots)

        return -1

    def getNextShotIndex(shots, current_index):
        next_index = (current_shot_index + 1) % len(shots)
        while current_index != next_index:
            if shots[next_index].enabled:
                return next_index
            next_index = (next_index + 1) % len(shots)

        return -1

    def getFirstShotFrameIfEndReached(currentFrame):
        """ Return an array with next frame and next shot index.
            Next frame is current frame if no frame is found
            Next shot index is -1 if not found
        """
        # print("   getFirstShotFrameIfEndReached, currentFrame: ", currentFrame)
        frameAndShotToUse = [currentFrame, -1]
        firstShotIndContainingFrame = -1

        if (scene.use_preview_range and scene.frame_preview_end <= currentFrame) or (
            not scene.use_preview_range and scene.frame_end <= currentFrame
        ):
            if verbose:
                print("        *** getFirstShotFrameIfEndReached Current frame at end of range : ", currentFrame)
            startRangeFrame = scene.frame_preview_start if scene.use_preview_range else scene.frame_start
            if verbose:
                print("        startRangeFrame: ", startRangeFrame)
            firstShotIndContainingFrame = props.getFirstShotIndexContainingFrame(startRangeFrame, ignoreDisabled=True)

            # if shot found
            if -1 != firstShotIndContainingFrame:
                if verbose:
                    print("       firstShotIndContainingFrame for start range frame: ", firstShotIndContainingFrame)
                frameAndShotToUse = [startRangeFrame, firstShotIndContainingFrame]
            else:
                if verbose:
                    print("       No firstShotIndContainingFrame for frame: ", startRangeFrame)
                firstShotIndAfterFrame = props.getFirstShotIndexAfterFrame(startRangeFrame, ignoreDisabled=True)
                if -1 != firstShotIndAfterFrame:
                    endRangeFrame = scene.frame_preview_end if scene.use_preview_range else scene.frame_end
                    if shotList[firstShotIndAfterFrame].start > endRangeFrame:
                        # found shot is out of range
                        frameAndShotToUse = [currentFrame, -1]
                    else:
                        frameAndShotToUse = [shotList[firstShotIndAfterFrame].start, firstShotIndAfterFrame]

                    if verbose:
                        print("       frameAndShotToUse for shot after: ", frameAndShotToUse)
                else:
                    frameAndShotToUse = [currentFrame, -1]

                # if firstShotIndAfterFrame trop grand...
            # wkip warning: firstShotIndContainingFrame peut etre -1 car pas de shot sous cette frame. Prendre alors le premier shot qui vient après

        # else:
        #     print(" *** Not End frame: ", scene.frame_current)
        #     firstRangeFrame = shotList[current_shot_index].start

        # -1 mal choisit!!!!

        return frameAndShotToUse

    props = scene.UAS_shot_manager_props
    shotList = props.get_shots()
    current_shot_index = props.current_shot_index
    old_shot_index = current_shot_index
    props.restartPlay = False

    # if scene.frame_end == scene.frame_current or scene.frame_preview_end == scene.frame_current:
    #     print(" *** *** End of range reached: ", scene.frame_current)
    #     print("\n")
    current_frame = scene.frame_current
    current_shot_end = shotList[ current_shot_index ].end


    if bpy.context.screen.is_animation_playing:
        ##   print(" *** Playing - after return, frame: ", scene.frame_current)
        print ( shotList[  current_shot_index ].name )
        if not shotList[current_shot_index].start < current_frame < current_shot_end:
            if current_frame > current_shot_end:
                disp = current_frame - current_shot_end
                next_shot_index = getNextShotIndex ( shotList, current_shot_index )
                while next_shot_index != -1:
                    shot = shotList[ next_shot_index ]
                    if disp < shot.getDuration ( ):
                        current_shot_index = next_shot_index
                        props.setCurrentShot ( shot )
                        scene.frame_current = shot.start + disp
                        break

                    disp -= shot.getDuration ( )
                    next_shot_index = getNextShotIndex ( shotList, next_shot_index )
                else:
                    pass #end of timeline
    # not playing
    else:
        if verbose:
            print(" ùùù NOT Playing - after return, frame: ", scene.frame_current)
        # having a separation between playing and not playing is very important to let the
        # shot manager playbar buttons work. They work without the time range restrictions.

    if old_shot_index != current_shot_index:
        if -1 < current_shot_index and shotList[current_shot_index].camera is not None:
            if scene.camera != shotList[current_shot_index].camera:
                scene.camera = shotList[current_shot_index].camera
            props.selected_shot_index = current_shot_index


# def jump_to_shot__frame_change_post(self):
#     scene = bpy.context.scene
#     props = scene.UAS_shot_manager_props
#     print("jump_to_shot__frame_change_post, fr: ", scene.frame_current)
#     if props.restartPlay:
#         props.restartPlay = False
#         #  bpy.app.handlers.frame_change_pre.append(jump_to_shot)
#         pass
