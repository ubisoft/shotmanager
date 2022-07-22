# GPLv3 License
#
# Copyright (C) 2022 Ubisoft
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
Classes and functions dedicated to check instances, attributes...
"""


def listAttrs(classInstance):
    attributes = list()

    for prop in classInstance.bl_rna.properties:
        # Ignores anything starting with underscore
        # (that is, private and protected attributes)
        if not prop.identifier.startswith("_"):
            if -1 == prop.identifier.find("rna"):
                if hasattr(prop, "default"):
                    # val = getattr(classInstance, prop.identifier)
                    # print(
                    #     f"{prop.identifier}   name: {prop.name}   value: {val}   default: {prop.default}   class: {prop.__class__.__name__}"
                    # )
                    #   EnumProperty
                    attributes.append(prop)

    return attributes


def resetAttrs(classInstance):
    attributes = listAttrs(classInstance)

    for prop in attributes:

        # val = getattr(classInstance, prop.identifier)
        # print(
        #     f"{prop.identifier}   name: {prop.name}   value: {val}   default: {prop.default}   class: {prop.__class__.__name__}"
        # )

        # required for enums where items are defined by a function and so there is no valid default value
        if "EnumProperty" == prop.__class__.__name__ and 0 == len(prop.enum_items):
            # if "EnumProperty" == prop.__class__.__name__ and 0 == len(prop.enum_items_static):
            classInstance.property_unset(prop.identifier)

        # required for arrays of float such as color
        elif "FloatProperty" == prop.__class__.__name__:
            classInstance.property_unset(prop.identifier)

        # required for arrays of int
        elif "IntProperty" == prop.__class__.__name__:
            classInstance.property_unset(prop.identifier)

        else:
            # for some reasons property_unset is not working in some cases, hence this line
            setattr(classInstance, prop.identifier, prop.default)

        # val = getattr(classInstance, prop.identifier)
        # print(
        #     f"{prop.identifier}   name: {prop.name}   value: {val}   default: {prop.default}   class: {prop.__class__.__name__}"
        # )
