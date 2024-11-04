# Third-party library to install
# python3-pypillowfight

import os, shutil, re
import xml.etree.ElementTree as ET
from PIL import Image

#roms type
# A curated and scraped ROM collection - 2.0 Reupload
# cps1.zip
# cps2.zip
# cps3.zip
# gamegear.zip
# gba.zip
# gbc.zip
# gb.zip
# megadrive.zip
# neogeo.zip
# nes.zip
# snes.zip

#console type
# CPS - Capcom
# FBA - Final Burn Alpha
# FC - Famicom / NES > fceumm_libretro.so
# GB - Game Boy > mgba_libretro.so
# GBA - Game Boy Advance > mgba_libretro.so
# GBC - Game Boy Color > mgba_libretro.so
# GG - Game Gear
# MD - Mega Drive > genesisplusgx_libretro.so
# NEOGEO - Neogeo
# PS - Playstation > pcsx_rearmed_libretro.so
# SFC - Super Famicom / SNES > snes9x_libretro.so

#set vars
console = ''
roms_folder = ''
roms_extensions = ['.7z', '.gb', '.gba', '.gbc', '.gg', '.md', '.nes', '.smc', '.zip']

#init folders
os.system('clear')
console = console.upper()
shutil.rmtree(f'tf/game/{console}', ignore_errors=True)
shutil.rmtree(f'tf/settings/res/{console}', ignore_errors=True)
shutil.rmtree(f'tf/settings/res/ALL', ignore_errors=True)
os.makedirs(f'tf/game/{console}')
os.makedirs(f'tf/settings/res/{console}/string')
os.makedirs(f'tf/settings/res/{console}/pic')
os.makedirs(f'tf/settings/res/ALL/string')

#functions
def normalize_under(name):
    return re.sub(' +', '_', re.sub('[^A-Za-z0-9. ]+', '', name))

def normalize_space(name):
    return re.sub(' +', ' ', re.sub('[^A-Za-z0-9 ]+', '', name))

#step 1 - copy roms and copy/convert images or thumb
copy_roms = 0
copy_image = 0
convert_image = 0
copy_thumb = 0
convert_thumb = 0
image_not_found = []
for rom_file in os.listdir(roms_folder):
    if rom_file.endswith(tuple(roms_extensions)):
        rom_name = os.path.splitext(rom_file)[0]
        norm_file = normalize_under(rom_file)
        norm_name = os.path.splitext(norm_file)[0]
        #copy roms
        copy_roms +=1
        shutil.copy(f'{roms_folder}/{rom_file}', f'tf/game/{console}/{norm_file}')
        #copy/convert images or thumb
        if os.path.exists(f'{roms_folder}/images/{rom_name}-image.png'):
            copy_image +=1
            shutil.copy(f'{roms_folder}/images/{rom_name}-image.png', f'tf/settings/res/{console}/pic/{norm_name}.png')
        elif os.path.exists(f'{roms_folder}/images/{rom_name}-image.jpg'):
            convert_image +=1
            convert_file = Image.open(f'{roms_folder}/images/{rom_name}-image.jpg')
            convert_file.save(f'tf/settings/res/{console}/pic/{norm_name}.png')
        elif os.path.exists(f'{roms_folder}/images/{rom_name}-thumb.png'):
            copy_thumb +=1
            shutil.copy(f'{roms_folder}/images/{rom_name}-thumb.png', f'tf/settings/res/{console}/pic/{norm_name}.png')
        elif os.path.exists(f'{roms_folder}/images/{rom_name}-thumb.png'):
            convert_thumb +=1
            convert_file = Image.open(f'{roms_folder}/images/{rom_name}-thumb.jpg')
            convert_file.save(f'tf/settings/res/{console}/pic/{norm_name}.png')
        else:
            image_not_found.append(rom_name)

#print report
print ('\033[91mReport:\033[0m')
print (f'Roms copied: {copy_roms}')
print (f'Images copied: {copy_image}')
print (f'Images converted: {convert_image}')
print (f'Thumb copied: {copy_thumb}')
print (f'Thumb converted: {convert_thumb}')
print (f'Images not found: {len(image_not_found)}')
print ()
print ('\033[91mRoms without images:\033[0m')
print (*image_not_found, sep='\n')
print ()
input('\033[93mPress enter to continue...\033[0m')

