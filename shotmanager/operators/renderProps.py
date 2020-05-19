#-*- coding: utf-8 -*-

import os
import json
import addon_utils
from pathlib import Path

import subprocess

import bpy
from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import IntProperty, StringProperty, EnumProperty, BoolProperty, FloatVectorProperty

from ..utils import utils

from ..scripts.RRS_StampInfo import setRRS_StampInfoSettings, set_StampInfoShotSettings

# for file browser:
#from bpy_extras.io_utils import ImportHelper


def get_media_path ( out_path, take_name, shot_name):
    
    if out_path.startswith ( "//" ):
        out_path = str ( Path ( bpy.data.filepath ).parent.absolute ( ) ) + out_path[ 1 : ]
    return f"{out_path}/{take_name}/{bpy.context.scene.UAS_shot_manager_props.render_shot_prefix + shot_name}.mp4"



##########
# Render
##########
class UAS_PT_ShotManagerRenderPanel ( Panel ):
    bl_label = "Rendering"
    bl_idname = "UAS_PT_ShotManagerRenderPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UAS Shot Man"
    bl_options = { "DEFAULT_CLOSED" }



    def draw ( self, context ):
        props = context.scene.UAS_shot_manager_props

        layout = self.layout
        layout.separator()
        row = layout.row()
        row.separator( factor = 3 )
        if not props.useProjectRenderSettings:
            row.alert = True
        row.prop( props, "useProjectRenderSettings" )
        row.operator( "uas_shot_manager.render_restore_project_settings" )
        row.separator( factor = 0.1 )
        
        row = layout.row()
        row.separator( factor = 3 )
        row.prop ( props, "useStampInfoDuringRendering" )

        row = layout.row( align = True)
        row.separator( factor = 3 )
        if not props.isRenderRootPathValid():
            row.alert = True
        row.prop ( props, "renderRootPath" )
        row.alert = False
        row.operator("uas_shot_manager.openpathbrowser", text="", icon='FILEBROWSER', emboss=True)
        row.separator()
        row.operator ( "uas_shot_manager.render_openexplorer", text="", icon='FILEBROWSER').path = props.renderRootPath
        row.separator()
        layout.separator()


        box = layout.box()
        row = box.row( align = True)
        row.scale_y = 1.6
        #row.operator ( renderProps.UAS_PT_ShotManager_RenderDialog.bl_idname, text = "Render Active", icon = "RENDER_ANIMATION" ).only_active = True
        
        #row.use_property_split = True
        #row           = layout.row(align=True)
       # split = row.split ( align = True )
        row.scale_x = 1.2
        row.prop( props, "displayStillProps", text = "", icon = "IMAGE_DATA" )
        row.operator ( "uas_shot_manager.render", text = "Render Image" ).renderMode = 'STILL'
        row.separator( factor = 2)

        row.scale_x = 1.2
        row.prop(  props, "displayAnimationProps", text = "", icon = "RENDER_ANIMATION" )
        row.operator ( "uas_shot_manager.render", text = "Render Current Shot" ).renderMode = 'ANIMATION'
        
        row.separator( factor = 4)
        row.scale_x = 1.2
        row.prop(  props, "displayProjectProps", text = "", icon = "RENDERLAYERS" )
        row.operator ( "uas_shot_manager.render", text = "Render All").renderMode = 'PROJECT'

        row = box.row()
        row.alert = True
        row.operator ("uas_shot_manager.lauchrrsrender")
        row.operator ( "uas_shot_manager.export_otio" )
        
     ### STILL ###
        if props.displayStillProps:
            row = box.row()
            row.prop( props.renderSettingsStill, "writeToDisk" )
            
            row = box.row()
            filePath = props.getCurrentShot().getOutputFileName(    frameIndex = bpy.context.scene.frame_current,
                                                                    fullPath = True )
            row.label( text = "Current Image: " + filePath )
            row.operator ( "uas_shot_manager.render_openexplorer", text="", icon='FILEBROWSER' ).path = filePath
     
     ### ANIMATION ###
        elif props.displayAnimationProps:
            row = box.row()
            row.prop( props.renderSettingsAnim, "renderWithHandles" )

            row = box.row()
            filePath = props.getCurrentShot().getOutputFileName(    fullPath = True )
            row.label( text = "Current Video: " + filePath )
            row.operator ( "uas_shot_manager.render_openexplorer", text="", icon='FILEBROWSER' ).path = filePath

     ### PROJECT ###
        elif props.displayProjectProps:
            row = box.row()
            row.prop(props.renderSettingsProject, "renderAllTakes")
            row.prop(props.renderSettingsProject, "renderAlsoDisabled")
            
            pass

        # ------------------------

        box = self.layout.box()
       # box.use_property_split = True
        
        row = box.row()
        if '' == bpy.data.filepath:
            row.alert = True
            row.label ( text = "*** Save file first ***" )
        # elif None == (props.getInfoFileFullPath(context.scene, -1)[0]):
        #     row.alert = True
        #     row.label ( text = "*** Invalid Output Path ***" )
        elif '' == props.getRenderFileName():
            row.alert = True
            row.label ( text = "*** Invalid Output File Name ***" )
        else:
            row.label ( text = "Ready to render" )

        row = box.row ( )
        row.prop ( context.scene.render, "filepath" )
        row.operator ( "uas_shot_manager.render_openexplorer", text="", icon="FILEBROWSER" ).path = props.getRenderFileName()
      
        box = self.layout.box()
        row = box.row ( )
        #enabled=False 
        row.prop ( props, "render_shot_prefix" )
      
        # row.separator()
        # row.operator("uas_shot_manager.render_openexplorer", emboss=True, icon='FILEBROWSER', text="")
      
        row = box.row ( )
        row.label( text="Handles:")
        row.prop ( props, "handles", text = "" )
        self.layout.separator ( factor = 1 )
        
        

    def check(self, context):
        # should we redraw when a button is pressed?
        if True:
            return True
        return False

    @classmethod
    def poll ( cls, context ):
        return len ( context.scene.UAS_shot_manager_props.takes ) and context.scene.UAS_shot_manager_props.get_shots()


