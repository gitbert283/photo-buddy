import click
import subprocess
import questionary
import usb.core
import usb.util
from photo_buddy.data.data_loader import UsbId
from photo_buddy.backup import UsbDevices
import photo_buddy.gphoto2_utils as gputils
import pymtp
import gphoto2cffi as gp


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

@run.command()
@click.option('--list-devices', '-l', help="list connected PTP devices", is_flag=True)
def gphoto(list_devices):
    if list_devices:
        cameras = gputils.get_camera_list()
        click.echo('\n'.join([c[0] for c in cameras]))
    pass


if __name__ ==  '__main__':
    pass
    import sys
    run(sys.argv[1:])