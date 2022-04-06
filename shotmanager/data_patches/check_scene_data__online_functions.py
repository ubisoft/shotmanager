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
Data check functions
"""

# set shot manager data version

# return a SM IDPropertyGroup if found, an exception otherwise
# this is the best way to know if SM is instanced in the scene when we are not sure it exists
# *** warning: this returns a IDPropertyGroup, not the SM props ***
from tabnanny import verbose


propGrp = C.scene["UAS_shot_manager_props"]
checkStr += f"propGrp: {propGrp}")

# >>> type(props)
# <class 'IDPropertyGroup'>

# this always returns False...
prop_hasattr = hasattr(C.scene, "UAS_shot_manager_props")
checkStr += f"prop_hasattr: {prop_hasattr}")


# *** warning: even if the SM IDPropertyGroup exists in the scene the current function can return None
# if SM add-on is not loaded! ***
props_getattr = getattr(C.scene, "UAS_shot_manager_props", None)
checkStr += f"props from getattr: {props_getattr}")

# can return an error if SM add-on is not loaded
props = C.scene.UAS_shot_manager_props

# to test if SM addon is loaded:
# return an exception if not found
C.preferences.addons["shotmanager"]


# use this to get and display the scene data:
check_shotmanager_file_data()


props = C.scene.UAS_shot_manager_props
props.project_naming_project_format
# works great
"project_naming_project_format" in props
# to get the value:
p = getattr(props, "project_naming_project_format")
# this is not forcing the value to None:
p = getattr(props, "project_naming_project_format", None)
print(f"p: {p}")