class UAS_OT_OpenPathBrowser( Operator ):
    bl_idname   = "uas_shot_manager.openpathbrowser"
    bl_label    = "Open"
    bl_description  =   "Open a path browser to define the directory to use to render the images" \
                        "Relative path must be set directly in the text field and must start with ''//''"

    #https://docs.blender.org/api/current/bpy.props.html
  #  filepath = bpy.props.StringProperty(subtype="FILE_PATH") 
    directory: bpy.props.StringProperty(subtype="DIR_PATH") 

    # filter_glob : StringProperty(
    #     default = '*',
    #     options = {'HIDDEN'} )
    
    def execute(self, context):
        """Open a path browser to define the directory to use to render the images"""
        bpy.context.scene.UAS_shot_manager_props.renderRootPath = self.directory
        return {'FINISHED'}

    def invoke(self, context, event): # See comments at end  [1]
      #  self.filepath = bpy.context.scene.UAS_shot_manager_props.renderRootPath
        # https://docs.blender.org/api/current/bpy.types.WindowManager.html
        self.directory = bpy.context.scene.UAS_shot_manager_props.renderRootPath
        context.window_manager.fileselect_add(self) 

        return {'RUNNING_MODAL'}  


class UAS_LaunchRRSRender( Operator ):
    bl_idname   = "uas_shot_manager.lauchrrsrender"
    bl_label    = "RRS Render Script"
    bl_description  = "Run the RRS Render Script"

    def execute(self, context):
        """Use the selected file as a stamped logo"""
        print(" UAS_LaunchRRSRender")
        
        from ..scripts import publishRRS
       # publishRRS.publishRRS( context.scene.UAS_shot_manager_props.renderRootPath )
        publishRRS.publishRRS( "c:\\tmpRezo\\" )

        return {'FINISHED'}


# class UAS_ShotManager_Explorer ( Operator ):
#     bl_idname = "uas_shot_manager.explorer"
#     bl_label = "Open Explorer"
#     bl_description = "Open Explorer"
#     bl_options = { "INTERNAL" }

#     folder: StringProperty ( )

#     def execute ( self, context ):
#         pathToOpen = self.folder
#         absPathToOpen = bpy.path.abspath(pathToOpen)
#         #wkip pouvoir ouvrir path relatif

