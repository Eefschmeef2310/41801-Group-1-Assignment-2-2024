import os
import maya.cmds as cmds
import re

def pad_to_three_digits(number: int) -> str:
    return f"{number:03}"

def get_digits_after_v(input_string):
    # Use regex to search for ".v" followed by digits
    match = re.search(r'\.v(\d+)', input_string)
   
    # If a match is found, return the digits
    if match:
        return match.group(1)
   
    # If no match is found, return None or an appropriate message
    return None

def get_part_before_dot(input_string):
    # Find the index of the first period
    period_index = input_string.find('.')
   
    # If no period is found, return the entire string
    if period_index == -1:
        return input_string
   
    # Return the substring before the first period
    return input_string[:period_index]

def find_mb_files(*arg):
    global current_files
    global current_keys
    mb_files = []
   
    current_files = {}
    
    asset_type = cmds.optionMenuGrp('asset_types', q=True, v=True)
   
    directory = cmds.workspace(q=True, rd=True) + cmds.radioCollection('wip_or_publish', q=True, sl=True) + "/"
    
    # Walk through the directory and subdirectories
    for root, dirs, files in os.walk(directory):
        for name in files:
            # Check if the file has the .mb extension
            if name.endswith(".mb") and asset_type.lower() != "" and asset_type.lower() in name:
                # Get the full path to the file and append to list
                mb_files.append(name)
               
                if get_part_before_dot(name) not in current_files:
                    current_files[get_part_before_dot(name)] = [pad_to_three_digits(int(get_digits_after_v(name)))]
                else:
                    current_files[get_part_before_dot(name)].append(pad_to_three_digits(int(get_digits_after_v(name))))
       
    #Separate array required to load into text list    
    current_keys = []      
    for mb_file in current_files:
        current_keys.append(mb_file)
           
    cmds.textScrollList('searchResults', e=True, ra=True)
    cmds.textScrollList('searchResults', e=True, a=current_keys)
    
    #If list is not empty, activate the search filter and version dropdown
    cmds.textFieldGrp('search_filter', e= True, en = cmds.textScrollList('searchResults', q=True, ni=True) > 0, tx="")
    cmds.optionMenuGrp('version_number_dropdown', e=True, en=False)
    cmds.button('load_file', e=True, en=False)
    
def update_versions():
    #Clear all version numbers before filling
    cmds.optionMenuGrp('version_number_dropdown', e=True, dai=True)
    
    option_menu = cmds.optionMenuGrp('version_number_dropdown', query=True, select=True)
   
    #Load versions into dropdown
    for version in current_files[str(cmds.textScrollList('searchResults', q=True, si=True)[0])]:
        cmds.menuItem(version, l=str(version),p='version_number_dropdown|OptionMenu')
    cmds.optionMenuGrp('version_number_dropdown', e=True, en=True)
    
    cmds.button('load_file', e=True, en = True)
    
def load_file(*args):
    file_name = str(cmds.textScrollList('searchResults', q=True, si=True)[0]) + ".v" + str(cmds.optionMenuGrp('version_number_dropdown', q=True, v=True) + ".mb")
    
    directory = cmds.workspace(q=True, rd=True) + cmds.radioCollection('wip_or_publish', q=True, sl=True) + "/"
    
    for root, dirs, files in os.walk(directory):
        for name in files:
            if name == file_name:
                cmds.file(root + "/" + file_name, open=True, force=True)

def search(*arg):
    global current_keys
    
    filtered_keys = current_keys.copy()
    
    search_filter = str(cmds.textFieldGrp('search_filter', q=True, tx=True))
    
    for key in current_keys:
        if search_filter not in key:
            filtered_keys.remove(key)
            
    #Maintain current seletion in case it is still present
    current_selection = cmds.textScrollList('searchResults', q=True, si=True)
     
    cmds.textScrollList('searchResults', e=True, ra=True)
    cmds.textScrollList('searchResults', e=True, a=filtered_keys)
    
    if current_selection and current_selection[0] and current_selection[0] in cmds.textScrollList('searchResults', q=True, ai=True):
        cmds.textScrollList('searchResults', e=True, si=current_selection[0])
    else:
        cmds.optionMenuGrp('version_number_dropdown', e=True, en=False)
        cmds.button('load_file', e=True, en=False)
   
def file_open_tool():
    if cmds.window('fileOpenTool', exists = True):
        cmds.deleteUI('fileOpenTool')
       
    cmds.window('fileOpenTool', resizeToFitChildren=True)
   
    cmds.columnLayout()
   
    cmds.rowLayout(nc=4)
    cmds.text('Publish or WIP?')
    cmds.radioCollection('wip_or_publish')
    cmds.radioButton( 'wip', label='WIP', sl=True, cc=find_mb_files )
    cmds.radioButton( 'publish', label='Publish' )
    cmds.setParent('..')
   
    #File types dropdown
    cmds.columnLayout()
    cmds.optionMenuGrp('asset_types', l='What do you want to open?', cc=find_mb_files)
    cmds.menuItem('')
    cmds.menuItem('Model')
    cmds.menuItem('Rig')
    cmds.menuItem('Layout')
    cmds.menuItem('Animation')
    cmds.menuItem('Lighting')
   
    #Filter search results
    cmds.textFieldGrp('search_filter', l='Filter results', en = False, tcc=search)
   
    #Show search results
    cmds.textScrollList('searchResults', sc=update_versions)
   
    #Version number dropdown
    cmds.optionMenuGrp('version_number_dropdown', l='Version Number?', en = False)
   
    #Load button
    cmds.button('load_file', l='Load file', en = False, c=load_file)
   
    cmds.showWindow('fileOpenTool')

current_files = {}
current_keys = []

file_open_tool()

# Example usage
#mb_files_list = find_mb_files()

# Print the list of .mb files
#for mb_file in mb_files_list:
    #print(mb_file)