'''
MobuCore is a library of functions for common scripting tasks in Autodesk Motionbuilder. It is created by Dan Lowe. You can reach Dan Lowe on Twitter at https://twitter.com/danlowlows (at time of writing, direct messages are open).

MobuCore is made available under the following license terms:

Copyright (c) 2019 Dan Lowe

This software is provided 'as-is', without any express or implied warranty. In no event will the author be held liable for any damages arising from the use of this software.

Permission is granted to anyone to use this software for any purpose, including commercial applications, and to alter it and redistribute it freely, subject to the following restrictions:

1. The origin of this software must not be misrepresented; you must not claim that you wrote the original software.

2. If you use this software, in source or binary form, an acknowledgment in the product documentation or credits would be appreciated but is not required. Example: "This product uses MobuCore (c) 2019 Dan Lowe."

3. Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.

4. This notice may not be removed or altered from any source distribution.
'''

from pyfbsdk import FBPropertyListComponent, FBModelTransformationType, FBModel, FBSystem, FBCharacterPose, FBFindObjectsByName, FBEffectorId, FBPlugModificationFlag, FBMesh, FBCharacterPoseOptions, FBConstraintManager, FBBeginChangeAllModels, FBCamera, FBTime, FBConnect, FBComponentList, FBModelMarker, FBVector3d, FBBodyNodeId, FBCharacterExtension, FBEndChangeAllModels, FBModelSkeleton, FBPlotOptions, FBMesh, FBApplication, FBModelNull, FBComponentList, FBTimeSpan, FBNamespace, FBPlayerControl

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
def FindByName(name, includeWildcards = False, includeNamespace = True, sceneObjectsOnly = False):
    foundObjects = []
    for obj in FBSystem().Scene.Components:
        if not isinstance(obj, FBMesh):
            if sceneObjectsOnly:
                if isinstance(obj, FBModel) or isinstance(obj, FBModelMarker) or isinstance(obj, FBModelSkeleton) or isinstance(obj, FBModelNull) or isinstance(obj, FBCamera):
                    SearchFiltering(obj, name, includeNamespace, includeWildcards, foundObjects)
            else:
                SearchFiltering(obj, name, includeNamespace, includeWildcards, foundObjects)
    if len(foundObjects) == 0:
        print 'Search for "%s" found nothing' % (name)
    elif len(foundObjects) == 1:
        foundObjects = foundObjects[0]
    return foundObjects

# Getting the selected objects from the scene.
def GetSelected(sceneObjectsOnly = True):
    foundObjects = []
    for obj in FBSystem().Scene.Components:
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
def FindByNamespace(namespace):
    if namespace[-1] != ":":
        namespace = namespace + ":"
    foundObjects = []
    for obj in FBSystem().Scene.Components:
        if not isinstance(obj, FBNamespace):
            if obj.LongName.replace(obj.Name,"") == namespace:
                foundObjects.append(obj)
    if len(foundObjects) == 1:
        foundObjects = foundObjects[0]
    elif foundObjects == []:
        foundObjects = None
    return foundObjects

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
    if character:
        fkEffectors = []
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
    if character:
        ctrlRig = GetControlRigForCharacter(character)
        ikEffectors = []
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

'''
The following are functions for getting character extention objects for a given character.
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
    for obj in FBSystem().Scene.Components:
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
    return options

# Plots all objects in a list.
def FastPlotList(objectsToPlot, allTakes = False):
    if isinstance(objectsToPlot, list):
        if len(objectsToPlot) > 0:
            objList = GetSelected()
            DeselectAll()
            take = FBSystem().CurrentTake
            take.PlotTakeOnObjects(PlotOptions(allTakes), objectsToPlot)
            SelectList(objList)
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
    if len(poseList) == 1:
        poseList = poseList[0]
    elif poseList == []:
        poseList = None
    return poseList

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
        pose.PastePose(character, options)
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

# Search for a take using the take name then delete that take. Can search using wildcards to delete multiple takes, but this is disabled by default.
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

# Keys a character at the current time (including extensions).
def KeyCharacter(character = None, layerName = None, includeScale = False):
    if not character:
        character = FBApplication().CurrentCharacter
    if character:
        if layerName:
            take = FBSystem().CurrentTake
            layer = take.GetLayerByName(layerName)
            if layer:
                take.SetCurrentLayer(layer.GetLayerIndex())
        characterModels = GetCharacterEffectorsAndExtensions(character)
        if characterModels:
            for obj in characterModels:
                FBSystem().Scene.Evaluate
                KeyObject(obj, includeScale)

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
def KeySelected(includeScale = False):
    objs = GetSelected()
    for obj in objs:
        KeyObject(obj, includeScale)

# Paste pose and key on a layer.
def PastePoseAndKeyOnLayer(poseName, character = None, pivot = None, match = True, layerName = None, includeScale = False, ):
    PastePoseByName(poseName, character, pivot, match)
    KeyCharacterOnLayer(character, layerName, includeScale)
            
'''
The following functions are for dealing with Namespace
'''         

# Get the namespace for an object.
def GetNamespaceForObject(obj):
    name = obj.Name
    longName = obj.LongName
    if name != longName:
        nameParts = longName.split(":")[:-1]
        namespace = ":".join(nameParts)
        namespace = namespace + ":"
    else:
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
            obj.ProcessObjectNamespace(FBNamespaceAction.kFBConcatNamespace, namespaceToAdd)

# Adds a namespace to all selected objects:
def AddNamespaceToSelected(namespaceToAdd):
    objs = GetSelected()
    AddNamespace(objs, namespaceToAdd)

# Replace a namespace in the scene. Replaces on all objects with that namespace.
def ReplaceNamespace(oldNamespace, newNamespace, objList = None):
    if not objList:
        objList = FBSystem().Scene.Components
    if not isinstance(objList, list) and not isinstance(objList, FBPropertyListComponent):
        objList = [objList]
    for obj in objList:
        obj.ProcessObjectNamespace(FBNamespaceAction.kFBReplaceNamespace, oldNamespace, newNamespace)
    objs = FindByNamespace(oldNamespace)
    if not objs:
        DeleteObjectsByNamespace(oldNamespace)

# Removes a namespace from the scene.
def RemoveNamespace(namespace):
    ReplaceNamespace(namespace, "")
      
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
    if not extension:
        if character:
            extension = FBCharacterExtension(character.LongName + "_Extension")
        else:
            extension = FBCharacterExtension("Character_Extension")
    if not isinstance(objList, list) and not isinstance(objList, FBPropertyListComponent):
        objList = [objList]
    for obj in objList:
        FBConnect(obj,extension)
        extension.AddObjectProperties(obj)
        extension.UpdateStancePose()
    if character:
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
        constraint.snap()
    if zero:
        if constraintType == "Position" or constraintType == "Parent/Child":
            SetGlobalRotation(child, GetGlobalRotation(parent[0]))
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

# Gets a box from a relation constraint by searching for the box's name.
def GetBoxFromRelationByName(constraint, boxName):
    for box in constraint.Boxes:
        if box.Name == boxName:
            return box

# Repositins a relations box.
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
def SetBoxInputValueByName(boxName, inputNodeName, value):
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