#         if Path ( pathToOpen ).exists():
#             subprocess.Popen ( f"explorer \"{bpy.path.abspath(pathToOpen)}\"" )
#         else:
#             print("Open Explorer failed: Path not found: \"" + bpy.path.abspath(pathToOpen) + "\"")

#         return { "FINISHED" }


class UAS_PT_ShotManager_Render ( Operator ):
    bl_idname = "uas_shot_manager.render"
    bl_label = "Render"
    bl_description = "Render."
    bl_options = { "INTERNAL" }


    renderMode: bpy.props.EnumProperty (
        name = "Display Shot Properties Mode",
        description = "Update the content of the Shot Properties panel either on the current shot\nor on the shot seleted in the shots list",
        items = (   ('STILL', "Still", ""),
                    ('ANIMATION', "Animation", ""),
                    ('PROJECT', "Project", "") ),
        default = 'STILL' )

    def execute ( self, context ):
        props = context.scene.UAS_shot_manager_props

        rootPath = props.renderRootPath
        if "" == rootPath:
            rootPath = os.path.dirname(bpy.data.filepath)
        if props.isRenderRootPathValid():
            launchRender( self.renderMode, renderRootFilePath = rootPath, useStampInfo = props.useStampInfoDuringRendering )
        else:
            from ..utils.utils import ShowMessageBox
            ShowMessageBox( "Render root path is invalid", "Render Aborted", 'ERROR')
            print("Render aborted before start: Invalid Root Path")

        return { "FINISHED" }


def launchRender( renderMode, renderRootFilePath = "", useStampInfo = True ):
    print("\n\n*** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** ***")
    print("\n*** uas_shot_manager launchRender ***\n")
    context = bpy.context
    scene = bpy.context.scene
    props = scene.UAS_shot_manager_props

    rootPath = renderRootFilePath if "" != renderRootFilePath else os.path.dirname(bpy.data.filepath)
    print("   rootPath: ", rootPath)

    #wkip for debug only:
 #   props.createRenderSettings()
    # tester le chemin

    preset_useStampInfo = False
    if "UAS_StampInfo_Settings" in scene:
        RRS_StampInfo = scene.UAS_StampInfo_Settings
        preset_useStampInfo = useStampInfo
        if not useStampInfo:
            RRS_StampInfo.stampInfoUsed = False
        #    RRS_StampInfo.activateStampInfo = False
        #    props.useStampInfoDuringRendering = False

    preset = None
    if 'STILL' == renderMode:
        preset = props.renderSettingsStill
        print("   STILL, preset: ", preset.name)
    elif 'ANIMATION' == renderMode:
        preset = props.renderSettingsAnim
        print("   ANIMATION, preset: ", preset.name)
    else:
        preset = props.renderSettingsProject
        print("   PROJECT, preset: ", preset.name)



    # with utils.PropertyRestoreCtx ( (scene.render, "filepath"),
    #                         ( scene, "frame_start"),
    #                         ( scene, "frame_end" ),
    #                                 ( scene.render.image_settings, "file_format" ),
    #                                 ( scene.render.ffmpeg, "format" )
    #                               ):
    if True:
    # prepare render settings
        # camera
        # range
        # takes

        take = props.getCurrentTake()
        if take is None:
            take_name = ""
        else:
            take_name = take.name


        context.window_manager.UAS_shot_manager_handler_toggle = False
        context.window_manager.UAS_shot_manager_display_timeline = False
    
    #    shot = props.getCurrentShot()
        #wkip use handles
        # scene.frame_start = shot.start + props.handles
        # scene.frame_end = shot.end + props.handles

        if props.useProjectRenderSettings:
            props.restoreProjectSettings()

            if preset_useStampInfo:     # framed output resolution is used only when StampInfo is used
                if 'UAS_PROJECT_RESOLUTIONFRAMED' in os.environ.keys():
                    resolution = json.loads( os.environ['UAS_PROJECT_RESOLUTIONFRAMED'] )
                    scene.render.resolution_x   = resolution[0]
                    scene.render.resolution_y   = resolution[1]

     #   if preset_useStampInfo:
        ################
        #     scene.UAS_StampInfo_Settings.clearRenderHandlers()
    
        #     #stamper.clearInfoCompoNodes(context.scene)
        #         ### wkip to remove !!! ###
        #     #clear all nodes
        #     allCompoNodes = scene.node_tree
        #     for currentNode in allCompoNodes.nodes:
        #         allCompoNodes.nodes.remove(currentNode)
        #         scene.use_nodes = False

        #     scene.UAS_StampInfo_Settings.registerRenderHandlers()
        # ################

            #props.useStampInfoDuringRendering = False
        #    RRS_StampInfo.stampInfoUsed = False
      #      RRS_StampInfo.activateStampInfo = False
            #setRRS_StampInfoSettings(scene, shot.name)
        #    RRS_StampInfo.activateStampInfo = True
        #    RRS_StampInfo.stampInfoUsed = True
            #props.useStampInfoDuringRendering = True

       #     RRS_StampInfo.projectName = os.environ['UAS_PROJECT_NAME']  #"RR Special"


        print("hEre un 01")

        # render window
        if 'STILL' == preset.renderMode:
            print("hEre un 02 still")
            shot = props.getCurrentShot()
            #take = props.getCurrentTake()

            if preset_useStampInfo:
         #       RRS_StampInfo.stampInfoUsed = False
          #      RRS_StampInfo.activateStampInfo = False
                setRRS_StampInfoSettings(scene)
                
                # set current cam
                # if None != shot.camera:
            #    props.setCurrentShot(shot)

                # editingCurrentTime = props.getEditCurrentTime( ignoreDisabled = False )
                # editingDuration = props.getEditDuration( ignoreDisabled = True )
                # set_StampInfoShotSettings(  scene, shot.name, take.name,
                #                             #shot.notes,
                #                             shot.camera.name, scene.camera.data.lens,
                #                             edit3DFrame = editingCurrentTime,
                #                             edit3DTotalNumber = editingDuration )

                

        #        RRS_StampInfo.activateStampInfo = True
          #      RRS_StampInfo.stampInfoUsed = True
                

            if props.useProjectRenderSettings:
                scene.render.image_settings.file_format = 'PNG'
            

            # bpy.ops.render.opengl ( animation = True )
            scene.render.filepath = shot.getOutputFileName( frameIndex = scene.frame_current,
                                                            fullPath = True,
                                                            rootFilePath = renderRootFilePath)

            print("hEre un 03 still")

            bpy.ops.render.render('INVOKE_DEFAULT',animation = False, write_still = preset.writeToDisk)
