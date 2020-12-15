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

# from . import sequencer_draw


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
<<<<<<< HEAD


#   sequencer_draw.register ( )
=======
    sequencer_draw.register()
>>>>>>> 9e4343492f6dd09de835ef81412be5e0f0030a07


def unregister():

    try:
        sequencer_draw.unregister()
    except Exception as e:
        print("Error in Unregister sequencer_draw")

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
<<<<<<< HEAD

#  sequencer_draw.unregister ( )
=======
>>>>>>> 9e4343492f6dd09de835ef81412be5e0f0030a07

