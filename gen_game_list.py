import os, shutil
from pathlib import Path
from PIL import Image
os.system('clear')
shutil.rmtree('tf', ignore_errors=True)
print ('Remove tf folder')

#set vars
romsfolder = 'source/roms'
console = 'neogeo'

#create folder
os.makedirs('tf/game/' + console.upper())
os.makedirs('tf/settings/res/' + console.upper() + '/string')
os.makedirs('tf/settings/res/' + console.upper() + '/pic')

#generate gamelist
gamelist = []
gamefile = ''
for gamefile in os.listdir(romsfolder + '/' + console):
    if gamefile.endswith('.zip') or gamefile.endswith('.7z'):
        gamelist.append(gamefile)
gamelist.sort()
gamelistcount = len(gamelist)
print ('Found ' + str(gamelistcount) + ' games')
print ()

#init outfile
pagecount = 1
itemcount = 0
outfile = '<?xml version="1.0" encoding="utf-8"?>\r\n<strings_resources>\r\n'
outfile = outfile + '  <icon_para game_list_total="' + str(gamelistcount) + '"/>\r\n'

#manage game
gamefile = ''
for gamefile in gamelist:
    #copy file
    print ('Copy game\t> ' + romsfolder + '/' + console + '/' + gamefile)
    shutil.copy(romsfolder + '/' + console + '/' + gamefile, 'tf/game/' + console.upper() + "/")
    gamename = os.path.splitext(gamefile)[0]

    #find image
    picfile = ''
    for picimg in Path(romsfolder + '/' + console).rglob(gamename + '-image*'):
        picfile = str(picimg)
    if not picfile:
        for picfile in Path(romsfolder + '/' + console).rglob(gamename + '-thumb*'):
            picfile = str(picfile)
    
    #copy image
    if not picfile:
        print ('\x1b[0;31;40m' + 'No image' + '\x1b[0m')
    elif 'jpg' in picfile:
        print ('Convert image\t> ' + picfile)
        picjpg = Image.open(picfile)
        picfile = picfile.replace(".jpg", ".png")
        picjpg.save(picfile)
        print ('Move image\t> ' + picfile)
        shutil.move(picfile, 'tf/settings/res/' + console.upper() + '/pic/' + gamename + '.png' )
    else:
        print ('Copy image\t> ' + picfile)
        shutil.copy(picfile, 'tf/settings/res/' + console.upper() + '/pic/' + gamename + '.png' )
    print ()

    #page outfile
    if (itemcount == 0):
        outfile = outfile + '  <icon_page' + str(pagecount) + '>\r\n'
    outfile = outfile + '      <icon' + str(itemcount) + '_para id="' + console.upper() + '" name=\"' + gamename.capitalize() + '\" game_path=\"' + gamename + ".zip" + '\"/>\r\n'
    if (itemcount == 9 or gamefile == gamelist[-1]):
        outfile = outfile + '  </icon_page' + str(pagecount) + '>\r\n'
        itemcount = -1
        pagecount +=1
    itemcount +=1

# end outfile
outfile = outfile + '</strings_resources>'

#save outfile
print ('Save config\t> tf/settings/res/' + console.upper() + '/string/game_strings_en.xml')
with open('tf/settings/res/' + console.upper() + '/string/game_strings_en.xml', 'w') as xmlfile:
    xmlfile.write(outfile)
