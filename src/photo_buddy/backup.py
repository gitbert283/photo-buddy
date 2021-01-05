import usb.core
import usb.util
from photo_buddy.data.data_loader import UsbId


class Backup(object):
    pass


class UsbDevice(object):

    def __init__(self, usb_device):

        self.idVendor = usb_device.idVendor
        self.idProduct = usb_device.idProduct
        self.iSerialNumber = usb_device.iSerialNumber


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


class UsbDevices(object):

    @staticmethod
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
                sn = usb.util.get_string(d, d.iSerialNumber).replace('\x00', '')

                devices.append(' '.join(
                    [v for v in ret if v is not None] +
                    [sn if sn else '']
                ))

        return devices



class BackupSource(Backup):

    def __init__(self, type,):
        pass
