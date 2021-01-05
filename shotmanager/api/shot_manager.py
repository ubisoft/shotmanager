import bpy


def get_shot_manager(scene):
    return scene.UAS_shot_manager_props


def initialize_shot_manager(shot_manager):
    shot_manager.initialize_shot_manager()


def get_parent_scene(shot_manager):
    return shot_manager.getParentScene()


def get_warnings(shot_manager):
    """ Return an array with all the warnings
    """
    if shot_manager is not None:
        return shot_manager.getWarnings(shot_manager.getParentScene())
    else:
        return None


# takes
#############


def get_unique_take_name(shot_manager, name):
    return shot_manager.getUniqueTakeName(name)


def get_takes(shot_manager):
    return shot_manager.takes


def get_take_by_index(shot_manager, take_index):
    """ Return the take corresponding to the specified index
    """
    return shot_manager.getTakeByIndex(take_index)


def get_take_index(shot_manager, take):
    return shot_manager.getTakeIndex(take)


def get_current_take_index(shot_manager):
    return shot_manager.getCurrentTakeIndex()


def set_current_take_by_index(shot_manager, current_take_index):
    shot_manager.setCurrentTakeByIndex(current_take_index)


def get_current_take(shot_manager):
    return shot_manager.getCurrentTake()


def get_current_take_name(shot_manager):
    """ Return the name of the current take, 
    """
    return shot_manager.getCurrentTakeName()


def add_take(shot_manager, at_index=-1, name="New Take"):
    """ Add a new take after the current take if possible or at the end of the take list otherwise
        Return the newly added take. If it is the only take of the Shot Manager then its name will be "Main Take"
    """
    return shot_manager.addTake(atIndex=at_index, name=name)


def copy_take(shot_manager, take, at_index=-1, copy_camera=False):
    """ Copy a take after the current take if possible or at the end of the takes list otherwise
        Return the newly added take
    """
    return shot_manager.copyTake(take, atIndex=at_index, copyCamera=copy_camera)


####################
# shots
####################


def get_unique_shot_name(shot_manager, name, take_index):
    return shot_manager.getUniqueShotName(shot_manager, name, takeIndex=take_index)


def add_shot(
    shot_manager,
    at_index=-1,
    take_index=-1,
    name="defaultShot",
    start=10,
    end=20,
    camera=None,
    color=(0.2, 0.6, 0.8, 1),
    enabled=True,
):
    """ Add a new shot after the current shot if possible or at the end of the shot list otherwise (case of an add in a take
        that is not the current one)
        Return the newly added shot
        Since this function works also with takes that are not the current one the current shot is not taken into account not modified
    """
    return shot_manager.addShot(
        atIndex=at_index,
        takeIndex=take_index,
        name=name,
        start=start,
        end=end,
        camera=camera,
        color=color,
        enabled=enabled,
    )


def copy_shot(shot_manager, shot, at_index=-1, target_take_index=-1, copy_camera=False):
    """ Copy a shot after the current shot if possible or at the end of the shot list otherwise (case of an add in a take
        that is not the current one)
        Return the newly added shot
        Since this function works also with takes that are not the current one the current shot is not taken into account not modified
    """
    return shot_manager.copyShot(shot, atIndex=at_index, targetTakeIndex=target_take_index, copyCamera=copy_camera)


def remove_shot(shot_manager, shot):
    shot_manager.removeShot(shot)


def move_shot_to_index(shot_manager, shot, new_index):
    shot_manager.moveShotToIndex(shot, new_index)


def set_current_shot_by_index(shot_manager, current_shot_index):
    """ Changing the current shot doesn't affect the selected one
    """
    return shot_manager.setCurrentShotByIndex(current_shot_index)


def set_current_shot(shot_manager, current_shot):
    return shot_manager.setCurrentShot(current_shot)


def get_shot_index(shot_manager, shot, take_index=-1):
    return shot_manager.getShotIndex(shot, takeIndex=take_index)


