from shotmanager.otio import exports


def export_otio(shot_manager, file_path="", file_name="", add_take_name_to_path=False, take_index=-1, fps=-1):
    """ Create an OpenTimelineIO XML file for the specified take
        Return the file path of the created file
        If file_name is left to default then the rendered file will be a .xml
    """
    parent_scene = shot_manager.getParentScene()
    res = exports.exportShotManagerEditToOtio(
        parent_scene,
        filePath=file_path,
        fileName=file_name,
        addTakeNameToPath=add_take_name_to_path,
        takeIndex=take_index,
        fps=fps,
    )
    return res


# wkip to do: add import otio

