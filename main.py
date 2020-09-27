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
            # formatted as ClientSideMod.esm0xFFFFFFFFServerSideMod.esm0xFFFFFFFF
            # .esm or .esp interchangeable
            # some mod authors publish with capital file extensions, but we can't just .lower() since OpenMW cares about the mod name's casing
            extensionIdx = line.find(".es")
            uppercaseExtensionIdx = line.find(".ES")

            # TODO: clean this up
            # neither found, garbage line
            if uppercaseExtensionIdx == -1 and extensionIdx == -1:
                continue
            # all mod extensions are uppercase, just use first found
            elif extensionIdx == -1 and uppercaseExtensionIdx != -1:
                extensionIdx = uppercaseExtensionIdx
            # one of each type, use whichever comes first
            elif extensionIdx != -1 and uppercaseExtensionIdx != -1 and uppercaseExtensionIdx < extensionIdx:
                extensionIdx = uppercaseExtensionIdx

            hashIdx = line.find("0x")
            if hashIdx == -1:
                continue

            # from start of string to end of extension
            modName = line[0:extensionIdx + 4]            

            # full hex value
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
