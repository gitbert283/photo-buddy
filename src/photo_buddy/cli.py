import click
import subprocess
import questionary
import usb.core
import usb.util
from photo_buddy.data.data_loader import UsbId


def usb_devices(type='imaging'):
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
        val = questionary.select(self.prompt, choices=usb_devices()).unsafe_ask()
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
@click.option('--usb-devices', '-u', help="scan usb devices", is_flag=True)
@click.option('--imaging', '-i', help="filter usb imaging devices", is_flag=True, default=True)
# @click.argument('--device', '-d', prompt='Device', type=click.Choice([]), cls=QuestionaryOption)

def scan(usb_devices, imaging):
    """ scanning connected devices
    """
    if usb_devices:
        usbid = UsbId()
        if imaging:
            devices = usb.core.find(find_all=True, custom_match=find_class(6))
        else:
            devices = usb.core.find(find_all=True)
        devices_choice = []
        for d in devices:
            ret = usbid.get_usbid_names("{0:0{1}x}".format(d.idVendor, 4), "{0:0{1}x}".format(d.idProduct, 4))
            if ret:
                sn = usb.util.get_string(d, d.iSerialNumber).replace('\x00', '')

                devices_choice.append(' '.join(
                    [v for v in ret if v is not None] +
                    [sn if sn else '']
                ))

        val = questionary.select("devices found(vendor, product, serial number)", choices=devices_choice).unsafe_ask()



if __name__ ==  '__main__':
    pass
    import sys
    run(sys.argv[1:])