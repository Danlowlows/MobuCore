'''
Menu script for adding MobuCore tools to the Motionbuilder tool bar.

The full MobuCore package is required for this script.
____________________________________________________________________

This script was written by Dan Lowe as part of the MobuCore package.  You can reach Dan Lowe on Twitter at https://twitter.com/danlowlows (at time of writing, direct messages are open).

MobuCore is made available under the following license terms:

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

# Import of all the different functions from different files.
from pyfbsdk import FBMenuManager, FBMessageBox
from MobuCore.MobuCoreTools.AdjustmentBlend.AdjustmentBlend import AdjustmentBlendCharacter
from MobuCore.MobuCoreTools.StoryFunctions.StoryFunctions import CopySelectedStoryClipsToTracks, CopySelectedStoryClipsToTakes, CenterSelectedClips

# Checks against the given event name and if it finds it, runs the associated function.
def OnMenuClick(eventName):
    if eventName == "Adjustment Blend":
        AdjustmentBlendCharacter()
    elif eventName == "Center Selected Story Clips":
        CenterSelectedClips()
    elif eventName == "Copy Selected Story Clips To Tracks":
        CopySelectedStoryClipsToTracks()
    elif eventName == "Copy Selected Story Clips To Takes":
        CopySelectedStoryClipsToTakes(False)
    elif eventName == "Copy Selected Story Clips To Takes - Centered":
        CopySelectedStoryClipsToTakes()
    else:
        FBMessageBox("Error...", "Menu Error: This option hasn't been set up yet.", "OK")

# Creates the menu.
def LoadMenu():
       
    def MenuOptions(control, event):
        eventName = event.Name
        OnMenuClick(eventName)
    
    mainMenuName = "MobuCore"
    
    menuManager = FBMenuManager()
    
    menuManager.InsertLast( None, mainMenuName )
    menuManager.InsertLast( mainMenuName, "Adjustment Blend" )
    menuManager.InsertLast( mainMenuName, "" )
    menuManager.InsertLast( mainMenuName, "Center Selected Story Clips" )
    menuManager.InsertLast( mainMenuName, "Copy Selected Story Clips To Tracks" )
    menuManager.InsertLast( mainMenuName, "Copy Selected Story Clips To Takes" )
    menuManager.InsertLast( mainMenuName, "Copy Selected Story Clips To Takes - Centered" )
    
    # Example menu structure for future menu items...
    # Line break:                   menuManager.InsertLast( mainMenuName, "" )
    # Sub-menu:                     menuManager.InsertLast( mainMenuName, "TestSubMenu" )
    # Menu option inside sub-menu:  menuManager.InsertLast( mainMenuName + "/TestSubMenu", "TestFunction" )

    # Adds the created menu to the Mobu tool bar.    
    def AddMenu(mainMenuName, subMenuName = ""):
        menu = FBMenuManager().GetMenu( mainMenuName + subMenuName)
        if menu:
            menu.OnMenuActivate.Add( MenuOptions )
    
    AddMenu(mainMenuName)

    # Example...
    # New sub-menus are added after the main menu add: AddMenu(mainMenuName + "/TestSubMenu")
