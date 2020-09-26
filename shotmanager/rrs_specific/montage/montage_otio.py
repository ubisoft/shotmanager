import logging

_logger = logging.getLogger(__name__)

import os
from pathlib import Path
from urllib.parse import unquote_plus, urlparse
import re

from shotmanager.utils import utils
from .montage_interface import MontageInterface, SequenceInterface, ShotInterface
from shotmanager.otio import otio_wrapper as ow
import opentimelineio


class MontageOtio(MontageInterface):
    """ 
    """

    def __init__(self):
        super().__init__()

        # new properties:
        self.otioFile = None
        self.timeline = None

    def initialize(self, otioFile, read=True):
        # wkip release memory from exisiting otio montage???

        self.otioFile = otioFile
        if read:
            self.timeline = ow.get_timeline_from_file(self.otioFile)
            self._name = self.timeline.name

    def get_montage_type(self):
        return "OTIO"

    def get_fps(self):
        time = self.timeline.duration()
        rate = int(time.rate)
        return rate

    def get_frame_duration(self):
        time = self.timeline.duration()
        duration = int(time.value)
        return duration

    def newSequence(self):
        if self.sequencesList is None:
            self.sequencesList = list()
        newSeq = SequenceOtio(self)
        self.sequencesList.append(newSeq)
        return newSeq

    def getSequenceNameFromMediaName(self, fileName):
        seqName = ""

        media_name_splited = fileName.split("_")
        if 2 <= len(media_name_splited):
            seqName = media_name_splited[1]

        return seqName

    def fillMontageInfoFromOtioFile(self, otioFile, verboseInfo=False):
        self.initialize(otioFile)

        if self.timeline is None:
            _logger.error("fillMontageInfoFromOtioFile: self.timeline is None!")
            return

        def _getParentSeqIndex(seqList, seqName):
            #    print("\n_getParentSeqIndex: seqName: ", seqName)
            for i, seq in enumerate(seqList):
                if seqName in seq.get_name().lower():
                    #    print(f"    : {seq.name}, i: {i}")
                    return i

            return -1

        tracks = self.timeline.video_tracks()
        for track in tracks:
            for clip in track:
                if isinstance(clip, opentimelineio.schema.Clip):
                    print(f"** clip: {clip}")
                    print(f"** clip.media_reference: {clip.media_reference}")
                    media_path = Path(utils.file_path_from_url(clip.media_reference.target_url))
                    print(f"** media_path: {media_path}")
                    # wkip ici mettre une exception pour attraper les media manquants (._otio.MissingReference)

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
                                newSeq = self.newSequence()
                                newSeq.set_name(self.getSequenceNameFromMediaName(media_name))

                            else:
                                newSeq = self.sequencesList[parentSeqInd]
                            newSeq.newShot(clip)

        # for seq in self.sequencesList:
        #     # get the start and end of every seq
        #     seq.setStartAndEnd()
        #     if verboseInfo:
        #         seq.printInfo()

        # # get file names only
        # file_list = list()
        # for item in media_list:
        #     filename = os.path.split(item)[1]
        #     file_list.append(os.path.splitext(filename)[0])
        #     # print(item)

        # # get sequences
        # seq_list = list()
        # seq_pattern = "_seq"
        # for item in file_list:
        #     if seq_pattern in item.lower():
        #         itemSplited = item.split("_")
        #         if 2 <= len(itemSplited):
        #             if itemSplited[1] not in seq_list:
        #                 seq_list.append(itemSplited[1])


class SequenceOtio(SequenceInterface):
    """ Custom sequence to contain the clips related to the shots
    """

    def __init__(self, parent):
        super().__init__(parent)
        pass

    def newShot(self, shot):
        """
            shot is an otio clip
        """
        if self.shotsList is None:
            self.shotsList = list()
        newShot = ShotOtio(self, shot)
        self.shotsList.append(newShot)
        return newShot


class ShotOtio(ShotInterface):
    """ 
    """

    def __init__(self, parent, shot):
        super().__init__()
        self.initialize(parent)
        self.clip = shot
        pass

    def get_name(self):
        return self.clip.name

    def printInfo(self, only_clip_info=False):
        super().printInfo(only_clip_info=only_clip_info)
        infoStr = f"             - Media: {ow.get_clip_media_path(self.clip)}"
        emptyDuration = ow.get_clip_empty_duration(self.clip, self.parent.parent.get_fps())
        if 0 != emptyDuration:
            infoStr += f"\n               Empty duration lenght: {emptyDuration}"
        print(infoStr)

    def get_frame_start(self):
        return ow.get_clip_frame_start(self.clip, self.parent.parent.get_fps())

    def get_frame_end(self):
        # get_clip_frame_end is exclusive
        return ow.get_clip_frame_end(self.clip, self.parent.parent.get_fps())

    def get_frame_duration(self):
        return ow.get_clip_frame_duration(self.clip, self.parent.parent.get_fps())

    def get_frame_final_start(self):
        return ow.get_clip_frame_final_start(self.clip, self.parent.parent.get_fps())

    def get_frame_final_end(self):
        # get_clip_frame_final_end is exclusive
        return ow.get_clip_frame_final_end(self.clip, self.parent.parent.get_fps())

    def get_frame_final_duration(self):
        return ow.get_clip_frame_final_duration(self.clip, self.parent.parent.get_fps())

    def get_frame_offset_start(self):
        return ow.get_clip_frame_offset_start(self.clip, self.parent.parent.get_fps())

    def get_frame_offset_end(self):
        return ow.get_clip_frame_offset_end(self.clip, self.parent.parent.get_fps())
