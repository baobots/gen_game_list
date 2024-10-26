import os, shutil, itertools, xml.etree.ElementTree, re
from pathlib import Path
from PIL import Image
from urllib.request import urlretrieve

#set vars
romsfolder = ''
imagesfolder = ''
console = 'neogeo'

#init folders
os.system('clear')
start = input(f'Remove tf_{console} folder? [y/n]')
if start != 'y':
    print ()
    print ('Exit')
    quit()
print(f'Remove tf_{console} folder')
print ()
shutil.rmtree(f'tf_{console}', ignore_errors=True)
os.makedirs(f'tf_{console}/game/{console.upper()}')
os.makedirs(f'tf_{console}/settings/res/{console.upper()}/string')
os.makedirs(f'tf_{console}/settings/res/{console.upper()}/pic')

#init realnames and customnanes
urlretrieve('https://raw.githubusercontent.com/RetroPie/EmulationStation/master/resources/mamenames.xml', 'mamenames.xml')
with open('mamenames.xml', 'r+') as norootfile:
    with open('customnames.xml') as customnames:
        shutil.copyfileobj(customnames, norootfile)
    rootfile = itertools.chain('<root>', norootfile, '</root>')
    mamenamexml = xml.etree.ElementTree.fromstringlist(rootfile)

#generate gamelist
gamelist = []
reallist = []
bioslist = []
for romfile in os.listdir(romsfolder):
    if romfile.endswith('.zip') or romfile.endswith('.7z'):
        mamenametag = os.path.splitext(romfile)[0]
        realnametag = mamenamexml.find(f'.//*[mamename=\'{mamenametag}\']')
        if realnametag is not None:
            gamelist.append(romfile)
            reallist.append(re.sub(' +', ' ', re.sub('[^A-Za-z0-9 ]+', '', realnametag.find('realname').text))[:28])
        else:
            print (f'Copy bios\t> {romfile}')
            bioslist.append(romfile)
            shutil.copy(f'{romsfolder}{romfile}', f'tf_{console}/game/{console.upper()}/')
gamedict = dict(zip(reallist,gamelist))
gamedict = dict(sorted((key,value) for (key,value) in gamedict.items()))
gamedictcount = len(gamedict)
print ()
print (f'Copied {len(bioslist)} bios')
print (f'Found {gamedictcount} games')
input('Press enter to continue...')

#init outfilexml
pagecount = 1
itemcount = 0
outfilexml = '<?xml version="1.0" encoding="utf-8"?>\r\n<strings_resources>\r\n'
outfilexml = outfilexml + f'  <icon_para game_list_total="{gamedictcount}"/>\r\n'

#manage game
picnotfound = 0
for realname, gamefile in gamedict.items():
    print (f'Magane game\t> {realname}')
    
    #copy game
    print (f'Copy game\t> {romsfolder}{gamefile}')
    shutil.copy(f'{romsfolder}{gamefile}', f'tf_{console}/game/{console.upper()}/')

    #find image
    gamename = os.path.splitext(gamefile)[0]
    picfile = ''
    for picimg in Path(f'{imagesfolder}').rglob(f'{gamename}-image*'):
        picfile = str(picimg)
    if not picfile:
        for picfile in Path(f'{imagesfolder}').rglob(f'{gamename}-thumb*'):
            picfile = str(picfile)
    
    #copy image
    if not picfile:
        print ('\x1b[0;31;40m' + 'No image' + '\x1b[0m')
        picnotfound +=1
    elif 'jpg' in picfile:
        print (f'Convert image\t> {picfile}')
        picjpg = Image.open(picfile)
        picfile = picfile.replace(".jpg", ".png")
        picjpg.save(picfile)
        print (f'Move image\t> {picfile}')
        shutil.move(picfile, f'tf_{console}/settings/res/{console.upper()}/pic/{gamename}.png')
    else:
        print (f'Copy image\t> {picfile}')
        shutil.copy(picfile, f'tf_{console}/settings/res/{console.upper()}/pic/{gamename}.png')
    print ()

    #page outfilexml
    if (itemcount == 0):
        outfilexml = outfilexml + f'  <icon_page{str(pagecount)}>\r\n'
    outfilexml = outfilexml + f'      <icon{str(itemcount)}_para id="{console.upper()}" name="{realname}" game_path="{gamename}.zip"/>\r\n'
    if (itemcount == 9 or realname == list(gamedict)[-1]):
        outfilexml = outfilexml + f'  </icon_page{str(pagecount)}>\r\n'
        itemcount = -1
        pagecount +=1
    itemcount +=1

# end outfilexml
outfilexml = outfilexml + '</strings_resources>'

#save outfilexml
print (f'No image games\t> {picnotfound}')
print (f'Save config\t> tf_{console}/settings/res/{console.upper()}/string/game_strings_en.xml')
print ()
print ('All done')
with open(f'tf_{console}/settings/res/{console.upper()}/string/game_strings_en.xml', 'w') as xmlfile:
    xmlfile.write(outfilexml)
