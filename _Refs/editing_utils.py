# coding: utf-8
# Copyright (c) 2020 Ubisoft Animation Studio
import os
import importlib

import bpy
import opentimelineio as otio

from uas_pipe.flows.lib.utils.defines import CommonDefines, EditDefines
from uas_pipe.flows.previz.blender_flows.blender_utils import get_blender_emon_api
from uas_pipe.misc import naming
from uas_pipe.misc.perforce_utils import get_blender_p4


def append_to_timeline(main_track,input_timeline):

    for track in input_timeline.tracks:
        # print(dir(track))
        # new_track   = otio.schema.Track()
        # new_track.name=track.name
        # master_timeline.tracks.append(new_track)

        for clip in track.each_clip():
            print('\t\t',clip.media_reference)

            new_clip                    = otio.schema.Clip()
            new_clip.name               = clip.name
            new_clip.media_reference    = clip.media_reference

            new_clip.source_range       = clip.source_range
            new_clip.trimmed_range      = clip.trimmed_range
            new_clip.media_reference.target_url  = new_clip.media_reference.target_url.replace('\\','/')
            main_track.append(new_clip)

def merge_sequences(act_name:str, use_gattaca_order:bool=True)->bool:
    importlib.reload(naming)
    emon_api    = get_blender_emon_api()
    act         = emon_api.Act.get(act_name)
    if act is None:
        print(f'Act not found: {act_name}')
        return False

    act_name    = act.name()

    project_root    = os.getenv(CommonDefines.ENV_PROJECT_ROOT)
    project_name    = os.getenv(CommonDefines.ENV_PROJECT_NAME)
    fps             = os.getenv(CommonDefines.ENV_PROJECT_FRAME_RATE)
    out_xml = naming.Naming.resolve(
        production_root= project_root,
        entity= '',
        project=  project_name,
        name=act_name,
        category= "Act",
        department= "Previz",
        extension= '.xml'
        )

    print(f'Merging sequences for Act: {act.name()} "{out_xml}"')

    sequences   = act.sequences()
    naming_data = {
        "production_root": project_root,
        "entity": '',
        "project":  project_name,
        # "name": self.sequence.name(),
        "category": "Sequence",
        "department": "Previz",
        "extension": '.xml',
        "extras": {"act_name": act.name()}

    }

    blank_media     = os.path.join(project_root,project_name,EditDefines.INVALID_MEDIA_IMAGE).replace('\\','/')
    blank_source_range = otio.opentime.range_from_start_end_time(
        otio.opentime.RationalTime(0, 1.0),
        otio.opentime.RationalTime(EditDefines.INVALID_MEDIA_DURATION+1, 1.0)
    )
    blank_reference = otio.schema.ExternalReference(str(blank_media))
    print(f'blank reference {blank_reference}')

    p4_utils    = get_blender_p4(project_name)
    p4_utils.check_out(out_xml)
    timeline = otio.schema.Timeline()
    timeline.name = act_name
	

    videoTrack = otio.schema.Track()
    videoTrack.name = "Video track"
	videoTrack.kind = "Video"
	timeline.tracks.append(videoTrack)
	
    audioTrack = otio.schema.Track()
    audioTrack.kind = "Audio"
    audioTrack.tracks.append(audioTrack)
	timeline.tracks.append(audioTrack)
    

    ordered_sequences   = []
    if use_gattaca_order:
        tmp_dict = {}
        for seq in sequences:
            order = seq.orderInEdit()
            if order is None:
                continue

            tasks = seq.tasks(name='blocking')
            if len(tasks) != 1:
                continue

            if tasks[0].status().name().lower() == 'cancelled':
                continue

            tmp_dict[order] = seq
        for o in sorted(tmp_dict.keys()):
            ordered_sequences.append(tmp_dict[o])

    else:
        ordered_sequences   = sequences


    for sequence in ordered_sequences:
        print(f'Add {sequence.name()} sequence')
        otio_path    = naming.Naming.resolve(
            **naming_data,
            name    = sequence.name()
        )
        if os.path.exists(otio_path):

            print(f'\tMerging OTIO Path: {otio_path}')
            otio_tl = otio.adapters.read_from_file(otio_path)
            append_to_timeline(videoTrack,otio_tl)
            append_to_timeline(audioTrack,otio_tl)

        else:
            print(f'\tAdding Invalid image')

            new_clip = otio.schema.Clip()
            new_clip.name = sequence.name()
            new_clip.source_range=blank_source_range
            new_clip.media_reference=blank_reference
            # new_clip.media_reference.name=sequence.name()
            new_clip.media_reference.available_range=blank_source_range
            # new_clip.media_reference.target_url  = blank_media
            # newClip.metadata = {"clip_name": shot["name"], "camera_name": shot["camera"].name_full}
            # new_clip.metadata["clip_name"] = sequence.name()
            # newClip.metadata["camera_name"] = shot["camera"].name_full
            videoTrack.append(new_clip)

            # break

    otio.adapters.write_to_file(timeline,out_xml)
    p4_utils.add_files([out_xml])

    return True


# def newSequence(self):
#     if self.sequencesList is None:
#         self.sequencesList = list()
#     newSeq = SequenceOtio(self)
#     self.sequencesList.append(newSeq)
#     return newSeq
#
# def getSequenceNameFromMediaName(self, fileName):
#     seqName = ""
#
#     media_name_splited = fileName.split("_")
#     if 2 <= len(media_name_splited):
#         seqName = media_name_splited[1]
#
#     return seqName
#
# def fillMontageInfoFromOtioFile(self, otioFile, verboseInfo=False):
#     self.initialize(otioFile)
#
#     if self.timeline is None:
#         _logger.error("fillMontageInfoFromOtioFile: self.timeline is None!")
#         return
#
#     def _getParentSeqIndex(seqList, seqName):
#         #    print("\n_getParentSeqIndex: seqName: ", seqName)
#         for i, seq in enumerate(seqList):
#             if seqName in seq.get_name().lower():
#                 #    print(f"    : {seq.name}, i: {i}")
#                 return i
#
#         return -1
#
#     tracks = self.timeline.video_tracks()
#     for track in tracks:
#         for clip in track:
#             if isinstance(clip, opentimelineio.schema.Clip):
#                 # print(clip.media_reference)
#                 media_path = Path(utils.file_path_from_url(clip.media_reference.target_url))
#                 # print(f"{media_path}")
#
#                 # get media name
#                 filename = os.path.split(media_path)[1]
#                 media_name = os.path.splitext(filename)[0]
#                 media_name_lower = media_name.lower()
#
#                 # get parent sequence
#                 seq_pattern = "_seq"
#                 if seq_pattern in media_name_lower:
#                     #    print(f"media_name: {media_name}")
#
#                     media_name_splited = media_name_lower.split("_")
#                     if 2 <= len(media_name_splited):
#                         parentSeqInd = _getParentSeqIndex(self.sequencesList, media_name_splited[1])
#
#                         # add new seq if not found
#                         newSeq = None
#                         if -1 == parentSeqInd:
#                             newSeq = self.newSequence()
#                             newSeq.set_name(self.getSequenceNameFromMediaName(media_name))
#
#                         else:
#                             newSeq = self.sequencesList[parentSeqInd]
#                         newSeq.newShot(clip)
#