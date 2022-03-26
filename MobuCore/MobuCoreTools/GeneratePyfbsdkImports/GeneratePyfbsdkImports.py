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
