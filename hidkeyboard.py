import random
import datetime
from USBIP import BaseStucture, USBDevice, InterfaceDescriptor, DeviceConfigurations, EndPoint, USBContainer

# Emulating USB mouse

# HID Configuration

class HIDClass(BaseStucture):
    _fields_ = [
        ('bLength', 'B', 9),
        ('bDescriptorType', 'B', 0x21),  # HID
        ('bcdHID', 'H'),
        ('bCountryCode', 'B'),
        ('bNumDescriptors', 'B'),
        ('bDescriptprType2', 'B'),
        ('wDescriptionLength', 'H'),
    ]


hid_class = HIDClass(bcdHID=0x0110,  # Mouse
                     bCountryCode=0x0,
                     bNumDescriptors=0x1,
                     bDescriptprType2=0x22,  # Report
                     wDescriptionLength=0x3400)  # Little endian


interface_d = InterfaceDescriptor(bAlternateSetting=0,
                                  bNumEndpoints=1,
                                  bInterfaceClass=3,  # class HID
                                  bInterfaceSubClass=1,
                                  bInterfaceProtocol=1,
                                  iInterface=0)

end_point = EndPoint(bLength=0x7,
                      bDescriptorType=0x05,
                      bEndpointAddress=0x81,
                     bmAttributes=0x3,
                     wMaxPacketSize=0x0008,  # Little endian
                     bInterval=0x0A)  # interval to report


configuration = DeviceConfigurations(bDescriptorType=0x2,
                                      wTotalLength=0x2200,
                                     bNumInterfaces=0x1,
                                     bConfigurationValue=0x1,
                                     iConfiguration=0x0,  # No string
                                     bmAttributes=0xA0,  # valid self powered
                                     bMaxPower=0x32)  # 100 mah current

interface_d.descriptions = [hid_class]  # Supports only one description
interface_d.endpoints = [end_point]  # Supports only one endpoint
configuration.interfaces = [interface_d]   # Supports only one interface


class USBHID(USBDevice):
    bLength = 0x12
    bDescriptorType =0x01
    bMaxPacketSize0 = 0x08
    vendorID = 0x03F0
    productID = 0x0024
    bcdDevice = 0x0300
    bcdUSB = 0x0110
    bNumConfigurations = 0x1
    bNumInterfaces = 0x1
    bConfigurationValue = 0x1
    configurations = []
    bDeviceClass = 0x0
    bDeviceSubClass = 0x0
    bDeviceProtocol = 0x0
    configurations = [configuration]  # Supports only one configuration

    def __init__(self):
        USBDevice.__init__(self)
        self.start_time = datetime.datetime.now()

    def generate_mouse_report(self):

        arr = [0x05, 0x01,                  # USAGE_PAGE (Generic Desktop)
              0x09, 0x06,                 # USAGE (Keyboard)
              0xa1, 0x01,                 # COLLECTION (Application)
                0x05, 0x07,                 # Usage Page (Keyboard/Keypad)
                0x19, 0xE0,                 # Usage Minimum (Keyboard Left Control)
                0x29, 0xE7,                 #Usage Maximum (Keyboard Right GUI)
                0x15, 0x00,                 #Logical Minimum (0)
                0x25, 0x01,                 #Logical Maximum (1)
                0x75, 0x01,                 #Report Size (1)
                0x95, 0x08,                 #Report Count (8)
                0x81, 0x02,                 #Input (Data,Var,Abs,NWrp,Lin,Pref,NNul,Bit)
                0x95, 0x01,                 #Report Count (1)
                0X75, 0X08,                 #Report Size (8)
                0X81, 0X01,                 #Input (Cnst,Ary,Abs)
                0X95, 0X03,                 #Report Count (3)
                0X75, 0X01,                 #Report Size (1)
                0X05, 0X08,                 #Usage Page (LEDs)
                0X19, 0X01,                 #Usage Minimum (Num Lock)
                0X29, 0X03,                 #Usage Maximum (Scroll Lock)
                0X91, 0X02,                 #Output (Data,Var,Abs,NWrp,Lin,Pref,NNul,NVol,Bit)
                0X95, 0X05,                 #Report Count (5)
                0X75, 0X01,                 #Report Size (1)
                0X91, 0X01,                 #Output (Cnst,Ary,Abs,NWrp,Lin,Pref,NNul,NVol,Bit)
                0X95, 0X06,                 #Report Count (6)
                0X75, 0X08,                 #Report Size (8)
                0X15, 0X00,                 #Logical Minimum (0)
                0X26, 0XFF,0x00,                 #Logical Maximum (255)
                0X05,0X07,                  #Usage Page (Keyboard/Keypad)
                0X19,0X00,                  #Usage Minimum (Undefined)
                0X2A,0XFF,0x00,                 #Usage Maximum 
                0X81,0X00,                  #Input (Data,Ary,Abs)
              0XC0]		# End Collection
        return_val = ''
        for val in arr:
            return_val+=chr(val)
        return return_val

    def handle_data(self, usb_req):
        # Sending random mouse data
        # Send data only for 5 seconds
        if (datetime.datetime.now() - self.start_time).seconds < 5:
            return_val = chr(0x0) + chr(random.randint(1, 16)) + chr(random.randint(1, 16)) + chr(random.randint(1, 16))
            self.send_usb_req(usb_req, return_val)


    def handle_unknown_control(self, control_req, usb_req):
        if control_req.bmRequestType == 0x81:
            if control_req.bRequest == 0x6:  # Get Descriptor
                if control_req.wValue == 0x22:  # send initial report
                    print 'send initial report'
                    self.send_usb_req(usb_req, self.generate_mouse_report())

        if control_req.bmRequestType == 0x21:  # Host Request
            if control_req.bRequest == 0x0a:  # set idle
                print 'Idle'
                # Idle
                pass


usb_Dev = USBHID()
usb_container = USBContainer()
usb_container.add_usb_device(usb_Dev)  # Supports only one device!
usb_container.run()

# Run in cmd: usbip.exe -a 127.0.0.1 "1-1"
