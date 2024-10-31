import os
import maya.cmds as cmds
import re

#Used for padding the version number to 3 digits
def pad_to_three_digits(number: int) -> str:
    return f"{number:03}"

#Extracts the version number from the filename
def get_digits_after_v(input_string):
    # Use regex to search for ".v" followed by digits
    match = re.search(r'\.v(\d+)', input_string)
   
    # If a match is found, return the digits
    if match:
        return match.group(1)
   
    # If no match is found, return None or an appropriate message
    return None

#Gets the filename without anything following eg. armchair01_model
def get_part_before_dot(input_string):
    # Find the index of the first period
    period_index = input_string.find('.')
   
    # If no period is found, return the entire string
    if period_index == -1:
        return input_string
   
    # Return the substring before the first period
    return input_string[:period_index]

#Finds all files within the filesystem
def find_mb_files(*arg):
    #Call globals
    global current_files
    global current_keys
    
    mb_files = []   
    current_files = {}
    
    asset_type = arg[0]
    if asset_type == '':
        #If no asset type selected, reset the system and exit early
        cmds.text("results_instruction", edit=True, l="No files found")
        cmds.textScrollList('searchResults', e=True, ra=True)
        cmds.textFieldGrp('search_filter', e= True, en = cmds.textScrollList('searchResults', q=True, ni=True) > 0, tx="")
        cmds.optionMenuGrp('version_number_dropdown', e=True, en=False)
        cmds.button('load_file', e=True, en=False)
        return
   
    #Get the relative filepath and whether or not we're working in WIP or publish
    directory = cmds.workspace(q=True, rd=True) + cmds.radioCollection('wip_or_publish', q=True, sl=True) + "/"
    
    #Ascertain more info about the specific file the user wants to search through.
    if cmds.optionMenuGrp('sequence_id', q=True, v=True):
        directory += "sequence/" + cmds.optionMenuGrp('sequence_id', q=True, v=True) + "/"
        if cmds.optionMenuGrp('shot_id', q=True, v=True):
            directory += cmds.optionMenuGrp('shot_id', q=True, v=True) + "/"
    else:
        directory += "assets/"
    
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
                    
    #By this point, we should have two list of all found files, one with full names and one with just the name of the asset
       
    #Separate array required to load into text list    
    current_keys = []
    for mb_file in current_files:
        current_keys.append(mb_file)
        
    #load all relevant files into the results list          
    cmds.textScrollList('searchResults', e=True, ra=True)
    cmds.textScrollList('searchResults', e=True, a=current_keys)
    
    #If list is not empty, activate the search filter and version dropdown
    cmds.textFieldGrp('search_filter', e= True, en = cmds.textScrollList('searchResults', q=True, ni=True) > 0, tx="")
    cmds.text("results_instruction", edit=True, l="Select which file you want to load")
    cmds.optionMenuGrp('version_number_dropdown', e=True, en=False)
    cmds.button('load_file', e=True, en=False)
    
#Gets all the version numbers for a specific asset and loads into the dropdown
def update_versions():
    #Clear all version numbers before filling
    cmds.optionMenuGrp('version_number_dropdown', e=True, dai=True)
    
    option_menu = cmds.optionMenuGrp('version_number_dropdown', query=True, select=True)
   
    #Load versions into dropdown
    for version in reversed(current_files[str(cmds.textScrollList('searchResults', q=True, si=True)[0])]):
        cmds.menuItem(version, l=str(version),p='version_number_dropdown|OptionMenu')
    cmds.optionMenuGrp('version_number_dropdown', e=True, en=True)
    
    cmds.button('load_file', e=True, en = True)
    
def load_file(*args):
    #stitch together the complete filename with version number
    file_name = str(cmds.textScrollList('searchResults', q=True, si=True)[0]) + ".v" + str(cmds.optionMenuGrp('version_number_dropdown', q=True, v=True) + ".mb")
    
    #get the overall directory
    directory = cmds.workspace(q=True, rd=True) + cmds.radioCollection('wip_or_publish', q=True, sl=True) + "/"
    
    #Find where the file is located in the filesystem and load it
    for root, dirs, files in os.walk(directory):
        for name in files:
            if name == file_name:
                cmds.file(root + "/" + file_name, open=True, force=True)

#Actively updates the results based on the search filter
def search(*arg):
    global current_keys
    
    filtered_keys = current_keys.copy()
    
    search_filter = arg[0]
    
    #Remove any assets that do not fit into the filter
    for key in current_keys:
        if search_filter not in key:
            filtered_keys.remove(key)
            
    #Maintain current seletion in case it is still present
    current_selection = cmds.textScrollList('searchResults', q=True, si=True)
     
    cmds.textScrollList('searchResults', e=True, ra=True)
    cmds.textScrollList('searchResults', e=True, a=filtered_keys)
    
    #update UI elements 
    if current_selection and current_selection[0] and current_selection[0] in cmds.textScrollList('searchResults', q=True, ai=True):
        cmds.textScrollList('searchResults', e=True, si=current_selection[0])
    else:
        cmds.text("results_instruction", edit=True, l="No files found")
        cmds.optionMenuGrp('version_number_dropdown', e=True, en=False)
        cmds.button('load_file', e=True, en=False)

