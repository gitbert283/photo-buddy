import re
from pathlib import Path
class UsbId:

    file = Path(__file__).parent.joinpath('usb.ids')

    @staticmethod
    def get_usbid_names(vendorid, deviceid=None, interfaceid=None):
        vendor = None
        device = None
        interface = None
        with open(UsbId.file, encoding='iso-8859-1') as f:
            text = f.read()
            m = re.search(fr'\n{vendorid}  (.*?)\n', text)
            if m:
                vendor = m.group(1)
                if deviceid:
                    m = re.search(f'\t{deviceid}  (.*?)\n', text[m.end():])
                    if m:
                        device = m.group(1)
                if interfaceid:
                    m = re.search(f'\t\t{interfaceid}  (.*?)\n', text[m.end():])
                    if m:
                        interface = m.group(1)
        if not vendor and not device and not interface:
            return None
        else:
            return vendor, device, interface

