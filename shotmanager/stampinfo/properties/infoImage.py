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
Generation of the frame images
"""


import os
from pathlib import Path
import getpass

import bpy

from datetime import datetime
from .stamper import getInfoFileFullPath

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


# Preparation of the files
def renderStampedImage(
    scene, currentFrame, renderW, renderH, innerH, renderPath=None, renderFilename=None, verbose=False
):
    """Called by the Pre renderer callback
    Preparation of the files
    """
    # Notes
    #   - Image origine is at TOP LEFT corner
    #   - Everything is proportionnal to the HEIGHT of the output image
    #
    # Metadata from Blender:
    #   top:    file, date, render time, host, note, memory         frame range
    #   bottom: marker, timecode, frame, camera, lens               sequencer strip, strip metadata

    from PIL import Image, ImageDraw, ImageFont

    if verbose:
        print("\n       renderTmpImageWithStampedInfo ")

    siSettings = scene.UAS_SM_StampInfo_Settings
    # prefs = config.getAddonPrefs()
    paddingLeftMetadataTopNorm = 0.0
    paddingLeftMetadataBottomNorm = 0.0

    # stamp_background
    # stamp_font_size
    # stamp_foreground
    # stamp_note_text
    # use_stamp
    # use_stamp_camera
    # use_stamp_date
    # use_stamp_filename
    # use_stamp_frame
    # use_stamp_frame_range
    # use_stamp_hostname
    # use_stamp_labels
    # use_stamp_lens
    # use_stamp_marker
    # use_stamp_memory
    # use_stamp_note
    # use_stamp_render_time
    # use_stamp_scene
    # use_stamp_sequencer_strip
    # use_stamp_strip_meta
    # use_stamp_time
    # support of metadata from Blender

    # !!! Removed !!! Wkip: to rewrite in a smarter way !!!
    # if scene.render.use_stamp:
    if False:
        if (
            scene.render.use_stamp_filename
            or scene.render.use_stamp_date
            or scene.render.use_stamp_render_time
            or scene.render.use_stamp_hostname
            or scene.render.use_stamp_note
            or scene.render.use_stamp_frame_range
            or scene.render.use_stamp_memory
        ):
            paddingLeftMetadataTopNorm = 0.2

        if (
            scene.render.use_stamp_marker
            or scene.render.use_stamp_time
            or scene.render.use_stamp_frame
            or scene.render.use_stamp_camera
            or scene.render.use_stamp_lens
            or scene.render.use_stamp_sequencer_strip
            or scene.render.use_strip_meta
        ):
            paddingLeftMetadataBottomNorm = 0.2

    borderTopH = max(
        int((renderH - innerH) * 0.5), 0
    )  # border cannot be negative, which happens if render ratio < inner ratio
    borderBottomH = borderTopH

    # ---------- framing control settings ----------------
    paddingTopExtNorm = siSettings.extPaddingNorm
    # 0.03      # padding near the exterior of the image on the border rectangle
    paddingTopIntNorm = 0.04  # not used here # padding near the interior of the image on the border rectangle
    paddingLeftNorm = siSettings.extPaddingHorizNorm

    textLineNorm = siSettings.fontScaleHNorm
    textInterlineNorm = siSettings.interlineHNorm  # 0.01
    numLinesTop = 3
    numLinesBottom = numLinesTop

    if siSettings.automaticTextSize:
        borderTopNorm = min(0.5, borderTopH / renderH)
        paddingTopExtNormInBorder = siSettings.extPaddingNorm * 10.0  # 0.2
        paddingTopIntNormInBorder = 0.1
        paddingTopExtNorm = paddingTopExtNormInBorder * borderTopNorm
        paddingTopIntNorm = paddingTopIntNormInBorder * borderTopNorm

        textInterlineNormInBorder = siSettings.interlineHNorm  # 0.04
        textInterlineNorm = textInterlineNormInBorder * borderTopNorm

        textBorderNorm = borderTopNorm - paddingTopExtNorm - paddingTopIntNorm
        if textBorderNorm <= (numLinesTop - 1) * textInterlineNorm:
            textBorderNorm = 0.0
            textLineNorm = 0.0
        else:
            textLineNorm = min(textLineNorm, (textBorderNorm - (numLinesTop - 1) * textInterlineNorm) / 3.0)

    # ---------- framing control settings ----------------

    # All dimensions are normalized as if the image had the size 1.0 * 1.0
    # fontScaleHNorm      = siSettings.fontScaleHNorm        #0.03
    # fontsize            = int(fontScaleHNorm * renderH)
    # font                = ImageFont.truetype("arial", fontsize)
    # textLineH           = (font.getsize("Aj"))[1]            # line height

    textLineH = int(renderH * textLineNorm)
    textInterlineH = int(renderH * textInterlineNorm)

    fontsize = int(1.0 * textLineNorm * renderH)
    font = ImageFont.truetype("arial", fontsize)
    fontHeight = (font.getsize("Text"))[1]
    fontLargeFactor = 1.6
    fontLarge = ImageFont.truetype("arial", int(fontsize * fontLargeFactor))
    fontLargeHeight = (fontLarge.getsize("Text"))[1]

    paddingLeft = int((paddingLeftNorm) * renderW)
    paddingLeftMetadataTop = int((paddingLeftMetadataTopNorm) * renderW)
    paddingLeftMetadataBottom = int((paddingLeftMetadataBottomNorm) * renderW)
    # paddingLeft         = int((paddingLeftNorm + paddingLeftMetadataTopNorm) * renderW)
    #    paddingRight = paddingLeft

    paddingTopExt = int(paddingTopExtNorm * renderH)
    paddingBottomExt = paddingTopExt
    #    paddingTopInt = int(paddingTopIntNorm * renderH)
    #    paddingBottomInt = paddingTopInt

    borderColorRGB = siSettings.borderColor  # (0, 0, 0, 255)
    borderColorRGBA = (
        int(borderColorRGB[0] * 255),
        int(borderColorRGB[1] * 255),
        int(borderColorRGB[2] * 255),
        int(borderColorRGB[3] * 255),
    )

    #   borderColorOpacity  = siSettings.borderColorOpacity                  #(0, 0, 0, 255)
    #   borderColorRGBA = (int(borderColorRGB[0] * borderColorOpacity * 255), int(borderColorRGB[1] * borderColorOpacity * 255), int(borderColorRGB[2] * borderColorOpacity * 255), int(borderColorOpacity * 255) )
    #   borderColorRGBA = (int(borderColorRGB[0] * 255), int(borderColorRGB[1] * 255), int(borderColorRGB[2] * 255), int(borderColorOpacity * 255) )
    # print("borderColor: " + str(borderColor[0]))
    #  borderColor         = (0, 0, 0, 255)

    # innerAspectRatio    = siSettings.innerImageRatio              #16/9   # must be >= 1
    # if 1.0 >= innerAspectRatio:
    #     innerAspectRatio = 1.0
    # innerH              = renderW * 1.0 / innerAspectRatio
    textColorRGB = siSettings.textColor  # (0, 0, 0, 255)
    #   textColorOpacity  = siSettings.textColorOpacity                  #(0, 0, 0, 255)
    #  textColorRGBA = (int(textColorRGB[0] * textColorOpacity * 255), int(textColorRGB[1] * textColorOpacity * 255), int(textColorRGB[2] * textColorOpacity * 255), int(textColorOpacity * 255) )
    textColorRGBA = (
        int(textColorRGB[0] * 255),
        int(textColorRGB[1] * 255),
        int(textColorRGB[2] * 255),
        int(textColorRGB[3] * 255),
    )

    # textColorWhite = (235, 235, 235, 255)

    # alertColorRGB = siSettings.textColor
    alertColorRGB = (0.7, 0.2, 0.2, 255)
    alertColorRGBA = (
        int(alertColorRGB[0] * 255),
        int(alertColorRGB[1] * 255),
        int(alertColorRGB[2] * 255),
        int(alertColorRGB[3] * 255),
    )

    # move the content (border + text) toward center
    offsetToCenterH = int(siSettings.offsetToCenterHNorm * renderH)

    imgInfo = Image.new("RGBA", (renderW, renderH), (0, 0, 0, 0))

    def _debug_drawPadding(borderInd):
        myCol = (200, 250, 0, 100)
        if 0 == borderInd:  # top
            imgBorderRect = Image.new("RGBA", (renderW - 2 * paddingLeft, borderTopH - 2 * paddingTopExt), myCol)
            imgInfo.paste(imgBorderRect, (paddingLeft, paddingTopExt))
        else:  # bottom
            imgBorderRect = Image.new("RGBA", (renderW - 2 * paddingLeft, borderBottomH - 2 * paddingBottomExt), myCol)
            imgInfo.paste(imgBorderRect, (paddingLeft, renderH - borderBottomH + paddingTopExt))
        return

    # -------------------------------- #
    # stamp borders with PIL
    # -------------------------------- #
    if siSettings.borderUsed:
        imgBorderRect = Image.new("RGBA", (renderW, borderTopH), borderColorRGBA)
        imgInfo.paste(imgBorderRect, (0, offsetToCenterH))
        imgBorderRect = Image.new("RGBA", (renderW, borderBottomH), borderColorRGBA)
        imgInfo.paste(imgBorderRect, (0, renderH - borderBottomH - offsetToCenterH))

    # -------------------------------- #
    # Debug - Draw text lines
    # -------------------------------- #
    if siSettings.debug_DrawTextLines:
        currentTextLeft = paddingLeft + paddingLeftMetadataTop
        currentTextTop = offsetToCenterH + paddingTopExt

        for borderInd in range(0, 2):
            if 0 == borderInd:  # top
                numLines = 6  # numLinesTop
                currentTextLeft = paddingLeft + paddingLeftMetadataTop
                currentTextTop = offsetToCenterH + paddingTopExt
                directionSign = 1
            else:  # bottom
                numLines = 6  # numLinesBottom
                currentTextLeft = paddingLeft + paddingLeftMetadataTop
                currentTextTop = (
                    renderH
                    - paddingBottomExt
                    # - numLines * textLineH
                    - textLineH
                    - offsetToCenterH
                )
                directionSign = -1

            _debug_drawPadding(borderInd)

            for lineInd in range(0, numLines):
                # first line top
                myCol = (255, 20, 0, 200)
                imgBorderRect = Image.new("RGBA", (80, textLineH), myCol)
                imgInfo.paste(imgBorderRect, (currentTextLeft + lineInd * 20, currentTextTop))

                # first interline top
                myCol = (20, 250, 0, 100)
                imgBorderRect = Image.new("RGBA", (int(1.0 * renderW), textInterlineH), myCol)
                if 0 == borderInd:  # top
                    imgInfo.paste(
                        imgBorderRect, (currentTextLeft + lineInd * 20, currentTextTop + directionSign * textLineH)
                    )
                else:  # bottom
                    imgInfo.paste(
                        imgBorderRect, (currentTextLeft + lineInd * 20, currentTextTop + directionSign * textInterlineH)
                    )

                currentTextTop += directionSign * (textLineH + textInterlineH)

    # -------------------------------- #
    # stamp logo
    # if the logo is not found a red fake logo is stamped instead
    # -------------------------------- #

    if siSettings.logoUsed:

        logoFile = ""

        if "BUILTIN" == siSettings.logoMode:
            dir = siSettings.getBuiltInLogosPath()
            logoFile = str(dir) + "\\" + str(siSettings.logoBuiltinName)
        else:
            logoFile = siSettings.logoFilepath
        #  print("  Logo: siSettings.logoFilepath: " + siSettings.logoFilepath)

        filename, extension = os.path.splitext(logoFile)
        # print('Selected file:', self.filepath)
        # print('File name:', filename)
        # print('File extension:', extension)

        logoFilePathIsValid = False

        # if path is relative then get the full path
        if "//" == logoFile[0:2] and bpy.data.is_saved:
            # print("Logo path is relative")
            logoFile = bpy.path.abspath(logoFile)

        if os.path.exists(logoFile):
            logoFilePathIsValid = True
        else:
            if siSettings.logoUsed:
                _logger.error_ext(f"Logo path is NOT valid: {logoFile}")
                # wkip mettre alert rouge

        # logoScaleW = 0.09                                         # logo size is in % of width relatively to the outpur render size. In other words: 1.0 => logo width = renderW
        # logoScaleH = 0.08                                         # logo size is in % of height relatively to the outpur render size. In other words: 1.0 => logo height = renderH
        logoScaleH = siSettings.logoScaleH
        logoPositionNorm = [
            renderW * siSettings.logoPosNormX,
            renderH * siSettings.logoPosNormY,
        ]  # normalized in range [0,1]

        imgLogoSource = None
        if logoFilePathIsValid:
            imgLogoSource = Image.open(logoFile).convert("RGBA")
            if imgLogoSource is None:
                _logger.warning_ext(f"******* Cannot open specified logo !!! *** File: {logoFile} *********")
                logoFilePathIsValid = False
        else:
            imgLogoSource = Image.new("RGBA", (150, 150), "red")

        #   logoScaleH = logoScaleW * imgLogoSource.size[1] * 1.0 / imgLogoSource.size[0]
        #   newLogoSize = (int(logoScaleW * renderW), int(logoScaleH * renderW)                                         # preserve logo size on widht
        logoScaleW = logoScaleH * imgLogoSource.size[0] * 1.0 / imgLogoSource.size[1]
        newLogoSize = (int(logoScaleW * renderH), int(logoScaleH * renderH))  # preserve logo size on height

        #  newLogoSize = (int(logoScale * imgLogoSource.size[0]), int(logoScale * imgLogoSource.size[1]))             # to get a precise logo size when output res in pixels is known
        imgLogoSource = imgLogoSource.resize(newLogoSize, Image.ANTIALIAS)  # size in pixels # resamplming mode

        # put logo on image in position (0, 0)
        imgInfo.paste(
            imgLogoSource, (int(logoPositionNorm[0]), int(logoPositionNorm[1])), mask=imgLogoSource
        )  # left align
    # imgInfo.paste(imgLogoSource, (renderW - newLogoSize[0] - paddingRight, paddingRight), mask = imgLogoSource)      # right align

    # put text on image
    img_draw = ImageDraw.Draw(imgInfo)

    stampLabel = siSettings.stampPropertyLabel
    stampValue = siSettings.stampPropertyValue
    textProp = ""

    # ---------------------------------
    # top border
    # ---------------------------------

    col01 = paddingLeft
    col01 = col01 + paddingLeftMetadataTop
    col02 = 0.1 * renderW
    col028 = 0.69 * renderW
    col035 = 0.84 * renderW

    # col03 = 0.75 * renderW
    col04 = 0.8 * renderW

    currentTextTop = offsetToCenterH + paddingTopExt

    # ---------- project -------------
    if siSettings.projectUsed:
        textProp = "Project: " if stampLabel and not stampValue else ""
        textProp += siSettings.projectName if stampValue else ""
        img_draw.text((col02, currentTextTop), textProp, font=fontLarge, fill=textColorRGBA)

    # ---------------------
    # Code for date and time aligned from bottom:
    # ---------------------
    currentTextTop = borderTopH - paddingTopExt - fontHeight

    # ---------- user -------------
    if siSettings.userNameUsed:
        textProp = "By: "  # if stampLabel else ""
        textProp += getpass.getuser() if stampValue else ""

        img_draw.text((col01, currentTextTop), textProp, font=font, fill=textColorRGBA)

    # ---------- date -------------

    # wkip use pytz to get the right time zone
    currentTextTop -= textLineH + textInterlineH

    now = datetime.now()
    timeStr = now.strftime("%H:%M:%S")
    if siSettings.dateUsed:
        textProp = "Date: " if stampLabel else ""
        textProp += now.strftime("%b-%d-%Y") if stampValue else ""  # Month abbreviation, day and year
        if siSettings.timeUsed:
            textProp += "  " + timeStr if stampValue else ""
    elif siSettings.timeUsed:
        textProp = "Time: " if stampLabel else ""
        textProp += "  " + timeStr if stampValue else ""

    if siSettings.dateUsed or siSettings.timeUsed:
        img_draw.text((col01, currentTextTop), textProp, font=font, fill=textColorRGBA)

    # ---------------------
    # Code for date and time aligned from top:
    # ---------------------
    # currentTextTop += 2 * (textLineH + textInterlineH)

    # ---------- date -------------

    # wkip use pytz to get the right time zone

    # now = datetime.now()
    # timeStr = now.strftime("%H:%M:%S")
    # if siSettings.dateUsed:
    #     textProp = "Date: " if stampLabel else ""
    #     textProp += now.strftime("%b-%d-%Y") if stampValue else ""  # Month abbreviation, day and year
    #     if siSettings.timeUsed:
    #         textProp += "  " + timeStr if stampValue else ""
    # elif siSettings.timeUsed:
    #     textProp = "Time: " if stampLabel else ""
    #     textProp += "  " + timeStr if stampValue else ""

    # if siSettings.dateUsed or siSettings.timeUsed:
    #     img_draw.text((col01, currentTextTop), textProp, font=font, fill=textColorRGBA)

    # ---------- user -------------
    # currentTextTop += textLineH + textInterlineH
    # if True or siSettings.userNameUsed:
    #     textProp = "By: "  # if stampLabel else ""
    #     textProp += getpass.getuser() if stampValue else ""
    #     img_draw.text((col01, currentTextTop), textProp, font=font, fill=textColorRGBA)

    # ---------- image sequence indices in video ref system -------------
    # currentTextTop += textLineH + textInterlineH

    currentTextTopForVideoFrames = offsetToCenterH + paddingTopExt + textLineH + textInterlineH
    currentTextLeftForVideoFrames = renderW * (1.0 - paddingLeftNorm)

    if siSettings.videoFrameUsed:
        # textProp = "Video: " if stampLabel else ""
        textProp = "Video Frame: "

        if siSettings.videoFirstFrameIndexUsed:
            currentImage = scene.frame_current - scene.frame_start + siSettings.videoFirstFrameIndex
            firstFrameInd = siSettings.videoFirstFrameIndex
            lastFrameInd = scene.frame_end - scene.frame_start + siSettings.videoFirstFrameIndex
        else:
            currentImage = scene.frame_current - scene.frame_start
            firstFrameInd = 0
            lastFrameInd = scene.frame_end - scene.frame_start

        # _logger.debug_ext(
        #     f"drawRangesAndFrame: currentImage: {currentImage}, firstFrameInd: {firstFrameInd}, lastFrameInd: {lastFrameInd}"
        # )
        drawRangesAndFrame(
            scene,
            img_draw,
            "VIDEOFRAME",
            currentImage,
            firstFrameInd,
            lastFrameInd,
            siSettings.shotHandles,
            siSettings.currentFrameUsed,
            siSettings.animRangeUsed,
            siSettings.handlesUsed,
            currentTextLeftForVideoFrames,
            currentTextTopForVideoFrames,
            font,
            fontLarge,
            textColorRGBA,
            siSettings.frameDigitsPadding,
        )

    # ------------ corner note ---------------
    currentTextTop = offsetToCenterH + paddingTopExt / 2.0
    currentTextRight = renderW * (1.0 - paddingLeftNorm)

    if siSettings.cornerNoteUsed:
        # textProp = "Corner Note: " if stampLabel else ""
        textProp = siSettings.cornerNote if stampValue else ""
        img_draw.text(
            (currentTextRight - (font.getsize(textProp))[0], currentTextTop),
            textProp,
            font=font,
            fill=alertColorRGBA,
        )

    # ---------- fps and 3D edit -------------
    currentTextTop = currentTextTopForVideoFrames + textLineH + textInterlineH

    if siSettings.framerateUsed:
        textProp = "Framerate: " if stampLabel else ""
        textProp += str(scene.render.fps) + " fps" if stampValue else ""
        img_draw.text(
            (currentTextLeftForVideoFrames - (font.getsize(textProp))[0], currentTextTop),
            textProp,
            font=font,
            fill=textColorRGBA,
        )

    if siSettings.edit3DFrameUsed:
        textProp = "Index in 3D Edit: " if stampLabel else ""
        #  textProp += '{:03d}'.format(scene.render.fps) + " fps" if stampValue else ""
        currentImage = siSettings.edit3DFrame
        totalImages = siSettings.edit3DTotalNumber
        textProp += str(int(currentImage)) if stampValue else ""
        if siSettings.edit3DTotalNumberUsed:
            textProp += " / " + str(int(totalImages)) + " fr." if stampValue else ""
        img_draw.text((col035, currentTextTop), textProp, font=font, fill=textColorRGBA)

    # ---------- video duration -------------
    # currentTextTop += textLineH + textInterlineH
    if siSettings.animDurationUsed:
        textProp = "Duration: "
        textProp += str(scene.frame_end - scene.frame_start + 1) + " fr." if stampValue else ""
        img_draw.text((col028, currentTextTop), textProp, font=font, fill=textColorRGBA)

    # currentTextTop += textLineH + textInterlineH

    # ---------- notes -------------
    currentTextTop = offsetToCenterH + paddingTopExt

    if siSettings.notesUsed:
        # colNotes = col02

        currentBoxTop = currentTextTop - 0.005 * renderH
        currentBoxBottom = currentTextTop + 4 * (textLineH + textInterlineH) + 0.005 * renderH

        colBoxLeft = 0.26 * renderW
        colBoxRight = colBoxLeft + 0.43 * renderW
        colNotesLabel = colBoxLeft + 0.01 * renderW
        colNotes = colBoxLeft + 0.02 * renderW

        boxLineThickness = max(1, int(0.002 * renderH))
        textColorGray = (50, 50, 50, 255)

        textProp = "Notes: " if stampLabel else ""
        img_draw.text((colNotesLabel, currentTextTop), textProp, font=font, fill=textColorRGBA)

        currentTextTop += textLineH + textInterlineH
        textProp = siSettings.notesLine01 if stampValue else ("Notes Line 1" if stampLabel else "")
        img_draw.text((colNotes, currentTextTop), textProp, font=font, fill=textColorRGBA)

        currentTextTop += textLineH + textInterlineH
        textProp = siSettings.notesLine02 if stampValue else ("Notes Line 2" if stampLabel else "")
        img_draw.text((colNotes, currentTextTop), textProp, font=font, fill=textColorRGBA)

        currentTextTop += textLineH + textInterlineH
        textProp = siSettings.notesLine03 if stampValue else ("Notes Line 3" if stampLabel else "")
        img_draw.text((colNotes, currentTextTop), textProp, font=font, fill=textColorRGBA)

        # draw box
        img_draw.line(
            [(colBoxLeft, currentBoxTop), (colBoxRight, currentBoxTop)],
            fill=textColorGray,
            width=boxLineThickness,
        )
        img_draw.line(
            [(colBoxLeft, currentBoxBottom), (colBoxRight, currentBoxBottom)],
            fill=textColorGray,
            width=boxLineThickness,
        )
        img_draw.line(
            [(colBoxLeft, currentBoxTop), (colBoxLeft, currentBoxBottom)],
            fill=textColorGray,
            width=boxLineThickness,
        )
        img_draw.line(
            [(colBoxRight, currentBoxTop), (colBoxRight, currentBoxBottom)],
            fill=textColorGray,
            width=boxLineThickness,
        )

    # ---------------------------------
    # bottom border
    # ---------------------------------

    col01 = paddingLeft
    col02 = 0.19 * renderW
    # col03 = 0.34 * renderW
    col04 = 0.7 * renderW
    # col05 = 0.7 * renderW
    lineTextXEnd = col01
    separatorX = 0.015 * renderW
    currentTextTop = (
        renderH
        - paddingBottomExt
        - numLinesBottom * textLineH
        - (numLinesBottom - 1) * textInterlineH
        - offsetToCenterH
    )
    currentTextTopFor3DFrames = currentTextTop
    col01 = col01 + paddingLeftMetadataBottom
    currentTextFromBottom = renderH - paddingBottomExt - textLineH + textInterlineH

    # ---------- shot -------------
    stampLabel3D = stampLabel or stampValue

    yPos = currentTextTop + -1.0 * fontLargeHeight + 1.0 * textInterlineH
    if siSettings.shotUsed:
        # textProp = "Shot: " if stampLabel3D else ""
        textProp = siSettings.shotName if stampValue else ""
        img_draw.text((col01, yPos), textProp, font=fontLarge, fill=textColorRGBA)  # textColorRGBA
        lineTextXEnd += (fontLarge.getsize(textProp))[0] + separatorX

    # ---------- shot duration -------------
    # currentTextTop += fontHeight * (1.2 / fontLargeFactor)
    if siSettings.shotDurationUsed:
        # textProp = "Shot Duration: "
        textProp = (
            str(scene.frame_end - scene.frame_start + 1 - 2 * siSettings.shotHandles) + " fr." if stampValue else ""
        )
        img_draw.text((lineTextXEnd, yPos), textProp, font=font, fill=textColorRGBA)
        lineTextXEnd += (font.getsize(textProp))[0] + separatorX

    # ---------- sequence -------------
    if siSettings.sequenceUsed:
        textProp = "Seq: " if stampLabel3D else ""
        textProp += siSettings.sequenceName if stampValue else ""
        yPos = currentTextTop + -1.0 * fontHeight + 1.0 * textInterlineH
        img_draw.text((lineTextXEnd, yPos), textProp, font=font, fill=textColorRGBA)
        lineTextXEnd += (font.getsize(textProp))[0] + separatorX

    # ---------- take -------------
    if siSettings.takeUsed:
        textProp = "Take: " if stampLabel3D else ""
        textProp += siSettings.takeName if stampValue else ""
        yPos = currentTextTop + -1.0 * fontHeight + 1.0 * textInterlineH
        img_draw.text((lineTextXEnd, yPos), textProp, font=font, fill=textColorRGBA)
        lineTextXEnd += (font.getsize(textProp))[0] + separatorX

    # ---------- 3d frames and range -------------
    # currentTextTopFor3DFrames += textLineH + textInterlineH

    if siSettings.currentFrameUsed:
        currentTextTopFor3DFrames = currentTextTop  # - fontHeight
        currentTextLeftFor3DFrames = renderW * (1.0 - paddingLeftNorm)
        drawRangesAndFrame(
            scene,
            img_draw,
            "3DFRAME",
            currentFrame,
            scene.frame_start,
            scene.frame_end,
            siSettings.shotHandles,
            siSettings.currentFrameUsed,
            siSettings.animRangeUsed,
            siSettings.handlesUsed,
            currentTextLeftFor3DFrames,
            currentTextTopFor3DFrames,
            font,
            fontLarge,
            textColorRGBA,
            siSettings.frameDigitsPadding,
        )

    currentTextTop += textLineH + 2.0 * textInterlineH

    lineTextXEnd = col01
    # ---------- scene -------------
    if siSettings.sceneUsed:
        textProp = "Scene: " if stampLabel3D else ""
        textProp += str(scene.name) if stampValue else ""
        # yPos = currentTextTop
        yPos = currentTextFromBottom - textInterlineH - textLineH
        img_draw.text((lineTextXEnd, yPos), textProp, font=font, fill=textColorRGBA)
        lineTextXEnd += (font.getsize(textProp))[0] + separatorX

    # ---------- bottom note -------------
    if siSettings.bottomNoteUsed:
        # textProp = "Scene: " if stampLabel3D else ""
        # yPos = currentTextTop
        yPos = currentTextFromBottom - textInterlineH - textLineH
        textProp = siSettings.bottomNote if stampValue else ""
        img_draw.text((lineTextXEnd, yPos), textProp, font=font, fill=textColorRGBA)

    # ---------- camera -------------
    currentTextRight = renderW * (1.0 - paddingLeftNorm)

    if siSettings.cameraLensUsed:
        if siSettings.cameraUsed:
            textProp = ""
        else:
            textProp = "Lens: " if stampLabel else ""
        # textProp += f"{(scene.camera.data.lens):05.0f}" + " mm" if stampValue else ""       # :05.2f}
        textProp += (str(int(scene.camera.data.lens))).rjust(3, " ") + " mm" if stampValue else ""  # :05.2f}
        img_draw.text(
            (currentTextRight - (font.getsize(textProp))[0], currentTextTop), textProp, font=font, fill=textColorRGBA
        )

    if siSettings.cameraUsed:
        if siSettings.cameraLensUsed:
            currentTextRight -= (font.getsize(textProp))[0]
        textProp = "Cam: " if stampLabel3D else ""
        textProp += str(scene.camera.name) if stampValue else ""
        if siSettings.cameraLensUsed:
            textProp += "    "
        # if siSettings.cameraLensUsed:
        #     textProp += "   " + (str(int(scene.camera.data.lens))).rjust(3, " ") + " mm" if stampValue else ""
        # img_draw.text(
        #     (currentTextRight - (font.getsize(textProp))[0], currentTextTop), textProp, font=font, fill=textColorRGBA,
        # )
        img_draw.text(
            (col04, currentTextTop),
            textProp,
            font=font,
            fill=textColorRGBA,
        )

    # ---------- file -------------
    # currentTextTop += textLineH + textInterlineH  # * 2

    if siSettings.filenameUsed or siSettings.filepathUsed:
        textProp = "Blender file: " if stampLabel else ""
        if stampValue:
            filenameStr = ""
            if "" != siSettings.customFileFullPath:
                filenameStr = siSettings.customFileFullPath
                if "" == filenameStr:
                    textProp += "*** Custom File not specified ***"
            else:
                filenameStr = bpy.data.filepath
                if "" == filenameStr:
                    textProp += "*** File not saved ***"
            if "" != filenameStr:
                # head, tail = ntpath.split(filenameStr)
                if siSettings.filepathUsed:
                    textProp += str(Path(filenameStr).parent) + "\\"
                if siSettings.filenameUsed:
                    textProp += Path(filenameStr).name
            # textProp  += str(os.path.basename(bpy.data.filepath))
        # img_draw.text((col01, currentTextTop), textProp, font=font, fill=textColorRGBA)
        img_draw.text((col01, currentTextFromBottom), textProp, font=font, fill=textColorRGBA)

    dirAndFilename = getInfoFileFullPath(scene, currentFrame)
    if renderPath is None:
        renderPath = dirAndFilename[0]

    if not os.path.exists(renderPath):
        try:
            path = Path(renderPath)
            path.mkdir(parents=True, exist_ok=True)
        except Exception:
            print(f"\n*** Creation of the directory failed: {renderPath}\n")
            raise

    if renderFilename is None:
        filepath = renderPath + dirAndFilename[1]
    else:
        filepath = renderPath + renderFilename

    if verbose:
        print("Info file rendered name: ", (filepath))

    try:
        imgInfo.save(filepath)
    except BaseException:
        _logger.error_ext(f"Stamp Info: renderTmpImageWithStampedInfo Error: Cannot save file: {filepath}")
        raise


def drawRangesAndFrame(
    scene,
    img_draw,
    framemode,
    currentFrame,
    startRange,
    endRange,
    handle,
    frameUsed,
    rangeUsed,
    handlesUsed,
    textRight,
    textTop,
    font,
    fontLarge,
    color,
    padding,
):
    """
    framemode can be '3DFRAME' or 'VIDEOFRAME'
    """
    siSettings = scene.UAS_SM_StampInfo_Settings

    #    currentTextTopFor3DFrames += textLineH + textInterlineH
    #    currentTextLeftFor3DFrames = renderW * (1.0 - 0.05)

    # print(f"currentFrame: {currentFrame}")
    currentTextTopFor3DFrames = textTop
    currentTextLeftFor3DFrames = textRight
    textColorRGBA = color
    textColorGray = (128, 128, 128, 255)
    textColorGrayLight = (200, 200, 200, 255)
    textColorWhite = (235, 235, 235, 255)
    textColorRed = (200, 100, 100, 255)
    textColorGreen = (70, 210, 70, 255)
    textColorOrange = (245, 135, 42, 255)

    # stampLabel = siSettings.stampPropertyLabel
    stampValue = siSettings.stampPropertyValue
    textProp = ""

    # fontsize            = int(fontScaleHNorm * renderH)
    # font                = ImageFont.truetype("arial", fontsize)
    # textLineH           = (font.getsize("Aj"))[1]            # line height

    # text is aligned on the right !!! ###

    if stampValue:
        if rangeUsed or handlesUsed:
            textProp = " ]"
            currentTextLeftFor3DFrames -= (font.getsize(textProp))[0]
            img_draw.text(
                (currentTextLeftFor3DFrames, currentTextTopFor3DFrames), textProp, font=font, fill=textColorRGBA
            )

        if rangeUsed:
            fmt = f"0{padding}d"
            textProp = f"{endRange:{fmt}}"
            currentTextLeftFor3DFrames -= (font.getsize(textProp))[0]
            textColor = textColorOrange if not handlesUsed and currentFrame == endRange else textColorGray
            if handlesUsed and (endRange - handle < currentFrame):
                textColor = textColorRed
            img_draw.text((currentTextLeftFor3DFrames, currentTextTopFor3DFrames), textProp, font=font, fill=textColor)

        if rangeUsed and handlesUsed:
            textProp = " / "
            currentTextLeftFor3DFrames -= (font.getsize(textProp))[0]
            img_draw.text(
                (currentTextLeftFor3DFrames, currentTextTopFor3DFrames), textProp, font=font, fill=textColorRGBA
            )

        if handlesUsed:
            textProp = f"{(endRange - handle):{fmt}}"
            currentTextLeftFor3DFrames -= (font.getsize(textProp))[0]
            textColor = textColorOrange if currentFrame == endRange - handle else textColorGrayLight
            img_draw.text((currentTextLeftFor3DFrames, currentTextTopFor3DFrames), textProp, font=font, fill=textColor)

        if rangeUsed or handlesUsed:
            textProp = " / "
            currentTextLeftFor3DFrames -= (font.getsize(textProp))[0]
            img_draw.text(
                (currentTextLeftFor3DFrames, currentTextTopFor3DFrames), textProp, font=font, fill=textColorRGBA
            )

        if frameUsed:
            textProp = f"{currentFrame:{fmt}}"
            currentTextLeftFor3DFrames -= (fontLarge.getsize(textProp))[0]
            # currentTextHeight = (font.getsize(textProp))[1]
            textColor = textColorWhite
            if currentFrame < startRange + handle:
                textColor = textColorRed
            elif currentFrame == startRange + handle:
                textColor = textColorGreen
            elif currentFrame > endRange - handle:
                textColor = textColorRed
            elif currentFrame == endRange - handle:
                textColor = textColorOrange

            newTextHeight = (fontLarge.getsize(textProp))[1] - (font.getsize(textProp))[1]
            img_draw.text(
                (currentTextLeftFor3DFrames, currentTextTopFor3DFrames - newTextHeight),
                textProp,
                font=fontLarge,
                fill=textColor,
            )

        if (rangeUsed or handlesUsed) and frameUsed:
            textProp = " /  "
            currentTextLeftFor3DFrames -= (font.getsize(textProp))[0]
            img_draw.text(
                (currentTextLeftFor3DFrames, currentTextTopFor3DFrames), textProp, font=font, fill=textColorRGBA
            )

        if handlesUsed:
            textProp = f"{(startRange + handle):{fmt}}"
            currentTextLeftFor3DFrames -= (font.getsize(textProp))[0]
            textColor = textColorGreen if currentFrame == startRange + handle else textColorGrayLight
            img_draw.text((currentTextLeftFor3DFrames, currentTextTopFor3DFrames), textProp, font=font, fill=textColor)

        if rangeUsed and handlesUsed:
            textProp = " / "
            currentTextLeftFor3DFrames -= (font.getsize(textProp))[0]
            img_draw.text(
                (currentTextLeftFor3DFrames, currentTextTopFor3DFrames), textProp, font=font, fill=textColorRGBA
            )

        if rangeUsed:
            textProp = f"{startRange:{fmt}}"
            currentTextLeftFor3DFrames -= (font.getsize(textProp))[0]
            textColor = textColorGreen if not handlesUsed and currentFrame == startRange else textColorGray
            if handlesUsed and (currentFrame < startRange + handle):
                textColor = textColorRed
            img_draw.text((currentTextLeftFor3DFrames, currentTextTopFor3DFrames), textProp, font=font, fill=textColor)

        if rangeUsed or handlesUsed:
            textProp = "[ "
            currentTextLeftFor3DFrames -= (font.getsize(textProp))[0]
            img_draw.text(
                (currentTextLeftFor3DFrames, currentTextTopFor3DFrames), textProp, font=font, fill=textColorRGBA
            )

    if frameUsed:  # and stampLabel:
        textProp = ""
        # textProp += "Handle / " if handlesUsed else ""
        # textProp += "Range / " if rangeUsed else ""
        if "3DFRAME" == framemode:
            textProp += "3D Frame: " if frameUsed else ""
        else:
            textProp += "Video Frame: " if frameUsed else ""
        currentTextLeftFor3DFrames -= (font.getsize(textProp))[0]
        img_draw.text((currentTextLeftFor3DFrames, currentTextTopFor3DFrames), textProp, font=font, fill=textColorRGBA)

        # if siSettings.sceneFrameHandlesUsed:
        #     textProp += " / " + '{:03d}'.format(scene.frame_end - siSettings.shotHandles) + " / " if stampValue else ""
        # if siSettings.sceneFrameRangeUsed:
        #     textProp += '{:03d}'.format(scene.frame_end) + "]" if stampValue else ""
        # img_draw.text((currentTextLeftFor3DFrames, currentTextTop ), textProp, font=font, fill=textColorRGBA )

    # if siSettings.sceneFrameRangeUsed:
    #     textProp = "Range: " if stampLabel else ""
    #     textProp += "[" + str(scene.frame_start) + " / " + str(scene.frame_end) + "]" if stampValue else ""
    #     img_draw.text((col03, currentTextTop), textProp, font=font, fill=textColorRGBA )
