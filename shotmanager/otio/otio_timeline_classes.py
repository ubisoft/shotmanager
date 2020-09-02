import logging

_logger = logging.getLogger(__name__)

import os
from pathlib import Path
from urllib.parse import unquote_plus, urlparse
import re

import bpy
import opentimelineio


from ..utils import utils

from . import otio_wrapper as ow


class OtioTimeline:
    """ Custom timeline to contain the sequences read in the edl file
    """

    otioFile = None
    name = ""
    timeline = None
    sequenceList = None


class OtioSequence:
    """ Custom sequence to contain the clips related to the shots
    """

    name = ""
    clipList = None
    start = -1
    end = -1

    # warning: clips may not be on the same track, hence they may not be ordered!!
    def setStartAndEnd(self):
        if len(self.clipList):
            # start
            self.start = ow.get_clip_frame_final_start(self.clipList[0])
            for clip in self.clipList:
                if ow.get_clip_frame_final_start(clip) < self.start:
                    self.start = ow.get_clip_frame_final_start(clip)

            # end
            self.end = ow.get_timeline_clip_end_inclusive(self.clipList[0])
            for clip in self.clipList:
                if ow.get_timeline_clip_end_inclusive(clip) > self.end:
                    self.end = ow.get_timeline_clip_end_inclusive(clip)

    def printInfo(self):
        print(f"\nSeq: {self.name}, start: {self.start}, end: {self.end}")
        if self.clipList is not None:
            for item in self.clipList:
                print(f"  - {item.media_reference.target_url}")
