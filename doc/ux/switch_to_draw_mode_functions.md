# Switch to Draw Mode functions

List of all the functions used to change the drawing mode of a grease pencil object.

### When a shot has to be set to Draw mode
- To set the draw mode of a shot, when in Continuous mode: uas_shot_manager.greasepencil_select_and_draw is the prefered operator


## switchToDrawMode( gpencil ): function in utils_greasepencil

Change the current object to be the specified one.
If the previous object was in a sub-object mode it is set back to object mode.

Set the specified object to Draw mode

Change the drawing tool

Change the drawing stroke placement and axis

*** Do not change anything on the layer context. To add ???

Called by uas_shot_manager.toggle_grease_pencil_draw_mode


*** commented bpy.ops.object.select_all(action="DESELECT")


## uas_shot_manager.toggle_grease_pencil_draw_mode

Calling switchToDrawMode

Calls place3DCursor


## uas_shot_manager.greasepencil_select_and_draw

**Called in the UI when pressing the GP icon button**
Calling switchToDrawMode

Called by:
- uas_shot_manager.stb_frame_drawing
- drawStoryboardRow
- setCurrentShotByIndex
    called by uas_shot_manager.set_current_shot
        called by _update_selected_shot_index when the selected item is changed in the templateList 


## uas_shot_manager.draw_on_grease_pencil
*** Removed in V.2.1.31 ***

Called by:
- devDebug_displayAdv in storyboard_ui.py
- drawGpToolbar in storyboard_drawing_ui.py

Does:
    gp.setInkLayerReadyToDraw(gp_child)
    utils_greasepencil.switchToDrawMode(context, gp_child)
    props.isEditingStoryboardFrame = True
    utils.setPropertyPanelContext(context, "DATA")

