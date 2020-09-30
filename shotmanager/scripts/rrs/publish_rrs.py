import os
import json

import bpy
from shotmanager.otio.exports import exportOtio
from shotmanager.rendering import rendering

import logging

_logger = logging.getLogger(__name__)


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

    verbose_set("UAS_PROJECT_NAME", "BuiltIn RRSpecial", override_existing, verbose)
    verbose_set("UAS_PROJECT_FRAMERATE", "25.0", override_existing, verbose)
    verbose_set("UAS_PROJECT_RESOLUTION", "[1280,720]", override_existing, verbose)
    verbose_set("UAS_PROJECT_RESOLUTIONFRAMED", "[1280,960]", override_existing, verbose)
    verbose_set("UAS_PROJECT_SHOTFORMAT", r"Act{:02}_Seq{:04}_Sh{:04}", override_existing, verbose)
    verbose_set("UAS_PROJECT_OUTPUTFORMAT", "mp4", override_existing, verbose)
    verbose_set("UAS_PROJECT_USESHOTHANDLES", "True", override_existing, verbose)
    verbose_set("UAS_PROJECT_SHOTHANDLEDURATION", "10", override_existing, verbose)
    verbose_set("UAS_PROJECT_COLORSPACE", "", override_existing, verbose)
    verbose_set("UAS_PROJECT_ASSETNAME", "", override_existing, verbose)


def print_project_env():
    settingsList = []

    settingsList.append(["UAS_PROJECT_NAME", os.environ["UAS_PROJECT_NAME"]])
    settingsList.append(["UAS_PROJECT_FRAMERATE", os.environ["UAS_PROJECT_FRAMERATE"]])
    settingsList.append(["UAS_PROJECT_RESOLUTION", os.environ["UAS_PROJECT_RESOLUTION"]])
    settingsList.append(["UAS_PROJECT_RESOLUTIONFRAMED", os.environ["UAS_PROJECT_RESOLUTIONFRAMED"]])
    settingsList.append(["UAS_PROJECT_SHOTFORMAT", os.environ["UAS_PROJECT_SHOTFORMAT"]])
    settingsList.append(["UAS_PROJECT_USESHOTHANDLES", os.environ["UAS_PROJECT_USESHOTHANDLES"]])
    settingsList.append(["UAS_PROJECT_SHOTHANDLEDURATION", os.environ["UAS_PROJECT_SHOTHANDLEDURATION"]])
    settingsList.append(["UAS_PROJECT_OUTPUTFORMAT", os.environ["UAS_PROJECT_OUTPUTFORMAT"]])
    settingsList.append(["UAS_PROJECT_COLORSPACE", os.environ["UAS_PROJECT_COLORSPACE"]])
    settingsList.append(["UAS_PROJECT_ASSETNAME", os.environ["UAS_PROJECT_ASSETNAME"]])

    print("\n\nProject Environment Variables:\n")
    for prop in settingsList:
        print(prop[0] + ": " + prop[1])


def initializeForRRS(override_existing: bool, verbose=False):
    scene = bpy.context.scene
    print("\n\n *** UAS Pipe to Shot Manager: initializeForRRS ***")
    setup_project_env(override_existing, verbose)

    scene.UAS_shot_manager_props.setProjectSettings(
        use_project_settings=True,
        project_name=os.environ["UAS_PROJECT_NAME"],
        project_fps=float(os.environ["UAS_PROJECT_FRAMERATE"]),
        project_resolution=json.loads(os.environ["UAS_PROJECT_RESOLUTION"]),
        project_resolution_framed=json.loads(os.environ["UAS_PROJECT_RESOLUTIONFRAMED"]),
        project_shot_format=os.environ["UAS_PROJECT_SHOTFORMAT"],
        project_use_shot_handles=bool(os.environ["UAS_PROJECT_USESHOTHANDLES"]),
        project_shot_handle_duration=int(os.environ["UAS_PROJECT_SHOTHANDLEDURATION"]),
        project_output_format=os.environ["UAS_PROJECT_OUTPUTFORMAT"],
        project_color_space=os.environ["UAS_PROJECT_COLORSPACE"],
        project_asset_name=os.environ["UAS_PROJECT_ASSETNAME"],
    )

    print_project_env()


