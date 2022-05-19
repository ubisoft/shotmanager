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
Shot Manager debug package
"""

from . import sm_debug_operators
from . import sm_debug_ui
from . import sm_debug

from .scripts import WkTimelineModalRect

from ..config import sm_logging

_logger = sm_logging.getLogger(__name__)


def register():
    _logger.debug_ext("       - Registering Debug Package", form="REG")

    sm_debug_operators.register()
    sm_debug.register()
    sm_debug_ui.register()
    WkTimelineModalRect.register()


def unregister():
    _logger.debug_ext("       - Unregistering Debug Package", form="UNREG")

    WkTimelineModalRect.unregister()
    sm_debug_ui.unregister()
    sm_debug.unregister()
    sm_debug_operators.unregister()
