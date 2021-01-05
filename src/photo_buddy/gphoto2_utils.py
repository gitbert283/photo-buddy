import gphoto2 as gp


def get_camera_list():
    camera_list = list(gp.Camera.autodetect())
    return camera_list
