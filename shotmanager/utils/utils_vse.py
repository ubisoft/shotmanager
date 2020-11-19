import bpy

###################
# vse
###################


def clearChannel(scene, channelIndex):
    sequencesList = list()
    for seq in scene.sequence_editor.sequences:
        if channelIndex == seq.channel:
            sequencesList.append(seq)
    for seq in sequencesList:
        scene.sequence_editor.sequences.remove(seq)
    bpy.ops.sequencer.refresh_all()


def clearAllChannels(scene):
    for seq in scene.sequence_editor.sequences:
        scene.sequence_editor.sequences.remove(seq)
    bpy.ops.sequencer.refresh_all()


def getChannelClips(scene, channelIndex):
    sequencesList = list()
    for seq in scene.sequence_editor.sequences:
        if channelIndex == seq.channel:
            sequencesList.append(seq)
    return sequencesList


def getNumUsedChannels(scene):
    numChannels = 0
    for i, seq in enumerate(scene.sequence_editor.sequences):
        numChannels = max(seq.channel, numChannels)
    return numChannels


def changeClipsChannel(scene, sourceChannelIndex, targetChannelIndex):
    sourceSequencesList = getChannelClips(scene, sourceChannelIndex)
    targetSequencesList = list()

    if len(sourceSequencesList):
        targetSequencesList = getChannelClips(scene, targetChannelIndex)

        # we need to clear the target channel before doing the switch otherwise some clips may get moved to another channel
        if len(targetSequencesList):
            clearChannel(scene, targetChannelIndex)

        for clip in sourceSequencesList:
            clip.channel = targetChannelIndex

    return targetSequencesList


def swapChannels(scene, channelIndexA, channelIndexB):
    tempChannelInd = 0
    changeClipsChannel(scene, channelIndexA, tempChannelInd)
    changeClipsChannel(scene, channelIndexB, channelIndexA)
    changeClipsChannel(scene, tempChannelInd, channelIndexB)


def muteChannel(scene, channelIndex, mute):
    for i, seq in enumerate(scene.sequence_editor.sequences):
        if channelIndex == seq.channel:
            seq.mute = mute


def setChannelAlpha(scene, channelIndex, alpha):
    """Alpha is in range [0, 1]
    """
    channelClips = getChannelClips(scene, channelIndex)
    for clip in channelClips:
        clip.blend_alpha = alpha

