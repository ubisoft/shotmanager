import bpy

from shotmanager.config import config

# from .greasepencil_props import UAS_ShotManager_RenderGlobalContext, UAS_ShotManager_RenderSettings
from . import cameraBG_operators

import logging

_logger = logging.getLogger(__name__)


def register():
    if config.uasDebug:
        print("       - Registering Grease Pencil Package")

    # for cls in _classes:
    #     bpy.utils.register_class(cls)

    cameraBG_operators.register()
    # rendering_ui.register()    # done in shotmanager.__init__ in order to display the panel in the right order


def unregister():
    # for cls in reversed(_classes):
    #     bpy.utils.unregister_class(cls)

    # rendering_ui.unregister()   # done in shotmanager.__init__ in order to display the panel in the right order
    cameraBG_operators.unregister()
