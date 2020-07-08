import bpy
import os

from shotmanager.api import rrs

# Get current file path
current_file = bpy.data.filepath
current_dir = os.path.dirname(current_file)

if "" == current_file:
    print("*** Save the scene first ***")


# Initialize the shot manager of the current scene with the project environment variables
rrs.initialize_for_rrs(override_existing=True, verbose=True)

# launch the rendering process of the shots from the current take
rrs.publishRRS(current_dir, take_index=-1, verbose=True)
