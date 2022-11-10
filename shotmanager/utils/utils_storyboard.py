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
Functions to manipulate Shot Manager storyboard entities
"""

from . import utils
from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


def getStoryboardObjects(scene):
    """Return a list of all the objects of the scene that are belonging to storyboard shots
    This includes the shots cameras and all their hierarchy (empty, gp, children of all kinds),
    this for all takes

    See also shot.getStoryboardChildren()
    """
    props = config.getAddonProps(scene)

    shotCameras = props.getCameras(fromAllTakes=True, ignoreDisabled=False, onlyShotsOfType="STORYBOARD")
    allStbObjects = list()
    allStbObjects.extend(shotCameras)

    for cam in shotCameras:
        camChildren = utils.getChildrenHierarchy(cam)
        allStbObjects.extend(camChildren)

    return allStbObjects
