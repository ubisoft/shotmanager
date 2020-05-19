#-*- coding: utf-8 -*-
import bpy
from bpy.types import Panel, Operator
from bpy.props import CollectionProperty, StringProperty

import shot_manager.operators.shots as shots


#from ..properties import get_takes


def _copy_shot ( src_shot, dst_shot ):
    dst_shot.name = src_shot.name
    dst_shot.start = src_shot.start
    dst_shot.end = src_shot.end
    dst_shot.enabled = src_shot.enabled
    dst_shot.camera = src_shot.camera
    dst_shot.color = src_shot.color


class UAS_ShotManager_AddTake( Operator ):
    bl_idname = "uas_shot_manager.add_take"
    bl_label = "Add New Take"
    bl_description = "Add a new take"
    bl_options = { "INTERNAL" }

    name: StringProperty(
        name = "Name" )

    # @classmethod
    # def poll ( cls, context ):
    #     props = context.scene.UAS_shot_manager_props
    #     currentTakeInd = props.getCurrentTakeIndex()
    #     # take 0 (default, named Main Take) should not be removed !!
    #     if  len(props.getTakes()) <= 0 or currentTakeInd <= 0: 
    #         return False
    #     return True

    def draw ( self, context ):
        layout  = self.layout
        scene   = context.scene
        props   = scene.UAS_shot_manager_props

        box = layout.box()
        row = box.row( align = True )
        grid_flow = row.grid_flow ( align = True, columns = 2, even_columns = False )
        
        if len(props.getTakes()) <= 0:
            col = grid_flow.column( align = False )
            col.scale_x = 0.6
            col.label( text="Name (Base take):")
            col = grid_flow.column( align = False )
            col.enabled = False
            col.prop ( self, "name", text="" )
        else:
            col = grid_flow.column( align = False )
            col.scale_x = 0.6
            col.label( text="New Take Name:")
            col = grid_flow.column( align = True )
            col.prop ( self, "name", text="" )

        layout.separator()

    def execute ( self, context ):
        scene   = context.scene
        props   = scene.UAS_shot_manager_props

        takes = props.getTakes()
        take = None
        if len(takes) <= 0:
            take = props.createDefaultTake()
        else:
            self.name = props.getUniqueTakeName(self.name)
            take = takes.add()
            take.name = self.name
        
        props.current_take_name = take.name

        return { "FINISHED" }

    def invoke ( self, context, event ):
        takes = context.scene.UAS_shot_manager_props.getTakes()
        if len(takes) <= 0:
            self.name = "Main Take"
        else:
            self.name = f"Take_{len ( context.scene.UAS_shot_manager_props.getTakes() ) - 1 + 1:02}"
        
        return context.window_manager.invoke_props_dialog ( self )


class UAS_ShotManager_DuplicateTake( Operator ):
    bl_idname = "uas_shot_manager.duplicate_take"
    bl_label = "Duplicate Current Take"
    bl_description = "Duplicate the current take"
    bl_options = { "INTERNAL" }

    name: StringProperty( name = "Name" )

    def draw ( self, context ):
        layout  = self.layout

        box = layout.box()
        row = box.row( align = True )
        grid_flow = row.grid_flow ( align = True, columns = 2, even_columns = False )
        
        col = grid_flow.column( align = False )
        col.scale_x = 0.6
        col.label( text="New Take Name:")
        col = grid_flow.column( align = True )
        col.prop ( self, "name", text="" )

        layout.separator()

    def execute ( self, context ):
        props = context.scene.UAS_shot_manager_props
        takes = props.getTakes()
        shots = props.getShotsList()

        currentShotIndex = props.getCurrentShotIndex()

        newTake = takes.add()
        newTake.name = props.getUniqueTakeName(self.name)
        newTakeInd = props.getTakeIndex(newTake)
        for shot in shots:
            newShot = props.copyShot( shot, takeIndex = newTakeInd )
        props.current_take_name = self.name

        props.setCurrentShotByIndex(currentShotIndex)
        
        return { "FINISHED" }

    def invoke ( self, context, event ):
        self.name = f"Take_{len ( context.scene.UAS_shot_manager_props.getTakes() ) + 1:02}"
        return context.window_manager.invoke_props_dialog ( self )


