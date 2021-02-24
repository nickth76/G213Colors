'''
  *  The MIT License (MIT)
  *
  *  G213Colors v0.1 Copyright (c) 2016 SebiTimeWaster
  *
  *  Permission is hereby granted, free of charge, to any person obtaining a copy
  *  of this software and associated documentation files (the "Software"), to deal
  *  in the Software without restriction, including without limitation the rights
  *  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  *  copies of the Software, and to permit persons to whom the Software is
  *  furnished to do so, subject to the following conditions:
  *
  *  The above copyright notice and this permission notice shall be included in all
  *  copies or substantial portions of the Software.
  *
  *  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  *  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  *  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  *  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  *  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  *  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  *  SOFTWARE.
'''


from __future__ import print_function
import usb.core
import usb.util
import binascii


standardColor  = 'ffb4aa'         # Standard color, i found this color to produce a white color on my G213
idVendor       = 0x046d           # The id of the Logitech company
idProduct      = {"G213": 0xc336, # The id of the G213
                  "G203": 0xc084} # The id of the G203

#  The USB controll transfer parameters
bmRequestType  = 0x21
bmRequest      = 0x09
wValue         = {"G213": 0x0211,
                  "G203": 0x0210}
wIndex         = 0x0001

# binary commands in hex format
colorCommand   = {"G213": "11ff0c3a{}01{}0200000000000000000000",
                  "G203": "11ff0e3c{}01{}0200000000000000000000"} # field; color
breatheCommand = {"G213": "11ff0c3a0002{}{}006400000000000000",
                  "G203": "11ff0e3c0003{}{}006400000000000000"}     # color; speed
cycleCommand   = {"G213": "11ff0c3a0003ffffff0000{}64000000000000",
                  "G203": "11ff0e3c00020000000000{}64000000000000"}  # speed; brightness

device         = ""               # device resource
productName    = ""               # e.g. G213, G203
isDetached     = {"G213": False,  # If kernel driver needs to be reattached
                  "G203": False}
confFile       = "/etc/G213Colors.conf"


def connectG(Name):
    global device, isDetached, productName
    productName = Name
    print(productName)
    # find G product
    device = usb.core.find(idVendor=idVendor, idProduct=idProduct[productName])
    # if not found exit
    #print(device.manufacturer)
    if device is None:
        raise ValueError("USB device not found!")
    # if a kernel driver is attached to the interface detach it, otherwise no data can be send
    if device.is_kernel_driver_active(wIndex):
        device.detach_kernel_driver(wIndex)
        isDetached[productName] = True
        print("Connected " + productName)


def disconnectG():
    global productName
    # free device resource to be able to reattach kernel driver
    usb.util.dispose_resources(device)
    # reattach kernel driver, otherwise special key will not work
    if isDetached[productName]:
        device.attach_kernel_driver(wIndex)
        print("Disconnected " + productName)

def receiveData():
    device.read(0x82, 64)

def sendData(data):
    global productName
    print("Send data to " + productName)
    print("bmRequestType, bmRequest, wValue[productName], wIndex, binascii.unhexlify(data)")
    print(bmRequestType, bmRequest, wValue[productName], wIndex, binascii.unhexlify(data))
    # free device resource to uest, wValue[productName], wIndex, binascii.unhexlify(data))
    # decode data to binary and send it
    device.ctrl_transfer(bmRequestType, bmRequest, wValue[productName], wIndex, binascii.unhexlify(data))

def sendColorCommand(colorHex, field=0):
    global productName

    sendData(colorCommand[productName].format(str(format(field, '02x')), colorHex))

    if productName == "G213":
        receiveData()

def sendBreatheCommand(colorHex, speed):
    global productName
    sendData(breatheCommand[productName].format(colorHex, str(format(speed, '04x'))))

def sendCycleCommand(speed):
    global productName
    sendData(cycleCommand[productName].format(str(format(speed, '04x'))))

def saveData(data):
    file = open(confFile, "w")
    file.write(data)
    file.close()
