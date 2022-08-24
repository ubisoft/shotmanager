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
Markers navigation toolbar
"""

from . import markers_nav_bar
from . import markers_nav_bar_operators

# from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


def register():
    _logger.debug_ext("       - Registering Tool: Markers Nav Bar Package", form="REG")

    markers_nav_bar_operators.register()
    markers_nav_bar.register()


def unregister():
    _logger.debug_ext("       - Unregistering Tool: Markers Nav Bar Package", form="UNREG")

    markers_nav_bar.unregister()
    markers_nav_bar_operators.unregister()
