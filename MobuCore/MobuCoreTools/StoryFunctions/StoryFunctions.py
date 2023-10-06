'''
Functions for automating common tasks relating to Story clips.

MobuCoreLibrary functions are required for this script.
______________________________________________________________

MIT License

Copyright (c) 2023 Dan Lowe

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
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
