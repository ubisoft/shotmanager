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
To do: module description here.
"""

import re


def start_with_act(s):
    res = re.match(r"^Act(\d\d)", s)
    if res is not None:
        return True, res.group(1)
    return False, ""


def start_with_seq(s):
    res = re.match(r"^Act(\d\d)_Seq(\d\d\d\d)", s)
    if res is not None:
        return True, res.group(1), res.group(2)
    return False, "", ""


def start_with_shot(s):
    res = re.match(r"^Act(\d\d)_Seq(\d\d\d\d)_Sh(\d\d\d\d)", s)
    if res is not None:
        return True, res.group(1), res.group(2), res.group(3)
    return False, "", "", ""
