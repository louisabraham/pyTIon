#!/usr/bin/env python3

"""
screenshots from a TI83+/TI84+ in realtime
details on http://merthsoft.com/linkguide/ti83+/screenshot.html
"""


import usb.core
import matplotlib.pyplot as plt


# don't put a delay that is too small because
# the calculator becomes non-responsive
# while it sends the screenshot

delay = 1  # seconds


def data(s):
    return bytearray(int(i, 16) for i in s.split())


def aff(a):
    print(' '.join('%02x' % i for i in a))


calc = usb.core.find(idVendor=0x0451)
calc.set_configuration()
c = calc.get_active_configuration()
ein, eout = c.interfaces()[0].endpoints()

read = ein.read
write = eout.write


def do_screenshot():
    # we have to empty the buffer
    try:
        for i in range(32):
            read(32, 10)
    except:
        pass

    write(data("73 6D 00 00"))

    header = read(32)
    assert bytearray(header) == data('73 56 00 00')

    dat = bytearray()
    for i in range(25):
        x = read(32)
        # aff(x)
        dat += bytearray(x)

    pic, checksum = dat[4:-2], dat[-2:]

    assert checksum[0] + 0x100 * checksum[1] == sum(pic) & 0xffff

    write(data("73 56 00 00"))

    cols = 96
    lines = 64

    matrix = [[1 & (pic[(i * cols + j) // 8] >> (7 - (i * cols + j) % 8))
               for j in range(cols)] for i in range(lines)]

    return matrix


loop = True


def handle_close(evt):
    global loop
    loop = False

fig = plt.figure()
fig.canvas.mpl_connect('close_event', handle_close)

while loop:
    img = do_screenshot()
    plt.imshow(img, cmap='Greys')
    plt.pause(delay)
