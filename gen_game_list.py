import os, shutil, itertools, xml.etree.ElementTree, re
from pathlib import Path
from PIL import Image
from urllib.request import urlretrieve

#set vars
roms_folder = ''
console = ''

# CPS - Capcom
# FBA - Final Burn Alpha
# FC - Famicom / NES > fceumm_libretro.so
# GB - Game Boy > mgba_libretro.so
# GBA - Game Boy Advance > mgba_libretro.so
# GBC - Game Boy Color > mgba_libretro.so
# GG - Game Gear
# MD - Mega Drive > genesisplusgx_libretro.so
# N64(?) - Nintendo 64 > mupen64plus_libretro.so
# NEOGEO - Neogeo
# PS - Playstation > pcsx_rearmed_libretro.so
# SFC - Super Famicom / SNES > snes9x_libretro.so

#init folders
os.system('clear')
console = console.upper()
shutil.rmtree(f'tf/game/{console}', ignore_errors=True)
shutil.rmtree(f'tf/settings/res/{console}', ignore_errors=True)
os.makedirs(f'tf/game/{console}')
os.makedirs(f'tf/settings/res/{console}/string')
os.makedirs(f'tf/settings/res/{console}/pic')

#init real names
with open(f'{roms_folder}/gamelist.xml') as xml_tree:
    xml_list = xml.etree.ElementTree.fromstringlist(xml_tree)

#generate game list
game_list = []
real_list = []
bios_list = []
for rom_file in os.listdir(roms_folder):
    if rom_file.endswith('.zip') or rom_file.endswith('.7z'):
        real_name_tag = xml_list.find(f'.//*[path=\'./{rom_file}\']')
        if real_name_tag is not None:
            game_list.append(rom_file)
            real_list.append(re.sub(' +', ' ', re.sub('[^A-Za-z0-9 ]+', '', real_name_tag.find('name').text))[:28])
        else:
            print (f'Copy bios\t> {rom_file}')
            bios_list.append(rom_file)
            shutil.copy(f'{roms_folder}{rom_file}', f'tf/game/{console}/')
game_dict = dict(zip(real_list,game_list))
game_dict = dict(sorted((key,value) for (key,value) in game_dict.items()))
game_dict_count = len(game_dict)
print ()
print (f'Copied bios\t> {len(bios_list)}')
print (f'Games found\t> {game_dict_count}')
print ()
input('Press enter to continue...')

#init out file xml
page_count = 1
item_count = 0
out_file_xml = '<?xml version="1.0" encoding="utf-8"?>\r\n<strings_resources>\r\n'
out_file_xml = out_file_xml + f'  <icon_para game_list_total="{game_dict_count}"/>\r\n'

#manage game
pic_not_found = 0
for real_name, game_file in game_dict.items():
    print (f'Manage game\t> {real_name}')
    
    #copy game
    print (f'Copy game\t> {roms_folder}{game_file}')
    shutil.copy(f'{roms_folder}{game_file}', f'tf/game/{console}/')

    #find image
    game_name = os.path.splitext(game_file)[0]
    pic_file = ''
    for pic_img in Path(f'{roms_folder}').rglob(f'{game_name}-image*'):
        pic_file = str(pic_img)
    if not pic_file:
        for pic_file in Path(f'{roms_folder}').rglob(f'{game_name}-thumb*'):
            pic_file = str(pic_file)
    
    #copy image
    if not pic_file:
        print ('\x1b[0;31;40m' + 'No image' + '\x1b[0m')
        pic_not_found +=1
    elif 'jpg' in pic_file:
        print (f'Convert image\t> {pic_file}')
        pic_jpg = Image.open(pic_file)
        pic_file = pic_file.replace(".jpg", ".png")
        pic_jpg.save(pic_file)
        print (f'Move image\t> {pic_file}')
        shutil.move(pic_file, f'tf/settings/res/{console}/pic/{game_name}.png')
    else:
        print (f'Copy image\t> {pic_file}')
        shutil.copy(pic_file, f'tf/settings/res/{console}/pic/{game_name}.png')
    print ()

    #page out_file_xml
    if item_count == 0:
        out_file_xml = out_file_xml + f'  <icon_page{page_count}>\r\n'
    out_file_xml = out_file_xml + f'      <icon{str(item_count)}_para id="{console}" name="{real_name}" game_path="{game_name}.zip"/>\r\n'
    if item_count == 9 or real_name == list(game_dict)[-1]:
        out_file_xml = out_file_xml + f'  </icon_page{page_count}>\r\n'
        item_count = -1
        page_count +=1
    item_count +=1

# end out_file_xml
out_file_xml = out_file_xml + '</strings_resources>'

#save out_file_xml
print (f'No image games\t> {pic_not_found}')
print ()
print (f'Save config\t> tf/settings/res/{console}/string/game_strings_en.xml')
print (f'Console {console} are done')
print ()
with open(f'tf/settings/res/{console}/string/game_strings_en.xml', 'w') as xml_file:
    xml_file.write(out_file_xml)

#create xml fot all game
shutil.rmtree('tf/settings/res/ALL', ignore_errors=True)
os.makedirs('tf/settings/res/ALL/string/')

#get game from xml
xml_file = ''
game_list = []
for xml_file in Path('./').rglob('*strings*.xml'):
    with open(xml_file, 'r') as xml_tree:
        game_list_console = xml.etree.ElementTree.fromstringlist(xml_tree)
        for num in range(10):
            for game in game_list_console.iter(f'icon{num}_para'):
                game_list.append(game.attrib)
game_list.sort(key=lambda x: x['name'])
game_list_count = len(game_list)

#manage all games
file_count = 1
game_count = 0
for game in game_list:

    #init out file xml
    if game_count % 500 == 0:
        page_count = 1
        item_count = 0
        out_file_xml = '<?xml version="1.0" encoding="utf-8"?>\r\n<strings_resources>\r\n'
        out_file_xml = out_file_xml + f'  <icon_para game_list_total="{game_list_count}"/>\r\n'

    #page out file xml
    if item_count == 0:
        out_file_xml = out_file_xml + f'  <icon_page{page_count}>\r\n'
    out_file_xml = out_file_xml + '      <icon' + str(item_count) + '_para id="' + game['id'] + '" name="' + game['name'] + '" game_path="' + game['game_path'] + '"/>\r\n'
    if item_count == 9 or game == game_list[-1]:
        out_file_xml = out_file_xml + f'  </icon_page{page_count}>\r\n'
        item_count = -1
        page_count +=1
    item_count +=1

    if (game_count + 1) % 500 == 0 or game == game_list[-1]:
        # end out file xml
        out_file_xml = out_file_xml + '</strings_resources>'

        #save out file xml
        print (f'Save config\t> tf/settings/res/ALL/string/game_strings_en.xml')
        print (f'Console ALL are done')
        with open(f'tf/settings/res/ALL/string/game_strings_en_part{file_count}.xml', 'w') as xml_file:
            xml_file.write(out_file_xml)
        file_count +=1
    game_count +=1
