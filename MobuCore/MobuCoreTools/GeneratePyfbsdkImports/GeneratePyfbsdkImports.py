'''
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

def ReadFileToList(filePath):
    with open(filePath) as f:
        lineList = f.readlines()
    return lineList

# Replace pythonFilePath with your file path and run this function.
def GeneratePyfbsdkImports(pythonFilePath):
    lines = ReadFileToList(pythonFilePath)
    fbNames = []
    for line in lines:
        if " " in line:
            lineParts = line.split(" ")
            for part in lineParts:
                if part.startswith("FB"):
                    fbNames.append(part)   
    fbNames = [name.split("(")[0] for name in fbNames]
    fbNames = [name.split(")")[0] for name in fbNames]
    fbNames = [name.split(".")[0] for name in fbNames]
    fbNames = [name.strip('\n') for name in fbNames]
    fbNames = [name.strip('\,') for name in fbNames]
    try:
        fbNames.remove("FBDelete")
    except:
        pass
    fbNames = list(dict.fromkeys(fbNames))
    print(str(fbNames).replace("[","").replace("]","").replace("'",""))
