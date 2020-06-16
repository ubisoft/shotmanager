import bpy


def jump_to_shot(self):
    def next_index_enabled(shots, current_index):
        next_index = (current_shot_index + 1) % len(shots)
        while current_index != next_index:
            if shots[next_index].enabled:
                return next_index
            next_index = (next_index + 1) % len(shots)

        return -1

    scene = bpy.context.scene
    shots = scene.UAS_shot_manager_props.get_shots()
    current_shot_index = scene.UAS_shot_manager_props.current_shot_index

    if shots[current_shot_index].end + 1 == scene.frame_current:
        next_shot = next_index_enabled(shots, current_shot_index)
        if next_shot != -1:
            current_shot_index = next_shot
            scene.UAS_shot_manager_props.current_shot_index = current_shot_index
            scene.frame_current = shots[current_shot_index].start
    elif not shots[current_shot_index].start <= scene.frame_current <= shots[current_shot_index].end:
        scene.frame_current = shots[current_shot_index].start
    if shots[current_shot_index].camera is not None:
        scene.camera = shots[current_shot_index].camera
        scene.UAS_shot_manager_props.selected_shot_index = current_shot_index
