import bpy


def jump_to_shot(self):

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

    scene = bpy.context.scene
    props = scene.UAS_shot_manager_props
    shotList = props.get_shots()
    current_shot_index = props.current_shot_index
    props.restartPlay = False

    # if scene.frame_end == scene.frame_current or scene.frame_preview_end == scene.frame_current:
    #     print(" *** *** End of range reached: ", scene.frame_current)
    #     print("\n")

    if bpy.context.screen.is_animation_playing:
        ##   print(" *** Playing - after return, frame: ", scene.frame_current)
        if shotList[current_shot_index].end + 1 == scene.frame_current:
            if verbose:
                print("Just after shot end, jumping to next shot start: ", scene.frame_current)

            next_shot = getNextShotIndex(shotList, current_shot_index)
            if next_shot != -1:
                current_shot_index = next_shot
                props.current_shot_index = current_shot_index
                scene.frame_current = shotList[current_shot_index].start

        elif not (
            shotList[current_shot_index].start <= scene.frame_current
            and scene.frame_current <= shotList[current_shot_index].end
        ):
            if verbose:
                print(" *** Not in the range of current shot : ", scene.frame_current)

            # jog backward, go to previous shot
            # if scene.frame_current < shotList[current_shot_index].start:
            #     previous_shot = getNextShotIndex(shotList, current_shot_index)
            #     if previous_shot != -1:
            #         current_shot_index = previous_shot
            #         props.current_shot_index = current_shot_index
            #         scene.frame_current = shotList[current_shot_index].end

            # # jog forward

            # # play
            # else:
            frameAndShotToUse = getFirstShotFrameIfEndReached(scene.frame_current)
            if -1 != frameAndShotToUse[1]:
                scene.frame_current = frameAndShotToUse[0]
                current_shot_index = frameAndShotToUse[1]
                props.current_shot_index = current_shot_index

            else:
                #      print(" *** Not End frame: ", scene.frame_current)
                scene.frame_current = shotList[current_shot_index].start

        else:
            if verbose:
                print(" *** In a shot range : ", scene.frame_current)
            # test if end of range is reached and if so returns the computed index of the next frame, None otherwise
            frameAndShotToUse = getFirstShotFrameIfEndReached(scene.frame_current)
            if -1 != frameAndShotToUse[1]:
                scene.frame_current = frameAndShotToUse[0]
                current_shot_index = frameAndShotToUse[1]
                props.current_shot_index = current_shot_index
            # else we continue as normal

    # not playing
    else:
        if verbose:
            print(" ùùù NOT Playing - after return, frame: ", scene.frame_current)
        # having a separation between playing and not playing is very important to let the
        # shot manager playbar buttons work. They work without the time range restrictions.
        pass

    if shotList[current_shot_index].camera is not None:
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
