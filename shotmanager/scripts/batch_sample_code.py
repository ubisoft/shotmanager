import bpy

shots = bpy.context.scene.UAS_shot_manager_props.get_shots()
for shot in shots:
#    shot.name += "0"
    shot.name = shot.name.replace("H", "h")


    