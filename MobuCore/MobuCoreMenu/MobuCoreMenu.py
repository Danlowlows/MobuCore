'''
Menu script for adding MobuCore tools to the Motionbuilder tool bar.

The full MobuCore package is required for this script.
____________________________________________________________________

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