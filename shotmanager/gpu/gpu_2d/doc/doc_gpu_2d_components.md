# Structure of the classes

   Mesh2D  - draw simple quad (fill, line)
      \
       \
        \             Object2D     - pos, alignment, children
         \             /    \      - no draw functions !
          \           /      \
           \         /        \
            \       /        Text2D
             \     /
              \   /
            QuadObject
                \      
                 \
                  \         InteractiveComponent   - events
                   \          /     
                    \        /
                     \      /
                      \    /
                    Component2D

## Alignment:

  Instances of classes inheriting from Object2D have a transformation (only position is supported at the moment)
  that is dependent on the alignment of their pivot in regard to their bounding box and on their alignment
  to the parent. See [Object2D] description for more details.


## Draw:

  custom_component is a user class inheriting from Component2D. Eg: ShotClipComponent, ShotHandleComponent...

  [custom_component].draw()
     |
     |
     |_ _getShader()
     |      get the shader and specify the colors (highlight...)
     |
     |_ _draw()
     |
     |
     |_ [Component2D].draw()

  Children components are recursively drawn from parent to each ends of the hierarchy.
  To do so:
    - Do NOT explicitely call the draw() function of a child in the parent draw() function
    - Either:
      - Call the parent class (not the parent component!) draw() function, which will draw
        the component as expected and will also collect the children and draw them
        wkNote: add a drawChildren() somewhere?
      - Or, in case the component draw() function has been customized and the draw() of the
        parent class is not relevant, then explicitely call the children draw() functions
        with such code:
            sortedChildren = self.getChildren(sortedByIncreasingZ=True)
            for child in sortedChildren:
                child.draw(None, region)

## Event:

  item.draw()
     |
     |
     |_ _getShader()
     |      get the shader and specify the colors (highlight...)
     |
     |_ _draw()


### InteractiveComponent:

  handle_event()
     |
     |
     |_ _event_highlight
     |          |
     |          |_ _on_highlighted_changed()
     |
     |
     |_ _handle_event_custom()
                |
                |_ _on_selected_changed()
                |
                |_ _on_manipulated_changed()
                |
                |_ _on_manipulated_mouse_moved()
                |
                |_ _on_doublecliked()
      

     


## Notes:

  ### Bounding boxes:
    - In the bounding boxes, the max values, corresponding to pixel coordinates, are NOT included in the component
      Think about a rectangle would be drawn on X and how another rectangle after it, starting at its end, would behave.
      In order not to overlap then the end of the bBox of the first rectangle has to be not on the end pixel column.
    
    - Consequently the width of the rectangle, in pixels belonging to it, is given by xMax - xMin (and NOT xMax - xMin + 1 !)

  ### Event action callbacks:
    - Some attributes of InteractiveComponent have callbacks that are triggered when the attribute is changed. This is 
      the case for isHighlighted, isSelected, isManipulated.

## Tips:
  - Draw the parents before updating the position of the children.
    Indeed if a call to parent.getWidthInRegion or parent.getHeightInRegion is done they rely on the parent
    clampled bounding box, which is computed in the parent Draw function.

    In other words:
      - for each child override its draw() function
      - add a call to the parent class draw() function at the end of it, so that the draw of the children will
        be done by this parent class




# To do:
  - simplify the arguments of the draw() function, and in particular place the region arg first
  - add an alignmentToParent to [Object2D]
  - add a display / visible flag to hide the component
  - add a disable

  
  