class UAS_ShotManager_RemoveTake( Operator ):
    bl_idname = "uas_shot_manager.remove_take"
    bl_label = "Remove Current Take"
    bl_description = "Remove the current take.\nMain Take, as the base take, cannot be removed"
    bl_options = { "INTERNAL" }

    @classmethod
    def poll ( cls, context ):
        props = context.scene.UAS_shot_manager_props
        currentTakeInd = props.getCurrentTakeIndex()
        # take 0 (default, named Main Take) should not be removed !!
        if  len(props.getTakes()) <= 0 or currentTakeInd <= 0: 
            return False
        return True

    def execute ( self, context ):
        props = context.scene.UAS_shot_manager_props
        props.setCurrentShotByIndex(-1)
    
        currentTakeInd = props[ "current_take_name" ]
        newTakeInd = 0

        if props[ "current_take_name" ] == 0:
            if 1 < len(props.takes):
                props.takes.remove ( currentTakeInd )
                props[ "current_take_name" ] = 0
            else:
                print("   About to remove the only take...")
        else:
            props[ "current_take_name" ] = currentTakeInd - 1
            props.takes.remove ( currentTakeInd )
        
        props.setCurrentShotByIndex(0)

        return { "FINISHED" }



class UAS_ShotManager_RenameTake( Operator ):
    bl_idname = "uas_shot_manager.rename_take"
    bl_label = "Rename Take"
    bl_description = "Rename the current take.\nMain Take, as the base take, cannot be renamed"
    bl_options = { "INTERNAL" }

    name : StringProperty (
        name = "Name" )

    @classmethod
    def poll ( cls, context ):
        props = context.scene.UAS_shot_manager_props
        currentTakeInd = props.getCurrentTakeIndex()
        # take 0 (default, named Main Take) should not be renamed !!
        if  len(props.getTakes()) <= 0 or currentTakeInd <= 0: 
            return False
        return True

    def execute ( self, context ):
        props = context.scene.UAS_shot_manager_props
        currentTake = props.getCurrentTake()

        if currentTake.name != self.name:
            self.name = props.getUniqueTakeName(self.name)
            currentTake.name = self.name

        return { "FINISHED" }

    def invoke ( self, context, event ):
        self.name = context.scene.UAS_shot_manager_props.getCurrentTake().name
        return context.window_manager.invoke_props_dialog ( self )



class UAS_ShotManager_Debug_FixShotsParent( Operator ):
    """ Recompute the value of parentTakeIndex for each shot
    """
    bl_idname = "uas_shot_manager.debug_fixshotsparent"
    bl_label = "Debug - Fix Shots Parent"
    bl_description = "Recompute the value of parentTakeIndex for each shot"
    bl_options = { "INTERNAL" }

    def execute ( self, context ):
        context.scene.UAS_shot_manager_props.fixShotsParent()

        return { "FINISHED" }



class UAS_ShotManager_ResetTakesToDefault( Operator ):
    bl_idname = "uas_shot_manager.reset_takes_to_default"
    bl_label = "Reset Takes to Default"
    bl_description = "Clear all exisiting takes"
    bl_options = { "INTERNAL" }

    def draw ( self, context ):
        layout  = self.layout
        layout.separator()
        layout.label( text="This will remove all the takes from the current scene.")
        layout.label( text="Please confirm:")
        layout.separator()

    def execute ( self, context ):
        props = context.scene.UAS_shot_manager_props
        takes = props.getTakes()
        
        for i in range(len(takes), -1, -1):
            takes.remove(i)
        
        props.createDefaultTake()
        

        #https://docs.blender.org/api/current/bpy.props.html
#         props.takes.objects_remove_all()
# or c in bpy.data.collections:
#     if not c.users:
#         bpy.data.collections.remove(c)

        return { "FINISHED" }
    
    def invoke ( self, context, event ):
        return context.window_manager.invoke_props_dialog ( self )



_classes = (    
                UAS_ShotManager_AddTake,
                UAS_ShotManager_DuplicateTake,
                UAS_ShotManager_RemoveTake,
                UAS_ShotManager_RenameTake,
                UAS_ShotManager_Debug_FixShotsParent,
                UAS_ShotManager_ResetTakesToDefault )

def register ( ):
    for cls in _classes:
        bpy.utils.register_class ( cls )


def unregister ( ):
    for cls in reversed ( _classes ):
        bpy.utils.unregister_class ( cls )