def get_shot(shot_manager, shot_index, ignore_disabled=False, take_index=-1):
    return shot_manager.getShotByIndex(shot_index, ignoreDisabled=ignore_disabled, takeIndex=take_index)


def get_shot_by_name(shot_manager, shot_name, ignore_disabled=False, takeIndex=-1):
    return shot_manager.getShotByName(shot_name, ignoreDisabled=ignore_disabled, takeIndex=takeIndex)


def get_shots(shot_manager, take_index=-1):
    """ Return the actual shots array of the specified take
    """
    return shot_manager.get_shots(takeIndex=take_index)


def get_shots_list(shot_manager, ignore_disabled=False, take_index=-1):
    """ Return a filtered shots array of the specified take
    """
    return shot_manager.getShotsList(ignoreDisabled=ignore_disabled, takeIndex=take_index)


def get_num_shots(shot_manager, ignore_disabled=False, take_index=-1):
    """ Return the number of shots of the specified take
    """
    return shot_manager.getNumShots(ignoreDisabled=ignore_disabled, takeIndex=take_index)


def get_current_shot_index(shot_manager, ignore_disabled=False, take_index=-1):
    """ Return the index of the current shot in the enabled shot list of the current take
        Use this function instead of a direct call to shot_manager.current_shot_index
        
        if ignoreDisabled is false (default) then the shot index is relative to the whole shot list,
            otherwise it is relative to the list of the enabled shots
        can return -1 if all the shots are disabled!!
        if takeIndex is different from the current take then it returns -1 because other takes than the current one are not supposed to
        have a current shot
    """
    return shot_manager.getCurrentShotIndex(ignoreDisabled=ignore_disabled, takeIndex=take_index)


def get_current_shot(shot_manager):
    return shot_manager.getCurrentShot()


def get_first_shot_index(shot_manager, ignore_disabled=False, take_index=-1):
    return shot_manager.getFirstShotIndex(ignoreDisabled=ignore_disabled, takeIndex=take_index)


# # can return -1 if all the shots are disabled!!
# def getCurrentShotIndexInEnabledList( shot_manager ):
#     currentIndexInEnabledList = shot_manager.current_shot_index
#     #for i, shot in enumerate ( shot_manager.context.scene.UAS_shot_manager_props.takes[shot_manager.context.scene.UAS_shot_manager_props.current_take_name].shots ):
#     for i in range(shot_manager.current_shot_index + 1):
#         if not shot_manager.takes[shot_manager.current_take_name].shots[i].enabled:
#             currentIndexInEnabledList -= 1

#     return currentIndexInEnabledList
def get_last_shot_index(shot_manager, ignore_disabled=False, take_index=-1):
    return shot_manager.getLastShotIndex(ignoreDisabled=ignore_disabled, takeIndex=take_index)


def get_first_shot(shot_manager, ignore_disabled=False, take_index=-1):
    return shot_manager.getFirstShot(ignoreDisabled=ignore_disabled, takeIndex=take_index)


def get_last_shot(shot_manager, ignore_disabled=False, take_index=-1):
    return shot_manager.getLastShot(ignoreDisabled=ignore_disabled, takeIndex=take_index)


# currentShotIndex is given in the WHOLE list of shots (including disabled)
# returns the index of the previous enabled shot in the WHOLE list, -1 if none
def get_previous_enabled_shot_index(shot_manager, current_shot_index, take_index=-1):
    return shot_manager.getPreviousEnabledShotIndex(current_shot_index, takeIndex=take_index)


# currentShotIndex is given in the WHOLE list of shots (including disabled)
# returns the index of the next enabled shot in the WHOLE list, -1 if none
def get_next_enabled_shot_index(shot_manager, current_shot_index, take_index=-1):
    return shot_manager.getNextEnabledShotIndex(current_shot_index, takeIndex=take_index)


