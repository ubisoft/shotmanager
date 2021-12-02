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
Draw an interactive timeline in the 3D viewport
"""

import bpy
from bpy.props import BoolProperty

from . import seq_timeline
from . import seq_timeline_operators

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


def register():
    _logger.debug_ext("       - Registering Sequence Timeline", form="REG")

    seq_timeline.register()
    seq_timeline_operators.register()


def unregister():
    _logger.debug_ext("       - Unregistering Sequence Timeline", form="UNREG")

    seq_timeline_operators.unregister()

    try:
        seq_timeline.unregister()
    except Exception:
        print("       - Paf in Unregistering Sequence Timeline Package")

