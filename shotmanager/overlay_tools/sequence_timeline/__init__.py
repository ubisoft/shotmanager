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

from . import timeline_ui


def register():
    print("       - Registering Viewport Timeline Package")

    timeline_ui.register()


def unregister():
    print("       - Unregistering Viewport Timeline Package")

    try:
        timeline_ui.unregister()
    except Exception:
        print("       - Paf in Unregistering Viewport Timeline Package")

