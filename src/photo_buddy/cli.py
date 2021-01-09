import time
import re
import click
import subprocess
import questionary
import usb.core
import usb.util
from photo_buddy.data.data_loader import UsbId
from photo_buddy.backup import UsbDevices
import photo_buddy.gphoto2_utils as gputils
import pymtp
from gi.repository import GLib, Gio


def get_usb_devices_list(type='imaging'):
    usbid = UsbId()
    if type == 'imaging':
        devices_raw = usb.core.find(find_all=True, custom_match=find_class(6))
    else:
        devices_raw = usb.core.find(find_all=True)
    devices = []
    for d in devices_raw:
        ret = usbid.get_usbid_names("{0:0{1}x}".format(d.idVendor, 4), "{0:0{1}x}".format(d.idProduct, 4))
        if ret:
            sn = usb.util.get_string(d, d.iSerialNumber)

            devices.append(' '.join(
                [v for v in ret if v is not None] +
                [sn if sn else '']
            ))

    return devices


class QuestionaryOption(click.Option):

    def __init__(self, param_decls=None, **attrs):
        click.Option.__init__(self, param_decls, **attrs)
        if not isinstance(self.type, click.Choice):
            raise Exception('ChoiceOption type arg must be click.Choice')

    def prompt_for_value(self, ctx):
        val = questionary.select(self.prompt, choices=get_usb_devices_list()).unsafe_ask()
        return val

class find_class(object):
    def __init__(self, class_):
        self._class = class_
    def __call__(self, device):
        # first, let's check the device
        if device.bDeviceClass == self._class:
            return True
        # ok, transverse all devices to find an
        # interface that matches our class
        for cfg in device:
            # find_descriptor: what's it?
            intf = usb.util.find_descriptor(
                                        cfg,
                                        bInterfaceClass=self._class
                                )
            if intf is not None:
                return True

        return False

@click.group()
def run():
    pass


@run.command()
@click.option('--src', '-s', prompt='Device', type=click.Choice(['sony-xa2', 'icloud']), cls=QuestionaryOption)
@click.option('--des', '-d', type=click.Choice(['syno']), cls=QuestionaryOption)
@click.option('--uid', default='1000')
def backup(src, des, uid):
    if src == 'sony-xa2':
        pfind = subprocess.Popen(
            ['find', f'/var/run/user/{uid}/gvfs/', '-name', 'mtp:*'],
            stderr=subprocess.DEVNULL
        )
        out, err = pfind.communicate()
        click.echo(out)

@run.command()
@click.option('--usb-device', '-u', help="add usb device", is_flag=True)
@click.option('--imaging', '-i', help="filter usb imaging devices", is_flag=True, default=True)

def add_backup_point(usb_device, imaging):
    """ scanning connected devices
    """
    if usb_device:
        val = questionary.select("devices found(vendor, product, serial number)", choices=UsbDevices.get_usb_devices_list()).unsafe_ask()

@run.command()
def mtp():
    device = pymtp.MTP()
    device.connect()
    print(device)

@run.command()
@click.option('--list-devices', '-l', help="list connected PTP devices", is_flag=True)
def ptp(list_devices):
    pshowdevices = subprocess.Popen(
        ['gphoto2', '--auto-detect'],
        stderr=subprocess.DEVNULL
    )
    out, err = pshowdevices.communicate()
    click.echo(out)
    pass

def callback_unmount_gio(obj, result):
    pass
    click.echo('callback' + result)
    return True

def umount_gphoto2_usb_gio(usb_addr):

    vm = Gio.VolumeMonitor.get()
    mo = Gio.MountOperation()
    mo.set_anonymous(True)

    for vol in vm.get_volumes():
        # import pdb;
        # pdb.set_trace()
        root = vol.get_activation_root()
        m = re.match(rf'gphoto2://%5Busb%3A{usb_addr}%5D/', root.get_uri())
        if m:
            root.unmount_mountable_with_operation_finish(0, mo,  None, callback_unmount_gio)
            time.sleep(3)
            import pdb; pdb.set_trace()



@run.command()
@click.option('--list-devices', '-l',
              help="list connected devices supporting gphoto2"
                   "(hint:connect your device in PTP)",
              is_flag=True)
@click.option('--auto-detect', '-a',
              help="auto detect camera connected with gphoto2"
                   "(hint:connect your device in PTP)"
                   " and apply further commands",
              is_flag=True)
@click.option('--list-files', '-f',
              help="missing text",
              is_flag=True)
def gp2(list_devices, auto_detect, list_files):
    """ gphoto 2

    Args:
        list_devices:
        auto_detect:
        list_files:

    Returns:

    """
    vm = Gio.VolumeMonitor.get()
    for v in vm.get_volumes():
        name = v.get_name()
        click.echo([name, v.get_uuid(), v.get_activation_root().get_uri()])
    if list_devices:
        cameras = gputils.get_camera_list()
        click.echo('\n'.join([c[0] for c in cameras]))
    elif auto_detect:
        cameras = gputils.get_camera_list()
        camera_str = questionary.select(
            "devices found(name, addr)",
            choices=[c[0] + ', ' + c[1] for c in cameras]).unsafe_ask()
    camera_usbaddr = [c[1] for c in cameras if c[1] in camera_str][0]
    umount_gphoto2_usb_gio(camera_usbaddr.split(':')[1])
    camera = gputils.init_camera(*[c[1] for c in cameras if c[1] in camera_str])


    click.echo(camera.get_summary())



if __name__ ==  '__main__':
    pass
    import sys
    run(sys.argv[1:])