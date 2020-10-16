import bpy

previous_frame = 0
def jump_to_shot(scene):
    props = scene.UAS_shot_manager_props
    verbose = False

    def get_previous_shot ( shots, current_shot ):
        index = props.getShotIndex ( current_shot )
        if index > 0:
            previous_shots = [ s for s in shots[ : index ] if s.enabled ]
            if len ( previous_shots ):
                return  previous_shots[ -1 ]

        return None


    def get_next_shot (shots, current_shot ):
        index = props.getShotIndex ( current_shot )
        if index < len ( shots ) -1:
            next_shots = [ s for s in shots[ index + 1: ] if s.enabled ]
            if len ( next_shots ):
                return next_shots[ 0 ]

        return None

    global previous_frame
    shotList = props.get_shots()
    current_shot_index = props.current_shot_index
    props.restartPlay = False

    current_shot = shotList[ current_shot_index ]
    current_frame = scene.frame_current

    # clip shot to scene timeframe. Might not be necessary
    current_shot_start = current_shot.start
    current_shot_end = current_shot.end

    scene_frame_start = scene.frame_preview_start if scene.use_preview_range else scene.frame_start
    scene_frame_end = scene.frame_preview_end if scene.use_preview_range else scene.frame_end

    if not bpy.context.screen.is_animation_playing:
        return

    if not bpy.context.screen.is_scrubbing:
        if current_frame == scene_frame_end and get_previous_shot ( shotList, current_shot ) is None:
            props.setCurrentShot ( shotList[ -1 ] )
            scene.frame_current = shotList[ -1 ].end
        elif current_frame > current_shot_end:
            disp = current_frame - current_shot_end
            next_shot = get_next_shot  ( shotList, current_shot )
            while next_shot is not None:
                if disp < next_shot.getDuration ( ):
                    props.setCurrentShot ( next_shot )
                    scene.frame_current = next_shot.start + disp
                    break
                disp -= next_shot.getDuration ( )
                next_shot = get_next_shot  ( shotList, next_shot )
        elif current_frame == scene_frame_start and get_next_shot  ( shotList, current_shot ) is None: # Loop back at start.
            # Seems that the first frame is always hit even in frame dropping playblack
            props.setCurrentShot ( shotList[ 0 ] )
        elif current_frame < current_shot_start:
            disp = current_shot_start - current_frame
            previous_shot = get_previous_shot ( shotList, current_shot )
            while previous_shot is not None:
                if disp < previous_shot.getDuration ( ):
                    props.setCurrentShot ( previous_shot )
                    scene.frame_current = previous_shot.end - disp
                    break
                disp -= previous_shot.getDuration ( )
                previous_shot = get_next_shot ( shotList, previous_shot )

    else:
        pass

    previous_frame = scene.frame_current