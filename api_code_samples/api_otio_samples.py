import bpy
import os

from shotmanager.api import shot_manager
from shotmanager.api import otio

# This should work with any scene where a Shot Manager instance has been instanced and where
# there are several shots
# In case a scene is required you can use this one from the GitLab:
# https://gitlab-ncsa.ubisoft.org/animation-studio/blender/shotmanager-addon/-/blob/master/fixtures/shots_sceneRunningRabbid/shots_sceneRunningRabbid.blend

# Get the shot manager instance of the scene
sm_props = shot_manager.get_shot_manager(bpy.context.scene)

# Get current file path
current_file = bpy.data.filepath
current_dir = os.path.dirname(current_file)

if "" == current_file:
    print("*** Save the scene first ***")

# Export otio file from the specified scene to the directory containing the current file
print("Exporting Otio File to: ", current_dir)
otio.export_otio(sm_props, take_index=-1, render_root_file_path=current_dir)

