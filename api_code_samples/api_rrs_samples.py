import bpy
import os

from shotmanager.api import rrs

# This should work with any scene where a Shot Manager instance has been instanced and where
# there are several shots
# In case a scene is required you can use this one from the GitLab:
# https://gitlab-ncsa.ubisoft.org/animation-studio/blender/shotmanager-addon/-/blob/master/fixtures/shots_sceneRunningRabbid/shots_sceneRunningRabbid.blend


# Get current file path
current_file = bpy.data.filepath
current_dir = os.path.dirname(current_file)

if "" == current_file:
    print("*** Save the scene first ***")


# Initialize the shot manager of the current scene with the project environment variables
rrs.initialize_for_rrs(override_existing=True, verbose=True)

# launch the rendering process of the shots from the current take and get a dictionary of
# the rendered and failed files
# filesDict = {"rendered_files": newMediaFiles, "failed_files": failedFiles}
files_dico = rrs.publishRRS(current_dir, take_index=-1, verbose=True)

print("\nRendered files: ", len(files_dico["rendered_files"]))
for f in files_dico["rendered_files"]:
    print("   - ", f)

print("\nFailed files: ", len(files_dico["failed_files"]))
for f in files_dico["failed_files"]:
    print("   - ", f)

