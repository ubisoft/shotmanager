import logging

_logger = logging.getLogger(__name__)

import os
from pathlib import Path
from urllib.parse import unquote_plus, urlparse
import re

import bpy
import opentimelineio


# was OtioTimeline
class MontageInterface:
    """ 
    """

    def __init__(self):
        self.montageType = "INTERFACE"
        self.name = ""
        self.sequencesList = list()

    def newSequence(self):
        if self.sequencesList is None:
            self.sequencesList = list()
        newSeq = SequenceInterface()
        self.sequencesList.append(newSeq)
        return newSeq


class SequenceInterface:
    """ 
    """

    def __init__(self):
        self.name = ""
        self.shotsList = list()
        self.start = -1
        self.end = -1

    def newShot(self, shot):
        if self.shotsList is None:
            self.shotsList = list()
        newShot = ShotInterface()
        self.shotsList.append(newShot)
        return newShot

    # warning: clips may not be on the same track, hence they may not be ordered!!
    def setStartAndEnd(self):
        pass

    def printInfo(self):
        pass


class ShotInterface:
    """ 
    """

    def __init__(self):
        self.name = ""