#                bpy.ops.render.view_show()
#                bpy.ops.render.render(animation=False, use_viewport=True, write_still = preset.writeToDisk)

        elif 'ANIMATION' == preset.renderMode:
            
            shot = props.getCurrentShot()

            if props.renderSettingsAnim.renderWithHandles:
                scene.frame_start = shot.start - props.handles
                scene.frame_end = shot.end + props.handles
            else:
                scene.frame_start = shot.start
                scene.frame_end = shot.end

            print("shot.start: ", shot.start)
            print("scene.frame_start: ", scene.frame_start)

            if preset_useStampInfo:
                RRS_StampInfo.stampInfoUsed = False
                RRS_StampInfo.activateStampInfo = False
                setRRS_StampInfoSettings(scene)
                RRS_StampInfo.activateStampInfo = True
                RRS_StampInfo.stampInfoUsed = True

                RRS_StampInfo.shotName = shot.name
                RRS_StampInfo.takeName = take_name


            # wkip
            if props.useProjectRenderSettings:
                scene.render.image_settings.file_format = 'FFMPEG'
                scene.render.ffmpeg.format = 'MPEG4'

                scene.render.filepath = shot.getOutputFileName(fullPath = True, rootFilePath = renderRootFilePath)
                print("scene.render.filepath: ", scene.render.filepath)

            bpy.ops.render.render('INVOKE_DEFAULT', animation = True)


        else:
        #   wkip to remove
            shot = props.getCurrentShot()
            if preset_useStampInfo:
                RRS_StampInfo.stampInfoUsed = False
                RRS_StampInfo.activateStampInfo = False
                setRRS_StampInfoSettings(scene)
                RRS_StampInfo.activateStampInfo = True
                RRS_StampInfo.stampInfoUsed = True

            
                        
            #if preset.render
        
                
            shots = props.get_shots()

            if props.useProjectRenderSettings:
                scene.render.image_settings.file_format = 'FFMPEG'
                scene.render.ffmpeg.format = 'MPEG4'
            
            for i, shot in enumerate(shots):
                if shot.enabled:
                    print("\n  Shot rendered: ", shot.name)
                #     props.setCurrentShotByIndex(i)
                #     props.setSelectedShotByIndex(i)

                    scene.camera = shot.camera
                    
                    if preset_useStampInfo:
                        RRS_StampInfo.shotName = shot.name
                        RRS_StampInfo.takeName = take_name
                        print("RRS_StampInfo.takeName: ", RRS_StampInfo.takeName)

                    #area.spaces[0].region_3d.view_perspective = 'CAMERA'
                    scene.frame_current = shot.start
                    scene.frame_start = shot.start - props.handles
                    scene.frame_end = shot.end + props.handles
                    scene.render.filepath = shot.getOutputFileName(fullPath = True, rootFilePath = renderRootFilePath)
                    print("scene.render.filepath: ", scene.render.filepath)


                    #bpy.ops.render.render('INVOKE_DEFAULT', animation = True)
                    bpy.ops.render.render(animation = True)
                    #bpy.ops.render.opengl ( animation = True )




        # xwkip to remove
        if preset_useStampInfo:
            #scene.UAS_StampInfo_Settings.stampInfoUsed = False
            #  props.useStampInfoDuringRendering = False
            pass




