# Interactive shots stack

    shots_stack.py                  - Entry point: holds the modal loop
        |
        |
        |_shots_stack_widget        - Main graphic widget: holds the events on the widget and its components,
                |                     as well as the draw functions
                |
                |
                |_shots_stack_clip_component
                        |           - Main graphic component:displays a clip related to a given shot
                        |
                        |
                        |_text2D    - Text on the clip
                        |
                        |
                        |_shots_stack_handle_component
                                    - Start and end interactive handles on a clip


## To do

- See how to cut the name of the shot instead of having it desappear at the left side of the timeline
- Clamp the shot clips when they ovelap with the time ruler
- Have an icon by type of shot
- See when they are locked
- Set a better UI scaling based on remap


- Have a Range button
- Have a way to have the timeline buttons on a dopesheet also

- Documentation
