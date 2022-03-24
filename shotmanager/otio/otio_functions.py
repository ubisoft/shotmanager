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
Useful functions for Shot Manager Otio package
"""

from ..config import sm_logging

_logger = sm_logging.getLogger(__name__)


def isOtioAvailable():
    """Return True if OpenTimelineIO is installed and the Shot Manager package can be imported and used"""

    try:
        import opentimelineio

        _logger.debug_ext(f"isOtioAvailable: True - OTIO can be imported: {opentimelineio.__version__}", col="GREEN")
        return True

    except ModuleNotFoundError:
        _logger.debug_ext("*** isOtioAvailable: False - OTIO CANNOT be imported", col="RED")

        return False
