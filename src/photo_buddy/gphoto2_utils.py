import gphoto2 as gp


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
