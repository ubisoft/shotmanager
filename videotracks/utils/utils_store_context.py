import bpy


def storeUserRenderSettings(context, userRenderSettings):
    scene = context.scene

    #    userRenderSettings["show_overlays"] = bpy.context.space_data.overlay.show_overlays
    userRenderSettings["resolution_x"] = scene.render.resolution_x
    userRenderSettings["resolution_y"] = scene.render.resolution_y
    userRenderSettings["resolution_percentage"] = scene.render.resolution_percentage
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

    #######################
    # image stamping
    #######################

    # not used: "stamp_background",
    propertiesArr = ["stamp_font_size", "stamp_foreground", "stamp_note_text"]
    propertiesArr += [
        "use_stamp",
        "use_stamp_camera",
        "use_stamp_camera",
        "use_stamp_date",
        "use_stamp_filename",
        "use_stamp_frame",
        "use_stamp_frame_range",
        "use_stamp_hostname",
        "use_stamp_labels",
        "use_stamp_lens",
        "use_stamp_marker",
        "use_stamp_memory",
        "use_stamp_note",
        "use_stamp_render_time",
        "use_stamp_scene",
        "use_stamp_sequencer_strip",
        # "use_stamp_strip_meta",
        "use_stamp_time",
    ]

    categImageStamping = dict()
    for prop in propertiesArr:
        categImageStamping[prop] = getattr(context.scene.render, prop)

    userRenderSettings["categ_image_stamping"] = categImageStamping
    # print(f"userRenderSettings: \n{userRenderSettings}")

    return userRenderSettings


def restoreUserRenderSettings(context, userRenderSettings):
    scene = context.scene
    # wkip bug here dans certaines conditions vse
    #    bpy.context.space_data.overlay.show_overlays = userRenderSettings["show_overlays"]

    scene.render.resolution_x = userRenderSettings["resolution_x"]
    scene.render.resolution_y = userRenderSettings["resolution_y"]
    scene.render.resolution_percentage = userRenderSettings["resolution_percentage"]
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

    #######################
    # image stamping
    #######################
    categImageStamping = userRenderSettings["categ_image_stamping"]
    for key in categImageStamping:
        setattr(context.scene.render, key, categImageStamping[key])

    return
