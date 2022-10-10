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
Rendering functions
"""


def applyVideoSettings(scene, props, mode, renderMode, renderPreset):
    """
    Args:
        mode:   defines at which step the settings are required
                SHOT: to render the shot images
                SHOT_COMPO: to composite the shot video in the VSE
                SEQUENCE: to render the whole sequence in the VSE
    """

    # *** Playblast mode is NOT related to the use of Project Settings ***

    if "SHOT" == mode:
        if "PLAYBLAST" == renderMode:
            # wkip use jpg
            scene.render.image_settings.file_format = "JPEG"
            scene.render.image_settings.quality = 85

            # add the file extention to the rendered file names
            scene.render.use_file_extension = True
        else:
            if props.use_project_settings:
                scene.render.image_settings.file_format = props.project_images_output_format
                # scene.render.image_settings.file_format = "FFMPEG"
                # scene.render.ffmpeg.format = "MPEG4"
                # scene.render.ffmpeg.constant_rate_factor = "PERC_LOSSLESS"  # "PERC_LOSSLESS"
                # scene.render.ffmpeg.gopsize = 5  # keyframe interval
                # scene.render.ffmpeg.audio_codec = "AAC"

                scene.render.use_file_extension = True

            else:
                scene.render.image_settings.file_format = "PNG"
                scene.render.use_file_extension = True
                # renderMode = "PROJECT" if renderPreset is None else renderPreset.renderMode
