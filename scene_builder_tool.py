#Scene Builder Tool
#This tool is designed to load the latest version of the set as well as the camera, character and prop caches.
import os
import maya.cmds as cmds
import re


#get_sequences() method from Ethan's Asset Loading tool + then tweaked
def get_sequences():
    directory = cmds.workspace(q=True, rd=True) + "publish/sequence/"
    
    cmds.optionMenuGrp('sequence_id', e=True, dai=True)
    
    cmds.menuItem('', parent='sequence_id|OptionMenu')
    for folder in [name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]:
        cmds.menuItem(folder, parent='sequence_id|OptionMenu')
    cmds.setParent('..')

#get_shots() method from Ethan's Asset Loading tool + then tweaked    
def get_shots(*args):
    cmds.textScrollList('set_list', e=True, ra=True)
    cmds.optionMenuGrp('shot_id', e=True, en=False, dai=True)
    
    if args[0] != '':    
        directory = cmds.workspace(q=True, rd=True) + "publish/sequence/" + args[0] + "/"
        
        cmds.menuItem(l='', parent='shot_id|OptionMenu')
        for folder in [name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]:
            cmds.menuItem(folder, parent='shot_id|OptionMenu')
            
        cmds.optionMenuGrp('shot_id', e=True, en=True)
        cmds.setParent('..')
        #load_asset_types("hawk tuah") #ethan what does this mean?????
    else:
        cmds.optionMenuGrp('shot_id', e=True, en=False, dai=True)
        

#function from Ethan's Asset Loading tool    
def pad_to_three_digits(number: int) -> str:
    return f"{number:03}"

#function from Ethan's Asset Loading tool
def get_digits_after_v(input_string):
    # Use regex to search for ".v" followed by digits
    match = re.search(r'\.v(\d+)', input_string)
   
    # If a match is found, return the digits
    if match:
        return match.group(1)
   
    # If no match is found, return None or an appropriate message
    return None

#function from Ethan's Asset Loading tool
def get_part_before_dot(input_string):
    # Find the index of the first period
    period_index = input_string.find('.')
   
    # If no period is found, return the entire string
    if period_index == -1:
        return input_string
   
    # Return the substring before the first period
    return input_string[:period_index]
    
def populate_lists(*arg):
    find_files('Set')
    find_files('Camera')
    find_files('Animation')
        
#find_mb_files() function from Ethan's Asset Loading tool + then tweaked a lot by me
def find_files(*arg):
    global current_files
    global current_keys
    found_files = []
   
    current_files = {}
    directory = cmds.workspace(q=True, rd=True) + "publish/"
    
    supplied_asset = arg[0]
    if (supplied_asset == 'Set'):
        asset_type = 'Model'
        file_type = '.mb'         
        results_field = 'set_list'
        directory += "assets/set/"
        
    elif (supplied_asset == 'Camera'):
        asset_type = 'layout'
        file_type = '.abc'
        results_field = 'camera_list'
        directory += "sequence/" + cmds.optionMenuGrp('sequence_id', q=True, v=True) + "/" + cmds.optionMenuGrp('shot_id', q=True, v=True) + "/layout/caches/"
        
    elif (supplied_asset == 'Animation'):
        asset_type = supplied_asset
        file_type = '.abc'
        results_field = 'animation_list'
        directory += "sequence/" + cmds.optionMenuGrp('sequence_id', q=True, v=True) + "/" + cmds.optionMenuGrp('shot_id', q=True, v=True) + "/animation/caches/"
        
    else:
        print("unknown asset string. aborting")
        return    
     
    # Walk through the directory and subdirectories
    for root, dirs, files in os.walk(directory):
        for name in files:
            print(name)
            # Check if the file has the right extension
            if name.endswith(file_type) and asset_type.lower() != "" and asset_type.lower() in name:
                # Get the full path to the file and append to list
                found_files.append(name)
                
                if get_part_before_dot(name) not in current_files:
                    current_files[get_part_before_dot(name)] = [pad_to_three_digits(int(get_digits_after_v(name)))]
                else:
                    current_files[get_part_before_dot(name)].append(pad_to_three_digits(int(get_digits_after_v(name))))
       
    #Separate array required to load into text list    
    current_keys = []      
    for file_var in current_files:
        current_keys.append(file_var)
           
    cmds.textScrollList(results_field, e=True, ra=True)
    cmds.textScrollList(results_field, e=True, a=current_keys)
    
