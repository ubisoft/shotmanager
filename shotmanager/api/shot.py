def shotManager(self):
    """Return the shot manager properties instance the shot is belonging to.
    """
    parentShotManager = None

    # wkip dirty if self.parentScene is not None
    if self.parentScene is None:
        self.parentScene = bpy.context.scene

    if self.parentScene is not None and "UAS_shot_manager_props" in self.parentScene:
        parentShotManager = self.parentScene.UAS_shot_manager_props
    return parentShotManager

def getDuration(self):
    """ Returns the shot duration in frames
        in Blender - and in Shot Manager - the last frame of the shot is included in the rendered images
    """
    duration = self.end - self.start + 1
    return duration

def getOutputFileName(self, frameIndex=-1, fullPath=False, fullPathOnly=False, rootFilePath=""):
    return bpy.context.scene.UAS_shot_manager_props.getShotOutputFileName(
        self, frameIndex=frameIndex, fullPath=fullPath, fullPathOnly=fullPathOnly, rootFilePath=rootFilePath
    )

def getName_PathCompliant(self):
    shotName = self.name.replace(" ", "_")
    return shotName


def get_color(self):
    
    return val

def set_color(self, value):


def getEditStart(self, scene):
    return scene.UAS_shot_manager_props.getEditTime(self, self.start)

def getEditEnd(self, scene):
    return scene.UAS_shot_manager_props.getEditTime(self, self.end)

