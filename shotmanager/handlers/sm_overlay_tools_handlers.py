# GPLv3 License
#
# Copyright (C) 2021 Ubisoft
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Handlers specific to overlay tools
"""

import bpy

from shotmanager.utils import utils_handlers


from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


def install_handler_for_shot(self, context):
    """Called in the update function of WindowManager.UAS_shot_manager_shots_play_mode"""
    scene = context.scene
    props = config.getAddonProps(scene)

    props.setResolutionToScene()

    if (
        self.UAS_shot_manager_shots_play_mode
        and shotMngHandler_frame_change_pre_jumpToShot not in bpy.app.handlers.frame_change_pre
    ):
        shots = props.get_shots()
        for i, shot in enumerate(shots):
            if shot.start <= scene.frame_current <= shot.end:
                props.current_shot_index = i
                break
        bpy.app.handlers.frame_change_pre.append(shotMngHandler_frame_change_pre_jumpToShot)
    #     bpy.app.handlers.frame_change_post.append(shotMngHandler_frame_change_pre_jumpToShot__frame_change_post)

    #    bpy.ops.uas_shot_manager.sequence_timeline ( "INVOKE_DEFAULT" )
    elif (
        not self.UAS_shot_manager_shots_play_mode
        and shotMngHandler_frame_change_pre_jumpToShot in bpy.app.handlers.frame_change_pre
    ):
        utils_handlers.removeAllHandlerOccurences(
            shotMngHandler_frame_change_pre_jumpToShot, handlerCateg=bpy.app.handlers.frame_change_pre
        )
        # utils_handlers.removeAllHandlerOccurences(
        #     shotMngHandler_frame_change_pre_jumpToShot__frame_change_post, handlerCateg=bpy.app.handlers.frame_change_post
        # )


def toggle_overlay_tools_display(context):
    # print("  toggle_overlay_tools_display:  self.UAS_shot_manager_display_overlay_tools: ", self.UAS_shot_manager_display_overlay_tools)
    prefs = config.getAddonPrefs()
    from shotmanager.overlay_tools.interact_shots_stack.shots_stack import display_state_changed_intShStack

    if context.window_manager.UAS_shot_manager_display_overlay_tools:
        if prefs.toggle_overlays_turnOn_sequenceTimeline:
            a = bpy.ops.uas_shot_manager.sequence_timeline("INVOKE_DEFAULT")

        if prefs.toggle_overlays_turnOn_interactiveShotsStack:
            display_state_changed_intShStack(context)
    #         context.window_manager.UAS_shot_manager__useInteracShotsStack = True

    # bpy.ops.uas_shot_manager.draw_camera_hud_in_viewports("INVOKE_DEFAULT")
    else:
        if prefs.toggle_overlays_turnOn_sequenceTimeline:
            a = bpy.ops.uas_shot_manager.sequence_timeline("INVOKE_DEFAULT")

        if prefs.toggle_overlays_turnOn_interactiveShotsStack:
            #         context.window_manager.UAS_shot_manager__useInteracShotsStack = False
            display_state_changed_intShStack(context)

        pass
        # print(f"a operator timeline not updated")

        # bpy.ops.uas_shot_manager.sequence_timeline.cancel(context)
        # print(f"a b operator timeline not updated")
    # pistes pour killer un operateur:
    #   - mettre un Poll
    #   - faire un return Cancel dans le contenu
    #   - killer, d'une maniere ou d'une autre

    # redraw all
    # print("REdraw all attempt **********************************")
    # for area in context.screen.areas:
    #     area.tag_redraw()
    # context.scene.frame_current = context.scene.frame_current


def shotMngHandler_frame_change_pre_jumpToShot(scene):
    props = config.getAddonProps(scene)

    def _get_range_start():
        return scene.frame_preview_start if scene.use_preview_range else scene.frame_start

    def _get_range_end():
        return scene.frame_preview_end if scene.use_preview_range else scene.frame_end

    def _get_previous_shot(shots, current_shot_index):
        index = current_shot_index
        if index > 0:
            previous_shots = [s for s in shots[:index] if s.enabled]
            if len(previous_shots):
                return previous_shots[-1]

        return None

    def _get_next_shot(shots, current_shot_index):
        """If next shot is out of the anim range then return None"""
        index = current_shot_index + 1
        # if index < len(shots) - 1:
        #     next_shots = [s for s in shots[index + 1 :] if s.enabled]
        #     if len(next_shots):
        #         return next_shots[0]

        while index < len(shots):
            if shots[index].enabled:
                if shots[index].start <= _get_range_end() and shots[index].start >= _get_range_start():
                    return shots[index]
                else:
                    return None
            else:
                index += 1
        return None

    def _get_max_start_frame(shot):
        """Return the max between the start of the shot and the start of the anim range"""
        time = _get_range_start()
        if shot.start >= _get_range_start() and shot.start <= _get_range_end():
            time = shot.start
        return time

    def _get_first_continuous_shot_index(shots, current_shot_index):
        """Return the index of the first enabled shot that is:
            - before current_shot_index
            - either completely in the anim range or has just its start out (not the end!)
            - that can be reached by going back in the shot list from current_shot_index without meeting
              a shot that has its end out
        If no such shot is found them we use current shot
        """

        if shots[current_shot_index].start < _get_range_start():
            return current_shot_index

        lastValidShotInd = current_shot_index
        i = current_shot_index - 1
        while 0 <= i:
            if shots[i].enabled:
                if shots[i].end > _get_range_end():
                    break
                if shots[i].end < _get_range_start():
                    break
                if shots[i].start < _get_range_start():
                    lastValidShotInd = i
                    break
                if shots[i].start >= _get_range_start():
                    lastValidShotInd = i
            i -= 1

        return lastValidShotInd

    shotList = props.get_shots()
    if len(shotList) <= 0:
        return

    props.restartPlay = False

    current_shot_index = props.current_shot_index
    current_shot = shotList[current_shot_index]
    current_frame = scene.frame_current

    # clip shot to scene timeframe. Might not be necessary
    current_shot_start = current_shot.start
    current_shot_end = current_shot.end

    if not bpy.context.screen.is_animation_playing:
        return

    if (2, 90, 0) <= bpy.app.version:
        scrubbing = bpy.context.screen.is_scrubbing
    else:
        scrubbing = not bpy.context.screen.is_animation_playing

    #########################################
    ## animation is playing
    #########################################
    if not scrubbing:
        # Order of if clauses is very important.

        #   _logger.debug_ext("*** Not Scrubbing:", col="RED", tag="SHOTS_PLAY_MODE")

        # messages for range start and end
        inforStr = ""
        if _get_range_start() == current_frame:
            inforStr = "  ** Range Start **"
        if _get_range_end() == current_frame:
            inforStr = "  ** Range End **"

        _logger.debug_ext(f"current_frame: {current_frame}  {inforStr}", col="YELLOW", tag="SHOTS_PLAY_MODE")

        if current_frame == current_shot.start:
            _logger.debug_ext(
                f"   current frame is at start of current shot: {current_shot.name}",
                col="GREEN_LIGHT",
                tag="SHOTS_PLAY_MODE",
            )
        elif current_frame == current_shot.end:
            _logger.debug_ext(
                f"   current frame is at end of current shot: {current_frame}", col="ORANGE", tag="SHOTS_PLAY_MODE"
            )

        if current_frame == _get_range_start():
            # we are here when the play head reached the anim range end and has been put back by Blender
            # to the start of the range

            if current_frame == current_shot.start:
                # case where the current shot is not the first one of the edit, starts at the same time as the first one and
                # this time is also the anim range start. Then we want to preserve the current shot
                _logger.debug_ext(
                    f"1 current_frame == range start and current_frame == current_shot.start, current shot: {current_shot.name}",
                    col="GREEN",
                    tag="SHOTS_PLAY_MODE",
                )
                pass
            else:
                lookForFirstShot = True
                if _get_range_end() == current_shot.end:
                    next_shot = _get_next_shot(shotList, current_shot_index)
                    if next_shot is not None:
                        # next_shot_index = props.getShotIndex(next_shot)

                        _logger.debug_ext(
                            f"2 current_frame == range start, current shot: {current_shot.name}, next_shot: {next_shot.name}",
                            col="GREEN",
                            tag="SHOTS_PLAY_MODE",
                        )

                        props.setCurrentShot(next_shot, changeTime=False)
                        scene.frame_current = next_shot.start

                        lookForFirstShot = False

                if lookForFirstShot:
                    # if True:
                    firstShotInd = _get_first_continuous_shot_index(shotList, current_shot_index)
                    _logger.debug_ext(
                        f"3 current_frame == range start, current shot: {current_shot.name}, first conti: {shotList[firstShotInd].name}",
                        col="GREEN",
                        tag="SHOTS_PLAY_MODE",
                    )
                    firstFrame = _get_max_start_frame(shotList[firstShotInd])
                    if current_shot_index != firstShotInd:
                        props.setCurrentShot(shotList[firstShotInd], changeTime=False)
                    # if we put this condition we avoid the frame to be played 2 times but we don't see the new shot becoming current
                    # if firstFrame != current_frame:
                    scene.frame_current = firstFrame
        elif (
            current_frame == _get_range_end() and _get_previous_shot(shotList, current_shot_index) is None
        ):  # While backward playing if we hit the last frame and we are playing the first shot jump to the last shot.
            _logger.debug_ext("current_frame == _get_range_end()", col="PURPLE", tag="SHOTS_PLAY_MODE")
            firstShotInd = _get_first_continuous_shot_index(shotList, current_shot_index)
            firstFrame = _get_max_start_frame(shotList[firstShotInd])
            if current_shot_index != firstShotInd:
                props.setCurrentShot(shotList[firstShotInd], changeTime=False)
            # if we put this condition we avoid the frame to be played 2 times but we don't see the new shot becoming current
            # if firstFrame != current_frame:
            scene.frame_current = firstFrame

            # last_enabled = [s for s in shotList if s.enabled][-1]
            # props.setCurrentShot(last_enabled, changeTime=False)
            # scene.frame_current = last_enabled.end
        elif current_frame > current_shot_end:
            _logger.debug_ext("current_frame > current_shot_end", col="PURPLE", tag="SHOTS_PLAY_MODE")
            disp = current_frame - current_shot_end
            next_shot = _get_next_shot(shotList, current_shot_index)

            if next_shot is None:
                _logger.debug_ext("next shot is none", col="PURPLE", tag="SHOTS_PLAY_MODE")

                firstShotInd = _get_first_continuous_shot_index(shotList, current_shot_index)
                firstFrame = _get_max_start_frame(shotList[firstShotInd])
                if current_shot_index != firstShotInd:
                    props.setCurrentShot(shotList[firstShotInd], changeTime=False)
                # if we put this condition we avoid the frame to be played 2 times but we don't see the new shot becoming current
                # if firstFrame != current_frame:
                scene.frame_current = firstFrame
            else:
                _logger.debug_ext("next shot is NOT none", col="PURPLE", tag="SHOTS_PLAY_MODE")
                if current_shot != next_shot:
                    _logger.debug_ext("   next shot is NOT none 01", col="PURPLE", tag="SHOTS_PLAY_MODE")
                    props.setCurrentShot(next_shot, changeTime=False)
                _logger.debug_ext(f"   next shot is {next_shot.name}", col="PURPLE", tag="SHOTS_PLAY_MODE")
                scene.frame_current = next_shot.start

            # while next_shot is not None:
            #     if disp < next_shot.getDuration():
            #         props.setCurrentShot(next_shot, changeTime=False)
            #         scene.frame_current = next_shot.start + disp
            #         break
            #     disp -= next_shot.getDuration()
            #     next_shot = _get_next_shot(shotList, current_shot_index)
            # else:
            #     # Scene end is farther than the last shot so loop back.
            #     props.setCurrentShot([s for s in shotList if s.enabled][0], changeTime=False)
        elif (
            current_frame == _get_range_start() and _get_next_shot(shotList, current_shot_index) is None
        ):  # While forward playing if we hit the first frame and we are playing the last shot jump to the first shot.
            # Seems that the first frame is always hit even in frame dropping playblack
            _logger.debug_ext("current_frame == _get_range_start()", col="PURPLE")
            props.setCurrentShot([s for s in shotList if s.enabled][0], changeTime=False)
        elif current_frame < current_shot_start:
            _logger.debug_ext("current_frame < current_shot_start", col="ORANGE")
            disp = current_shot_start - current_frame
            previous_shot = _get_previous_shot(shotList, current_shot_index)
            while previous_shot is not None:
                if disp < previous_shot.getDuration():
                    props.setCurrentShot(previous_shot, changeTime=False)
                    scene.frame_current = previous_shot.end - disp
                    break
                disp -= previous_shot.getDuration()
                previous_shot = _get_previous_shot(shotList, current_shot_index)
            else:
                # Scene end is farther than the first shot so loop back.
                last_enabled = [s for s in shotList if s.enabled][-1]
                props.setCurrentShot(last_enabled, changeTime=False)
                scene.frame_current = last_enabled.end
        else:
            # _logger.debug_ext("current_frame Else", col="RED")
            pass

    #########################################
    ## user is scrubbing
    #########################################
    else:
        #   _logger.debug_ext("--- Scrubbing:", col="BLUE", tag="SHOTS_PLAY_MODE")

        # User is scrubbing in the timeline so try to guess a shot in the range of the timeline.
        if not (current_shot.start <= current_frame <= current_shot.end):
            candidates = list()
            for i, shot in enumerate(shotList):
                # wk
                if shot.enabled and shot.start <= current_frame <= shot.end:
                    candidates.append((i, shot))

            if 0 < len(candidates):
                props.setCurrentShot(candidates[0][1], changeTime=False)
                scene.frame_current = current_frame
            else:
                # case were the new current time is out of every shots
                # we then get the first shot BEFORE current time, or the very first shot if there is no shots after
                prevShotInd = props.getFirstShotIndexBeforeFrame(current_frame, ignoreDisabled=True)
                if -1 != prevShotInd:
                    props.setCurrentShot(shotList[prevShotInd], changeTime=False)
                    # don't change current time in order to let the user see changes in the scene
                    # scene.frame_current = shotList[prevShotInd].start
                else:
                    nextShotInd = props.getFirstShotIndexAfterFrame(current_frame, ignoreDisabled=True)
                    if -1 != nextShotInd:
                        props.setCurrentShot(shotList[nextShotInd], changeTime=False)
                        # don't change current time in order to let the user see changes in the scene
                        # scene.frame_current = shotList[nextShotInd].start
                    else:
                        # paf what to do?
                        # props.setCurrentShot(candidates[0][1], changeTime=False)
                        _logger.error("SM: Paf in shotMngHandler_frame_change_pre_jumpToShot: No valid shot found")
