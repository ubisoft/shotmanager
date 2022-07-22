# GPLv3 License
#
# Copyright (C) 2022 Ubisoft
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
All the functions used to write on the output frame images
"""

import os

import bpy
import bpy.utils.previews

from shotmanager.utils import utils

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


def getRenderRange(scene):
    rangeStart, rangeEnd = scene.frame_start, scene.frame_end
    return (rangeStart, rangeEnd)


# wk fix: now retunrs an array of ints!
def getRenderResolution(scene, usePercentage=True):
    """Get the current scene rendered image output resolution as float tupple (not int !) and with taking into account the render percentage"""
    resPercentage = scene.render.resolution_percentage * 0.01 if usePercentage else 1

    renderResolution = (
        scene.render.resolution_x * resPercentage,
        scene.render.resolution_y * resPercentage,
    )
    renderResolution = [int(renderResolution[0]), int(renderResolution[1])]
    return renderResolution


def getRenderRatio(scene):
    return scene.render.resolution_x / scene.render.resolution_y


def getRenderResolutionForStampInfo(scene, usePercentage=True, forceMultiplesOf2=False):
    """Get the rendered stamp info image output resolution - based on the current scene render settings! -
    as int array and with taking into account the render percentage
    """
    resPercentage = scene.render.resolution_percentage * 0.01 if usePercentage else 1
    siSettings = scene.UAS_SM_StampInfo_Settings
    stampRenderRes = [-1, -1]

    sceneRes = getRenderResolution(scene, usePercentage=False)

    if "OVER" == siSettings.stampInfoRenderMode:
        stampRenderRes = [sceneRes[0], sceneRes[1]]

    elif "OUTSIDE" == siSettings.stampInfoRenderMode:
        stampRenderRes[0] = sceneRes[0]
        stampRenderRes[1] = max(
            sceneRes[1],
            sceneRes[1] * (siSettings.stampRenderResYOutside_percentage + 100.0) * 0.01,
        )

    if usePercentage:
        stampRenderRes[0] = stampRenderRes[0] * resPercentage
        stampRenderRes[1] = stampRenderRes[1] * resPercentage

    # make the resolutions valid for video rendering
    if forceMultiplesOf2:
        stampRenderRes = utils.convertToSupportedRenderResolution(stampRenderRes)

    stampRenderRes = [int(stampRenderRes[0]), int(stampRenderRes[1])]

    return stampRenderRes


def getInnerHeight(scene):
    """Get the height (integer) in pixels of the image between the 2 borders according to the current mode"""
    siSettings = scene.UAS_SM_StampInfo_Settings
    innerH = -1

    if "OVER" == siSettings.stampInfoRenderMode:
        innerH = min(
            int(getRenderResolution(scene)[1]),
            int(getRenderResolution(scene)[1] * siSettings.stampRenderResOver_percentage * 0.01),
        )

    elif "OUTSIDE" == siSettings.stampInfoRenderMode:
        innerH = int(getRenderResolution(scene)[1])

    return innerH


# TODO wkip traiter cas quand aps de nom de fichier
def getRenderFileName(scene):
    #   print("\n getRenderFileName ")
    # filename is parsed in order to remove the last block in case it doesn't finish with \ or / (otherwise it is
    # the name of the file)
    filename = scene.render.filepath
    lastOccSeparator = filename.rfind("\\")
    if -1 != lastOccSeparator:
        filename = filename[lastOccSeparator + 1 :]

    #   print("    filename: " + filename)
    return filename


# TODO wkip cleaning
def getInfoFileFullPath(scene, renderFrameInd=None):
    """Get the path of the info image corresponding to the specified frame

    Path of temp info files is the same as the render output files
    renderFrameInd can be None to get only the path
    *** Validity of the path is NOT tested ***
    """
    #   print("\n getInfoFileFullPath ")
    siSettings = scene.UAS_SM_StampInfo_Settings
    filepath = ""

    if siSettings.renderRootPathUsed:
        filepath = siSettings.renderRootPath
    else:
        filepath = scene.render.filepath

    filepath = bpy.path.abspath(filepath)
    #    print("    Temp Info Filepath: ", filepath)

    head, tail = os.path.split(filepath)

    #  filepath = head
    #   print("    Temp Info Filepath head: ", head)
    #   print("    Temp Info Filepath tail: ", tail)

    filePathIsValid = False

    #     # if path is relative then get the full path
    #     if '//' == filepath[0:2]:                        #and bpy.data.is_saved:
    #         # print("Rendering path is relative")
    #         filepath = bpy.path.abspath(filepath)

    #     filepath = bpy.path.abspath(filepath)
    # #    print("    Temp Info Filepath 02: ", filepath)

    # filename is parsed in order to remove the last block in case it doesn't finish with \ or / (otherwise it is
    # the name of the file)
    #     lastOccSeparator = filepath.rfind("\\")
    #     if -1 != lastOccSeparator:
    #         filepath = filepath[0:lastOccSeparator + 1]
    # #        print("    Temp Info Filepath 03: ", filepath)

    if os.path.exists(head):
        #        print("  Rendering path is valid")
        filePathIsValid = True

    # validity is NOT tested
    filePathIsValid = True

    renderPath = None
    renderedInfoFileName = None
    if filePathIsValid:
        renderPath = head + "\\"  # get only path part
        #  renderPath = os.path.dirname(head) + "\\"              # get only path part
        #     renderPath = os.path.dirname(filepath)
        #      filenameNoExt, fileExt = os.path.splitext(getRenderFileName(scene))
        filenameNoExt, fileExt = os.path.splitext(tail)

        renderedInfoFileName = filenameNoExt
        if renderFrameInd is None:
            renderedInfoFileName += r"_tmp_StampInfo." + "{:05d}".format(renderFrameInd) + ".png"

    #       renderedInfoFileName = r"\_tmp_StampInfo." + '{:05d}'.format(renderFrameInd) + ".png"

    #  print("    Temp Info Filepath renderPath: ", renderPath)
    #  print("    Temp Info Filepath renderedInfoFileName: ", renderedInfoFileName)
    return (renderPath, renderedInfoFileName)


def getStampInfoRenderFilepath(scene, useTempDir=False):
    """Get a functional render file path to render the temporary files

    Returns: If the file is not saved and the path is relative then a temporary file path is returned
    """
    filepath = scene.render.filepath

    # in case of file not saved and use of a relative path then we use the temp dir
    if (not bpy.data.is_saved and 0 == filepath.find("/")) or 0 == filepath.find("/tmp\\") or useTempDir:
        filepath = bpy.app.tempdir + "TmpSeq.png"
    # else:
    #     filepath = bpy.path.abspath(scene.render.filepath)

    return filepath


def getTempBGImageBaseName():
    return r"_tmp_StampInfo_BGImage.png"


def createTempBGImage(scene):
    """Create the temporaty image used to set the render size (not the one with the stamped info)"""
    from PIL import Image

    print("\n createTempBGImage ")
    dirAndFilename = getInfoFileFullPath(scene, 0)
    filepath = dirAndFilename[0] + getTempBGImageBaseName()
    print("    filepath tmp image in create: " + filepath)

    renderStampInfoResW = getRenderResolutionForStampInfo(scene, forceMultiplesOf2=True)[0]
    renderStampInfoResH = getRenderResolutionForStampInfo(scene, forceMultiplesOf2=True)[1]

    # PIL
    # Black image with transparent alpha
    #   imgTmpInfo             = Image.new('RGBA', (100, 100), (255,0,128,1))
    #   imgTmpInfo             = Image.new('RGBA', (1280, 960), (0,0,0,1))
    imgTmpInfo = Image.new("RGBA", (renderStampInfoResW, renderStampInfoResH), (0, 0, 0, 1))
    imgTmpInfo.save(filepath)

    return filepath


# Not used...
def deleteTempImage(scene):
    print("\n deleteTempImage ")
    dirAndFilename = getInfoFileFullPath(scene, -1)
    filepath = dirAndFilename[0] + r"_StampInfo_TmpImage.png"
    print("    filepath tmp image in delete: " + filepath)

    try:
        os.remove(filepath)
    except OSError:
        print(" *** Cannot delete file " + filepath)
        pass


def deletePreviousInfoImage(scene, currentFrame):
    """Delete only the info image file rendered in the previous frame"""
    print("\n   deletePreviousInfoImage [ ")
    rangeStart = getRenderRange(scene)[0]

    print("\n    rangeStart: ", rangeStart)
    print("\n    frame to delete: ", (currentFrame - 1))

    if rangeStart <= currentFrame - 1:
        dirAndFilename = getInfoFileFullPath(scene, currentFrame - 1)
        filepath = dirAndFilename[0] + dirAndFilename[1]

        print("   getInfoFileFullPath in deletePreviousInfoImage filepath: " + filepath)
        try:
            os.remove(filepath)
        except OSError:
            print(" *** Cannot delete file " + filepath)
            pass

    print("\n   deletePreviousInfoImage ] ")
