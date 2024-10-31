import os
import re
import maya.cmds as cmds
import maya.mel as mel

workspace_path = cmds.workspace(q=True, fullName=True) + "/" #ROOT dir 
print(workspace_path)
wip_path = workspace_path + "wip" #Path to WIP folder
publish_path = workspace_path + "publish" #Path to publish folder

directory = os.path.dirname(cmds.file(q=True, location=True)) #Path to current folder
base_file = os.path.basename(cmds.file(q=True, location=True))
file_name = base_file.rsplit(".", 2)[0]
current_version = base_file.rsplit(".", 2)[1]
file_no_end = file_name + "." + current_version

if not cmds.pluginInfo("fbxmaya", query=True, loaded=True):
    cmds.loadPlugin("fbxmaya")
if not cmds.pluginInfo("mayaUsdPlugin", query=True, loaded=True):
    cmds.loadPlugin("mayaUsdPlugin")
    
#mel.eval("FBXExportBakeComplexAnimation -v true")
#mel.eval("FBXExportBakeComplexStart -v " + str(cmds.playbackOptions(q=True, min=True)))
#mel.eval("FBXExportBakeComplexEnd -v " + str(cmds.playbackOptions(q=True, min=True)))
#mel.eval("FBXExportBakeComplexStep -v 1")
#mel.eval("FBXExportConstraints -v false")

def get_latest_version():
    wip_dir = wip_path + re.sub(wip_path, "", re.sub(publish_path, "", directory))
    latest_version = -1
    latest_file = None
    for current_file in os.listdir(wip_dir):
        if current_file.rsplit(".", 2)[0] == file_name:
            version_number = int(re.search(r'\.v(\d+)', current_file).group(1))
            if version_number > latest_version:
                latest_version = version_number
                latest_file = os.path.join(directory, current_file)
    return latest_file
    
def save_file():
    cmds.text(feedback, e=True, label = "Saving...")
    #Gets latest version and "version it up"
    latest_file = get_latest_version()
    new_version_number = int(re.search(r'\.v(\d+)', latest_file).group(1)) + 1 if latest_file else 1
    new_file_path = os.path.join(directory, f"{file_name}.v{new_version_number:03d}.mb")
    #Rename and save file to new path
    cmds.file(rename=new_file_path)
    cmds.file(save=True, type="mayaBinary")
    cmds.text(feedback, e=True,  label="Finished!")

def publish_button():
    cmds.text(feedback, e=True, label ="Publishing...")
    #Non-shot files
    pub_dir = publish_path + re.sub(wip_path, "", re.sub(publish_path, "", directory))
    #Mean shot file and must export each asset inside
    if cmds.objExists("character") and cmds.nodeType("character") == "transform" and cmds.objExists("prop") and cmds.nodeType("prop") == "transform":
        character_group = cmds.listRelatives("character", children=True, fullPath=True) or []
        prop_group = cmds.listRelatives("prop", children=True, fullPath=True) or []
        list = character_group + prop_group
        for asset in list:
            print(asset)
            group_all = cmds.listRelatives(asset, children=True, allDescendents=True, fullPath=True) or []
            group_all.append(asset)
            cmds.select(asset, replace=True)
            asset_name = asset.rsplit(":", 1)[1]
            new_file_name = re.sub("_animation", "_" + asset_name + "_animation", file_no_end)
            export_asset(pub_dir, new_file_name)
        
    else:
        export_file(pub_dir, file_no_end)
    publish_copy(pub_dir)
    save_file()
    
def export_asset(pub_dir, name):
    caches_dir = re.sub("/source", "/caches", pub_dir)
    #Export fbx
    fbx_dir = caches_dir + "/fbx"
    if not os.path.exists(fbx_dir):os.makedirs(fbx_dir)
    fbx_file = fbx_dir + "/" + name + ".fbx"
    #Groups are selected before
    #cmds.file(fbx_file, force=True, options="v=0", type="FBX export", pr=True, es=True)
    start_frame = cmds.playbackOptions(q=True, min=True)
    end_frame = cmds.playbackOptions(q=True, max=True)
    command = f'FBXExport -f "{fbx_file}" -s true;'
    mel.eval(command)
    take_name = "animation"
    #cmds.FBXExport(f=fbx_file, s=True)  # Export selection only
    f'FBXExportSplitAnimationIntoTakes -v "{take_name}" {start_frame} {end_frame};'
    mel.eval(command)
    #Export USD
    usd_dir = caches_dir + "/usd"
    if not os.path.exists(usd_dir):os.makedirs(usd_dir)
    usd_file = usd_dir + "/" + name + ".usd"
    cmds.mayaUSDExport(
        file=usd_file,
        selection=True,
        frameRange=(start_frame, end_frame),
        exportSkels="auto",
        exportSkin="auto",
        nnu=True
    )
    
def export_file(pub_dir, name):
    caches_dir = re.sub("/source", "/caches", pub_dir)
    #Export fbx
    fbx_dir = caches_dir + "/fbx"
    if not os.path.exists(fbx_dir):os.makedirs(fbx_dir)
    fbx_file = fbx_dir + "/" + name + ".fbx"
    cmds.select(all=True)
    cmds.file(fbx_file, force=True, options="v=0", type="FBX export", pr=True, ea=True)
    #Export USD
    usd_dir = caches_dir + "/usd"
    if not os.path.exists(usd_dir):os.makedirs(usd_dir)
    usd_file = usd_dir + "/" + name + ".usd"
    cmds.mayaUSDExport(file=usd_file, selection=True)
    
def publish_copy(pub_dir):
    copy = pub_dir + "/" + base_file
    cmds.file(rename=copy)
    cmds.file(save=True, type="mayaBinary")


WINDOW_NAME = 'SavePublishTool'

if cmds.window(WINDOW_NAME, exists = True):
    cmds.deleteUI(WINDOW_NAME)
    
cmds.window(WINDOW_NAME, widthHeight=(10,10), resizeToFitChildren=True)

cmds.columnLayout(adj=True)

cmds.separator(h=10)
cmds.text('Save your file', w=400)
cmds.separator(h=10)

cmds.button(label = 'Save', command = lambda x: save_file(), sbm="Save current progress and version-up this file", width=300)
cmds.text("Saves your file to: " + wip_path + re.sub(wip_path, "", re.sub(publish_path, "", directory)), width = 300, ww=True)
cmds.separator(h=10)
cmds.button(label = 'Publish', command = lambda x: publish_button(), sbm="Publish assets from this file to specified formats", width=200)
cmds.text("Publish your file to: " + publish_path + re.sub(wip_path, "", re.sub(publish_path, "", directory)), width = 300, ww=True)


cmds.separator(h=10)
feedback = cmds.text(label = '', h=40)
    
cmds.showWindow(WINDOW_NAME)