def get_sequences():
    #Gets every sequence in the filesystem
    directory = cmds.workspace(q=True, rd=True) + cmds.radioCollection('wip_or_publish', q=True, sl=True) + "/sequence/"
    
    cmds.optionMenuGrp('sequence_id', e=True, dai=True)
    
    cmds.menuItem('', parent='sequence_id|OptionMenu')
    for folder in [name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]:
        cmds.menuItem(folder, parent='sequence_id|OptionMenu')
    cmds.setParent('..')

def get_shots(*args):
    #Gets every shot within the specified sequence, similar to above. Extra if statements present to reset UI elements if needed
    cmds.textScrollList('searchResults', e=True, ra=True)
    cmds.optionMenuGrp('shot_id', e=True, en=False, dai=True)
    
    if args[0] != '':    
        directory = cmds.workspace(q=True, rd=True) + cmds.radioCollection('wip_or_publish', q=True, sl=True) + "/sequence/" + args[0] + "/"
        
        cmds.menuItem(l='', parent='shot_id|OptionMenu')
        for folder in [name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]:
            cmds.menuItem(folder, parent='shot_id|OptionMenu')
            
        cmds.optionMenuGrp('shot_id', e=True, en=True)
        cmds.setParent('..')
        load_asset_types("hawk tuah")
    else:
        cmds.optionMenuGrp('shot_id', e=True, en=False, dai=True)
        
        cmds.optionMenuGrp('asset_types', e=True, en=True)
        cmds.textFieldGrp('search_filter', e=True, en=False)
        
        load_asset_types('')

def load_asset_types(*args):
    #Get the possible asset types and load into the dropdown
    cmds.optionMenuGrp('asset_types', e=True, dai=True)
    
    if args[0] == '':
        #If no sequence is specified, allow for models and rigs
        cmds.optionMenuGrp('asset_types', e=True, dai=True)
        
        cmds.menuItem(l='', parent='asset_types|OptionMenu')
        cmds.menuItem('Model', parent='asset_types|OptionMenu')
        cmds.menuItem('Rig', parent='asset_types|OptionMenu')
    else:
        #If sequence is specified, allow for layout, lighting and animation
        cmds.menuItem(l='', parent='asset_types|OptionMenu')
        cmds.menuItem('Layout', parent='asset_types|OptionMenu')
        cmds.menuItem('Animation', parent='asset_types|OptionMenu')
        cmds.menuItem('Lighting', parent='asset_types|OptionMenu')
        
    cmds.setParent('..')
   
def file_open_tool():
    #Create initial window
    if cmds.window('fileOpenTool', exists = True):
        cmds.deleteUI('fileOpenTool')
    cmds.window('fileOpenTool', resizeToFitChildren=True)
   
    cmds.columnLayout(adj=True)
    
    #Title
    cmds.separator(h=10)
    cmds.text("Asset Loading System", fn="boldLabelFont")
    cmds.separator(h=10)
   
    #WIP or Publish Radio Buttons
    cmds.rowLayout(nc=4, adj=1)
    cmds.text('Publish or WIP?')
    cmds.radioCollection('wip_or_publish')
    cmds.radioButton( 'wip', label='WIP', sl=True, cc=find_mb_files )
    cmds.radioButton( 'publish', label='Publish' )
    cmds.setParent('..')
    
    #Sequence selection instruction
    cmds.separator(h=10)
    cmds.text("To load a layout, lighting scene or animation, please specify the sequence and shot you wish to load from. \nIf neither are filled in, you can load models and rigs.")
    
    #Sequence selection dropdown
    cmds.columnLayout(adj=True, cal="center")
    cmds.optionMenuGrp('sequence_id', l='Specify sequence?', adj=1, cal=[1,"center"], cc=get_shots)
    get_sequences()
    
    #Shot selection dropdown
    cmds.columnLayout(adj=True)
    cmds.optionMenuGrp('shot_id', l='Specify shot? Every shot will be searched if left empty.', cc=find_mb_files, en=False, adj=1, cal=[1,"center"])
   
    cmds.separator(h=10)
    cmds.columnLayout(adj=True)
    cmds.setParent("..")
    
    #Asset types dropdown    
    cmds.optionMenuGrp('asset_types', l='What asset type do you want to open?', cc=find_mb_files, adj=1)
    load_asset_types('')
    
    #Results title
    cmds.separator(h=10)    
    cmds.text("Results", fn="boldLabelFont")
    
    #Filter search results
    cmds.textFieldGrp('search_filter', l='Filter results', en = False, tcc=search, adj=1)
    
    #Results instruction
    cmds.text("results_instruction", l="No files found")
   
    #Show search results
    cmds.textScrollList('searchResults', sc=update_versions)
   
    #Version number dropdown
    cmds.optionMenuGrp('version_number_dropdown', l='Version Number?', en = False, adj=1)
   
    #Load button
    cmds.separator(h=10)
    cmds.button('load_file', l='Load file', en = False, c=load_file)
   
    cmds.showWindow('fileOpenTool')

#Define global variables
current_files = {}
current_keys = []

#Run initial window
file_open_tool()