class UAS_PT_ShotManager_RenderDialog ( Operator ):
    bl_idname = "uas_shot_manager.renderdialog"
    bl_label = "Render"
    bl_description = "Render"
    bl_options = { "INTERNAL" }

    only_active: BoolProperty ( 
        name = "Render Only Active",
        default = False )

    renderer: EnumProperty (
        items = (   ( "BLENDER_EEVEE", "Eevee", ""),
                    ( "CYCLES", "Cycles", ""),
                    ( "OPENGL", "OpenGL", "" ) ),
        default = 'BLENDER_EEVEE' )

    def execute ( self, context ):

        print("*** uas_shot_manager.renderDialog ***")

        scene = context.scene
        context.space_data.region_3d.view_perspective = "CAMERA"
        handles = context.scene.UAS_shot_manager_props.handles
        props = scene.UAS_shot_manager_props

        with utils.PropertyRestoreCtx ( (scene.render, "filepath" ),
                                 ( scene, "frame_start"),
                                 ( scene, "frame_end" ),
                                 ( scene.render.image_settings, "file_format" ),
                                 ( scene.render.ffmpeg, "format" ),
                                 ( scene.render, "engine" ),
                                 ( scene.render, "resolution_x" ),
                                 ( scene.render, "resolution_y" ) ):
            
            scene.render.image_settings.file_format = 'FFMPEG'
            scene.render.ffmpeg.format = 'MPEG4'

            if self.renderer != "OPENGL":
                scene.render.engine = self.renderer

            context.window_manager.UAS_shot_manager_handler_toggle = False
            context.window_manager.UAS_shot_manager_display_timeline = False

            out_path = scene.render.filepath
            shots = props.get_shots()
            take = props.getCurrentTake()
            if take is None:
                take_name = ""
            else:
                take_name = take.name

            if self.only_active:
                shot = scene.UAS_shot_manager_props.getCurrentShot()
                if shot is None:
                    return { "CANCELLED" }
                scene.frame_start = shot.start - handles
                scene.frame_end = shot.end + handles
                scene.render.filepath = get_media_path ( out_path, take_name, shot.name )
                print("      scene.render.filepath: ", scene.render.filepath)

                scene.camera = shot.camera

                if "UAS_StampInfo_Settings" in scene:
                    RRS_StampInfo.setRRS_StampInfoSettings(scene)


                if self.renderer == "OPENGL":
                    bpy.ops.render.opengl ( animation = True )
                else:
                    bpy.ops.render.render ( animation = True )

                if "UAS_StampInfo_Settings" in scene:
                    scene.UAS_StampInfo_Settings.stampInfoUsed = False
            else:
                for shot in shots:
                    if shot.enabled:
                        scene.frame_start = shot.start - handles
                        scene.frame_end = shot.end + handles
                        scene.render.filepath = get_media_path ( out_path, take_name, shot.name )
                        scene.camera = shot.camera
                        if "UAS_StampInfo_Settings" in scene:
                            scene.UAS_StampInfo_Settings.stampInfoUsed = True
                            scene.UAS_StampInfo_Settings.shotName = shot.name

                        if self.renderer == "OPENGL":
                            bpy.ops.render.opengl ( animation = True )
                        else:
                            bpy.ops.render.render ( animation = True )

                        if "UAS_StampInfo_Settings" in scene:
                            scene.UAS_StampInfo_Settings.stampInfoUsed = False

            
            scene.UAS_StampInfo_Settings.restorePreviousValues(scene)
            print(" --- RRS Settings Restored ---")

        return { "FINISHED" }


    def draw ( self, context ):
        l = self.layout
        row = l.row ( )
        row.prop ( self, "renderer" )


    # def invoke ( self, context, event ):
    #     wm = context.window_manager
    #     return wm.invoke_props_dialog ( self )


