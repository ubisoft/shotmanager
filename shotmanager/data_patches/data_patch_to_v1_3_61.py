import bpy
from ..utils import utils

# 05/11/2020
# Patch to upgrade the shot manager data created with a shot manager version older than V.1.3.61

# v1_3_61: 1003061


def data_patch_to_v1_3_61():
    """Patch to introduce the Playblast render settings
    """
    for scn in bpy.data.scenes:
        # if "UAS_shot_manager_props" in scn:
        if getattr(bpy.context.scene, "UAS_shot_manager_props", None) is not None:
            #   print("\n   Shot Manager instance found in scene " + scn.name)
            props = scn.UAS_shot_manager_props

            #   print("     Data version: ", props.dataVersion)
            #  print("     Shot Manager version: ", bpy.context.window_manager.UAS_shot_manager_version)
            if props.dataVersion <= 0 or props.dataVersion < bpy.context.window_manager.UAS_shot_manager_version:

                # apply patch and apply new data version
                #       print("       Applying data patch data_patch_to_v1_3_61 to scenes")

                props.renderSettingsPlayblast.name = "Playblast Preset"
                props.renderSettingsPlayblast.renderMode = "PLAYBLAST"
                props.renderSettingsPlayblast.useStampInfo = False

                # set right data version
                # props.dataVersion = bpy.context.window_manager.UAS_shot_manager_version
                props.dataVersion = bpy.context.window_manager.UAS_shot_manager_version
                print(
                    f"       Scene {scn.name}: Data upgraded to version V.{utils.convertVersionIntToStr(props.dataVersion)}"
                )

