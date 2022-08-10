"""Create a zip file to make the add-on ready to install

For Windows OS

Create a shortcut to this file and copy it to %AppData%\Roaming\Microsoft\Windows\SendTo\
Then run it with a right click in an explorer.

Usage:
    Once this file is in the SendTo folder of Windows it is accessible in the right click menu.
    In a file explorer go to your working directory, select the folder containing the addon code
    (eg: /shotmanager), right click to display the menu then pick wkzipaddon.py.
    This script will be ran and it will create an archive, cleaned from the .pyc, ready to
    be installed in Blender.
"""


import zipfile
import os
from os.path import basename
import sys
from pathlib import Path


def main():

    pathArr = sys.argv

    # to use for debug in VSC:
    # pathArr = [
    #     "self",
    #     "Z:\\EvalSofts\\Blender\\DevPython\\WkZipAddon\\WkSamples\\myAddon_Addon\\myaddon",
    # ]

    # "Z:\\EvalSofts\\Blender\\DevPython\\WkZipAddon\\WkSamples\\toto.py",
    # "Z:\\EvalSofts\\Blender\\DevPython\\WkZipAddon\\WkSamples\\wkzipaddon_data.txt"]

    # print(f"Arguments: {pathArr}")

    outString = ""

    if 1 >= len(pathArr):
        print("No file specified")
        # text_file = open("wkzipaddon_nodata.txt", "w")
        # text_file.write(f"Launched Python file: {pathArr[0]}\n")
        # text_file.write("No arg file specified!")
        # text_file.close()
        return

    outString += "\nArg files to zip:"
    print("\nArgs:")
    for i in range(1, len(pathArr)):
        strg = f"    Arg {i}: {pathArr[i]}"
        print(strg)
        outString += "\n" + strg

    # get the zip file name from the add-on declaration
    ###################################################

    def _getAddonCategory(init_file):
        nameStr = ""
        with open(init_file) as fp:
            line = fp.readline()
            versionFound = False
            while line and not versionFound:
                if -1 != line.find('"category":'):
                    print(f"Line : {line.strip()}")
                    versionFound = True
                    startInd = line.find(":")
                    nameStr = line[startInd + 1 :]
                    startInd = nameStr.find('"')
                    nameStr = nameStr[startInd + 1 :]
                    endInd = nameStr.find('"')
                    nameStr = nameStr[0:endInd]
                    nameStr = nameStr.replace(" ", "-")
                    print(f"category nameStr : {nameStr}")
                else:
                    line = fp.readline()
        return nameStr

    def _getAddonName(init_file):
        nameStr = ""
        with open(init_file) as fp:
            line = fp.readline()
            versionFound = False
            while line and not versionFound:
                if -1 != line.find('"name":'):
                    print(f"Line : {line.strip()}")
                    versionFound = True
                    startInd = line.find(":")
                    nameStr = line[startInd + 1 :]
                    startInd = nameStr.find('"')
                    nameStr = nameStr[startInd + 1 :]
                    endInd = nameStr.find('"')
                    nameStr = nameStr[0:endInd]
                    # nameStr = nameStr.replace(" ", "_")
                    nameStr = nameStr.replace(" ", "")
                    print(f"nameStr : {nameStr}")
                else:
                    line = fp.readline()
        return nameStr

    def _getAddonVersion(init_file):
        versionStr = ""
        with open(init_file) as fp:
            line = fp.readline()
            versionFound = False
            while line and not versionFound:
                if -1 != line.find('"version":'):
                    print(f"Line : {line.strip()}")
                    versionFound = True
                    startInd = line.find("(")
                    endInd = line.find(")")
                    numbers = line[startInd + 1 : endInd]
                    print(f"numbers : {numbers}")
                    numbersArr = numbers.split(", ")
                    versionStr = "V" + "-".join([str(s) for s in numbersArr])
                    print(f"versionStr : {versionStr}")
                else:
                    line = fp.readline()
        return versionStr

    p = Path(pathArr[1])
    output_dir = ""
    output_dir = str(p.parent) + "\\"

    if os.path.isfile(pathArr[1]):
        output_dir = str(p.parent) + "\\"
    else:
        output_dir = str(p.parent) + "\\"
    #  output_dir = str(p.parent.parent) + "\\"

    # get the init file
    init_file = Path(pathArr[1] + "\\__init__.py")
    print(f"\ninit_file: {init_file}")
    # file exists
    if init_file.is_file():
        print("init file found")
        categStr = _getAddonCategory(init_file)
        nameStr = _getAddonName(init_file)
        versionStr = _getAddonVersion(init_file)

        # if the category appears at the start of the name it is removed
        categInd = nameStr.find(categStr)
        if -1 != categInd:
            nameStr = nameStr[len(categStr) :]

    else:
        categStr = ""
        nameStr = ""
        versionStr = ""

    zip_file = output_dir
    if "" != nameStr:
        if "" != categStr:
            zip_file += categStr + "_"
        zip_file += nameStr
    else:
        zip_file += str(p.stem)
    if "" != versionStr:
        zip_file += "_" + versionStr
    zip_file += ".zip"

    outString += f"\n\nOutput Zip file: {zip_file}"
    print(f"\nzip_file: {zip_file}")

    #  try:
    if True:
        print("\n*** Create a zip file from multiple files ")

        def _addFileToZip(zipObj, fullpath, root):
            print(f"_addFileToZip:\n file: {fullpath},\n root: {root}")

            # exclude files
            if ".pyc" != Path(fullpath).suffix:
                filePath = os.path.join(folderName, filename)
                filePath = fullpath
                #    relFilePath = os.path.relpath(os.path.join(filePath, os.path.join(zip_file, '..')))
                relFilePath = fullpath[len(root) :]
                # print(f"filePath: {filePath}")
                # print(f"relFilePath: {relFilePath}")

                zipObj.write(filePath, relFilePath)
            return

        # create a ZipFile object
        # https://stackoverflow.com/questions/27526155/python-zipfile-how-to-set-the-compression-level
        zipObj = zipfile.ZipFile(zip_file, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=7)

        for i in range(1, len(pathArr)):
            print(f"\n  {i} Arg {i}: {pathArr[i]}")

            if os.path.isfile(pathArr[i]):
                _addFileToZip(zipObj, pathArr[i], output_dir)

            # Iterate over all the files in directory
            for folderName, subfolders, filenames in os.walk(pathArr[i]):
                # print(f"Folder name: {Path(folderName).name}")

                # exclude dirs
                if "__pycache__" != Path(folderName).name:

                    for filename in filenames:
                        filePath = os.path.join(folderName, filename)
                        _addFileToZip(zipObj, filePath, output_dir)

        # add some other files
        txtfiles = []
        txtfiles.append(output_dir + "\\README.md")
        txtfiles.append(output_dir + "\\CHANGELOG.md")
        txtfiles.append(output_dir + "\\LICENSE")

        for f in txtfiles:
            if Path(f).is_file():
                _addFileToZip(zipObj, f, output_dir)

        if False:
            text_file = open(output_dir + "wkzipaddon_data.txt", "w")
            text_file.write(f"{outString}")
            text_file.close()

    # except ValueError:
    #     print("Exception here")
    #     text_file.write(f"Error occured")

    #     #close file
    #     text_file.close()


if __name__ == "__main__":
    main()
