import io
import os
import json

# Takes tes3mp-client logs and converts the client side plugin list to a formatted server plugin list
def main():
    directory = os.path.dirname(__file__)

    # get readable tes3mp-client dump files to convert
    toConvert = []
    for name in os.listdir(directory):
        if "tes3mp-client" in name:
            if not os.path.exists(os.path.join(directory, name)):
                continue
        
            file = open(os.path.join(directory, name), 'r')
            if not file.readable():
                file.close()
                continue
            else:
                toConvert.append(file)

    if not toConvert:
        return

    converted = {}
    for file in toConvert:
        converted[file.name] = {}

        idx = 0
        # filter for the block of text following "[ERR]: Your current plugins are:  "
        for line in file:
            # filter out non-checksum dumps
            if not "0x" in line:
                continue

            # filter out "mod name checksum 0xETC doesn't match 0xETC2"
            if "doesn't match" in line:
                continue

            # strip spaces
            line.replace(" ", "")

            # first instance is client side list, second is server side
            # formatted as ClientSideMod.esm 0xFFFFFFFF ServerSideMod.esm 0xFFFFFFFF (without spaces)
            # .esm or .esp interchangeable, some mod authors inexplicably use .ESP so lower the line for the search
            extensionIdx = line.lower().find(".es")
            if extensionIdx == -1:
                continue

            hashIdx = line.find("0x")
            if hashIdx == -1:
                continue

            # from start of string + 4 for the extension name following the period
            modName = line[0:extensionIdx + 4]            

            # adding the 8 hex values and the seperator
            modHash = line[hashIdx:hashIdx + 10]

            # output as { "0": { "ModName.esp": ["Hash1"] } }
            converted[file.name][idx] = {
                modName: [modHash]
            }

            print(converted)
            idx += 1

        file.close()
    
    for k, v in converted.items():
        out = open(k + "-converted.json", "w")
        json.dump(v, out)
        out.close()

if __name__ == "__main__":
    main()
