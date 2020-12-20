import click
import subprocess
import questionary
import usb.core
import usb.util


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


        # f'/var/run/user/{uid}/gvfs/mtp:host=%5Busb%3A001%2C014%5D/Mass\ storage/Pictures/Camera'

@run.command()
def scan():
    imaging = usb.core.find(find_all=True)
    # imaging = usb.core.find(find_all=True, bDeviceClass=0)
    # Python 2, Python 3, to be or not to be
    for d in imaging:
        click.echo(d.idVendor)
        click.echo(d.iManufacturer)
        click.echo(d.idProduct)
        click.echo(d.iSerialNumber)
    pass

if __name__ ==  '__main__':
    pass
    import sys
    run(sys.argv[1:])