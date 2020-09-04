import logging

_logger = logging.getLogger(__name__)


# was OtioTimeline
class MontageInterface:
    """ 
    """

    def __init__(self):
        self.montageType = "INTERFACE"
        self._name = ""
        self.sequencesList = list()

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    def printInfo(self, printChildren=True):
        infoStr = "\n\n-----------------------------"
        infoStr += f"\n\n Montage: {self.get_name()}    -     Type: {self.montageType}"
        infoStr += f"\n    Start: {self.get_frame_start()}, End:{self.get_frame_end()}, Duration: {self.get_frame_duration()}, fps: {self.get_fps()}, Sequences: {len(self.sequencesList)}"
        print(infoStr)

        if printChildren:
            for seq in self.sequencesList:
                seq.printInfo()

    def get_fps(self):
        return -1

    def get_frame_start(self):
        if self.sequencesList is not None and len(self.sequencesList):
            return self.sequencesList[0].get_frame_start()
        else:
            return -1

    def get_frame_end(self):
        if self.sequencesList is not None and len(self.sequencesList):
            return self.sequencesList[len(self.sequencesList) - 1].get_frame_end()
        else:
            return -1

    def get_frame_duration(self):
        return -1

    def newSequence(self):
        if self.sequencesList is None:
            self.sequencesList = list()
        newSeq = SequenceInterface(self)
        self.sequencesList.append(newSeq)
        return newSeq


class SequenceInterface:
    """ 
    """

    def __init__(self, parent):
        # parent montage
        self.parent = parent

        self._name = ""
        self.shotsList = list()
        self.start = -1
        self.end = -1

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    def newShot(self, shot):
        if self.shotsList is None:
            self.shotsList = list()
        newShot = ShotInterface(self)
        self.shotsList.append(newShot)
        return newShot

    def printInfo(self, printChildren=True):
        infoStr = f"\n    - Sequence: {self.get_name()}, Start: {self.get_frame_start()}, End:{self.get_frame_end()}, Duration: {self.get_frame_duration()}, Shots: {len(self.shotsList)}"
        print(infoStr)
        if printChildren:
            for shot in self.shotsList:
                print("")
                shot.printInfo()

    def get_index_in_parent(self):
        if self in self.parent.sequencesList:
            return self.parent.sequencesList.index(self)
        else:
            return -1

    def get_frame_start(self):
        # warning: clips may not be on the same track, hence they may not be ordered!!
        start = self.shotsList[0].get_frame_final_start()
        for shot in self.shotsList:
            tmpStart = shot.get_frame_final_start()
            if tmpStart < start:
                start = tmpStart
        return start

    def get_frame_end(self):
        # warning: clips may not be on the same track, hence they may not be ordered!!
        end = self.shotsList[0].get_frame_final_end()
        for shot in self.shotsList:
            tmpEnd = shot.get_frame_final_end()
            if tmpEnd > end:
                end = tmpEnd
        return end

    def get_frame_duration(self):
        return self.get_frame_end() - self.get_frame_start()


class ShotInterface:
    """ 
    """

    def __init__(self, parent):
        # parent sequence
        self.parent = parent

        pass

    def get_name(self):
        return ""

    def get_index_in_parent(self):
        if self in self.parent.shotsList:
            return self.parent.shotsList.index(self)
        else:
            return -1

    def printInfo(self):
        infoStr = f"        - Shot {self.get_index_in_parent()}:    Name: {self.get_name()}"
        infoStr += f"\n             - Start: {self.get_frame_start()}, End: {self.get_frame_end()}, Duration: {self.get_frame_duration()}"
        infoStr += f"\n             - Final Start: {self.get_frame_final_start()}, Final End: {self.get_frame_final_end()}, Final Duration: {self.get_frame_final_duration()}"
        infoStr += (
            f"\n             - Offset Start: {self.get_frame_offset_start()}, Offset End: {self.get_frame_offset_end()}"
        )
        print(infoStr)

    def get_frame_start(self):
        return -1

    def get_frame_end(self):
        return -1

    def get_frame_duration(self):
        return -1

    def get_frame_final_start(self):
        return -1

    def get_frame_final_end(self):
        return -1

    def get_frame_final_duration(self):
        return -1

    def get_frame_offset_start(self):
        return -1

    def get_frame_offset_end(self):
        return -1

