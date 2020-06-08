import bpy
from ..operators import renderProps


def publishRRS(prodFilePath, verbose=False):
    scene = bpy.context.scene

    if "UAS_shot_manager_props" not in scene:
        print("\n*** publishRRS failed: No UAS_shot_manager_prop found in the scene ***\n")
        return False

    props = scene.UAS_shot_manager_props

    print("\n---------------------------------------------------------")
    print(" -- * publishRRS * --\n\n")

    cacheFilePath = "c:\\tmp\\"

    if verbose:
        print("Local cache path: ", cacheFilePath)
        print("Current Scene: " + scene.name + ", current take: " + props.getCurrentTakeName())

    print("\n---------------------------------------------------------")

    # batch render to generate the files
    # To do: specify the take?

    # renderProps.launchRender("PROJECT", renderRootFilePath=cacheFilePath)
    renderedFilesList = renderProps.launchRenderWithVSEComposite("PROJECT", renderRootFilePath=cacheFilePath)

    # generate the otio file

    # projProp_fps = json.loads( os.environ['UAS_PROJECT_FRAMERATE'] )
    # wkip beurk pour récuperer le bon contexte de scene
    bpy.context.window.scene = scene
    renderedOtioFile = renderProps.exportOtio(scene, renderRootFilePath=cacheFilePath)

    renderedFilesList.append(renderedOtioFile)

    if verbose:
        print("\nNewMediaList = ", renderedFilesList)

    # copy files to the network

    # Wkip to do: exclude .png
    # from distutils.dir_util import copy_tree
    # copy_tree(cacheFilePath, prodFilePath, update=1)

    import shutil
    import os

    for f in renderedFilesList:
        head, tail = os.path.split(f)
        target = prodFilePath
        if not target.endswith("\\"):
            target += "\\"
        target += tail

        if verbose:
            print("target: ", target)
        try:
            shutil.copyfile(f, target)
        except Exception as e:
            print("*** File cannot be copied: ", e)

    return True
