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
Shot Manager API - Interface with RRS Publishing
"""

from shotmanager.scripts.rrs import publish_rrs


def initialize_for_rrs(override_existing=True, verbose=False):
    publish_rrs.initializeForRRS(override_existing, verbose=verbose)


def publishRRS(
    prodFilePath,
    take_index=-1,
    verbose=False,
    use_cache=False,
    fileListOnly=False,
    rerender_existing_shot_videos=True,
    render_also_disabled=True,
    settings_dict=None,
):
    """
    Arguments:
    settings_dict: a dictionary with various custom settings

    Return a dictionary with the rendered and the failed file paths
    The dictionary have the following entries:
        - rendered_files_in_cache: rendered files when cache is used
        - failed_files_in_cache: failed files when cache is used
        - edl_files_in_cache: edl files when cache is used
        - rendered_files: rendered files (either from direct rendering or from copy from cache)
        - failed_files: failed files (either from direct rendering or from copy from cache)
        - edl_files: edl files
        - other_files: json dumped file list
    """
    return publish_rrs.publishRRS(
        prodFilePath,
        takeIndex=take_index,
        verbose=verbose,
        useCache=use_cache,
        fileListOnly=fileListOnly,
        rerenderExistingShotVideos=rerender_existing_shot_videos,
        renderAlsoDisabled=render_also_disabled,
        settingsDict=settings_dict,
    )
