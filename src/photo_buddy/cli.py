import click
import subprocess
import questionary
import usb.core
import usb.util
from photo_buddy.data.data_loader import UsbId


class QuestionaryOption(click.Option):

    def __init__(self, param_decls=None, **attrs):
        click.Option.__init__(self, param_decls, **attrs)
        if not isinstance(self.type, click.Choice):
            raise Exception('ChoiceOption type arg must be click.Choice')

    def prompt_for_value(self, ctx):
        val = questionary.select(self.prompt, choices=self.type.choices).unsafe_ask()
        return val


@click.group()
def run():
    pass


@run.command()
@click.option('--src', '-s', type=click.Choice(['sony-xa2', 'icloud']), cls=QuestionaryOption)
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
def scan(usb_devices):
    """ scanning connected devices

    Returns:

    """

    usbid = UsbId()
    # imaging = usb.core.find(find_all=True)
    imaging = usb.core.find(find_all=True, bDeviceClass=0)
    # Python 2, Python 3, to be or not to be
    for d in imaging:
        hex_idvendor = hex(d.idVendor)[2:]
        hex_idproduct = hex(d.iProduct)[2:]
        ret = usbid.get_usbid_names("{0:0{1}x}".format(d.idVendor, 4), "{0:0{1}x}".format(d.idProduct, 4))
        if ret:
            click.echo(ret)


if __name__ ==  '__main__':
    pass
    import sys
    run(sys.argv[1:])