import bpy
from ..operators import renderProps

import os
import json


def verbose_set(key: str, default: bool, override: str, verbose: bool = True) -> None:
    default_value = str(default)
    if key in os.environ.keys():
        if override and os.environ[key] != default_value:
            if verbose:
                print(f"Overrinding value for '{key}': {default}")
            os.environ[key] = default_value
        return  # already set

    if verbose:
        print(f"Key '{key}' not in the default environment, setting it to {default_value}")
    os.environ[key] = default_value


def setup_project_env(override_existing: bool, verbose: bool = True) -> None:

    verbose_set("UAS_PROJECT_NAME", "RRSpecial", override_existing, verbose)
    verbose_set("UAS_PROJECT_FRAMERATE", "25.0", override_existing, verbose)
    verbose_set("UAS_PROJECT_RESOLUTION", "[1280,720]", override_existing, verbose)
    verbose_set("UAS_PROJECT_RESOLUTIONFRAMED", "[1280,960]", override_existing, verbose)
    verbose_set("UAS_PROJECT_SHOTFORMAT", r"Act{:02}_Seq{:04}_Sh{:04}", override_existing, verbose)
    verbose_set("UAS_PROJECT_OUTPUTFORMAT", "mp4", override_existing, verbose)
    verbose_set("UAS_PROJECT_SHOTHANDLEDURATION", 10, override_existing, verbose)
    verbose_set("UAS_PROJECT_COLORSPACE", "", override_existing, verbose)
    verbose_set("UAS_PROJECT_ASSETNAME", "", override_existing, verbose)


def print_project_env():
    settingsList = []

    settingsList.append(["UAS_PROJECT_NAME", os.environ["UAS_PROJECT_NAME"]])
    settingsList.append(["UAS_PROJECT_FRAMERATE", os.environ["UAS_PROJECT_FRAMERATE"]])
    settingsList.append(["UAS_PROJECT_RESOLUTION", os.environ["UAS_PROJECT_RESOLUTION"]])
    settingsList.append(["UAS_PROJECT_RESOLUTIONFRAMED", os.environ["UAS_PROJECT_RESOLUTIONFRAMED"]])
    settingsList.append(["UAS_PROJECT_SHOTFORMAT", os.environ["UAS_PROJECT_SHOTFORMAT"]])
    settingsList.append(["UAS_PROJECT_SHOTHANDLEDURATION", os.environ["UAS_PROJECT_SHOTHANDLEDURATION"]])
    settingsList.append(["UAS_PROJECT_OUTPUTFORMAT", os.environ["UAS_PROJECT_OUTPUTFORMAT"]])
    settingsList.append(["UAS_PROJECT_COLORSPACE", os.environ["UAS_PROJECT_COLORSPACE"]])
    settingsList.append(["UAS_PROJECT_ASSETNAME", os.environ["UAS_PROJECT_ASSETNAME"]])

    print("\n\nProject Environment Variables:\n")
    for prop in settingsList:
        print(prop[0] + ": " + prop[1])


def initializeForRRS():
    scene = bpy.context.scene

    setup_project_env(True, True)

    scene.UAS_shot_manager_props.setProjectSettings(
        project_name=os.environ["UAS_PROJECT_NAME"],
        project_fps=float(os.environ["UAS_PROJECT_FRAMERATE"]),
        project_resolution=json.loads(os.environ["UAS_PROJECT_RESOLUTION"]),
        project_resolution_framed=json.loads(os.environ["UAS_PROJECT_RESOLUTIONFRAMED"]),
        project_shot_format=os.environ["UAS_PROJECT_SHOTFORMAT"],
        project_shot_format=os.environ["UAS_PROJECT_SHOTHANDLEDURATION"],
        project_output_format=os.environ["UAS_PROJECT_OUTPUTFORMAT"],
        project_color_space=os.environ["UAS_PROJECT_COLORSPACE"],
        project_asset_name=os.environ["UAS_PROJECT_ASSETNAME"],
    )

    print_project_env()


def publishRRS(prodFilePath, takeIndex=-1, verbose=False):
    scene = bpy.context.scene

    # To remove!!! Debug only
    #  setup_project_env(True, True)
    #  takeIndex = 1

    initializeForRRS()

    print_project_env()

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

    ################
    # batch render to generate the files
    ################

    # shot videos are rendered in the directory of the take, not anymore in a directory with the shot name
    renderedFilesList = renderProps.launchRenderWithVSEComposite(
        "PROJECT", takeIndex=takeIndex, renderRootFilePath=cacheFilePath
    )

    ################
    # generate the otio file
    ################

    # wkip beurk pour récuperer le bon contexte de scene
    bpy.context.window.scene = scene
    renderedOtioFile = renderProps.exportOtio(scene, takeIndex=takeIndex, renderRootFilePath=cacheFilePath)

    renderedFilesList.append(renderedOtioFile)

    if verbose:
        print("\nNewMediaList = ", renderedFilesList)

    ################
    # copy files to the network
    ################

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
