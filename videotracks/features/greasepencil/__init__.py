import bpy

from shotmanager.config import config

# from .greasepencil_props import UAS_ShotManager_RenderGlobalContext, UAS_ShotManager_RenderSettings
from . import greasepencil_operators

import logging

_logger = logging.getLogger(__name__)


# _classes = (UAS_ShotManager_OT_AddGreasePencil,)


def register():
    if config.uasDebug:
        print("       - Registering Grease Pencil Package")

    # for cls in _classes:
    #     bpy.utils.register_class(cls)

    greasepencil_operators.register()
    # rendering_ui.register()    # done in shotmanager.__init__ in order to display the panel in the right order


def unregister():
    # for cls in reversed(_classes):
    #     bpy.utils.unregister_class(cls)

    # rendering_ui.unregister()   # done in shotmanager.__init__ in order to display the panel in the right order
    greasepencil_operators.unregister()
