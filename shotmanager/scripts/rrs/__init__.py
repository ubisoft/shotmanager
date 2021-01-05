#############################################
# RRS Package
#############################################

import bpy

from .ui_rrs import UAS_PT_ShotManager_RRS_Debug
from .operators_rrs import UAS_InitializeRRSProject, UAS_LaunchRRSRender

_classes = (
    UAS_InitializeRRSProject,
    UAS_LaunchRRSRender,
    UAS_PT_ShotManager_RRS_Debug,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
