import gphoto2 as gp
import os


def get_camera_list():
    camera_list = list(gp.Camera.autodetect())
    return camera_list

def init_camera(addr):
    camera = gp.Camera()
    # search ports for camera port name
    port_info_list = gp.PortInfoList()
    port_info_list.load()
    idx = port_info_list.lookup_path(addr)
    camera.set_port_info(port_info_list[idx])
    camera.init()
    return camera


def get_file_list(camera, path='/'):
    result = []
    # get files
    for name, value in camera.folder_list_files(path):
        result.append(os.path.join(path, name))
    # read folders
    folders = []
    for name, value in camera.folder_list_folders(path):
        folders.append(name)
    # recurse over subfolders
    for name in folders:
        result.extend(get_file_list(camera, os.path.join(path, name)))
    return result
