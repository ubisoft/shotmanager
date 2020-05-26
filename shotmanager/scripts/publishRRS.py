import bpy
from ..operators import renderProps


def publishRRS(prodFilePath):
    print(" -- * publishRRS * --")

    cacheFilePath = "c:\\tmp\\"

    # batch render to generate the files
    # To do: specify the take?

    # renderProps.launchRender("PROJECT", renderRootFilePath=cacheFilePath)
    scene = bpy.context.scene
    renderedFilesList = renderProps.launchRenderWithVSEComposite("PROJECT", renderRootFilePath=cacheFilePath)

    # generate the otio file

    # projProp_fps = json.loads( os.environ['UAS_PROJECT_FRAMERATE'] )
    # wkip beurk pour récuperer le bon contexte de scene
    bpy.context.window.scene = scene
    renderedOtioFile = renderProps.exportOtio(scene, renderRootFilePath=cacheFilePath)

    renderedFilesList.append(renderedOtioFile)

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
        print("target: ", target)
        try:
            shutil.copyfile(f, target)
        except Exception as e:
            print("*** File cannot be copied: ", e)
