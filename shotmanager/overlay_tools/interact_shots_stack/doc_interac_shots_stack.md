# Interactive shots stack

    shots_stack.py                  - Entry point: holds the modal loop
        |
        |
        |_ shots_stack_widget       - Main graphic widget: holds the events on the widget and its components,
           (BL_UI_ShotStack)          as well as the draw functions
                |                     
                |
                |
                |_ shots_stack_clip_component
                        |           - Main graphic component:displays a clip related to a given shot
                        |
                        |
                        |_ text2D   - Text on the clip
                        |
                        |
                        |_ shots_stack_handle_component
                                    - Start and end interactive handles on a clip


## See classes inheritance here: [GPU 2D Components](../../gpu/gpu_2d/doc_gpu_2d_components)

## To do:

- echap et validation ou cancel
- Store the state of shots before the action and restore it if action canceled
- validate the action with Enter

- undo

- display des options sur les 2 dopesheets

- option pour single current shot

---------------------

- *** Remove the DrawAll debug flag
- *** re activate the escape keys

- Have an option so that the current time match the time of the start or end time of the clip being manipulated

## To do

- Have an icon by type of shot
- See when they are locked
- Set a better UI scaling based on remap


- Have a Range button
- Have a way to have the timeline buttons on a dopesheet also

- Documentation
