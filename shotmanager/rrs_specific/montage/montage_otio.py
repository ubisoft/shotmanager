import os
from pathlib import Path

from shotmanager.config import config
from shotmanager.utils import utils, utils_xml
from .montage_interface import MontageInterface, SequenceInterface, ShotInterface
from shotmanager.otio import otio_wrapper as ow
import opentimelineio

import logging

_logger = logging.getLogger(__name__)


class MontageOtio(MontageInterface):
    """ 
    """

    def __init__(self):
        super().__init__()

        # new properties:
        self.otioFile = None
        self.timeline = None
        # self.seqCharacteristics = None
        # self.videoCharacteristics = None

    def initialize(self, otioFile, read=True):
        # wkip release memory from exisiting otio montage???

        self.otioFile = otioFile
        if read:
            self.timeline = ow.get_timeline_from_file(self.otioFile)
            self._name = self.timeline.name

    def get_montage_type(self):
        return "OTIO"

    def get_montage_characteristics(self):
        """
            Return a dictionary with the characterisitics of the montage.
            This is required to export it as xml EDL.
        """
        print(f"-++ self.timeline: {self.timeline}")
        self._characteristics["framerate"] = self.get_fps()
        self._characteristics["duration"] = self.get_frame_duration()

        return self._characteristics

    def set_montage_characteristics(self, resolution_x=-1, resolution_y=-1, framerate=-1, duration=-1):
        """
        """
        self._characteristics = dict()
        # self._characteristics["framerate"] = framerate  # timebase
        self._characteristics["resolution_x"] = resolution_x  # width
        self._characteristics["resolution_y"] = resolution_y  # height
        self._characteristics["framerate"] = self.get_fps()  # timebase
        self._characteristics["duration"] = self.get_frame_duration()  # wkip may change afterwards...
        # self._characteristics["duration"] = duration  # wkip may change afterwards...

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

    def fillMontageInfoFromOtioFile(self, otioFile=None, refVideoTrackInd=0, verboseInfo=False):

        if otioFile is not None:
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

        def _getVideoCharacteristicsFromXML():
            print("_getVideoCharacteristicsFromXML")

            from xml.dom.minidom import parse

            dom1 = parse(self.otioFile)
            seq = dom1.getElementsByTagName("sequence")[0]

            seqCharacteristics = dict()

            seqDuration = utils_xml.getFirstChildWithName(seq, "duration")
            if seqDuration is not None:
                seqCharacteristics = {"duration": int(seqDuration.childNodes[0].nodeValue)}
            # seqRate = utils_xml.getFirstChildWithName(seq, "rate")
            # if seqRate is not None:
            #     seqRateDict = {
            #         "timebase": float(utils_xml.getFirstChildWithName(seqRate, "timebase").childNodes[0].nodeValue),
            #         "ntsc": utils_xml.getFirstChildWithName(seqRate, "ntsc").childNodes[0].nodeValue,
            #     }
            #     self.seqCharacteristics = {"rate": seqRateDict}

            seqMedia = None
            seqMediaVideo = None
            seqMediaVideoFormat = None
            videoSampleCharacteristics = None

            videoCharacteristics = dict()

            seqMedia = utils_xml.getFirstChildWithName(seq, "media")
            if seqMedia is not None:
                seqMediaVideo = utils_xml.getFirstChildWithName(seqMedia, "video")

            if seqMediaVideo is not None:
                seqMediaVideoFormat = utils_xml.getFirstChildWithName(seqMediaVideo, "format")

            if seqMediaVideoFormat is not None:
                videoSampleCharacteristics = utils_xml.getFirstChildWithName(
                    seqMediaVideoFormat, "samplecharacteristics"
                )

            print(f"videoSampleCharacteristics: {videoSampleCharacteristics}")

            if videoSampleCharacteristics is not None:
                seqRate = utils_xml.getFirstChildWithName(videoSampleCharacteristics, "rate")

                seqRateDict = {
                    "timebase": float(utils_xml.getFirstChildWithName(seqRate, "timebase").childNodes[0].nodeValue),
                    "ntsc": utils_xml.getFirstChildWithName(seqRate, "ntsc").childNodes[0].nodeValue,
                }

                videoCharacteristics["rate"] = seqRateDict
                videoCharacteristics["width"] = int(
                    utils_xml.getFirstChildWithName(videoSampleCharacteristics, "width").childNodes[0].nodeValue
                )
                videoCharacteristics["height"] = int(
                    utils_xml.getFirstChildWithName(videoSampleCharacteristics, "height").childNodes[0].nodeValue
                )
                # videoCharacteristics["anamorphic"] = (
                #     utils_xml.getFirstChildWithName(videoSampleCharacteristics, "anamorphic").childNodes[0].nodeValue
                # )
                # videoCharacteristics["pixelaspectratio"] = (
                #     utils_xml.getFirstChildWithName(videoSampleCharacteristics, "pixelaspectratio").childNodes[0].nodeValue
                # )
                # videoCharacteristics["fielddominance"] = (
                #     utils_xml.getFirstChildWithName(videoSampleCharacteristics, "fielddominance").childNodes[0].nodeValue
                # )
                # videoCharacteristics["colordepth"] = int(
                #     utils_xml.getFirstChildWithName(videoSampleCharacteristics, "colordepth").childNodes[0].nodeValue
                # )
                # videoCharacteristics["width"] = elem.nodeValue
                # print(f"width: {videoCharacteristics['width']}")
                # print(f"videoCharacteristics: {videoCharacteristics}")

                self.set_montage_characteristics(
                    #  videoCharacteristics["rate"]["timebase"],
                    resolution_x=videoCharacteristics["width"],
                    resolution_y=videoCharacteristics["height"],
                    #  duration=seqCharacteristics["duration"],
                )

            return ()

        if ".xml" == (Path(self.otioFile).suffix).lower():
            _getVideoCharacteristicsFromXML()

        self.sequencesList = None
        self.sequencesList = list()

        _logger.debug(f"refVideoTrackInd: {refVideoTrackInd}")
        # ref track is the first one
        tracks = self.timeline.video_tracks()
        for i, track in enumerate(tracks):
            if refVideoTrackInd == i:
                #     track = self.timeline.video_tracks[0]

                for clip in track:
                    print(f"Clip name 01: {clip.name}, type:{type(clip)}")

                    # if clip is a media
                    if isinstance(clip, opentimelineio.schema.Clip):
                        # if True:
                        #  print(f"  Clip name 02: {clip.name}")
                        if clip.media_reference.is_missing_reference:
                            print(f"Missing Media Reference for Clip: {clip.name}")
                            continue
                        media_path = Path(utils.file_path_from_url(clip.media_reference.target_url))
                        # if config.uasDebug:
                        #   print(f"\n** clip: {clip.name}")
                        # print(f"** clip.media_reference: {clip.media_reference}")
                        # print(f"** media_path: {media_path}")
                        # wkip ici mettre une exception pour attraper les media manquants (._otio.MissingReference)

                        # get media name
                        filename = os.path.split(media_path)[1]
                        media_name = os.path.splitext(filename)[0]
                        media_name_lower = media_name.lower()

                        # get parent sequence
                        seq_pattern = "_seq"
                        #    print(f"  Clip name 03: {clip.name}")

                        if seq_pattern in media_name_lower:
                            #   print(f"media_name: {media_name}")

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

                    # clip can be a nested edit (called a stack)
                    else:
                        stackName = clip.name
                        print(f"Stack Seq Name: {stackName}, seq: {self.getSequenceNameFromMediaName(stackName)}")
                        # get the name of the shot
                        stackNameLower = stackName.lower()
                        seq_pattern = "_seq"
                        if seq_pattern in stackNameLower:
                            media_name_splited = (stackName.lower()).split("_")
                            print(f"media_name_splited: {media_name_splited}")
                            if 2 <= len(media_name_splited):
                                parentSeqInd = _getParentSeqIndex(self.sequencesList, media_name_splited[1])

                                # add new seq if not found
                                newSeq = None
                                print(f"   Stack Seq Name: {self.getSequenceNameFromMediaName(stackName)}")

                                if -1 == parentSeqInd:
                                    newSeq = self.newSequence()
                                    newSeq.set_name(self.getSequenceNameFromMediaName(stackName))
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
        infoStr = ""
        super().printInfo(only_clip_info=only_clip_info)
        clipType = type(self.clip).__name__
        # print(f"clipType: {clipType}")
        if "Clip" == clipType:
            infoStr += f"             - Type: OTIO Media Clip"
        elif "Stack" == clipType:
            infoStr += f"             - Type: OTIO Nested Edit (Stack)"
        else:
            infoStr += f"             - Type: OTIO {clipType}"

        infoStr += f",    Media: {ow.get_clip_media_path(self.clip)}"
        emptyDuration = ow.get_clip_empty_duration(self.clip, self.parent.parent.get_fps())
        if 0 != emptyDuration:
            infoStr += f"\n               Empty duration lenght: {emptyDuration}"
        print(infoStr)

    def get_frame_start(self):
        return ow.get_clip_frame_start(self.clip, self.parent.parent.get_fps())

    def get_frame_end(self):
        """get_frame_end is exclusive in order to follow the Blender implementation of get_frame_end for its clips
        """
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
