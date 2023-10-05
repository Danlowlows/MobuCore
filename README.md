NOTE: The previous library of functions is still here. It's just moved to the \MobuCore\MobuCoreLibrary\ folder.
__________________________________________________________________________

MobuCore is a collection of python scripts and functions for common tasks in Autodesk Motionbuilder.

MobuCore was written by Dan Lowe, who you can reach on Twitter at https://twitter.com/danlowlows (at time of writing, direct messages are open).

MobuCore is made available with the MIT license terms:

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
__________________________________________________________________________

Installation instructions...

1. Download the entire MobuCore repository.
2. Drop the files in the Motionbuilder /PythonStartup/ folder located under \Documents\MB\ e.g. C:\Users\Dan\Documents\MB\2018-x64\config\PythonStartup\.
3. Start Motionbuilder.
4. You should see a new Menu in the top menu bar called MobuCore, which contains the correct menu items.

If you don't see the MobuCore menu, something went wrong. Be sure that the files are in the PythonStartup folder correctly. MobuCoreStartUp.py and the \MobuCore\ folder that contains MobuCoreLibrary, MobuCoreMenu and MobuCoreTools, should be directly in the PythonStartup folder, like so: C:\Users\Dan\Documents\MB\2018-x64\config\PythonStartup\MobuCoreStartup.py  and  C:\Users\Dan\Documents\MB\2018-x64\config\PythonStartup\MobuCore\.

Menu Options...

1. Adjustment Blending: This a method for adjusting additive layer interpolation between keyframes, so that movement on the layer is shifted to areas where there is already movement on the base layer. This helps to maintain the existing energy of the base layer motion, and helps to maintain contact points. For more information, see this talk from GDC 2016: https://youtu.be/eeWBlMJHR14?t=518

To use Adjustment Blending, add two or more keyframes on an additive layer. Make whatever changes you want to those keyframes, then run adjustment blending. You should notice that the script filled in the interpolation between your two keyframes, and in the right circumstances, should have fixed any unwanted velocity shifts in the layer change. Again, I highly recommend checking out the GDC talk for more info on the best use cases for this: It's extremely useful, but there are caveats to how it should be used to get the most out of it.

Unfortunately this version of Adjustment Blending doesn't include hyper-extension correction, so in some cases you may get hyper-extension if you try to stretch out the character's movement or posing. I would have added hyper-extension correction, but it's quite complex and time consuming to write and at time of writing I'm currently moving countries. Hopefully I'll have time to get back to it in future, if my employer allows me to continue to work on public scripts.

2. Center Selected Story Clips: Takes any selected clips in the Story Editor and centers them in the scene. Orientation is based on the start position and end position for the clip, so may be more suitible for some clips than others.

3. Copy Selected Story Clips to Tracks: Takes any selected clips in the Story Editor and copies them to individual tracks. Helpful when you want to extract coverage from one long mocap shot.

4. Copy Selected Story Clips to Takes: Takes any selected clips in the Story Editor, creates a new take for them, with the correct frame timings, and copies the clips to those takes (naming is based on the clip name, so there will likely be what seems like strange numbering at the end of the takes).

5. Copy Selected Story Clips to Takes - Centered: Basically does all 3 of the above scripts in order (copies to tracks, centers, then copies to takes). Again, very useful for quickly extracting mocap coverage into individual takes.