#function which gathers all of the selected assets and calls the load_file function for each    
def load_files(*args):
    selected_files = []
    
    #gather all the names of the selected assets from the lists
    selected_sets = cmds.textScrollList('set_list', q=True, si=True)
    if selected_sets != None:
        for set in selected_sets:
            selected_files.append(set)
    selected_cameras = cmds.textScrollList('camera_list', q=True, si=True)
    if selected_cameras != None:
        for camera_o in selected_cameras:
            selected_files.append(camera_o)
    selected_animations = cmds.textScrollList('animation_list', q=True, si=True)
    if selected_animations != None:
        for animation in selected_animations:
            selected_files.append(animation)
    
    #loop through all the selected assets and call load_file
    if(selected_files == None or selected_files == []):
        print("No files selected")
    else:
        for file_o in selected_files:
            file_name = find_latest_ver(file_o)
            if (file_name):
                 load_file(file_name)
            else:
                print("ERROR FINDING LATEST VERSION OF FILE")
            
#function which finds the latest version of the file            
def find_latest_ver(*args):
    asset_name = args[0]
    latest_ver = 0
    
    directory = cmds.workspace(q=True, rd=True) + "publish/"
    for root, dirs, files in os.walk(directory):
        for name in files:
            if (asset_name in name and (name.endswith('.mb') or name.endswith('.abc'))):
                ver = pad_to_three_digits(int(get_digits_after_v(name)))
                if int(ver) > int(latest_ver):
                    latest_ver = ver
    file_name = str(asset_name) + ".v" + str(latest_ver) + ".mb"
    return file_name
     
    
#method from ethan's asset loading system tool that has been tweaked by me
def load_file(*args):
    file_name = args[0]
    
    directory = cmds.workspace(q=True, rd=True) + "publish/"
    
    for root, dirs, files in os.walk(directory):
        for name in files:
            if name == file_name:
                cmds.file(root + "/" + file_name, open=True, force=True)

    
def create_ui():
    if cmds.window('sceneBuilder', exists = True):
        cmds.deleteUI('sceneBuilder')
    cmds.window('sceneBuilder', widthHeight=(10,10), resizeToFitChildren=True)
    cmds.columnLayout()
    
    
    #title of tool
    cmds.separator(h=10)
    cmds.text('SCENE BUILDER TOOL', fn='boldLabelFont')
    cmds.separator(h=10)
    cmds.text('Please select sequence and shot.')
    cmds.text('Then, please select which assets to load into scene.')
    
    cmds.separator(h=20)
    cmds.columnLayout(adj=True, cal="right")
    cmds.optionMenuGrp('sequence_id', l='Sequence:', adjustableColumn=1, cl2=["right", "right"], cc=get_shots)
    get_sequences()
    cmds.optionMenuGrp('shot_id', l='Shot:', enable=False, changeCommand=populate_lists, adj=1, cl2=["right", "right"])
    
    populate_lists
    cmds.separator(h=10)
    cmds.text('Set')
    cmds.textScrollList('set_list', h=50, allowMultiSelection=True)
    
    cmds.separator(h=10)
    cmds.text('Camera Cache')
    cmds.textScrollList('camera_list', h=50, allowMultiSelection=True)
    
    cmds.separator(h=10)
    cmds.text('Character + Prop Animation Cache')
    cmds.textScrollList('animation_list', h=50, allowMultiSelection=True)

    cmds.separator(h=10)
    cmds.button('build_scene', l='Build/Update Scene', c=load_files)
   
    
    
    cmds.showWindow('sceneBuilder')

create_ui()



def old_stuff_UNUSED():
    #go through files and create an array of how many different shots there are
    #define shot# dropdown menu and populate it with the different shots
    
    #set title
    cmds.separator(h=10)
    #cmds.text('Set')
    #check if there is a set currently loaded into the scene
        #if no
            #display checkbox for ""load into scene"
    cmds.checkBox('Load set into scene')
        #if yea
            #check if it latest verion
                #if ye
                    #grey out the checkbox make it uncheckable
    cmds.checkBox('Update current set in scene to latest', enable = False)
                #if no
                    #display checkbox "update into scene"
    cmds.checkBox('Update current set in scene to latest')
    #set checkbox
    
    #character title
    cmds.separator(h=10)
    #cmds.text('Character')
    #model checkbox
    cmds.checkBox('Load character model into scene')
    cmds.checkBox('Update character model in scene to latest', enable = False)
    cmds.checkBox('Update current character model in scene to latest')
    #animation checkbox
    cmds.checkBox('Load character animation into scene')
    cmds.checkBox('Update current character animation in scene to latest', enable = False)
    cmds.checkBox('Update current character animation in scene to latest')
    
    #props title
    cmds.separator(h=10)
    #cmds.text('Props')
    #props checkbox
    cmds.checkBox('Load props into scene')
    cmds.checkBox('Update current props in scene to latest', enable = False)
    cmds.checkBox('Update current props in scene to latest')
    
    cmds.separator(h=10)
    #cmds.text('Layout')