###########
# utils
###########
class UAS_ShotManager_Render_RestoreProjectSettings ( Operator ):
    bl_idname = "uas_shot_manager.render_restore_project_settings"
    bl_label = "Restore Project Settings"
    bl_description = "Restore Project Settings"
    bl_options = { "INTERNAL" }

    def execute ( self, context ):
        context.scene.UAS_shot_manager_props.restoreProjectSettings()
        return { "FINISHED" }


class UAS_PT_ShotManager_Render_StampInfoProperties ( Panel ):
    bl_label = "Stamp Info Properties"
    bl_idname = "UAS_PT_Shot_Manager_StampInfoPrefs"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UAS Shot Man"
    bl_options = { "DEFAULT_CLOSED" }
    bl_parent_id = "UAS_PT_ShotManagerRenderPanel"
    
    def draw_header_preset(self, context):
        scene  = context.scene
        render = scene.render
        
        layout        = self.layout
        layout.emboss = 'NONE'
        row           = layout.row(align=True)
        
        if None == context.scene.UAS_StampInfo_Settings:
            _emboss   = True
            row.alert = True
            row.label( text="Not found !")
        else:
            _emboss   = False
            row.alert = False
            versionTupple = [addon.bl_info.get('version', (-1,-1,-1)) for addon in addon_utils.modules() if addon.bl_info['name'] == 'UAS_StampInfo'][0]
            versionStr = str(versionTupple[0]) + "." + str(versionTupple[1]) + "." + str(versionTupple[2])
            
            row.label( text=("Loaded - V." + versionStr))


    def draw ( self, context ):
        box = self.layout.box ( )
        row = box.row ( )
        row.prop ( context.scene.UAS_shot_manager_props, "useStampInfoDuringRendering" )
      


######
# IO #
######

