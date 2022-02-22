# GPLv3 License
#
# Copyright (C) 2021 Ubisoft
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Generic montage class used to host the content of an edit
"""

from pathlib import Path

from ..config import sm_logging

_logger = sm_logging.getLogger(__name__)


class MontageInterface(object):
    """ 
    """

    def __init__(self):
        self._name = ""
        self.sequencesList = list()
        self._characteristics = dict()

    def get_montage_type(self):
        return "INTERFACE"

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    def printInfo(self, printChildren=True):
        infoStr = "\n\n-----------------------------"
        # infoStr += (
        #     f"\nNote: All the end values are EXCLUSIVE (= not the last used frame of the range but the one after)"
        # )
        infoStr += f"\n\n Montage: {self.get_name()}    -     Type: {self.get_montage_type()}"
        infoStr += f"\n    Start: {self.get_frame_start()}, End (incl.):{self.get_frame_end() - 1}, Duration: {self.get_frame_duration()}, fps: {self.get_fps()}, Sequences: {self.get_num_sequences()}"
        print(infoStr)

        if printChildren:
            self.printChildrenInfo()

    def getInfoAsDictionnary(self, dictMontage=None, shotsDetails=True):
        if dictMontage is None:
            dictMontage = dict()
            dictMontage["montage"] = self.get_name()
        dictMontage["sequences"] = []
        for seq in self.sequencesList:
            #    dictMontage[seq.get_name()] = seq.getInfoAsDictionnary()
            dictMontage["sequences"].append(seq.getInfoAsDictionnary(shotsDetails=shotsDetails))
        return dictMontage

    def printChildrenInfo(self):
        for seq in self.sequencesList:
            seq.printInfo()

    def get_montage_characteristics(self):
        """
            Return a dictionary with the characterisitics of the montage.
            This is required to export it as xml edit file.
        """
        return self._characteristics

    def set_montage_characteristics(self, framerate=-1, resolution_x=-1, resolution_y=-1, duration=-1):
        """
        """
        self._characteristics = dict()
        self._characteristics["framerate"] = framerate  # timebase
        self._characteristics["resolution_x"] = resolution_x  # width
        self._characteristics["resolution_y"] = resolution_y  # height
        self._characteristics["duration"] = duration  # duration

    def get_fps(self):
        if "framerate" in self._characteristics:
            return self._characteristics["framerate"]
        else:
            return -1

    def get_frame_start(self):
        if self.sequencesList is not None and len(self.sequencesList):
            return self.sequencesList[0].get_frame_start()
        else:
            return -1

    def get_frame_end(self):
        """get_frame_end is exclusive in order to follow the Blender implementation of get_frame_end for its clips
        """
        if self.sequencesList is not None and len(self.sequencesList):
            return self.sequencesList[len(self.sequencesList) - 1].get_frame_end()
        else:
            return -1

    def get_frame_duration(self):
        if "duration" in self._characteristics:
            return self._characteristics["duration"]
        else:
            return -1

    def get_num_sequences(self):
        return len(self.sequencesList)

    def get_sequences(self):
        return self.sequencesList

    def newSequence(self):
        if self.sequencesList is None:
            self.sequencesList = list()
        newSeq = SequenceInterface(self)
        self.sequencesList.append(newSeq)
        return newSeq

    def get_sequence_by_name(self, sequence_name):
        refSeq = None

        sequences = self.get_sequences()
        for seq in sequences:
            #  print(f"seq: {seq}, sequence_name: {sequence_name}")
            if seq.get_name() == sequence_name:
                refSeq = seq
                break
        return refSeq

    def conformToRefMontage(self, ref_montage, ref_sequence_name=""):
        WARNING = "\033[93m"
        ENDC = "\033[0m"
        infoStr += f"\n\n {WARNING}Conform to ref montge (in Montage_interface.py):{ENDC}\n"
        print(infoStr)

    def compareWithMontage(self, ref_montage, ref_sequence_name=""):
        """
            Compare current montage with specified montage
            If ref_sequence_name is specified then only this sequence is compared
        """

        def printInfoLine(col00, col01, col02):
            print(f"{col00: >10}   {col01: <37}    - {col02: <30}")

        textSelf = ""
        textRef = ""
        WARNING = "\033[93m"
        ENDC = "\033[0m"
        infoStr = "\n\n ------ ------ ------ ------ ------ ------ ------ ------ ------ "
        infoStr += f"\n\n {WARNING}Comparing montages (in Montage_interface.py):{ENDC}\n"
        print(infoStr)

        # infoStr += (
        #     f"\nNote: All the end values are EXCLUSIVE (= not the last used frame of the range but the one after)"
        # )
        # infoStr += f"\n        Ref: {ref_montage.get_name(): >30}       -  {self.get_name() : >30}"
        textRef = ref_montage.get_name()
        textSelf = self.get_name()
        # printInfoLine("", textRef, textSelf)
        print(f"     {textRef + ':' :<44} {textSelf + ':' :<30}")

        # selfSeq = self.get_sequence_by_name(ref_sequence_name)
        selfSeq = (self.get_sequences())[0]  # wkip limité à 1 take pour l'instant
        textSelf = f"  Current Sequence: {selfSeq.get_name()}"

        refSeq = ref_montage.get_sequence_by_name(ref_sequence_name)
        if "" != ref_sequence_name:
            if refSeq is not None:
                textRef = f"  Ref Sequence: {refSeq.get_name()}"

        print(f"     {textRef + ':' :<44} {textSelf + ':' :<30}")

        if refSeq is None:
            print(" Ref Sequence is None, aborting comparison...")
            return ()

        ###################
        # compare order and enable state
        ###################

        comparedShotsList = selfSeq.getEditShots(ignoreDisabled=False)
        newEditShots = list()
        numShotsInRefEdit = len(refSeq.getEditShots())
        for i, shot in enumerate(refSeq.getEditShots()):
            shotRef = shot
            textRef = shotRef.get_name()
            shotRefName = Path(shotRef.get_name()).stem

            shotSelf = None
            for sh in comparedShotsList:
                # if sh.get_name() == shotRef.get_name():
                shotName = sh.get_name()
                # print(f"shotName: {shotName}, shotRefName: {shotRefName}")
                if shotName == shotRefName:
                    shotSelf = sh
                    newEditShots.append(shotSelf)
                    break

            if shotSelf is None:
                textSelf = "** Not found **"
            else:
                textSelf = shotSelf.get_name()
                textSelf += "   "

                if shotSelf.get_frame_final_duration() != shotRef.get_frame_final_duration():
                    textSelf += f" / different durations ({shotSelf.get_frame_final_duration()} fr.)"

                # wkip we don't know the length of the handles!!!
                # if shotSelf.get_frame_offset_start() != shotRef.get_frame_final_duration():
                #     textSelf += f" / different durations ({shotSelf.get_frame_final_duration()} fr.)"

                if not shotSelf.enabled:
                    textSelf += " / to enable"

            # wkip wkip here mettre les diffs

            printInfoLine(str(i), f"{textRef}  ({shotRef.get_frame_final_duration()} fr.)", textSelf)
        # print(f"Shot: {shot.get_name()}")
        #         pass

        ###################
        # list other shots and disabled them
        ###################
        print("\n\n       Shots not used in current sequence (set to disabled):")
        ind = 0
        for i, sh in enumerate(comparedShotsList):
            if sh not in newEditShots:
                # sh.enabled = False
                textSelf = sh.get_name() + " / to disable"
                printInfoLine(str(ind + numShotsInRefEdit), "-", textSelf)
                ind += 1

        if 0 == ind:
            printInfoLine("", "-", "-")

        print("")


class SequenceInterface(object):
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
        newShot = ShotInterface()
        # newShot = ShotInterface(self)
        self.initialize(self)
        self.shotsList.append(newShot)
        return newShot

    # use getEditShots
    # def get_shots(self, ignoreDisabled=True):
    #     return self.getEditShots(ignoreDisabled=ignoreDisabled)

    def getEditShots(self, ignoreDisabled=True):
        return self.shotsList

    def printInfo(self, printChildren=True):
        infoStr = f"\n    - Sequence: {self.get_name()}, Start: {self.get_frame_start()}, End(incl.):{self.get_frame_end() - 1}, Duration: {self.get_frame_duration()}, Shots: {len(self.shotsList)}"
        print(infoStr)
        if printChildren:
            for shot in self.shotsList:
                print("")
                shot.printInfo()

    def getInfoAsDictionnary(self, shotsDetails=True):
        dictSeq = dict()
        dictSeq["sequence_name"] = self.get_name()

        if shotsDetails:
            dictSeq["shots"] = []
            for shot in self.getEditShots():
                dictSeq["shots"].append(shot.getInfoAsDictionnary())

        return dictSeq

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
        """get_frame_end is exclusive in order to follow the Blender implementation of get_frame_end for its clips
        """
        # warning: clips may not be on the same track, hence they may not be ordered!!
        end = self.shotsList[0].get_frame_final_end()
        for shot in self.shotsList:
            tmpEnd = shot.get_frame_final_end()
            if tmpEnd > end:
                end = tmpEnd
        return end

    def get_frame_duration(self):
        return self.get_frame_end() - self.get_frame_start()


class ShotInterface(object):
    """ 
    """

    def __init__(self):
        # print(" *** self Init in ShotInterface *** ")
        # parent sequence
        self.parent = None

        pass

    def initialize(self, parent):
        self.parent = parent

    # def __init__(self, parent):
    #     print(" *** Init parent in ShotInterface *** ")
    #     # parent sequence
    #     self.parent = parent

    #     pass

    def get_name(self):
        return ""

    def get_index_in_parent(self):
        # if "parent" in self:
        if self in self.parent.shotsList:
            return self.parent.shotsList.index(self)
        else:
            return -1
        # else:
        #     return -1

    def printInfo(self, only_clip_info=False):
        infoStr = ""
        infoStr += f"        - Shot {self.get_name()}  ({self.get_index_in_parent()}):"
        if not only_clip_info:
            infoStr += f"\n             - Start: {self.get_frame_start()}, End(Incl.): {self.get_frame_end() - 1}, Duration: {self.get_frame_duration()}"
        infoStr += f"\n             - Final Start: {self.get_frame_final_start()}, Final End(Incl.): {self.get_frame_final_end() - 1}, Final Duration: {self.get_frame_final_duration()}"
        if not only_clip_info:
            infoStr += f"\n             - Offset Start: {self.get_frame_offset_start()}, Offset End: {self.get_frame_offset_end()}"
        print(infoStr)

    def getInfoAsDictionnary(self, shotsDetails=True):
        dictShot = dict()
        dictShot["shot"] = self.get_name()
        if shotsDetails:
            dictShot["frame_final_start"] = self.get_frame_final_start()
            dictShot["frame_final_duration"] = self.get_frame_final_duration()

        return dictShot

    def get_frame_start(self):
        return -1

    def get_frame_end(self):
        """get_frame_end is exclusive in order to follow the Blender implementation of get_frame_end for its clips
        """
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
