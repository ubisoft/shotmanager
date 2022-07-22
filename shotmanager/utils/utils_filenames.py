# GPLv3 License
#
# Copyright (C) 2022 Ubisoft
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
Classes and functions dedicated to filenames management such as sequence names.
"""


from pathlib import Path
import bpy

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


class SequencePath:
    # to do:
    # - support / and \
    # - support creation with file name already with an index (have a parameter
    #   to get generic infos or index specific infos)
    # - support absolute and relative paths
    """
    Split a file path into parts. Dedicated to sequence filename management.

    Returns an instance made of:
        - fullpath: the file path and name
        - parent: the file path without the file name AND with a "\" at the end
        - name: the name of the file with extension
        - stem: the name of the file without extension
        - seq_name: the name of the sequence when # are removed
        - suffix: the file extension

    When the initial sequence path and name is submitted with no extension then it is seen as a path

    Eg.: myPath = SequencePath("c:\temp\mySequence_####.png")
        - myPath._fullpath(): "c:\temp\mySequence_####.png"
        - myPath.parent(): "c:\temp\"
        - myPath.name(): "mySequence_####.png"
        - myPath.stem(): "mySequence_####"
        - myPath.sequence_name(): "mySequence"
        - myPath.sequence_indices: "####"
        - myPath.suffix: ".png"     or myPath.extension(): ".png"
    """

    fullpath = None

    def __init__(self, filepath):
        self._fullpath = filepath

    def is_file_extension_valid(self, filepath=None):
        """
        Return False if the extension is empty, containts only digits or contains at least one # character
        """
        fullpath = self._fullpath if filepath is None else filepath
        suf = str(Path(fullpath).suffix)
        if 0 == len(suf):
            return False
        if "." == suf[0]:
            suf = suf[1:]
            try:
                # if suf can be converted to an int then the extension is not valid
                int(suf)
                return False
            except Exception:
                pass

        # case where there is no file extension but filename ends with '.###'
        if -1 != suf.find("#"):
            return False

        return True

    # TOFIX wkip to finish
    def format_path(self, path, separator_at_end=True):
        """
        Return a path made with by the specified separator
        """
        formatted_path = path

        if self.is_file_extension_valid(filepath=path):
            # wkip set here / or \
            formatted_path = path
        else:
            if separator_at_end and not (path.endswith("\\") or path.endswith("/")):
                # wkip set here / or \
                formatted_path += "\\"
        return formatted_path

    # ------------------------------
    # standard filepath functions

    def fullpath(self):
        return self.format_path(self._fullpath)

    def parent(self):
        if not self.is_file_extension_valid():
            return self.format_path(self._fullpath)
        return self.format_path(str(Path(self._fullpath).parent))

    def name(self):
        if not self.is_file_extension_valid():
            return ""
        return str(Path(self._fullpath).name)

    def stem(self):
        if not self.is_file_extension_valid():
            return ""
        return str(Path(self._fullpath).stem)

    def extension(self):
        """
        Same as function self.suffix(). Available for consistency with operating systems.
        """
        return self.suffix()

    def suffix(self):
        """
        Same as function self.extension(). Available for consistency with Python pathlib terminology.
        If the file name extension contains a # its end will not be considered as an extension
        but as an index.
        """
        suf = str(Path(self._fullpath).suffix)
        if self.is_file_extension_valid():
            return suf
        return ""

    # ------------------------------
    # sequence filepath functions

    def sequence_fullpath(self, at_frame=None):
        if at_frame is None:
            return self.format_path(self._fullpath)

        fullp = f"{self.parent()}{self.sequence_name(at_frame=at_frame)}"
        return fullp

    def sequence_root(self, at_frame=None):
        return self.parent()

    def sequence_name(self, at_frame=None):
        if at_frame is None:
            # return str(Path(self._fullpath).name)
            return self.name()

        indices_pattern = self.sequence_indices(at_frame=at_frame)
        seq_name = f"{self.sequence_basename()}{indices_pattern}{self.suffix()}"
        return seq_name

    def sequence_stem(self, at_frame=None):
        """
        If the file name extension contains a # its end will not be considered as an extension
        but as an index.
        """
        # case where there is no file extention but filename ends with '.###'
        if self.is_file_extension_valid():
            seq_stem = self.sequence_basename() + self.sequence_indices(at_frame=at_frame)
        else:
            seq_stem = self.sequence_basename()
            indices = self.sequence_indices(at_frame=at_frame)
            seq_stem += indices

        return seq_stem

    def sequence_basename(self):
        if self._fullpath is None:
            return None

        lastInd = self._fullpath.rfind("#")
        if -1 == lastInd:
            name = self.stem()
        else:
            while lastInd > 0 and "#" == self._fullpath[lastInd]:
                lastInd -= 1
            name = str(Path(self._fullpath[0 : lastInd + 1]).stem)

        return name

    def sequence_indices(self, at_frame=None):
        """
        at_frame: frame index at which the indices should be set.
            Returns an empty string if there is no indice pattern in the filename.
        """
        if self._fullpath is None:
            return ""

        indices = ""
        lastInd = self._fullpath.rfind("#")
        while lastInd > 0 and "#" == self._fullpath[lastInd]:
            indices += "#"
            lastInd -= 1

        if at_frame is not None and 0 < len(indices):
            at_frame_str = str(at_frame)
            while len(at_frame_str) < len(indices):
                at_frame_str = "0" + at_frame_str
            indices = at_frame_str

        return indices

    def print(self, at_frame=None, spacer=""):
        outStr = ""
        outStr += f"{spacer}fullpath:           {self.fullpath()}\n"
        outStr += f"{spacer}parent:             {self.parent()}\n"
        outStr += f"{spacer}name:               {self.name()}\n"
        outStr += f"{spacer}stem:               {self.stem()}\n"
        outStr += f"{spacer}extension (suffix): {self.extension()}\n"

        outStr += "\n"
        outStr += f"{spacer}sequence_fullpath:  {self.sequence_fullpath()}\n"
        outStr += f"{spacer}sequence_root:      {self.sequence_root()}\n"
        outStr += f"{spacer}sequence_name:      {self.sequence_name()}\n"
        outStr += f"{spacer}sequence_stem:      {self.sequence_stem()}\n"
        outStr += f"{spacer}sequence_basename:  {self.sequence_basename()}\n"
        outStr += f"{spacer}sequence_indices:   {self.sequence_indices()}\n"

        if at_frame is not None:
            outStr += f"\n - At frame {at_frame}:\n"
            outStr += f"{spacer}sequence_fullpath: {self.sequence_fullpath(at_frame=at_frame)}\n"
            outStr += f"{spacer}sequence_root:     {self.sequence_root(at_frame=at_frame)}\n"
            outStr += f"{spacer}sequence_name:     {self.sequence_name(at_frame=at_frame)}\n"
            outStr += f"{spacer}sequence_stem:     {self.sequence_stem(at_frame=at_frame)}\n"
            outStr += f"{spacer}sequence_basename: {self.sequence_basename()}\n"
            outStr += f"{spacer}sequence_indices:  {self.sequence_indices(at_frame=at_frame)}\n"

        print(outStr)


def run_sequence_path_tests(at_frame=None):

    print("\nrun_sequence_path_tests:")

    filenames = []
    filenames.append("c:\\root\\seq\\singleImage.jpg")
    filenames.append("c:\\root\\seq\\seqNoExt.###")
    filenames.append("c:\\root\\seq\\seqWithUnderscore_###.jpg")
    filenames.append("c:\\root\\seq\\seqWitDot.###.jpg")
    filenames.append("c:\\root\\seq")
    filenames.append("c:\\root\\seq\\")

    for f in filenames:
        print(f"File path: {f}")
        myPath = SequencePath(f)
        myPath.print(at_frame=at_frame, spacer="   ")


# display test paths for debug and unit tests
# run_sequence_path_tests(at_frame=25)


# """ Find the name template for the specified images sequence in order to create it
#    """
#    import re
#    from pathlib import Path

