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
To do: module description here.
"""

import os
import json
from pathlib import Path

import bpy
from shotmanager.rendering import rendering

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


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

    props = config.getAddonProps(scene)
    props.setProjectSettings(
        use_project_settings=True,
        project_name=os.environ["UAS_PROJECT_NAME"],
        project_fps=float(os.environ["UAS_PROJECT_FRAMERATE"]),
        project_resolution=json.loads(os.environ["UAS_PROJECT_RESOLUTION"]),
        project_resolution_framed=json.loads(os.environ["UAS_PROJECT_RESOLUTIONFRAMED"]),
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
    """Return a dictionary with the rendered and the failed file paths
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

    props = config.getAddonProps(scene)
    # _logger.debug(
    #     f" + len takes: {len(props.getTakes())}, takeInd: {takeIndex}, len truc: {len(props.getTakes()[takeIndex].getShotList(ignoreDisabled=True))}"
    # )

    # if (
    #     not len(props.getTakes())
    #     or len(props.getTakes()) <= takeIndex
    #     or (not len(props.getTakes()[takeIndex].getShotList(ignoreDisabled=True)))
    # ):

    takeInd = 0 if -1 == takeIndex else takeIndex

    if not len(props.getTakes()):
        errorStr = "No take found to render - Aborting Publish"
        print(errorStr)
        return errorStr
    elif len(props.getTakes()) <= takeInd:
        errorStr = "Take index higher than the number of takes - Aborting Publish"
        print(errorStr)
        return errorStr
    elif not len(props.getTakes()[takeInd].getShotList(ignoreDisabled=True)):
        errorStr = f"No take or no shots to render in take {props.getTakes()[takeInd].name} - Aborting Publish"
        print(errorStr)
        return errorStr

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
        renderPreset=None,
        takeIndex=takeInd,
        filePath=renderDir,
        fileListOnly=fileListOnly,
        rerenderExistingShotVideos=rerenderExistingShotVideos,
        renderAlsoDisabled=renderAlsoDisabled,
        area=bpy.context.area,
        stampInfoCustomSettingsDict=stampInfoCustomSettingsDict,
        override_all_viewports=True,
    )

    ################
    # generate the otio file
    ################

    # wkip beurk pour récuperer le bon contexte de scene
    bpy.context.window.scene = scene
    print("publish RRS")

    from shotmanager.otio.exports import exportShotManagerEditToOtio

    renderedOtioFile = exportShotManagerEditToOtio(
        scene, takeIndex=takeInd, filePath=renderDir, fileListOnly=fileListOnly
    )
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

    ################
    # get the list of all the sound files used in the VSE of the sequence
    ################
    vse_render = bpy.context.window_manager.UAS_vse_render
    # Return a dictionary made of "media_video" and "media_audio", both having an array of media filepaths
    # obsolete cause we now export the sound from the shot videos:
    # soundsMedia = vse_render.getMediaList(scene, listVideo=False, listAudio=True)
    # generatedFilesDict["sounds_media"] = soundsMedia["media_audio"]

    soundsMedia = dict()
    soundsList = []
    fileDir = Path(r"C:\_UAS_ROOT\RRSpecial\05_Acts\Act01\_Montage\Shots\\")
    # my_icons_dir = os.path.join(os.path.dirname(__file__), "../icons")
    seqName = scene.name
    for soundFile in Path(fileDir).rglob("*.mp3"):
        if seqName in soundFile.stem:
            soundsList.append(str(soundFile))

    soundsMedia["media_audio_mixed"] = soundsList

    generatedFilesDict["sounds_media"] = soundsMedia["media_audio_mixed"]

    ################
    # build the output dictionary
    ################

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
    dictMontage = dict()
    dictMontage["sequence"] = scene.name
    props.getInfoAsDictionnary(dictMontage=dictMontage)

    generatedFilesDict.update(dictMontage)

    if verbose:
        print(json.dumps(generatedFilesDict, indent=3))

    if not fileListOnly:
        with open(jsonFile, "w") as fp:
            json.dump(generatedFilesDict, fp, indent=3)

    return generatedFilesDict
