import bpy


class HelloWorldPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""

    bl_label = "Hello World Panel"
    bl_idname = "OBJECT_PT_hello"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        obj = context.active_object

        row = layout.row()
        row.label(text="Hello world!", icon="WORLD_DATA")

        row = layout.row()
        row.label(text="Active object is: " + obj.name)
        row = layout.row()
        row.prop(obj, "name")

        row = layout.row()
        row.operator("mesh.primitive_cube_add")


def register():
    bpy.utils.register_class(HelloWorldPanel)


def unregister():
    bpy.utils.unregister_class(HelloWorldPanel)


# import bpy
# for a in bpy.context.screen.areas:
#     if a.type == 'PROPERTIES':
#         break

# s = a.spaces.active
# s.context
# print(f"s.context: {s.context}")

# for k in s.rna_type.properties['context'].enum_items_static.items():
#     print(f"key: {k.key}")

# TOOL Tool, Active Tool and Workspace settings.
# SCENE Scene, Scene.
# RENDER Render, Render.
# OUTPUT Output, Output.
# VIEW_LAYER View Layer, View Layer.
# WORLD World, World.
# OBJECT Object, Object.
# CONSTRAINT Constraints, Object Constraints.
# MODIFIER Modifiers, Modifiers.
# DATA Data, Object Data.
# BONE Bone, Bone.
# BONE_CONSTRAINT Bone Constraints, Bone Constraints.
# MATERIAL Material, Material.
# TEXTURE Texture, Texture.
# PARTICLES Particles, Particles.
# PHYSICS Physics, Physics.
# SHADERFX Effects, Object visual effects.
