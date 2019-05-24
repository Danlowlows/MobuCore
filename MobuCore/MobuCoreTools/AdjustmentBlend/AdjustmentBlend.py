'''
Adjustment Blending is a method for adjusting additive layer interpolation between keyframes, so that movement on the layer is shifted to areas where there is already movement on the base layer.

This helps to maintain the existing energy of the base layer motion, and helps to maintain contact points. For more information, see this talk from GDC 2016: https://youtu.be/eeWBlMJHR14?t=518

MobuCoreLibrary functions are required for this script.
____________________________________________________________________

This script was written by Dan Lowe as part of the MobuCore package.  You can reach Dan Lowe on Twitter at https://twitter.com/danlowlows (at time of writing, direct messages are open).

MobuCore is made available under the following license terms:

Copyright (c) 2019 Dan Lowe

This software is provided 'as-is', without any express or implied warranty. In no event will the author be held liable for any damages arising from the use of this software.

Permission is granted to anyone to use this software for any purpose, including commercial applications, and to alter it and redistribute it freely, subject to the following restrictions:

1. The origin of this software must not be misrepresented; you must not claim that you wrote the original software.

2. If you use this software, in source or binary form, an acknowledgment in the product documentation or credits would be appreciated but is not required. Example: "This product uses MobuCore (c) 2019 Dan Lowe."

3. Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.

4. This notice may not be removed or altered from any source distribution.
'''

from pyfbsdk import FBSystem, FBApplication, FBTime, FBMessageBox
from MobuCore.MobuCoreLibrary.MobuCoreLibrary import GetCharacterEffectorsAndExtensions

# Groups pairs of keys from the layer fcurve, between which it will run an independent adjustment blend (allows adjustment blend to work with multiple key poses on the layer).
def GetKeyPairsFromFCurve(keys):
    keyPairsList = []
    for i in range(len(keys)-1):
        startKeyTime = keys[i].Time
        startKeyValue = keys[i].Value
        stopKeyTime = keys[i+1].Time
        stopKeyValue = keys[i+1].Value
        keyPairsList.append([startKeyTime, stopKeyTime, startKeyValue, stopKeyValue])
    return keyPairsList

# Gets the transform nodes for an object.
def GetObjTransformNodes(obj):
    transProp = obj.PropertyList.Find("Lcl Translation")
    rotProp = obj.PropertyList.Find("Lcl Rotation")
    if not transProp:
        transProp.SetAnimated(True)
        transProp = obj.PropertyList.Find("Lcl Translation")
    if not rotProp:
        rotProp.SetAnimated(True)
        rotProp = obj.PropertyList.Find("Lcl Rotation")
    transNodes = transProp.GetAnimationNode().Nodes
    rotNodes = rotProp.GetAnimationNode().Nodes
    nodes = list(transNodes) + list(rotNodes)
    return nodes

# Gets the fcurves for an object from a specified layer.
def GetObjectFCurvesForLayer(obj, layerIndex):
    FBSystem().CurrentTake.SetCurrentLayer(layerIndex)
    try:
        return [node.FCurve for node in GetObjTransformNodes(obj)]
    except:
        return []

# Reads the per frame values from an fcurve (doesn't require keys to be on those frames).
def EvaluateFCurveForKeyPairTimespan(fcurve, startTime, stopTime):
    keyPairSpanValues = []
    current = startTime
    while not current > stopTime:
        keyPairSpanValues.append([current, fcurve.Evaluate(current)])
        current += FBTime(0,0,0,1)
    return keyPairSpanValues

# Finds the percentage of change that occured on the base layer curve, for the key pair.
def GetPercentageOfChangeValues(spanValues):
    changeValues = [0.0]
    for i in range(len(spanValues)-1):
        frameChangeValue = abs(spanValues[i+1][1] - spanValues[i][1])
        changeValues.append(frameChangeValue)
    totalBaseLayerChange = sum(changeValues)
    percentageValues = []
    for i in range(len(changeValues)):
        if totalBaseLayerChange != 0:
            percentageValues.append([spanValues[i][0], (100.0 / totalBaseLayerChange) * changeValues[i]])
    return percentageValues, totalBaseLayerChange

# The main adjustment blend function that does everything else. This is what you'd run if you were just adjustment blending a single object.
def AdjustmentBlendObject(obj):
    take = FBSystem().CurrentTake
    if take.GetLayerCount() > 1:
        poseLayerFCurves = GetObjectFCurvesForLayer(obj, take.GetLayerCount()-1)
        baseLayerFCurves = GetObjectFCurvesForLayer(obj, 0)
        for i in range(len(poseLayerFCurves)):
            poseFCurve = poseLayerFCurves[i]
            keys = poseFCurve.Keys
            if len(keys) > 1:
                keyPairsList = GetKeyPairsFromFCurve(keys)
                for keyPair in keyPairsList:
                    startTime = keyPair[0]
                    stopTime = keyPair[1]
                    startValue = keyPair[2]
                    stopValue = keyPair[3]
                    spanValues = EvaluateFCurveForKeyPairTimespan(baseLayerFCurves[i], startTime, stopTime)
                    percentageValues, totalBaseLayerChange = GetPercentageOfChangeValues(spanValues)
                    totalPoseLayerChange = abs(stopValue - startValue)
                    previousValue = startValue
                    for value in percentageValues:
                        valueDelta = (totalPoseLayerChange / 100.0) * value[1]
                        if stopValue > startValue:
                            currentValue = previousValue + valueDelta
                        else:
                            currentValue = previousValue - valueDelta
                        poseLayerFCurves[i].KeyAdd(value[0], currentValue)
                        previousValue = currentValue

# The main adjustment blending function for running it on an entire character.
def AdjustmentBlendCharacter(character = None):
    if not character:
        character = FBApplication().CurrentCharacter
    if character:
        take = FBSystem().CurrentTake
        if take.GetLayerCount() > 1:
            characterObjs = GetCharacterEffectorsAndExtensions(character)
            for obj in characterObjs:
                if obj:
                    AdjustmentBlendObject(obj)
        else:
            FBMessageBox("Error...", "No additive layer found. Adjustment blending affects interpolation between keys on the the top most additive layer.", "OK")
    else:
        FBMessageBox("Error...", "No additive layer found. Adjustment blending affects interpolation between keys on the top most additive layer.", "OK")