def publishRRS(
    prodFilePath,
    takeIndex=-1,
    verbose=False,
    useCache=False,
    fileListOnly=False,
    rerenderExistingShotVideos=True,
    renderAlsoDisabled=True,
    settingsDict=None,
):
    """ Return a dictionary with the rendered and the failed file paths
        The dictionary have the following entries:
            - rendered_files_in_cache: rendered files when cache is used
            - failed_files_in_cache: failed files when cache is used
            - edl_files_in_cache: edl files when cache is used
            - rendered_files: rendered files (either from direct rendering or from copy from cache)
            - failed_files: failed files (either from direct rendering or from copy from cache)
            - edl_files: edl files
            - other_files: json dumped file list
    """
    import os
    import errno

    # print("*** publishRRS useCache: ", useCache)
    # print("     prodFilePath: ", prodFilePath)
    # import tempfile

    scene = bpy.context.scene

    # To remove!!! Debug only
    # setup_project_env(True, True)
    # takeIndex = 1

    # initializeForRRS()

    # print_project_env()

    if "UAS_shot_manager_props" not in scene:
        print("\n*** publishRRS failed: No UAS_shot_manager_prop found in the scene ***\n")
        return False

    props = scene.UAS_shot_manager_props
    if (
        not len(props.getTakes())
        or len(props.getTakes()) <= takeIndex
        or (not len(props.getTakes()[takeIndex].getShotList(ignoreDisabled=True)))
    ):
        print("No take or no shots to render - Aborting Publish")
        return False

    print("\n---------------------------------------------------------")
    print(" -- * publishRRS * --\n\n")

    renderDir = prodFilePath

    if useCache:
        # wkip récup temp dir dans l'os?
        # print("Temp dir:", tempfile.gettempdir())
        renderDir = "c:\\tmp\\" + scene.name + "\\"

        # create cache dir
        if not os.path.exists(os.path.dirname(renderDir)):
            try:
                os.makedirs(os.path.dirname(renderDir), exist_ok=True)
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

    if verbose:
        print("Use Cache: ", useCache)
        if useCache:
            print("Local cache path: ", renderDir)
        print("Render Dir: ", renderDir)
        print("Current Scene: " + scene.name + ", current take: " + props.getCurrentTakeName())

    print("\n---------------------------------------------------------")

    ################
    # batch render to generate the files
    ################

    stampInfoCustomSettingsDict = None
    if settingsDict is not None:
        stampInfoCustomSettingsDict = dict()
        stampInfoCustomSettingsDict["customFileFullPath"] = settingsDict["publish_rendering_file"]
        stampInfoCustomSettingsDict["asset_tracking_step"] = settingsDict["publish_step"]

    # shot videos are rendered in the directory of the take, not anymore in a directory with the shot name
    renderedFilesDict = rendering.launchRenderWithVSEComposite(
        bpy.context,
        "PROJECT",
        takeIndex=takeIndex,
        filePath=renderDir,
        fileListOnly=fileListOnly,
        rerenderExistingShotVideos=rerenderExistingShotVideos,
        renderAlsoDisabled=renderAlsoDisabled,
        area=bpy.context.area,
        stampInfoCustomSettingsDict=stampInfoCustomSettingsDict,
    )

    ################
    # generate the otio file
    ################

    # wkip beurk pour récuperer le bon contexte de scene
    bpy.context.window.scene = scene
    renderedOtioFile = exportOtio(scene, takeIndex=takeIndex, filePath=renderDir, fileListOnly=fileListOnly)
    renderedFilesDict["edl_files"] = [renderedOtioFile]

    # if verbose:
    #     print("\nNewMediaList = ", generatedFilesDict)

    ################
    # keep track of files
    ################

    ################
    # copy files to the network
    ################

    generatedFilesDict = dict()

    if useCache:
        import shutil
        import os
        import errno

        generatedFilesDict["rendered_files_in_cache"] = renderedFilesDict["rendered_files"]
        generatedFilesDict["failed_files_in_cache"] = renderedFilesDict["failed_files"]
        generatedFilesDict["edl_files_in_cache"] = renderedFilesDict["edl_files"]

        # create dirs
        if not os.path.exists(os.path.dirname(prodFilePath)):
            try:
                os.makedirs(os.path.dirname(prodFilePath), exist_ok=True)
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        def _MoveFile(f):
            head, tail = os.path.split(f)
            target = prodFilePath
            if not target.endswith("\\"):
                target += "\\"
            target += tail

            # if verbose:
            #     print("target: ", target)

            if fileListOnly:
                copiedFiles.append(target)
            else:
                try:
                    shutil.copyfile(f, target)
                    copiedFiles.append(target)
                except Exception as e:
                    print("*** File cannot be copied: ", e)
                    notCopiedFiles.append(target)

        copiedFiles = []
        notCopiedFiles = []
        for f in renderedFilesDict["rendered_files"]:
            _MoveFile(f)

        generatedFilesDict["rendered_files"] = copiedFiles
        generatedFilesDict["failed_files"] = notCopiedFiles

        copiedFiles = []
        notCopiedFiles = []
        _MoveFile(renderedOtioFile)
        generatedFilesDict["edl_files"] = copiedFiles if len(copiedFiles) else []

    # if cache is not used
    else:
        generatedFilesDict["rendered_files_in_cache"] = []
        generatedFilesDict["failed_files_in_cache"] = []
        generatedFilesDict["edl_files_in_cache"] = []
        generatedFilesDict["rendered_files"] = renderedFilesDict["rendered_files"]
        generatedFilesDict["failed_files"] = renderedFilesDict["failed_files"]
        generatedFilesDict["edl_files"] = renderedFilesDict["edl_files"]

    generatedFilesDict["sequence_video_file"] = renderedFilesDict["sequence_video_file"]

    jsonFile = prodFilePath
    if not jsonFile.endswith("\\"):
        jsonFile += "\\"
    jsonFile += "renderedFiles.json"

    # json dumped file is also added to the list of the rendered files
    otherFiles = []
    otherFiles.append(jsonFile)
    generatedFilesDict["other_files"] = otherFiles

    # if verbose:
    #     print("\n")
    #     for k in generatedFilesDict:
    #         if len(generatedFilesDict[k]):
    #             print(f" - {k}:")
    #             for item in generatedFilesDict[k]:
    #                 print(f"       {item}")
    #         else:
    #             print(f" - {k}: []")
    #     print(" ")

    # add shots info

    # dictMontage = dict()
    # dictMontage["sequence"] = scene.name
    # props.getInfoAsDictionnary(dictMontage=dictMontage)

    # generatedFilesDict.update(dictMontage)

    if verbose:
        print(json.dumps(generatedFilesDict, indent=3))

    if not fileListOnly:
        with open(jsonFile, "w") as fp:
            json.dump(generatedFilesDict, fp, indent=3)

    return generatedFilesDict
