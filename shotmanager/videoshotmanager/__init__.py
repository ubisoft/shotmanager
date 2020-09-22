from .operators import general
from .operators import tracks
from .operators import prefs
from .operators import vsm_tools
from .properties import vsm_props

# from .ui.vsm_ui import UAS_PT_VideoShotManager
from .ui import vsm_ui


def register():
    print("       - Registering Video Shot Manager Package")

    general.register()
    prefs.register()
    vsm_props.register()
    tracks.register()
    vsm_tools.register()
    vsm_ui.register()


def unregister():
    vsm_ui.unregister()
    vsm_tools.unregister()
    tracks.unregister()
    vsm_props.unregister()
    prefs.unregister()
    general.unregister()

