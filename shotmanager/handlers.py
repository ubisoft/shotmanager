import bpy


def jump_to_shot(self):
    def getNextShotIndex(shots, current_index):
        next_index = (current_shot_index + 1) % len(shots)
        while current_index != next_index:
            if shots[next_index].enabled:
                return next_index
            next_index = (next_index + 1) % len(shots)

        return -1

    def getFirstRangeFrameIfEndReached():
        firstFrameToUse = -1
        firstRangeFrame = -1

        if (scene.use_preview_range and scene.frame_preview_end <= scene.frame_current) or (
            not scene.use_preview_range and scene.frame_end <= scene.frame_current
        ):
            print(" *** End frame: ", scene.frame_current)
            startRangeFrame = scene.frame_preview_start if scene.use_preview_range else scene.frame_start
            firstShotIndContainingFrame = props.getFirstShotIndexContainingFrame(startRangeFrame, ignoreDisabled=True)

            # wkip warning: firstShotIndContainingFrame peut etre -1 car pas de shot sous cette frame. Prendre alors le premier shot qui vient après

            if -1 == firstShotIndContainingFrame:
                firstShotIndAfterFrame = props.getFirstShotIndexAfterFrame(
                    firstShotIndContainingFrame, ignoreDisabled=True
                )

            # newFrame = shotList[firstShotIndContainingFrame].start
            newFrame = max(startRangeFrame)
            print("newFrame: ", newFrame)
            # firstRangeFrame = newFrame


        # else:
        #     print(" *** Not End frame: ", scene.frame_current)
        #     firstRangeFrame = shotList[current_shot_index].start

        # -1 mal choisit!!!!
        return firstRangeFrame

    scene = bpy.context.scene
    props = scene.UAS_shot_manager_props
    shotList = props.get_shots()
    current_shot_index = props.current_shot_index
    props.restartPlay = False

    if scene.frame_end == scene.frame_current or scene.frame_preview_end == scene.frame_current:
        print(" *** *** End frame: ", scene.frame_current)
        print("\n")
    #     props.restartPlay = True
    #  bpy.app.handlers.frame_change_pre.remove(jump_to_shot)
    #     return ()
    #        bpy.app.handlers.frame_change_pre.append(jump_to_shot__frame_change_post)

    print(" *** after return ")
    if shotList[current_shot_index].end + 1 == scene.frame_current:
        print("Just after end: ", scene.frame_current)
        next_shot = getNextShotIndex(shotList, current_shot_index)
        if next_shot != -1:
            current_shot_index = next_shot
            props.current_shot_index = current_shot_index
            scene.frame_current = shotList[current_shot_index].start

    elif not shotList[current_shot_index].start <= scene.frame_current <= shotList[current_shot_index].end:
        firstRangeFrame = getFirstRangeFrameIfEndReached()
        if -1 != firstRangeFrame:
            scene.frame_current = firstRangeFrame
        else:
            print(" *** Not End frame: ", scene.frame_current)
            firstRangeFrame = shotList[current_shot_index].start

    else:
        print("Fr: ", scene.frame_current)
        firstRangeFrame = getFirstRangeFrameIfEndReached()
        if -1 != firstRangeFrame:
            scene.frame_current = firstRangeFrame

    if shotList[current_shot_index].camera is not None:
        scene.camera = shotList[current_shot_index].camera
        props.selected_shot_index = current_shot_index


def jump_to_shot__frame_change_post(self):
    scene = bpy.context.scene
    props = scene.UAS_shot_manager_props
    print("jump_to_shot__frame_change_post, fr: ", scene.frame_current)
    if props.restartPlay:
        props.restartPlay = False
        #  bpy.app.handlers.frame_change_pre.append(jump_to_shot)
        pass
