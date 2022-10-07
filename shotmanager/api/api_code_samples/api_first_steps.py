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
Shot Manager API samples - First steps

Documentation and general concepts: https://github.com/ubisoft/shotmanager/blob/main/doc/shot_manager_api.md
"""


import bpy

from shotmanager.api import shot_manager
from shotmanager.api import shot
from shotmanager.api import take


#############################
# Initialisation
#############################

# Create an instance of Shot Manager: No need to create it, it is created automatically in each new scene when the add-on is enabled.

# Get the shot manager instance of the scene
sm_props = shot_manager.get_shot_manager(bpy.context.scene)

# Initialyse shot manager instance to create, amonst other things, a default take
shot_manager.initialize_shot_manager(sm_props)

# Possible verification that the parent scene of this instance is the scan
print("Current scene name: ", bpy.context.scene.name)
sm_scene = shot_manager.get_parent_scene(sm_props)
print("SM scene name: ", sm_scene.name)


#############################
# Takes manipulation
#############################


# Get current take
current_take = shot_manager.get_current_take(sm_props)
print("Current take name: ", current_take.name)
print("Current take name (path compliant): ", take.get_name_path_compliant(current_take))

take_index = shot_manager.get_take_index(sm_props, current_take)
print("Current take index: ", take_index)

# Create another take at the end of the list
my_other_take = shot_manager.add_take(sm_props, at_index=-1, name="My New Take")

# Get the number of takes in the shot manager
num_takes = len(shot_manager.get_takes(sm_props))
print("Number of takes: ", num_takes)

# Get the index of the new take
my_other_take_index = shot_manager.get_take_index(sm_props, my_other_take)
print("New take index: ", my_other_take_index)

# Make the new take the current one
shot_manager.set_current_take_by_index(sm_props, my_other_take_index)

# Change take name
current_take = shot_manager.get_current_take(sm_props)
take.set_name(current_take, "My New Take Renamed")


# Duplicate take
# wkip to do

# Delete take
# wkip to do


#############################
# Shots manipulation
#############################


# Add a new shot to the current take
my_first_shot = shot_manager.add_shot(
    sm_props,
    at_index=-1,  # will be added at the end
    take_index=-1,  # will be added to the current take (the new renamed one)
    name="Hello World Shot",
    start=15,  # avoid using a short start value before the lenght of the handles (which is 10)
    end=50,
    camera=None,
    color=(0.2, 0.6, 0.8, 1),
    enabled=True,
)

# Get shot name
print("Shot name: ", shot.get_name(my_first_shot))

# Rename shot
shot.set_name(my_first_shot, "My First Shot Renamed")
print("Shot name: ", shot.get_name(my_first_shot))

# Change shot start and end
# Remember that the end frame is INCLUDED in the range
shot.set_start(my_first_shot, 34)
shot.set_end(my_first_shot, 67)
print("Shot duration:", shot.get_duration(my_first_shot))

# Enable or disable the shot
print("Shot enable state:", shot.get_enable_state(my_first_shot))
shot.set_enable_state(my_first_shot, False)
print("Shot new enable state:", shot.get_enable_state(my_first_shot))

# Create 2 cameras
cam = bpy.data.cameras.new("Camera01")
cam_ob = bpy.data.objects.new(cam.name, cam)
bpy.context.collection.objects.link(cam_ob)
bpy.data.cameras[cam.name].lens = 40
cam_ob.location = (0.0, 0.0, 0.0)

cam_shot_1 = cam_ob

cam = bpy.data.cameras.new("Camera02")
cam_ob = bpy.data.objects.new(cam.name, cam)
bpy.context.collection.objects.link(cam_ob)
bpy.data.cameras[cam.name].lens = 50
cam_ob.location = (2.0, 0.0, 0.0)

cam_shot_2 = cam_ob

# Assign the first camera to the shot
shot.set_camera(my_first_shot, cam_shot_1)

# Create another shot with a camera, before the first one
my_second_shot = shot_manager.add_shot(
    sm_props,
    at_index=1,
    name="My Second Shot",
    start=80,
    end=98,
    camera=cam_shot_2,
    color=(0.1, 0.8, 0.3, 1),
)

# And another one
my_third_shot = shot_manager.add_shot(
    sm_props,
    at_index=1,
    name="My third Shot",
    start=62,
    end=120,
    camera=cam_shot_2,
    color=(0.9, 0.2, 0.3, 1),
)

# Get the number of takes
shots = shot_manager.get_shots(sm_props)
print("\nShots number: ", len(shots))
for s in shots:
    print("  - ", s.name)

# Make this new shot the current one
shot_manager.set_current_shot(sm_props, my_second_shot)

# Get the list of all the enabled shots
shots = shot_manager.get_shots_list(sm_props, ignore_disabled=True)
print("\nEnabled shots number: ", len(shots))
for s in shots:
    print("  - ", s.name)


# Delete first added shot
my_first_shot = shot_manager.get_shot(sm_props, 1)
shot_manager.remove_shot(sm_props, my_first_shot)
