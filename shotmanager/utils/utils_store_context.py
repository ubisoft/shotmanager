import bpy


def storeUserRenderSettings(context, userRenderSettings):
    scene = context.scene

    #    userRenderSettings["show_overlays"] = bpy.context.space_data.overlay.show_overlays
    userRenderSettings["resolution_x"] = scene.render.resolution_x
    userRenderSettings["resolution_y"] = scene.render.resolution_y
    userRenderSettings["render_engine"] = scene.render.engine

    userRenderSettings["frame_start"] = scene.frame_start
    userRenderSettings["frame_end"] = scene.frame_end
    userRenderSettings["use_preview_range"] = scene.use_preview_range
    userRenderSettings["frame_preview_start"] = scene.frame_preview_start
    userRenderSettings["frame_preview_end"] = scene.frame_preview_end

    userRenderSettings["view_transform"] = scene.view_settings.view_transform

    userRenderSettings["render_use_compositing"] = scene.render.use_compositing
    userRenderSettings["render_use_sequencer"] = scene.render.use_sequencer

    # eevee
    ##############
    # if "BLENDER_EEVEE" == bpy.scene.render.engine:
    userRenderSettings["eevee_taa_render_samples"] = scene.eevee.taa_render_samples
    userRenderSettings["eevee_taa_samples"] = scene.eevee.taa_samples

    # workbench
    ##############
    # if "BLENDER_WORKBENCH" == bpy.scene.render.engine:
    userRenderSettings["workbench_render_aa"] = scene.display.render_aa
    userRenderSettings["workbench_viewport_aa"] = scene.display.viewport_aa

    # cycles
    ##############
    #  if "CYCLES" == bpy.scene.render.engine:
    userRenderSettings["cycles_samples"] = scene.cycles.samples
    userRenderSettings["cycles_preview_samples"] = scene.cycles.preview_samples

    return userRenderSettings


def restoreUserRenderSettings(context, userRenderSettings):
    scene = context.scene
    # wkip bug here dans certaines conditions vse
    #    bpy.context.space_data.overlay.show_overlays = userRenderSettings["show_overlays"]

    scene.render.resolution_x = userRenderSettings["resolution_x"]
    scene.render.resolution_y = userRenderSettings["resolution_y"]
    scene.render.engine = userRenderSettings["render_engine"]

    scene.frame_start = userRenderSettings["frame_start"]
    scene.frame_end = userRenderSettings["frame_end"]
    scene.use_preview_range = userRenderSettings["use_preview_range"]
    scene.frame_preview_start = userRenderSettings["frame_preview_start"]
    scene.frame_preview_end = userRenderSettings["frame_preview_end"]

    scene.view_settings.view_transform = userRenderSettings["view_transform"]

    scene.render.use_compositing = userRenderSettings["render_use_compositing"]
    scene.render.use_sequencer = userRenderSettings["render_use_sequencer"]

    # eevee
    ##############
    #   if "BLENDER_EEVEE" == bpy.scene.render.engine:
    scene.eevee.taa_render_samples = userRenderSettings["eevee_taa_render_samples"]
    scene.eevee.taa_samples = userRenderSettings["eevee_taa_samples"]

    # workbench
    ##############
    # if "BLENDER_WORKBENCH" == bpy.scene.render.engine:
    scene.display.render_aa = userRenderSettings["workbench_render_aa"]
    scene.display.viewport_aa = userRenderSettings["workbench_viewport_aa"]

    # cycles
    ##############
    #        if "CYCLES" == bpy.scene.render.engine:
    scene.cycles.samples = userRenderSettings["cycles_samples"]
    scene.cycles.preview_samples = userRenderSettings["cycles_preview_samples"]

    return