def delete_shot_camera(shot_manager, shot):
    """ Check in all takes if the camera is used by another shot and if not then delete it
    """
    return shot_manager.deleteShotCamera(shot)


###############
# functions working only on current take !!!
###############


def get_shots_play_mode(shot_manager):
    """ Return True if the Shots Play Mode is active, False otherwise
        Warning: Currently the play mode status is shared between all the scenes of the file,
        it is not (yet) specific to an instance of shot manager.
    """
    return bpy.context.window_manager.UAS_shot_manager_shots_play_mode


def set_shots_play_mode(shot_manager, activate):
    """ Set to True to have the Shots Play Mode active, False otherwise
        Warning: Currently the play mode status is shared between all the scenes of the file,
        it is not (yet) specific to an instance of shot manager.
    """
    bpy.context.window_manager.UAS_shot_manager_shots_play_mode = activate


def go_to_previous_shot(shot_manager, current_frame):
    """ 
        works only on current take
        behavior of this button:
        if current shot is enabled:
        - first click: put current time at the start of the current enabled shot
        else:
        - fisrt click: put current time at the end of the previous enabled shot
    """
    return shot_manager.goToPreviousShot(current_frame)


# works only on current take
def go_to_next_shot(shot_manager, current_frame):
    return shot_manager.goToNextShot(current_frame)


# works only on current take
# behavior of this button:
#  if current shot is enabled:
#   - first click: put current time at the start of the current enabled shot
#  else:
#   - fisrt click: put current time at the end of the previous enabled shot


def go_to_previous_frame(shot_manager, current_frame):
    #  print(" ** -- ** goToPreviousFrame")
    return shot_manager.goToPreviousFrame(current_frame)


# works only on current take
def go_to_next_frame(shot_manager, current_frame):
    #   print(" ** -- ** goToNextShot")
    return shot_manager.goToNextFrame(current_frame)


# works only on current take
def get_first_shot_index_containing_frame(shot_manager, frame_index, ignore_disabled=False):
    """Return the first shot containing the specifed frame, -1 if not found
    """
    return shot_manager.getFirstShotIndexContainingFrame(frame_index, ignoreDisabled=ignore_disabled)


# works only on current take
def get_first_shot_index_after_frame(shot_manager, frame_index, ignore_disabled=False):
    """Return the first shot after the specifed frame (supposing thanks to getFirstShotIndexContainingFrame than 
        frameIndex is not in a shot), -1 if not found
    """
    return shot_manager.getFirstShotIndexAfterFrame(frame_index, ignoreDisabled=ignore_disabled)


def get_shots_using_camera(cam, ignore_disabled=False, take_index=-1):
    """ Return the list of all the shots used by the specified camera in the specified take
    """
    return shot_manager.getShotsUsingCamera(self, cam, ignoreDisabled=ignore_disabled, takeIndex=take_index)


####################
# editing
####################


def get_edit_duration(shot_manager, take_index):
    """ Return edit duration in frames
    """
    return shot_manager.getEditDuration(takeIndex=take_index)


def get_edit_time(shot_manager, reference_shot, frame_index_in_3D_time, reference_level="TAKE"):
    """ Return edit current time in frames, -1 if no shots or if current shot is disabled
        Works on the take from which referenceShot is coming from.
        Disabled shots are always ignored and considered as not belonging to the edit.
        reference_level can be "TAKE" or "GLOBAL_EDIT"
        wkip negative times issues coming here... :/
    """
    return shot_manager.getEditTime(reference_shot, frame_index_in_3D_time, referenceLevel=reference_level)


def get_edit_current_time(shot_manager, reference_level="TAKE"):
    """ Return edit current time in frames, -1 if no shots or if current shot is disabled
        works only on current take
        reference_level can be "TAKE" or "GLOBAL_EDIT"
        wkip negative times issues coming here... :/
    """
    return shot_manager.getEditCurrentTime(referenceLevel=reference_level)
