# Structure of the classes

                
      Mesh2D       Object2D
         \          /    \
          \        /      \
           \      /      text2D
            \    /
          QuadObject
              \      
               \         InteractiveComponent
                \          /     
                 \        /
                  \      /
                   \    /
                 Component2D


Notes:
  - In the bounding boxes, the max values, corresponding to pixel coordinates, are NOT included in the component
    Think about a rectangle would be drawn on X and how another rectangle after it, starting at its end, would behave.
    In order not to overlap then the end of the bBox of the first rectangle has to be not on the end pixel column.
  
  - Consequently the width of the rectangle, in pixels belonging to it, is given by xMax - xMin (and NOT xMax - xMin + 1 !)


Tips:
  - Draw the parents before updating the position of the children.
    Indeed if a call to parent.getWidthInRegion or parent.getHeightInRegion is done they rely on the parent
    clampled bounding box, which is computed in the parent Draw function.

    In other words:
      - for each child override its draw() function
      - add a call to the parent class draw() function at the end of it, so that the draw of the children will
        be done by this parent class

# To do:
  - simplify the arguments of the draw() function