# wkip donner en parametre un nom ou indice de take!!!!
def exportOtio( renderRootFilePath = "", fps = -1 ):
    print("  ** -- ** exportOtio")
    scene = bpy.context.scene
    props = scene.UAS_shot_manager_props
    
    sceneFps = fps if fps != -1 else scene.render.fps

    import opentimelineio as otio

    take = props.getCurrentTake()
    if take is None:

        print("No Take found")
        return()
        take_name = ""
    else:
        take_name = take.getName_PathCompliant()

    shots = props.get_shots()

    # wkip note: scene.frame_start probablement à remplacer par start du premier shot enabled!!!
    timeline = otio.schema.Timeline ( name = scene.name, global_start_time = otio.opentime.from_frames ( scene.frame_start, sceneFps ) )
    track = otio.schema.Track ( )
    timeline.tracks.append ( track )

    clips = list ( )
    playhead = 0
    for s in shots:
        if s.enabled:
            duration = s.end - s.start + 1
            start_time, end_time_exclusive = ( otio.opentime.from_frames ( playhead, sceneFps ), otio.opentime.from_frames ( playhead + duration, sceneFps ) )
            source_range = otio.opentime.range_from_start_end_time ( start_time, end_time_exclusive )
            playhead += duration
            
            #shotFilePath = get_media_path ( scene.render.filepath, take_name ,s.name )
            shotFilePath = s.getOutputFileName(fullPath = True)
            shotFileName = s.getOutputFileName()

            media_reference = otio.schema.ExternalReference ( target_url = shotFilePath, available_range = source_range )
            c = otio.schema.Clip ( name = shotFileName,
                                    source_range = source_range,
                                    media_reference = media_reference )
            c.metadata  = {
                "clip_name":s['name'],
                "camera_name":s['camera'].name_full
            }

            clips.append ( c )

    track.extend ( clips )

    renderPath = renderRootFilePath if "" != renderRootFilePath else props.renderRootPath
    renderPath +=  take_name + "\\" + take_name + ".xml"
    if Path ( renderPath ).suffix == "":
        renderPath += ".otio"

    print("   OTIO renderPath:", renderPath)

    Path ( renderPath ).parent.mkdir ( parents = True, exist_ok = True )
    if renderPath.endswith ( ".xml" ):
        otio.adapters.write_to_file ( timeline, renderPath, adapter_name = "fcp_xml" )
    else:
        otio.adapters.write_to_file ( timeline, renderPath )



class UAS_ShotManager_Export_OTIO ( Operator ):
    bl_idname = "uas_shot_manager.export_otio"
    bl_label = "Export otio"
    bl_description = "Export otio"
    bl_options = { "INTERNAL" }

    file: StringProperty ( )
    
    def execute ( self, context ):
        props = context.scene.UAS_shot_manager_props
  
        if props.isRenderRootPathValid():
            print("Here OTIIO")
            exportOtio(renderRootFilePath = props.renderRootPath, fps = context.scene.render.fps)
        else:
            print("Here not OTIIO")
            from ..utils.utils import ShowMessageBox
            ShowMessageBox( "Render root path is invalid", "OpenTimelineIO Export Aborted", 'ERROR')
            print("OpenTimelineIO Export aborted before start: Invalid Root Path")

        return { "FINISHED" }


    # def invoke ( self, context, event ):
    #     props = context.scene.UAS_shot_manager_props
        
    #     if not props.isRenderRootPathValid():
    #         from ..utils.utils import ShowMessageBox
    #         ShowMessageBox( "Render root path is invalid", "OpenTimelineIO Export Aborted", 'ERROR')
    #         print("OpenTimelineIO Export aborted before start: Invalid Root Path")
        
    #     return {'RUNNING_MODAL'}
        
        # wkip a remettre plus tard pour définir des chemins alternatifs de sauvegarde.
        # se baser sur 
        # wm = context.window_manager
        # self.fps = context.scene.render.fps
        # out_path = context.scene.render.filepath
        # if out_path.startswith ( "//" ):

        #     out_path = str ( Path ( props.renderRootPath ).parent.absolute ( ) ) + out_path[ 1 : ]
        # out_path = Path ( out_path)

        # take = context.scene.UAS_shot_manager_props.getCurrentTake ()
        # if take is None:
        #     take_name = ""
        # else:
        #     take_name = take.getName_PathCompliant()

        # if out_path.suffix == "":
        #     self.file = f"{out_path.absolute ( )}/{take_name}/export.xml"
        # else:
        #     self.file = f"{out_path.parent.absolute ( )}/{take_name}/export.xml"

        # return wm.invoke_props_dialog ( self )



_classes = ( 
            UAS_PT_ShotManagerRenderPanel,
            UAS_PT_ShotManager_Render,
            UAS_PT_ShotManager_RenderDialog,
            UAS_PT_ShotManager_Render_StampInfoProperties,

            UAS_OT_OpenPathBrowser,
        #    UAS_ShotManager_Explorer,
            UAS_LaunchRRSRender,

            UAS_ShotManager_Render_RestoreProjectSettings,
            UAS_ShotManager_Export_OTIO )


def register ( ):
    for cls in _classes:
        bpy.utils.register_class ( cls )


def unregister ( ):
    for cls in reversed ( _classes ):
        bpy.utils.unregister_class ( cls )
