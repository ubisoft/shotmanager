from . import rendering_operators
from . import rendering_ui


def register():
    print("       - Registering Rendering Package")
    rendering_operators.register()
    rendering_ui.register()


def unregister():
    rendering_ui.unregister()
    rendering_operators.unregister()
