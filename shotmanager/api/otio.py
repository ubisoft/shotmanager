from shotmanager.otio import exportOtio


def export_otio(shot_manager, take_index=-1, render_root_file_path="", fps=-1):
    """ Create an OpenTimelineIO XML file for the specified take
        Return the file path of the created file
    """
    parent_scene = shot_manager.parentScene
    res = exportOtio(parent_scene, takeIndex=take_index, renderRootFilePath=render_root_file_path, fps=fps)
    return res


# wkip to do: add import otio