#step 2 - create dictionary name and check file match
os.system('clear')
xml_tree_game = ET.parse(f'{roms_folder}/gamelist.xml')
xml_root_game = xml_tree_game.getroot()

#create dictionary roms : name
game_dict = {}
roms_not_found = []
for game in xml_root_game.findall('./game'):
    norm_file = normalize_under(re.sub('./','', game[0].text))
    if os.path.exists(f'tf/game/{console}/{norm_file}'):
        norm_name = normalize_space(game[1].text)[:28]
        game_dict[norm_file] = norm_name
    else:
        roms_not_found.append(norm_file)
game_dict = dict(sorted(game_dict.items(), key = lambda item: item[1]))
game_dict_count = len(game_dict)

#check file to dict match
names_not_found = []
for rom_file in os.listdir(f'tf/game/{console}'):
    if game_dict.get(rom_file) is None:
        names_not_found.append(rom_file)

#print report
print ('\033[91mReport:\033[0m')
print (f'Roms matched: {game_dict_count}')
print (f'Names not found: {len(names_not_found)}')
print (f'Roms not found: {len(roms_not_found)}')
print ()
print ('\033[91mRoms without name:\033[0m')
print (*names_not_found, sep='\n')
print ()
print ('\033[91mNames without rom:\033[0m')
print (*roms_not_found, sep='\n')
print ()
input('\033[93mPress enter to continue...\033[0m')

#step 3 - create xml from dictionary
os.system('clear')
xml_root_strings = ET.Element('strings_resources')
ET.SubElement(xml_root_strings, 'icon_para', game_list_total = f'{game_dict_count}')

#from dictionary to xml entry
item_count = 0
page_count = 1
for game_key in game_dict:
    game_value = game_dict.get(game_key)
    if item_count == 0:
        xml_page_strings = ET.SubElement(xml_root_strings, f'icon_page{page_count}')
    ET.SubElement(xml_page_strings, f'icon{item_count}_para', id = console, name = game_value, game_path = game_key)
    item_count +=1
    if item_count == 10:
        item_count = 0
        page_count +=1

#print report
print ('\033[91mReport:\033[0m')
print (f'Saved xml for {console}: tf/settings/res/{console}/string/game_strings_en.xml')
xml_tree_strings = ET.ElementTree(xml_root_strings)
ET.indent(xml_tree_strings, '\t')
xml_tree_strings.write(f'tf/settings/res/{console}/string/game_strings_en.xml', xml_declaration = True, encoding = 'utf-8')

#step 4 - create global dictionary from all xml files
game_dict = {}
for console_dir in os.listdir('tf/settings/res/'):
    if os.path.exists(f'tf/settings/res/{console_dir}/string/game_strings_en.xml'):
        xml_tree_game = ET.parse(f'tf/settings/res/{console_dir}/string/game_strings_en.xml')
        xml_root_game = xml_tree_game.getroot()
        for game in xml_root_game.findall('.//*[@game_path]'):
            game_dict[game.attrib['game_path']] = game.attrib['name']
game_dict = dict(sorted(game_dict.items(), key = lambda item: item[1]))
game_dict_count = len(game_dict)

#from dictionary to xml entry in 500 group
item_count = 0
item_global_count = 0
page_count = 1
file_count = 0
for game_key in game_dict:
    game_value = game_dict.get(game_key)
    if item_global_count % 500 == 0:
        xml_root_strings = ET.Element('strings_resources')
        ET.SubElement(xml_root_strings, 'icon_para', game_list_total = f'{game_dict_count}')
        item_count = 0
        page_count = 1
    if item_count == 0:
        xml_page_strings = ET.SubElement(xml_root_strings, f'icon_page{page_count}')
    ET.SubElement(xml_page_strings, f'icon{item_count}_para', id = console, name = game_value, game_path = game_key)
    item_count +=1
    if item_count == 10:
        item_count = 0
        page_count +=1
    if (item_global_count + 1) % 500 == 0 or game_key == list(game_dict)[-1]:
        print (f'Saved xml for ALL: tf/settings/res/ALL/string/game_strings_en_part{file_count}.xml')
        xml_tree_strings = ET.ElementTree(xml_root_strings)
        ET.indent(xml_tree_strings, '\t')
        xml_tree_strings.write(f'tf/settings/res/ALL/string/game_strings_en_part{file_count}.xml', xml_declaration = True, encoding = 'utf-8')
        file_count +=1
    item_global_count +=1
print ()
