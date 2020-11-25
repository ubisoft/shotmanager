from .operators import general
from .operators import tracks
from .operators import prefs
from .operators import vsm_tools
from .properties import vsm_props

# from .ui.vsm_ui import UAS_PT_VideoShotManager
from .ui import vsm_ui
from .ui import vsm_panels_ui
from .ui import vsm_time_control_ui

from shotmanager.rrs_specific import rrs_vsm_tools


def register():
    print("       - Registering Video Shot Manager Package")

    # rrs specific
    rrs_vsm_tools.register()

    general.register()
    prefs.register()
    vsm_props.register()
    tracks.register()
    vsm_tools.register()
    vsm_ui.register()
    vsm_panels_ui.register()
    vsm_time_control_ui.register()


def unregister():

    vsm_time_control_ui.unregister()
    vsm_panels_ui.unregister()
    vsm_ui.unregister()
    vsm_tools.unregister()
    tracks.unregister()
    vsm_props.unregister()
    prefs.unregister()
    general.unregister()

    # rrs specific
    rrs_vsm_tools.unregister()