#    seq = None
#    p = Path(images_path)
#    folder, name = p.parent, str(p.name)

#    mov_name = ""
#    # Find frame padding. Either using # formating or printf formating
#    file_re = ""
#    padding_match = re.match(".*?(#+).*", name)
#    if not padding_match:
#        padding_match = re.match(".*?%(\d\d)d.*", name)
#        if padding_match:
#            padding_length = int(padding_match[1])
#            file_re = re.compile(
#                r"^{1}({0}){2}$".format(
#                    "\d" * padding_length, name[: padding_match.start(1) - 1], name[padding_match.end(1) + 1 :]
#                )
#            )
#            mov_name = (
#                str(p.stem)[: padding_match.start(1) - 1] + str(p.stem)[padding_match.end(1) + 1 :]
#            )  # Removes the % and d which are not captured in the re.
#    else:
#        padding_length = len(padding_match[1])
#        file_re = re.compile(
#            r"^{1}({0}){2}$".format(
#                "\d" * padding_length, name[: padding_match.start(1)], name[padding_match.end(1) :]
#            )
#        )
#        mov_name = str(p.stem)[: padding_match.start(1)] + str(p.stem)[padding_match.end(1) :]

#    if padding_match:
#        # scene.render.filepath = str(folder.joinpath(mov_name))

#        frames = dict()
#        max_frame = 0
#        min_frame = 999999999
#        for f in sorted(list(folder.glob("*"))):
#            _folder, _name = f.parent, f.name
#            re_match = file_re.match(_name)
#            if re_match:
#                frame_nb = int(re_match[1])
#                max_frame = max(max_frame, frame_nb)
#                min_frame = min(min_frame, frame_nb)

#                frames[frame_nb] = f

#        frame_keys = list(frames.keys())  # As of python 3.7 should be in the insertion order.
#        if frames:
#            seq = scene.sequence_editor.sequences.new_image(
#                clipName, str(frames[frame_keys[0]]), channelInd, atFrame
#            )

#            for i in range(min_frame + 1, max_frame + 1):
#                pp = frames.get(i, Path(""))
#                seq.elements.append(pp.name)

#
#


_classes = (SequencePath,)


def register():
    _logger.debug_ext("       - Registering Filenames Package", form="REG")

    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    _logger.debug_ext("       - Unregistering Filenames Package", form="UNREG")

    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
