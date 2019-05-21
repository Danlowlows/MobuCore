'''
Functions for automating common tasks relating to Story clips.

MobuCoreLibrary functions are required for this script.
______________________________________________________________

This script was written by Dan Lowe as part of the MobuCore package. You can reach Dan Lowe on Twitter at https://twitter.com/danlowlows (at time of writing, direct messages are open).

MobuCore is made available under the following license terms:

Copyright (c) 2019 Dan Lowe

This software is provided 'as-is', without any express or implied warranty. In no event will the author be held liable for any damages arising from the use of this software.

Permission is granted to anyone to use this software for any purpose, including commercial applications, and to alter it and redistribute it freely, subject to the following restrictions:

1. The origin of this software must not be misrepresented; you must not claim that you wrote the original software.

2. If you use this software, in source or binary form, an acknowledgment in the product documentation or credits would be appreciated but is not required. Example: "This product uses MobuCore (c) 2019 Dan Lowe."

3. Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.

4. This notice may not be removed or altered from any source distribution.
'''

from pyfbsdk import FBStory, FBStoryTrack, FBStoryTrackType, FBTime, FBVector3d, FBSystem, FBCharacterPlotWhere
from MobuCore.MobuCoreLibrary.MobuCoreLibrary import CreateNewTake, PlotToCharacter

# Gets the selected Story clips from the Story Editor.
def GetSelectedStoryClips(includeTrack = False):
    clipsList = []
    tracks = FBStory().RootFolder.Tracks
    for track in tracks:
        trackCharacter = track.Character
        for clip in track.Clips:
            if clip.Selected:
                if includeTrack:
                    clipsList.append([track, clip])
                else:
                    clipsList.append(clip)
    return clipsList

# Copies a Story Clip to a new Story Track.
def CopyClipToNewTrack(clipInfo):
    newTrack = FBStoryTrack(FBStoryTrackType.kFBStoryTrackCharacter)
    newTrack.Character = clipInfo[0].Character
    newClip = clipInfo[1].Clone()
    newTrack.Clips.append(newClip)
    newClip.Start = FBTime(0)
    return newTrack, newClip

# Copies multiple Story Clips to new Story Tracks.
def CopySelectedStoryClipsToTracks():
    clipsList = GetSelectedStoryClips(True)
    if not clipsList == []:
        for clipInfo in clipsList:
            CopyClipToNewTrack(clipInfo)

# Centers and orients the selected Story Clips in the scene. Orientation is based on Clip Rotation, which is derived from the characters scene position at the start and end of the clip.
def CenterSelectedClips():
    clipsList = GetSelectedStoryClips()
    for clip in clipsList:
        clip.Translation = FBVector3d(0,0,0)
        clip.Rotation = FBVector3d(0,-90,0)

# Copies selected Story Clips to takes. Centers clips by default. To note: I mute the Story Editor at the end because it seemed natural to check the newly plotted takes without the Story Editor overriding.
def CopySelectedStoryClipsToTakes(centerClips = True):
    clipsList = GetSelectedStoryClips(True)
    trackMuteStatus = []
    for track in FBStory().RootFolder.Tracks:
        trackMuteStatus.append([track, track.Mute])
        track.Mute = True
    for clipInfo in clipsList:
        newTrack, newClip = CopyClipToNewTrack(clipInfo)
        if centerClips:
            newClip.Translation = FBVector3d(0,0,0)
            newClip.Rotation = FBVector3d(0,-90,0)
        newTake = CreateNewTake(newClip.Name)
        FBSystem().CurrentTake = newTake
        span = newTake.LocalTimeSpan
        span.Set(newClip.Start, newClip.Stop)
        newTake.LocalTimeSpan = span
        character = newTrack.Character
        if not character:
            character = FBApplication().CurrentCharacter
        PlotToCharacter(character)
        newTrack.FBDelete()
    for trackInfo in trackMuteStatus:
        trackInfo[0].Mute = trackInfo[1]
    FBStory().Mute = True