import logging

_logger = logging.getLogger(__name__)

import os
from pathlib import Path
from urllib.parse import unquote_plus, urlparse
import re

import bpy
import opentimelineio

from .montage_interface import MontageInterface, SequenceInterface, ShotInterface

from shotmanager.utils import utils

from shotmanager.otio import otio_wrapper as ow


# was OtioTimeline
class MontageOtio(MontageInterface):
    """ 
    """

    def __init__(self):
        super().__init__()

        # new properties:
        self.otioFile = None
        self.timeline = None

    def newSequence(self):
        if self.sequencesList is None:
            self.sequencesList = list()
        newSeq = SequenceOtio()
        self.sequencesList.append(newSeq)
        return newSeq

    def getSequenceNameFromMediaName(self, fileName):
        seqName = ""

        seq_pattern = "Seq"
        media_name_splited = fileName.split("_")
        if 2 <= len(media_name_splited):
            seqName = media_name_splited[1]

        return seqName

    def fillMontageInfoFromOtioFile(self, otioFile, verboseInfo=False):
        # wkip code taken from getSequenceClassListFromOtioTimeline

        # timeline = opentimelineio.adapters.read_from_file(otioFile)

        self.otioFile = otioFile
        self.timeline = ow.get_timeline_from_file(otioFile)

        if self.timeline is None:
            _logger.error("fillMontageInfoFromOtioFile: self.timeline is None!")
            return

        def _getParentSeqIndex(seqList, seqName):
            #    print("\n_getParentSeqIndex: seqName: ", seqName)
            for i, seq in enumerate(seqList):
                if seqName in seq.name.lower():
                    #    print(f"    : {seq.name}, i: {i}")
                    return i

            return -1

        tracks = self.timeline.video_tracks()
        for track in tracks:
            for clip in track:
                if isinstance(clip, opentimelineio.schema.Clip):
                    # print(clip.media_reference)
                    media_path = Path(utils.file_path_from_url(clip.media_reference.target_url))
                    # print(f"{media_path}")

                    # get media name
                    filename = os.path.split(media_path)[1]
                    media_name = os.path.splitext(filename)[0]
                    media_name_lower = media_name.lower()

                    # get parent sequence
                    seq_pattern = "_seq"
                    if seq_pattern in media_name_lower:
                        #    print(f"media_name: {media_name}")

                        media_name_splited = media_name_lower.split("_")
                        if 2 <= len(media_name_splited):
                            parentSeqInd = _getParentSeqIndex(self.sequencesList, media_name_splited[1])

                            # add new seq if not found
                            newSeq = None
                            if -1 == parentSeqInd:
                                # newSeq = otc.OtioSequence()
                                newSeq = self.newSequence()
                                newSeq.name = self.getSequenceNameFromMediaName(media_name)
                                # cList = list()
                                # cList.append(clip)
                                # newSeq.clipList = cList
                                # newSeq.clipList.append(clip)
                                # newSeq.name = media_name_splited[1]
                                # sequenceList.append(newSeq)

                            else:
                                newSeq = self.sequencesList[parentSeqInd]

                            # newSeq.clipList.append(clip)
                            newSeq.newShot(clip)

        for seq in self.sequencesList:
            # get the start and end of every seq
            seq.setStartAndEnd()
            if verboseInfo:
                seq.printInfo()


class SequenceOtio(SequenceInterface):
    """ Custom sequence to contain the clips related to the shots
    """

    def __init__(self):
        super().__init__()
        pass

    def newShot(self, shot):
        if self.shotsList is None:
            self.shotsList = list()
        newShot = ShotOtio(shot)
        self.shotsList.append(newShot)
        return newShot

    # warning: clips may not be on the same track, hence they may not be ordered!!
    def setStartAndEnd(self):
        if len(self.shotsList):
            # start
            self.start = ow.get_clip_frame_final_start(self.shotsList[0].clip)
            for shot in self.shotsList:
                if ow.get_clip_frame_final_start(shot.clip) < self.start:
                    self.start = ow.get_clip_frame_final_start(shot.clip)

            # end
            self.end = ow.get_timeline_clip_end_inclusive(self.shotsList[0].clip)
            for shot in self.shotsList:
                if ow.get_timeline_clip_end_inclusive(shot.clip) > self.end:
                    self.end = ow.get_timeline_clip_end_inclusive(shot.clip)

    def printInfo(self):
        print(f"\nSeq: {self.name}, start: {self.start}, end: {self.end}")
        if self.shotsList is not None:
            for item in self.shotsList:
                print(f"  - {item.media_reference.target_url}")


class ShotOtio(ShotInterface):
    """ 
    """

    def __init__(self, shot):
        super().__init__()
        self.clip = shot
        pass

