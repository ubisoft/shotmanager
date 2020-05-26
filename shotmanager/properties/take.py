from bpy.types import PropertyGroup
from bpy.props import StringProperty, CollectionProperty

from .shot import UAS_ShotManager_Shot


class UAS_ShotManager_Take(PropertyGroup):
    def getName_PathCompliant(self):
        takeName = self.name.replace(" ", "_")
        return takeName

    def getShotList(self, ignoreDisabled=False):
        """ Return a filtered copy of the shots associated to this take
        """
        shotList = []

        for shot in self.shots:
            if not ignoreDisabled or shot.enabled:
                shotList.append(shot)

        return shotList

    name: StringProperty(name="Name")

    shots: CollectionProperty(type=UAS_ShotManager_Shot)
