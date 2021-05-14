'''
Core functions library for the MobuCore package. Contains functions for common scripting tasks in Autodesk Motionbuilder.
_________________________________________________________________________________________________________________________

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

from pyfbsdk import FBGroup, FBTangentConstantMode, FBCharacterPoseFlag, FBInterpolation, FBFilterManager, FBTangentMode, FBPropertyListComponent, FBFCurve, FBModelTransformationType, FBPropertyType, FBModel, FBMarkerLook, FBNamespaceAction, FBSystem, FBCharacterPose, FBFindObjectsByName, FBEffectorId, FBPlugModificationFlag, FBMesh, FBCharacterPoseOptions, FBConstraintManager, FBBeginChangeAllModels, FBCamera, FBTime, FBConnect, FBComponentList, FBModelMarker, FBVector3d, FBBodyNodeId, FBCharacterExtension, FBEndChangeAllModels, FBModelSkeleton, FBPlotOptions, FBMesh, FBApplication, FBModelNull, FBComponentList, FBTimeSpan, FBNamespace, FBPlayerControl
import os
import json
import math
from datetime import datetime, timedelta

'''
The following function is for getting all scene components while avoiding the RTTI error that you sometimes get with FBSystem().Scene.Components.
'''

# Gets all scene components and adds them to a list.
def GetSceneComponents():
    sceneComponents = []
    components = FBSystem().Scene.Components
    numberOfComponents = len(components)
    count = 0
    while count != numberOfComponents:
        try:
            for i in range(count,numberOfComponents):
                count += 1
                sceneComponents.append(components[i])
        except:
            pass    
    return sceneComponents 

'''
The following functions are for finding objects from the scene and adding them to variables.
'''

# Default Motionbuilder approach to finding things from the scene.
def FindByNameMobu(name, includeNamespace = True, modelsOnly = True):
    components = FBComponentList()
    FBFindObjectsByName(name, components, includeNamespace, modelsOnly)
    components = list(components)
    if len(components) == 0:
        components = None
    elif len(components) == 1:
        components = components[0]
    return components

# Filter the search results of FindByName (see below)
def SearchFiltering(obj, name, includeNamespace, includeWildcards, foundObjects):
    if includeNamespace:
        if includeWildcards:
            if name in obj.LongName:
                foundObjects.append(obj)
        else:
            if obj.LongName == name:
                foundObjects.append(obj)
    else:
        if includeWildcards:
            if name in obj.Name:
                foundObjects.append(obj)
        else:
            if name == obj.Name:
                foundObjects.append(obj)
    return foundObjects

# Find objects from the scene. Supports wildcards.
def FindByName(name, includeWildcards = False, includeNamespace = True, sceneObjectsOnly = False, returnSingleObj = False):
    foundObjects = []
    comps = GetSceneComponents()
    for obj in comps:
        if not isinstance(obj, FBMesh):
            if sceneObjectsOnly:
                if isinstance(obj, FBModel) or isinstance(obj, FBModelMarker) or isinstance(obj, FBModelSkeleton) or isinstance(obj, FBModelNull) or isinstance(obj, FBCamera):
                    SearchFiltering(obj, name, includeNamespace, includeWildcards, foundObjects)
            else:
                SearchFiltering(obj, name, includeNamespace, includeWildcards, foundObjects)
    if len(foundObjects) == 0:
        pass
        #print 'Search for "%s" found nothing' % (name)
    elif len(foundObjects) == 1 or returnSingleObj:
        foundObjects = foundObjects[0]            
    return foundObjects

# Getting the selected objects from the scene.
def GetSelected(sceneObjectsOnly = True):
    foundObjects = []
    components = GetSceneComponents()
    for obj in components:
        if not isinstance(obj, FBMesh) and obj.Selected:
            if sceneObjectsOnly:
                if isinstance(obj, FBModel) or isinstance(obj, FBModelMarker) or isinstance(obj, FBModelSkeleton) or isinstance(obj, FBModelNull) or isinstance(obj, FBCamera):
                    foundObjects.append(obj)
            else:
                foundObjects.append(obj)
    if len(foundObjects) == 0:
        print 'No objects selected'
    elif len(foundObjects) == 1:
        foundObjects = foundObjects[0]
    return foundObjects

# Find all objects with a specific namespace (excluding other namespaces).
def FindByNamespace(searchNamespace, wildcardSearch = False):
    if not wildcardSearch:
        if searchNamespace[-1] != ":":
            searchNamespace = searchNamespace + ":"
    foundObjects = []
    components = GetSceneComponents()
    for obj in components:
        if not isinstance(obj, FBNamespace):
            objectNamespace = GetNamespaceForObject(obj)
            if objectNamespace:
                if wildcardSearch:
                    if searchNamespace in objectNamespace:
                        foundObjects.append(obj)
                else:
                    if searchNamespace == objectNamespace:
                        foundObjects.append(obj)
    if len(foundObjects) == 1:
        foundObjects = foundObjects[0]
    elif foundObjects == []:
        foundObjects = None
    return foundObjects

'''
The following functions is for adding branches to lists.
'''

# Support function for AddBranchToList.
def AddBranchToListLoop(topModel, listOfObjs = []):
    for childModel in topModel.Children:
        #print topModel.Name + ": " + childModel.Name 
        listOfObjs.append(childModel)
        AddBranchToListLoop(childModel, listOfObjs)
    return listOfObjs

# Adds all children of a given object to a list.
def AddBranchToList(topModel, includeTopModel = True):
    listOfObjs = []
    listOfObjs = AddBranchToListLoop(topModel, listOfObjs)
    if includeTopModel:
        listOfObjs.append(topModel)
    return listOfObjs

'''
The following functions are for finding the top model in a hierarchy from an object in the hierarchy.
'''

# Finds the top object in a hierarchy when given an object lower down in the hierarchy.
def FindTopObject(hierarchyObj):
    count = 0
    if not hierarchyObj.Parent:
        topObj = hierarchyObj
    else:
        topObj = None
        parent = hierarchyObj
        while parent != None and count < 100:
            parent = parent.Parent
            if parent != None:
                topObj = parent
            count += 1
    return topObj   

'''
The following functions are for getting lists of files.
'''

# Gets a file list for a folder.
def GetFileList(dataPath):
    files = [f for f in os.listdir(dataPath) if os.path.isfile(os.path.join(dataPath, f))]
    return files

# Gets full file paths for a folder, including sub-directories.
def GetFilePaths(dataPath):
    dirs = []
    for x in os.walk(dataPath):
        path = str(x[0])
        pathTemp = path[:-3]
        if not pathTemp.endswith("."):
            dirs.append(path)
    fileList = []
    for folderPath in dirs:
        currentFolderFiles = GetFileList(folderPath)
        for f in currentFolderFiles:
            fileList.append(folderPath + "\\" + f)
    return fileList

'''
The following functions are meant to force Motionbuilder to update. Sometimes when executing a script, Motionbuilder doesn't register that a previous change happened because that change was running on a different thread. Running these functions can sometimes help to force Motionbuilder to register the change.
'''

# Shifts the timeslider from start to end, then back to the current frame. Moving the timeline can help to register some scene changes.
def JiggleTimeline():
    currentTime = FBPlayerControl().GetEditCurrentTime()
    FBPlayerControl().GotoStart()
    FBSystem().Scene.Evaluate()
    FBPlayerControl().GotoEnd()
    FBSystem().Scene.Evaluate()
    FBPlayerControl().Goto(currentTime)
    FBSystem().Scene.Evaluate()

'''
The following functions are for dealing with folders and filepaths.
'''

# Looks to see if a given folder path exists, and if not, creates a new folder there.
def CreateFolder(folderPath):
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)

# Gets the folder from a full file path.
def GetFolderFromPath(path):
    pathParts = path.split("\\")
    folderPath = "\\".join(pathParts[:-1]) + "\\"
    return folderPath

# Gets the file name from a full file path.
def GetFilenameFromFilePath(path):
    pathParts = path.split("\\")
    return pathParts[-1]

# Removes the file extention from a file name or path.
def RemoveFileExtensionFromString(string):
    pathParts = string.split(".")
    if len(pathParts) > 2:
        string = ".".join(pathParts[:-1])
    else:
        string = pathParts[0]
    return string

# The following function is for getting the Motionbuilder 'MB' folder in the user directory.
def GetMBDirectory():
    return os.path.expanduser('~') + "\\Documents\\MB\\"

'''
When you write tools, often you want the tools to remember the last path that the user selected. The following functions are for saving and loading those file paths. 
'''

# Saves metadata to a json file in the default Motionbuilder Documents\MB directory.
def SaveToolPath(toolName, pathToSave):
    mbDir = GetMBDirectory()
    SaveListToJson(mbDir + "ToolSavedPaths\\" + toolName + ".json", pathToSave)

# Loads metadata from the json file.
def LoadToolPath(toolName):
    try:
        mbDir = GetMBDirectory()
        path = LoadListFromJson(mbDir + "ToolSavedPaths\\" + toolName + ".json")
    except:
        path = None
    return path

'''
These functions are for loading and saving lists to a json file.
'''

# Support functions for saving and loading json files.
def LoadByteifiedJson(jsonText):
    return _byteify(
        json.load(jsonText, object_hook = _byteify),
        ignoreDicts = True
    )

def _byteify(data, ignoreDicts = False):
    if isinstance(data, unicode):
        return data.encode('utf-8')
    if isinstance(data, list):
        return [ _byteify(item, ignoreDicts = True) for item in data ]
    if isinstance(data, dict) and not ignoreDicts:
        return {
            _byteify(key, ignoreDicts = True): _byteify(value, ignoreDicts = True)
            for key, value in data.iteritems()
        }
    return data

# Saves a list to a json file.
def SaveListToJson(listPath, myList):
    folderPath = GetFolderFromPath(listPath)
    CreateFolder(folderPath)
    with open(listPath, "wb") as saveFile:
        json.dump(myList, saveFile)

# Loads a list from a json file.
def LoadListFromJson(listPath):
    with open(listPath, "rb") as loadedFile:
        newList = LoadByteifiedJson(loadedFile)
    return newList


'''
The following functions are for getting the current control rig models.
'''

# Gets the control rig for a given character.
def GetControlRigForCharacter(character = None):
    if not character:
        character = FBApplication().CurrentCharacter
    if character:
        ctrlRig = character.PropertyList.Find("ControlSet")
        if len(ctrlRig) != 0:
            ctrlRig = ctrlRig[0]
        else:
            ctrlRig = None
        if ctrlRig:
            return ctrlRig

# Gets the FK effectors for a given character.
def GetControlRigFKEffectors(character = None):
    if not character:
        character = FBApplication().CurrentCharacter
    fkEffectors = []
    if character:
        for nodeId in FBBodyNodeId.values.itervalues():
            if nodeId not in [FBBodyNodeId.kFBInvalidNodeId, FBBodyNodeId.kFBLastNodeId]:
                effector = character.GetCtrlRigModel(nodeId)
                if effector:
                    fkEffectors.append(effector)
        if fkEffectors == []:
            fkEffectors = None
    return fkEffectors

# Gets the IK effectors for a given character.                    
def GetControlRigIKEffectors(character = None):
    if not character:
        character = FBApplication().CurrentCharacter
    ikEffectors = []
    if character:
        ctrlRig = GetControlRigForCharacter(character)
        if ctrlRig:
            for nodeId in FBEffectorId.values.itervalues():
                if nodeId not in [FBEffectorId.kFBInvalidEffectorId, FBEffectorId.kFBLastEffectorId]:
                    effector = ctrlRig.GetIKEffectorModel(nodeId, 0)
                    if effector:
                        ikEffectors.append(effector)
            if ikEffectors == []:
                ikEffectors = None
    return ikEffectors

# Gets both the FK and IK effectors for a given character.
def GetControlRigEffectors(character = None):
    if not character:
        character = FBApplication().CurrentCharacter
    if character:
        controlRigEffectors = GetControlRigFKEffectors(character) + GetControlRigIKEffectors(character)
        return controlRigEffectors

# Gets a control rig effector by name.
def GetEffectorByName(effectorName, character = None):
    effectors = GetControlRigEffectors(character)
    effectorToReturn = None
    for effector in effectors:
        if effector.Name == effectorName:
            effectorToReturn = effector
    return effectorToReturn

'''
The following function is for merging/baking down layers.
'''

# Deletes all layers (not uncluding base layer).
def DeleteNonBaseLayers():
    layers = GetLayers()
    for layer in layers:
        if layer.Name != "BaseAnimation":
            layer.FBDelete()

# Deletes all layers (not uncluding base layer), for takes list.
def DeleteNonBaseLayersForTakes(takesList):
    for take in takesList:
        FBSystem().CurrentTake = take
        DeleteNonBaseLayers()

# Bakes down layers.
def BakeDownLayers(objsToBake, layerNameToRemove = None):
    if not isinstance(objsToBake, list):
        objsToBake = [objsToBake]
    take = FBSystem().CurrentTake
    take.SetCurrentLayer(0)
    FastPlotList(objsToBake)
    layers = GetLayers()
    if not layerNameToRemove:
        for layer in layers:
            if layer.Name != "BaseAnimation":
                layer.FBDelete()
    else:
        for layer in layers:
            if layer.Name == layerNameToRemove:
                layer.FBDelete()

'''
The following function is for adding a take to a story track (Warning: This will bake down layers before adding to the track).
'''

# Adds the current take to the Story Editor on a new track.
def AddTakeToStoryTrack():
    layers = GetLayers()
    if len(layers) > 1:
        BakeDownLayers(GetControlRigEffectors())
    track = FBStoryTrack(FBStoryTrackType.kFBStoryTrackCharacter)
    track.Details.append(FBApplication().CurrentCharacter)
    track.CopyTakeIntoTrack(FBSystem().CurrentTake.LocalTimeSpan, FBSystem().CurrentTake)
    return track

'''
The following function gets the closest value from a list of values. Commonly used for finding angle coverage, which is the default value list.
'''

# When given a target value and a list of values, will find the closest value in the list to the target value.
def GetClosestValue(value, valueList = None):
    if not valueList:
        valueList = [0, -45, 45, -90, 90, -135, 135, -180, 180]
    return min(valueList, key=lambda x:abs(x-value))

'''
The following functions are for getting the speed of an object.
'''

# Gets the translation values for an object for a given frame, from an objects curves.
def GetTranslationValueFromCurves(obj, frame):
    transFound = False
    animNode = obj.PropertyList.Find("Lcl Translation").GetAnimationNode()
    if animNode:
        nodes = animNode.Nodes
        keyValues = {}
        if len(nodes) == 3:
            for i in range(len(nodes)):
                fcurve = nodes[i].FCurve
                for key in fcurve.Keys:
                    if key.Time.GetFrame() == frame:
                        keyValues[i] = key.Value
            if len(keyValues) == 3:
                transFound = True
                return FBVector3d(keyValues[0], keyValues[1], keyValues[2])
    if not transFound:
        FBPlayerControl().Goto(FBTime(0,0,0,frame))
        return FBVector3d(obj.Translation[0], obj.Translation[1], obj.Translation[2])

# Gets the speed of an object between a given frame range (assumes movement in a straight line).
def GetSpeed(obj, frameRangeStart = None, frameRangeEnd = None):
    speed = None
    if not frameRangeStart or not frameRangeEnd:
        startEndTimes = GetStartAndEndTimes()
    if not frameRangeStart:
        frameRangeStart = startEndTimes[0]
    if not frameRangeEnd:
        frameRangeEnd = startEndTimes[1]
    numberOfFrames = frameRangeEnd - frameRangeStart
    startTrans = GetTranslationValueFromCurves(obj, frameRangeStart)
    endTrans = GetTranslationValueFromCurves(obj, frameRangeEnd)
    distance = GetDistance(startTrans, endTrans)
    speed = ((distance / numberOfFrames) * 30.0) / 100.0
    if speed != None:
        return speed, startTrans, endTrans, distance
    else:
        return None
        print "Speed not found for %s" % (obj.LongName)

'''
The following function is for clearing the animation on an object.
'''

# Clears all animation on a given object.
def ClearAnimation(obj):
    for prop in ["Lcl Translation", "Lcl Rotation", "Lcl Scaling"]:
        animNode = obj.PropertyList.Find(prop).SetAnimated(False)
        animNode = obj.PropertyList.Find(prop).SetAnimated(True)

'''
The following are functions for getting character extension objects for a given character.
'''

# Gets all referened objects for a given character extension.
def GetObjectsFromExtension(ext):
    extObjList = []
    for i in range(ext.GetSrcCount()):
        extObjList.append(ext.GetSrc(i))
    if extObjList == []:
        extObjList = None
    return extObjList

# Gets all referenced character extension objects for a given character.
def GetCharacterExtensionObjects(character = None):
    if not character:
        character = FBApplication().CurrentCharacter
    if character:
        characterExtentionObjects = []
        for ext in FBSystem().Scene.CharacterExtensions:
            attachedChar = ext.PropertyList.Find("AttachedCharacter")
            if len(attachedChar) > 0:
                if attachedChar[0] == character:
                    extObjList = GetObjectsFromExtension(ext)
                    characterExtentionObjects = characterExtentionObjects + extObjList
        if characterExtentionObjects == []:
            characterExtentionObjects = None
        else:
            characterExtentionObjects = list(dict.fromkeys(characterExtentionObjects))
        return characterExtentionObjects

'''
The following function is for getting the character models including extensions.
'''

# Get all character effectors and extensions.
def GetCharacterEffectorsAndExtensions(character = None):
    if not character:
        character = FBApplication().CurrentCharacter
    if character:
        effectors = GetControlRigEffectors(character)
        extensions = GetCharacterExtensionObjects(character)
        if not isinstance(effectors, list):
            effectors = [effectors]
        if not isinstance(extensions, list):
            extensions = [extensions]
        return effectors + extensions
        
'''
The following functions are for dealing with selection.
'''                    

# Selects every object in a list.
def SelectList(objList):
    if not isinstance(objList, list):
        objList = [objList]
    FBBeginChangeAllModels()
    for obj in objList:
        try:
            obj.Selected = True
        except:
            pass
    FBEndChangeAllModels()

# Deselects everything.
def DeselectAll():
    FBBeginChangeAllModels()
    components = GetSceneComponents()
    for obj in components:
        try:
            obj.Selected = False
        except:
            pass
    FBEndChangeAllModels()

'''
The following functions are for plotting things.
'''

# Plot options used by the other plotting functions.
def PlotOptions(allTakes = False):
    options = FBPlotOptions()
    options.PlotAllTakes = allTakes
    options.PlotOnFrame = True
    options.PlotPeriod = FBTime(0,0,0,1)  
    options.PlotTranslationOnRootOnly = False
    options.PreciseTimeDiscontinuities = True
    options.UseConstantKeyReducer = False
    options.PlotLockedProperties = True
    return options

# Plots all objects in a list.
def FastPlotList(objectsToPlot, allTakes = False):
    if isinstance(objectsToPlot, list):
        if len(objectsToPlot) > 0:
            #objList = GetSelected()
            DeselectAll()
            take = FBSystem().CurrentTake
            for obj in objectsToPlot:
                try:
                    obj.Translation.SetAnimated(True)
                    obj.Rotation.SetAnimated(True)
                except:
                    pass
            JiggleTimeline()
            try: # Added to support Mobu 2016 and earlier which didn't have plot options as an argument for this.
                take.PlotTakeOnObjects(PlotOptions(allTakes), objectsToPlot)
            except:
                print "Regular plot method failed, switching to Motionbuilder 2016 plot method."
                take.PlotTakeOnObjects(FBTime(0,0,0,1),objectsToPlot)
            #SelectList(objList)
        else:
            print("Plot failed: List of objects to plot is empty.")
    else:
        print("Plot failed: List of objects not found. Fast Plot List needs to be provided with a list of objects to plot.")

# Plots all selected objects.
def FastPlotSelected(allTakes = False):
    objList = GetSelected()
    if objList:
        if not isinstance(objList, list):
            objList = [objList]
        FastPlotList(objList, allTakes)

# Plots all objects in a list, only on takes that are selected.
def FastPlotListSelectedTakes(objectsToPlot):
    selectedTakes = []
    for take in FBSystem().Scene.Takes:
        if take.Selected:
            selectedTakes.append(take)
    for take in selectedTakes:
        FBSystem().CurrentTake = take
        FastPlotList(objectsToPlot)

# Plots a given character, or if no character is given, the current character.
def PlotToCharacter(character = None):
    if not character:
        character = FBApplication().CurrentCharacter
    if character:
        characterModels = GetCharacterEffectorsAndExtensions(character)
        FastPlotList(characterModels)

'''
The following function is for organizing lists
'''

# Removes duplicates from a list.
def RemoveListDuplicates(listData):
    listData = list(dict.fromkeys(listData))
    return listData

# Sorts a list alphabetically.    
def SortListAlphabetically(listData):
    listData.sort(key = str.lower)
    return listData

# Removes duplicates from a list and sorts the list.
def RemoveListDuplicatesAndSort(listData):
    listData = RemoveListDuplicates(listData)
    listData = SortListAlphabetically(listData)
    return listData

'''
The following functions are for dealing with poses.
'''

# Creates a new pose in Pose Controls from the current character pose.
def CreateNewPose(name = None, character = None):
    if not character:
        character = FBApplication().CurrentCharacter
    if character:
        if not name:
            name = "New Pose 1"
        pose = FBCharacterPose(name)
        pose.CopyPose(character)

# Searches for a pose in Pose Controls with a specific name and returns that pose (uses wildcard search by default).
def GetPoseByName(name, wildcardSearch = True):
    poseList = []
    for pose in FBSystem().Scene.CharacterPoses:
        if wildcardSearch:
            if name in pose.Name:
                poseList.append(pose)
        else:
            if name == pose.Name:
                poseList.append(pose)
    finalPose = None
    if len(poseList) == 1:
        finalPose = poseList[0]
    elif len(poseList) > 1:
        for pose in poseList:
            if pose.Name == name:
                finalPose = pose
        if not finalPose:
            finalPose = poseList[0]
    return finalPose

# Default pose options used for pasting poses (see below).
def PoseOptions(pivot = None, match = True):
    poseOptions = FBCharacterPoseOptions()
    if pivot:
        poseOptions.mModelToMatch = pivot
    poseOptions.SetFlag(FBCharacterPoseFlag.kFBCharacterPoseMatchTX, match)
    poseOptions.SetFlag(FBCharacterPoseFlag.kFBCharacterPoseMatchTY, match)
    poseOptions.SetFlag(FBCharacterPoseFlag.kFBCharacterPoseMatchTZ, match)
    poseOptions.SetFlag(FBCharacterPoseFlag.kFBCharacterPoseMatchR, match)
    poseOptions.SetFlag(FBCharacterPoseFlag.kFBCharacterPoseGravity, True)
    return poseOptions

# Pastes a pose on the character.   
def PastePose(pose, character = None, pivot = None, match = True):
    if not character:
        character = FBApplication().CurrentCharacter
    if character:
        poseOptions = PoseOptions(pivot, match)
        FBBeginChangeAllModels()
        pose.PastePose(character, poseOptions)
        FBEndChangeAllModels()
        FBSystem().Scene.Evaluate()

# Searches for a pose using a given pose name, and then pastes that pose on the character.
def PastePoseByName(poseName, character = None, pivot = None, match = True):
    pose = GetPoseByName(poseName)
    PastePose(pose, character, pivot, match)

'''
The following functions are for dealing with takes.
'''

# Create a new take.
def CreateNewTake(takeName):
    take = FBSystem().CurrentTake.CopyTake(takeName)
    take.ClearAllProperties(False)
    take.LocalTimeSpan = FBTimeSpan(FBTime(0), FBTime(0,0,0,150))
    FBPlayerControl().GotoStart()
    return take

# Copy a given take, or the current take if no take is provided.
def CopyTake(take = None):
    if not take:
        take = FBSystem().CurrentTake
    return take.CopyTake(take.Name)

# Search for a take using the take name then copy that take. Can search using wildcards to copy multiple takes, but this is disabled by default.
def CopyTakeByName(name, wildcardSearch = False):
    newTakeList = []
    for take in FBSystem().Scene.Takes:
        if wildcardSearch:
            if name in take.Name:
                newTake = take.CopyTake(take.Name)
                newTakeList.append(newTake)
        else:
            if take.Name == name:
                newTake = take.CopyTake(take.Name)
                newTakeList.append(newTake)
    if len(newTakeList) == 1:
        newTakeList = newTakeList[0]
    elif newTakeList == []:
        newTakeList = None
    return newTakeList

# Delete a given take, or the current take if no take is provided.
def DeleteTake(take = None):
    if not take:
        take = FBSystem().CurrentTake
    take.FBDelete()

# Search for a take using the take name then copy that take. Can search using wildcards to delete multiple takes, but this is disabled by default.
def DeleteTakeByName(name, wildcardSearch = False):
    for take in FBSystem().Scene.Takes:
        if wildcardSearch:
            if name in take.Name:
                take.FBDelete()
        else:
            if take.Name == name:
                take.FBDelete()

# Often when merging rigs, props, objects, etc, a default take is added to the scene that you don't want. This function deletes that default take.
def DeleteDefaultTake():
    if len(FBSystem().Scene.Takes) > 1:
        DeleteTakeByName("Take 001")

'''
The following functions are for creating Nulls and Markers with better default values.
'''

# Creates a null object with good default values.
def CreateNull(name):
    null = FBModelNull(name)
    null.Show = True
    null.Size = 500
    return null

# Creates a marker object with good default values.
def CreateMarker(name):
    marker = FBModelMarker(name)
    marker.Show = True
    marker.Size = 500
    marker.Look = FBMarkerLook.kFBMarkerLookHardCross
    return marker  

'''
The following functions are for dealing with layers.
'''

# Gets a list containing the layers for the current take.
def GetLayers():
    take = FBSystem().CurrentTake
    return [take.GetLayer(i) for i in range(take.GetLayerCount())]

# Creates a new layer.
def CreateNewLayer(layerName = None):
    take = FBSystem().CurrentTake
    oldLayersList = GetLayers()
    take.CreateNewLayer()
    newLayersList = GetLayers()
    for layer in newLayersList:
        if layer not in oldLayersList:
            newLayer = layer
    if layerName:
        newLayer.Name = layerName
    return newLayer

# Deletes a layer. Layer search can include wildcards to delete multiple layers, but this is disabled by default.
def DeleteLayerByName(name, wildcardSearch = False):
    layers = GetLayers()
    for layer in layers:
        if wildcardSearch:
            if name in layer.Name:
                layer.FBDelete()
        else:
            if layer.Name == name:
                layer.FBDelete()

# Deletes the current layer.
def DeleteCurrentLayer():
    take = FBSystem().CurrentTake
    layer = take.GetLayer(take.GetCurrentLayer())
    layer.FBDelete()

# Set the weight of a specified layer. If no layer is specified, set the weight of the current layer.
def SetLayerWeight(weight = 100.0, layerName = None):
    take = FBSystem().CurrentTake
    layer = None
    if layerName:
        layer = take.GetLayerByName(layerName)
    if not layer:
        layer = take.GetLayer(take.GetCurrentLayer())
    if layer:
        if layer.Name != "BaseAnimation":
            layer.Weight = weight

'''
The following functions are for keying objects.
'''

# Keys object translation and rotation at the current time. Option to also key scale, but this is disabled by default.
def KeyObject(obj, includeScale = False):
    obj.PropertyList.Find("Lcl Translation").Key()
    obj.PropertyList.Find("Lcl Rotation").Key()
    if includeScale:
        obj.PropertyList.Find("Lcl Scaling").Key()

# Keys an object on a named layer.
def KeyObjectOnLayer(obj, layerName = None, includeScale = False):
    layers = GetLayers()
    layerAlreadyExists = False
    layerToKey = None
    for layer in layers:
        if layer.Name == layerName:
            layerToKey = layer
    if not layerToKey:
        layerToKey = CreateNewLayer(layerName)
    take = FBSystem().CurrentTake
    take.SetCurrentLayer(layerToKey.GetLayerIndex())
    KeyObject(obj, includeScale)

# Key a curve on a named layer.
def KeyCurveOnLayer(obj, propName, keyTime, keyValue, channelIndex = None, layerName = None):
    layers = GetLayers()
    layerAlreadyExists = False
    layerToKey = None
    for layer in layers:
        if layer.Name == layerName:
            layerToKey = layer
    if not layerToKey:
        layerToKey = CreateNewLayer(layerName)
    take = FBSystem().CurrentTake
    take.SetCurrentLayer(layerToKey.GetLayerIndex())
    prop = obj.PropertyList.Find(propName)
    prop.SetAnimated(True)
    animNode = obj.PropertyList.Find(propName).GetAnimationNode()
    if animNode:
        if channelIndex != None:
            curve = animNode.Nodes[channelIndex].FCurve
        else:
            curve = animNode.FCurve
    if curve:
        curve.KeyAdd(keyTime, keyValue)

# Keys a character at the current time (including extensions).
def KeyCharacter(character = None, layerName = None, includeScale = False):
    if not character:
        character = FBApplication().CurrentCharacter
    if character:
        take = FBSystem().CurrentTake
        if layerName:
            layer = take.GetLayerByName(layerName)
            if layer:
                take.SetCurrentLayer(layer.GetLayerIndex())
        characterModels = GetCharacterEffectorsAndExtensions(character)
        if characterModels:
            for obj in characterModels:
                FBSystem().Scene.Evaluate
                KeyObject(obj, includeScale)
        take.SetCurrentLayer(0)

# Keys a character on a new layer.
def KeyCharacterOnLayer(character = None, layerName = None, includeScale = False):
    layers = GetLayers()
    layerAlreadyExists = False
    for layer in layers:
        if layer.Name == layerName:
            layerAlreadyExists = True
    if layerAlreadyExists:
        KeyCharacter(character, layerName, includeScale)
    else:
        newLayer = CreateNewLayer(layerName)
        KeyCharacter(character, newLayer.Name, includeScale)

# Keys selected objects.
def KeySelected(layerName = None, includeScale = False):
    objs = GetSelected()
    for obj in objs:
        KeyObject(obj, includeScale)

# Paste pose and key on a layer.
def PastePoseAndKeyOnLayer(poseName, character = None, pivot = None, match = True, layerName = None, includeScale = False):
    PastePoseByName(poseName, character, pivot, match)
    KeyCharacterOnLayer(character, layerName, includeScale)
            
'''
The following functions are for dealing with Namespace
'''         

# Get the namespace for an object.
def GetNamespaceForObject(obj):
    try:
        name = obj.Name
        longName = obj.LongName
        if name != longName:
            nameParts = longName.split(":")[:-1]
            namespace = ":".join(nameParts)
            namespace = namespace + ":"
        else:
            namespace = None
    except:
        namespace = None
    return namespace

# Add a namespace to an object.
def AddNamespace(objs, namespaceToAdd):
    if not isinstance(objs, list):
        objs = [objs]
    for obj in objs:
        existingNamespace = GetNamespaceForObject(obj)
        if existingNamespace:
            if existingNamespace.endswith(":"):
                existingNamespace = existingNamespace[:-1]
            ReplaceNamespace(existingNamespace, namespaceToAdd + ":" + existingNamespace, obj)
        else:
            try:
                obj.ProcessObjectNamespace(FBNamespaceAction.kFBConcatNamespace, namespaceToAdd)
            except:
                pass

# Adds a namespace to all selected objects:
def AddNamespaceToSelected(namespaceToAdd):
    objs = GetSelected()
    AddNamespace(objs, namespaceToAdd)

# Replace a namespace in the scene. Replaces on all objects with that namespace.
def ReplaceNamespace(oldNamespace, newNamespace, objList = None):
    if not objList:
        objList = GetSceneComponents()
    if not isinstance(objList, list) and not isinstance(objList, FBPropertyListComponent):
        objList = [objList]
    for obj in objList:
        obj.ProcessObjectNamespace(FBNamespaceAction.kFBReplaceNamespace, oldNamespace, newNamespace)
    objs = FindByNamespace(oldNamespace)
    if not objs:
        DeleteObjectsByNamespace(oldNamespace)

# Removes a namespace from the scene.
def RemoveNamespace(namespace, objList = None):
    ReplaceNamespace(namespace, "", objList)

# Gets a list of namespaces for the scene.
def GetListOfNamespaces():
    namespaces = FBSystem().Scene.Namespaces
      
'''
The following functions are for deleting objects from the scene.
'''  

# Deletes all objects with a specified namespace.
def DeleteObjectsByNamespace(namespace):
    FBSystem().Scene.NamespaceDeleteContent(namespace, FBPlugModificationFlag.kFBPlugAllContent, True)
    for ns in FBSystem().Scene.Namespaces:
        if ns.Name == namespace:
            ns.FBDelete()

# Safely deletes all objects in a list.
def DeleteListOfObjects(objList):
    AddNamespace(objList, "Temp_Namespace_For_Delete")
    DeleteObjectsByNamespace("Temp_Namespace_For_Delete")

# Safely deletes selected objects.
def DeleteSelected():
    objList = GetSelected()
    DeleteListOfObjects(objList)

'''
The following function is for adding objects to character extensions.
'''

# Adds objects to character extensions which are then added to the character.
def AddObjectsToExtension(objList, extension = None, character = None):
    if not character:
        character = FBApplication().CurrentCharacter
    if character:
        newExtension = False
        if not extension:
            extension = FindByName(character.LongName + "_Extension")
        if not extension:
            extension = FBCharacterExtension(character.LongName + "_Extension")
            newExtension = True
        if not isinstance(objList, list) and not isinstance(objList, FBPropertyListComponent):
            objList = [objList]
        for obj in objList:
            FBConnect(obj,extension)
            extension.AddObjectProperties(obj)
            extension.UpdateStancePose()
        if newExtension:
            FBSystem().SuspendMessageBoxes = True
            character.AddCharacterExtension(extension)
            FBSystem().SuspendMessageBoxes = False
    return extension

'''
The following functions are for getting and setting global translation and rotation.
'''

# Gets the global translation of an object.
def GetGlobalTranslation(obj):
    translation = FBVector3d()
    obj.GetVector(translation)
    return translation

# Gets the global rotation of an object.
def GetGlobalRotation(obj):
    rotation = FBVector3d()
    obj.GetVector(rotation, FBModelTransformationType.kModelRotation)
    return rotation

# Sets the global translation of an object.
def SetGlobalTranslation(obj, translation):
    obj.SetVector(FBVector3d(translation[0], translation[1], translation[2]))

# Sets the global rotation of an object.
def SetGlobalRotation(obj, rotation):
    obj.SetVector(FBVector3d(rotation[0], rotation[1], rotation[2]), FBModelTransformationType.kModelRotation)

'''
The following functions are for dealing with groups.
'''

# Creates a group and adds a list of objects to the group.
def CreateGroup(groupName = "Group", itemsToAdd = []):
    group = FBGroup(groupName)
    if len(itemsToAdd) > 0 :
        for item in itemsToAdd:
            group.ConnectSrc(item)
    return group

'''
The following functions are for dealing with constraints.
'''

# Adds an object to a constraint reference using the constraint reference's name.
def SetConstraintReference(constraint, obj, referenceName):
    for i in range(constraint.ReferenceGroupGetCount()):
        if referenceName == constraint.ReferenceGroupGetName(i):
            constraint.ReferenceAdd(i, obj)

# Prints the reference names for a given constraint (not something you'd use directly in scripts but useful debug function for figuring out the reference name for new constraint types).
def PrintConstraintReferenceNames(constraint):
    for i in range(constraint.ReferenceGroupGetCount()):
        print constraint.ReferenceGroupGetName(i)

# A generic function for creating Position, Rotation, and Parent/Child constraints. This isn't as clean as it could be, but there was a lot of duplicate code for these constraint types so I wanted to try and share as much as possible.
def GenericConstraint(constraintType, parent, child, active = True, snap = False, zero = True):
    constraint = FBConstraintManager().TypeCreateConstraint(constraintType)
    if not isinstance(parent, list) and not isinstance(parent, FBPropertyListComponent):
        parent = [parent]
    constraint.Name = constraintType + "_" + child.Name + "_to_" + parent[0].Name
    if constraintType == "Parent/Child":
        SetConstraintReference(constraint, child, "Constrained object (Child)")
    else:
        SetConstraintReference(constraint, child, "Constrained Object")
    for obj in parent:
        if constraintType == "Parent/Child":
            SetConstraintReference(constraint, obj, "Source (Parent)")
        else:
            SetConstraintReference(constraint, obj, "Source")
    if snap:
        constraint.Snap()
    if zero:
        constraint.Lock = False
        if constraintType == "Position" or constraintType == "Parent/Child":
            SetGlobalTranslation(child, GetGlobalTranslation(parent[0]))
        if constraintType == "Rotation" or constraintType == "Parent/Child":
            SetGlobalRotation(child, GetGlobalRotation(parent[0]))
    constraint.Active = active
    constraint.Lock = True
    return constraint

# Triggers the creation of a Parent/Child constraint.
def ParentChildConstrain(parent, child, active = True, snap = False, zero = True):
    constraint = GenericConstraint("Parent/Child", parent, child, active, snap, zero)
    return constraint

# Triggers the creation of a Position constraint.
def PositionConstrain(parent, child, active = True, snap = False, zero = True):
    constraint = GenericConstraint("Position", parent, child, active, snap, zero)
    return constraint

# Triggers the creation of a Rotation constraint.
def RotationConstrain(parent, child, active = True, snap = False, zero = True):
    constraint = GenericConstraint("Rotation", parent, child, active, snap, zero)
    return constraint

# Creates an Aim constraint.
def AimConstrain(constrainedObject, aimAtObject, worldUpObject = None, active = True, snap = False):
    constraint = FBConstraintManager().TypeCreateConstraint("Aim")
    constraint.Name = "Aim_" + constrainedObject.Name + "_to_" + aimAtObject.Name
    SetConstraintReference(constraint, constrainedObject, "Constrained Object")
    SetConstraintReference(constraint, aimAtObject, "Aim At Object")
    if worldUpObject:
        SetConstraintReference(constraint, worldUpObject, "World Up Object")
    if snap:
        constraint.snap()
    else:
        constraint.Active = active
    constraint.Lock = True
    return constraint

'''
The following functions are for dealing with Custom Properties.
'''

# Default reference info for custom property types.
def GetDefaultPropertyInfo(propertyType):
    propertyDict = {}
    propertyDict['Integer'] = ('Integer', FBPropertyType.kFBPT_int, 'Integer', True, True, None)
    propertyDict['Bool'] = ('Bool', FBPropertyType.kFBPT_bool, 'Bool', True, True, None)
    propertyDict['Float'] = ('Float', FBPropertyType.kFBPT_float, 'Float', False, True, None) # Not animatable
    propertyDict['Double'] = ('Double', FBPropertyType.kFBPT_double, 'Number',True, True, None)
    propertyDict['String'] = ('String', FBPropertyType.kFBPT_charptr, 'String', False, True, None) # Not animatable
    propertyDict['Enum'] = ('Enum', FBPropertyType.kFBPT_enum, 'Enum', True, True, None)
    propertyDict['Time'] = ('Time', FBPropertyType.kFBPT_Time, 'Time', True, True, None)
    propertyDict['TimeCode'] = ('TimeCode', FBPropertyType.kFBPT_TimeCode, 'TimeCode', True, True, None)
    propertyDict['Obj'] = ('Obj',  FBPropertyType.kFBPT_object, 'Object', False, True, None ) # Not animatable
    propertyDict['Stringlist'] = ('Stringlist', FBPropertyType.kFBPT_stringlist, 'StringList', False, True, None) # Not animatable
    propertyDict['Vector4D'] = ('Vector4D', FBPropertyType.kFBPT_Vector4D, 'Vector', True, True, None)
    propertyDict['Vector3D'] = ('Vector3D', FBPropertyType.kFBPT_Vector3D, 'Vector', True, True, None)
    propertyDict['Vector2D'] = ('Vector2D', FBPropertyType.kFBPT_Vector2D, 'Vector', True, True, None)
    propertyDict['Colour'] = ('Colour', FBPropertyType.kFBPT_ColorRGB, 'Color', True, True, None)
    propertyDict['ColourAndAlpha'] = ('ColourAndAlpha', FBPropertyType.kFBPT_ColorRGBA, 'ColorAndAlpha', True, True, None)
    propertyDict['Action'] = ('Action', FBPropertyType.kFBPT_Action, 'Action', True, True, None)
    propertyDict['TimeSpan'] = ('TimeSpan', FBPropertyType.kFBPT_TimeSpan, 'Time', False, True, None) # Not animatable
    return propertyDict[propertyType]

# Creates a custom property.             
def CreateCustomProperty(obj, propertyType, name = None, defaultValue = None):
    prop = None
    if name:
        prop = obj.PropertyList.Find(name)
    if not prop:
        propertyInfo = GetDefaultPropertyInfo(propertyType)       
        prop = obj.PropertyCreate( propertyInfo[0], propertyInfo[1], propertyInfo[2], propertyInfo[3], propertyInfo[4], propertyInfo[5] )
        if prop:
            if name:
                prop.Name = name
            if defaultValue:
                prop.Data = defaultValue
    return prop            

'''
The following functions are for setting fcurve key interplation.
'''

# Sets the interpolation type for a given curve.
def SetCurveInterpolation(fcurve, interpolationMode):
    for key in fcurve.Keys:
        if interpolationMode == "Stepped":
            key.Interpolation = FBInterpolation.kFBInterpolationConstant
            key.TangentConstantMode = FBTangentConstantMode.kFBTangentConstantModeNormal
        elif interpolationMode == "Linear":
            key.Interpolation = FBInterpolation.kFBInterpolationLinear
        elif interpolationMode == "Flat":
            key.Interpolation = FBInterpolation.kFBInterpolationCubic
            key.TangentMode = FBTangentMode.kFBTangentModeAuto
            key.TangentMode = FBTangentMode.kFBTangentModeTCB
            key.Tension = 1
            key.Continuity = 0 
            key.Bias = 0
        elif interpolationMode == "Smooth":
            key.Interpolation = FBInterpolation.kFBInterpolationCubic
            key.TangentMode = FBTangentMode.kFBTangentModeAuto
            key.TangentMode = FBTangentMode.kFBTangentModeTCB
            key.Tension = 0
            key.Continuity = 0 
            key.Bias = 0.5

# Sets the interpolation type for all transform fcurves on a given object.
def SetObjInterpolation(obj, interpolationMode):
    for transform in [obj.Translation, obj.Rotation, obj.Scaling]:
        node = transform.GetAnimationNode()
        if not node:
            transform.SetAnimated(True)
            node = transform.GetAnimationNode()
        if node:
            nodes = node.Nodes
            for transformAxis in nodes:
                fcurve = transformAxis.FCurve
                SetCurveInterpolation(fcurve, interpolationMode)

'''
The following function is for getting start and end times from the timeline.
'''

# Gets start and end frame values for the current take.
def GetStartAndEndTimes(take = None):
    if not take:
        take = FBSystem().CurrentTake
    span = take.LocalTimeSpan
    start = span.GetStart().GetFrame()
    stop = span.GetStop().GetFrame()
    timeInfo = [start, stop]
    return timeInfo

# Sets the timeline span so that it's using full frames (as in no sub-frames).
def SetTimespanToFullFrames():
    take = FBSystem().CurrentTake
    span = take.LocalTimeSpan
    start = span.GetStart().GetFrame()
    stop = span.GetStop().GetFrame()
    span.Set(FBTime(0,0,0,start), FBTime(0,0,0,stop))
    take.LocalTimeSpan = span

# Sets the timespan to given start and end frames.
def SetTimespan(start, stop):
    take = FBSystem().CurrentTake
    span = take.LocalTimeSpan
    span.Set(FBTime(0,0,0,start), FBTime(0,0,0,stop))
    take.LocalTimeSpan = span

'''
The following functions are for applying filters to curves.
'''

def FilterCurve(fcurve, filterType = "Butterworth", cutOffFrequency = 7.0):
    filterObj = FBFilterManager().CreateFilter(filterType)
    if filterType == "Butterworth":
        filterObj.PropertyList.Find("Cut-off Frequency (Hz)").Data = cutOffFrequency
    filterObj.Apply(fcurve)

'''
The following is a function for aligning two objects.
'''

# A function for aligning two objects.
def AlignObject(obj, objToAlignTo):
    SetGlobalTranslation(obj, GetGlobalTranslation(objToAlignTo))
    SetGlobalRotation(obj, GetGlobalRotation(objToAlignTo))

'''
The following functions are for creating and working with relation constraints.
'''

# Creates a new relation constraint.
def RelationConstrain(name = None):
    constraint = FBConstraintManager().TypeCreateConstraint("Relation")
    if name:
        constraint.Name = name
    return constraint

# Adds a new box to a relation constraint.
def AddBoxToRelationConstraint(constraint, boxCategory, boxType, boxXPos = 0, boxYPos = 0):
    box = constraint.CreateFunctionBox(boxCategory, boxType)
    if box:
        constraint.SetBoxPosition(box, boxXPos, boxYPos)
        return box
    else:
        print 'Box type "%s" not found' % (boxType)

# Adds an object to a relations constraint as either a source or a target object.
def AddObjToRelation(constraint, obj, objIsSource = True, boxXPos = 0, boxYPos = 0):
    if objIsSource:
        box = constraint.SetAsSource(obj)
    else:
        box = constraint.ConstrainObject(obj)
    constraint.SetBoxPosition(box, boxXPos, boxYPos) 
    return box

# Checks to find alternate box names if box name doesn't exist. This is here cause Mobu tends to add numbers to box names if a box was created before with that name, not based on if there's another box in the scene with that name.
def CheckBoxName(constraint, name):
    foundBox = False
    finalBoxName = None
    for box in constraint.Boxes:
        if box.Name == name:
            finalBoxName = box.Name
            foundBox = True
    if not foundBox:
        possibleNames = []
        for box in constraint.Boxes:
            if box.Name.startswith(name):
                possibleNames.append(box.Name)
        if len(possibleNames) == 1:
            finalBoxName = possibleNames[0]
    return finalBoxName 

# Gets a box from a relation constraint by searching for the box's name.
def GetBoxFromRelationByName(constraint, boxName):
    boxName = CheckBoxName(constraint, boxName)
    for box in constraint.Boxes:
        if box.Name == boxName:
            return box

# Repositions a relations box.
def RepositionBox(constraint, boxName, boxXPos, boxYPos):
    box = GetBoxFromRelationByName(constraint, boxName)
    constraint.SetBoxPosition(box, boxXPos, boxYPos)   

# Gets a box node by name. When the "inputNode" variable is True this searches Input nodes, when it's False it searches Output nodes.
def GetBoxNodeByName(box, nodeName, inputNode = True):
    foundNode = None
    if inputNode:
        nodes = box.AnimationNodeInGet().Nodes
    else:
        nodes = box.AnimationNodeOutGet().Nodes
    for node in nodes:
        if node.Name == nodeName:
            foundNode = node
            break
    return foundNode 

# Sets a value for a relations input box. To note: This works, but doesn't immediately refresh the UI. If you select something else in the Navigator then go back, you'll see the UI now shows the input value.
def SetBoxInputValue(box, inputNodeName, value):
    node = GetBoxNodeByName(box, inputNodeName)
    node.WriteData([value])

# Sets a box input value, as above, but allows you to search for the box by name.
def SetBoxInputValueByName(constraint, boxName, inputNodeName, value):
    box = GetBoxFromRelationByName(constraint, boxName)
    SetBoxInputValue(box, inputNodeName, value)
    
# Connects two box nodes.
def ConnectBoxNodes(outputBox, inputBox, outputNodeName, inputNodeName):
    outputNode = GetBoxNodeByName(outputBox, outputNodeName, False)
    inputNode = GetBoxNodeByName(inputBox, inputNodeName)
    if outputNode and inputNode:
        FBConnect(outputNode, inputNode)

# Connects two box nodes as above, but allows you to search for the boxes by name.
def ConnectBoxNodesByName(constraint, outputBoxName, inputBoxName, outputNodeName, inputNodeName):
    outputBox = GetBoxFromRelationByName(constraint, outputBoxName) 
    inputBox = GetBoxFromRelationByName(constraint, inputBoxName)
    ConnectBoxNodes(outputBox, inputBox, outputNodeName, inputNodeName)

'''
The following functions are for basic math operations.
'''

# Finds the distance between two positions.
def GetDistance(pos1, pos2):
    x1 = pos1[0]
    y1 = pos1[1]
    z1 = pos1[2]
    x2 = pos2[0]
    y2 = pos2[1]
    z2 = pos2[2]
    distance = math.sqrt( pow((x1-x2),2) + pow((y1-y2),2) + pow((z1-z2),2))
    return distance

# Get dot product
def DotProduct(v1, v2):
    return sum((a*b) for a, b in zip(v1, v2))

# Get length
def Length(v):
    return math.sqrt(DotProduct(v, v))

# Get angle between two vectors.
def GetAngleBetweenVectors(v1, v2):
    try:
        radian = math.acos(DotProduct(v1, v2) / (Length(v1) * Length(v2)))
        angle = radian*(180/math.pi)
    except:
        angle = 0
    return angle

# Gets the angle value from the world origin to a given object.
def GetWorldSpaceAngleToObj(obj):
    angle = GetAngleBetweenVectors([0,0,100000], obj.Translation)
    if obj.Translation[0] < 0:
        angle = angle * -1
    return angle

'''
The following functions are for profiling scripts. They allow you to create a time log and add time stamps to that timelog. You can then print a report of all timestamps with their time deltas.
'''

# Creates a timestamp and adds it to a list of timestamps. You would add this throughout your script, and keep feeding the returned list into the next timestamp function call.
def CreateTimeStamp(name, timeStampList = []):
    now = datetime.now()
    if len(timeStampList) < 1:
        delta = now - now
    else:
        delta = now - timeStampList[-1][1]
    timeStampList.append([name, now, delta])
    return timeStampList

# Support function for PrintTimestamp list.
def GetTitleSpace(title, titleWidth = 50):
    spaceNum = titleWidth - len(title)
    spaceList = []
    for i in range(spaceNum):
        spaceList.append(" ")
    space = "".join(spaceList)
    return space

# Once your script is done, takes the timestamp list you've been adding to, and prints it.
def PrintTimeStampList(timeStampList):
    totalTime = timeStampList[-1][1] - timeStampList[0][1]
    totalSeconds = totalTime.total_seconds()
    print "\nTime Stamp Log..."
    longestString = 0
    for timeStamp in timeStampList:
        stringLength = len(timeStamp[0])
        if stringLength > longestString:
            longestString = stringLength
    bufferAmount = longestString + 5
    for timeStamp in timeStampList:
        percentage = (100 / totalSeconds) * timeStamp[2].total_seconds()
        print "Name: %s%sTime: %s%sDelta: %s%sPercent: %s" % (timeStamp[0], GetTitleSpace(str(timeStamp[0]), bufferAmount), timeStamp[1].time(), GetTitleSpace(str(timeStamp[1].time()), 20), timeStamp[2], GetTitleSpace(str(timeStamp[2]), 18), percentage)
    print "Total Time: %s" % (totalTime)
    
'''
Function for getting the distance between objects.
'''

# Gets the distance between two given objects.
def GetDistance(pos1, pos2):
    from math import sqrt
    x1 = pos1[0]
    y1 = pos1[1]
    z1 = pos1[2]
    x2 = pos2[0]
    y2 = pos2[1]
    z2 = pos2[2]
    distance = sqrt( pow((x1-x2),2) + pow((y1-y2),2) + pow((z1-z2),2))
    return distance
