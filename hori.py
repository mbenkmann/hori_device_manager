#!/usr/bin/python
'''
The MIT License (MIT)

Copyright (c) 2023 Matthias S. Benkmann

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

'''
import sys
import usb.core
import usb.util
import time
import typing

PROFILE_MEM_SIZE = 421

seqnum = 0
devnum = 0

GIP_REQUEST = 0xf
GIP_REPLY = 0x10

CMD_WRITEMEM = 3
CMD_READMEM = 4
CMD_SWITCH_PROFILE = 7
CMD_GET_VERSION = 9
CMD_GET_PROFILE = 0xb

REPLY_MEM = 5
REPLY_DONE = 6
REPLY_VERSION = 0xa
REPLY_PROFILE = 0xc

# Default values to write to a profile starting at offset 0x20 (i.e. after the profile name)
PROFILE_DEFAULT = [
    0x00, 0x00, 0x01, 0x32, 0x32, 0x01, 0x32, 0x32, 0x01, 0x32, 0x32, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x20, 0x20, 0x20, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x00, 0x00, 0x00, 0x01,
    0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x00, 0x00, 0x00, 0x01, 0x02, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x00, 0x00, 0x00, 0x01, 0x02, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x00, 0x00, 0x00, 0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x01, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x0d, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x01, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x0e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x0c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x13, 0x01,
    0x37, 0x37, 0x00, 0x00, 0x01, 0x0c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x14, 0x01, 0x37, 0x37,
    0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01
]

BUTTON2OFS = {
    "A": 0xff,
    "B": 0x10d,
    "X": 0x11b,
    "Y": 0x129,
    "LB": 0x73,
    "RB": 0x81,
    "LT": 0xe3,
    "RT": 0xf1,
    "LSB": 0x8f,
    "RSB": 0x9d,
    "SELECT": 0x161,
    "VIEW": 0x161,
    "GUIDE": 0x153,
    "XBOX": 0x153,
    "SHARE": 0x17d,
    "START": 0x16f,
    "MENU": 0x16f
}

FUNCTION2CODE = {
    "A": 15,
    "B": 16,
    "X": 17,
    "Y": 18,
    "LB": 5,
    "RB": 6,
    "LT": 13,
    "RT": 14,
    "LSB": 7,
    "RSB": 8,
    "VIEW": 0x16,
    "SELECT": 0x16,
    "XBOX": 0x15,
    "GUIDE": 0x15,
    "SHARE": 0x18,
    "MENU": 0x17,
    "START": 0x17,
    "DPAD-UP": 1,
    "DPAD-DOWN": 2,
    "DPAD-LEFT": 3,
    "DPAD-RIGHT": 4,
    "LS-UP": 0x1a,
    "LS-DOWN": 0x19,
    "LS-LEFT": 0x1b,
    "LS-RIGHT": 0x1c,
    "RS-UP": 0x1e,
    "RS-DOWN": 0x1d,
    "RS-LEFT": 0x1f,
    "RS-RIGHT": 0x20,
    "DISABLED": 0x21
}


def hexstr(data: typing.Iterable[int]):
    st = ""
    for b in data:
        st = st + "{:02x}".format(b) + " "
    return st.rstrip()


def horicmd(cmd: typing.Iterable[int]):
    global seqnum
    seqnum += 1
    b = [GIP_REQUEST, 0, seqnum, len(cmd)]
    b.extend(cmd)
    return bytes(b)


def send(dev: usb.core.Device, cmd: typing.Iterable[int]):
    dev.write(2, horicmd(cmd))


def expect(dev: usb.core.Device, reply: int, sz: int = 0) -> bytes:
    timeout = time.time() + .1
    received = []
    while time.time() < timeout:
        try:
            result = dev.read(0x82, 128, 100)
            if result[0] == GIP_REPLY and result[1] == 0 and result[
                    2] == seqnum and result[3] - 1 >= sz and result[4] == reply:
                return result[5:5 + sz]
            received.append(result[0:9])
        except:
            pass

    sys.stderr.write(
        f"Did not receive expected reply {hex(reply)} with sequence number {hex(seqnum)}\n")
    if len(received) > 0:
        sys.stderr.write("Received:\n")
        for r in received:
            sys.stderr.write(hexstr(r) + "\n")
    sys.exit(1)


def get_devices():
    device_list = []
    devs = usb.core.find(find_all=True, idVendor=0x0f0d)
    for d in devs:
        if d.idProduct == 0x0150:
            device_list.append((d.idVendor, d.idProduct, d.bus, d.address))
    return device_list


def check_device():
    device_list = get_devices()
    if devnum < 0 or devnum >= len(device_list):
        sys.stderr.write(f"Incorrect device number: {devnum}\n")
        sys.exit(1)


def get_controller() -> usb.core.Device:
    device_list = get_devices()
    dev = usb.core.find(idVendor=device_list[devnum][0],
                        idProduct=device_list[devnum][1],
                        bus=device_list[devnum][2],
                        address=device_list[devnum][3])
    if dev is None:
        sys.stderr.write("Could not find device\n")
        sys.exit(1)

    try:
        dev.detach_kernel_driver(0)
    except:
        pass

    return dev


def release_controller(dev):
    usb.util.dispose_resources(dev)
    try:
        dev.attach_kernel_driver(0)
    except:
        pass


def hexdump(profile, ofs, sz):
    #print(f"Dumping {sz} bytes of mem from profile {profile} at offset {hex(ofs)}")
    dev = get_controller()

    bigblocks = sz // 55
    rest = sz % 55
    result = []

    for b in range(0, bigblocks):
        start = b * 55 + ofs
        send(dev, (CMD_READMEM, profile, start >> 8, start & 255, 55))
        result.extend(expect(dev, REPLY_MEM, 59)[4:])

    if rest > 0:
        start = bigblocks * 55 + ofs
        send(dev, (CMD_READMEM, profile, start >> 8, start & 255, rest))
        result.extend(expect(dev, REPLY_MEM, rest + 4)[4:])

    start = 0
    while start + 8 <= len(result):
        print(hexstr(result[start:start + 8]))
        start += 8
    if start < len(result):
        print(hexstr(result[start:]))

    release_controller(dev)


def write(profile, ofs, data):
    dev = get_controller()
    write_ex(dev, profile.ofs, data)
    release_controller(dev)


def write_ex(dev, profile, ofs, data):
    sz = len(data)
    bigblocks = sz // 55
    rest = sz % 55

    for b in range(0, bigblocks):
        start = b * 55 + ofs
        cmd = [CMD_WRITEMEM, profile, start >> 8, start & 255, 55]
        cmd.extend(data[start - ofs:start - ofs + 55])
        send(dev, cmd)
        expect(dev, REPLY_DONE)

    if rest > 0:
        start = bigblocks * 55 + ofs
        cmd = [CMD_WRITEMEM, profile, start >> 8, start & 255, rest]
        cmd.extend(data[start - ofs:start - ofs + rest])
        send(dev, cmd)
        expect(dev, REPLY_DONE)


def activate_profile(profile):
    print(f"Activating profile {profile}")
    dev = get_controller()
    send(dev, (CMD_SWITCH_PROFILE, profile))
    expect(dev, REPLY_DONE)
    release_controller(dev)


def reset_profile(profile):
    print(f"Resetting profile {profile} to default values")
    write(profile, 0x20, PROFILE_DEFAULT)


def print_active_profile_number():
    dev = get_controller()
    send(dev, (CMD_GET_PROFILE, ))
    result = expect(dev, REPLY_PROFILE, 2)
    print(f"Current profile is {result[0]}")
    release_controller(dev)


def rename_profile(profile: int, name: str):
    if len(name) > 16:
        sys.stderr.write(f"Name too long (must be at most 16 characters): {name}\n")
        sys.exit(1)

    dev = get_controller()

    cmd = [CMD_WRITEMEM, profile, 0, 0, 32]
    for ch in name:
        n = ord(ch)
        cmd.append(n & 255)
        cmd.append((n >> 8) & 255)

    while len(cmd) < 37:
        cmd.append(0)

    send(dev, cmd)
    expect(dev, REPLY_DONE)

    release_controller(dev)


def print_profile_name(profile: int):
    dev = get_controller()
    print_profile_name_ex(dev, profile)
    release_controller(dev)


def print_profile_name_ex(dev: usb.core.Device, profile: int):
    send(dev, (CMD_READMEM, profile, 0, 0, 32))
    name_utf16 = expect(dev, REPLY_MEM, 36)[4:]
    name = ""

    for i in range(16):
        n = (name_utf16[2 * i + 1] << 8) + name_utf16[2 * i]
        if n == 0:
            break
        name += chr(n)

    print(f"{profile}: {name}")


def print_profile_names():
    dev = get_controller()
    print_profile_name_ex(dev, 1)
    print_profile_name_ex(dev, 2)
    print_profile_name_ex(dev, 3)
    print_profile_name_ex(dev, 4)
    release_controller(dev)


def check_mappings(args):
    mappings = []
    for a in args:
        arg = a.upper()
        if arg == "DEFAULT":
            mappings = [(0, 0)]
            continue

        button, _, function = arg.partition("=")
        try:
            mappings.append((BUTTON2OFS[button], FUNCTION2CODE[function]))
        except KeyError:
            sys.stderr.write(f"Incorrect mapping argument: {a}\n")
            sys.exit(1)
    return mappings


def map_buttons(profile, mappings):
    dev = get_controller()

    for m in mappings:
        ofs, code = m
        if ofs == 0:
            write_ex(dev, profile, 0x73, PROFILE_DEFAULT[0x73 - 0x20:])
        else:
            cmd = [CMD_WRITEMEM, profile, ofs >> 8, ofs & 255, 8, 4, 0, 0, 0, 0, 0, 1, code]
            send(dev, cmd)
            expect(dev, REPLY_DONE)

    release_controller(dev)


def print_mappings(profile):
    dev = get_controller()
    print_mappings_ex(dev, profile)
    release_controller(dev)


def print_mappings_ex(dev, profile):
    ofs = 0x73
    sz = 0x185 - 0x73

    bigblocks = sz // 55
    rest = sz % 55
    result = []

    for b in range(0, bigblocks):
        start = b * 55 + ofs
        send(dev, (CMD_READMEM, profile, start >> 8, start & 255, 55))
        result.extend(expect(dev, REPLY_MEM, 59)[4:])

    if rest > 0:
        start = bigblocks * 55 + ofs
        send(dev, (CMD_READMEM, profile, start >> 8, start & 255, rest))
        result.extend(expect(dev, REPLY_MEM, rest + 4)[4:])

    prev_bofs = 0
    for button, bofs in BUTTON2OFS.items():
        if bofs == prev_bofs:  # Skip entry with same offset but different name
            continue
        prev_bofs = bofs

        bofs -= ofs
        function = button
        if result[bofs] == 4 and result[bofs + 6] == 1:  # override active
            function = "DISABLED"
            code = result[bofs + 7]
            for f, c in FUNCTION2CODE.items():
                if c == code:
                    function = f
        print(f"{button}: {function}")


def set_stick(profile, stick):
    stick = stick.upper()
    if stick != "LS" and stick != "RS":
        sys.stderr.write(f"<stick> must be \"LS\" or \"RS\"\n")
        sys.exit(1)

    dev = get_controller()

    if stick == "LS":
        cmd = [
            CMD_WRITEMEM, profile, 1, 0x8a, 18, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0
        ]
    else:
        cmd = [
            CMD_WRITEMEM, profile, 1, 0x8a, 18, 1, 0, 0, 1, 0, 0, 2, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1
        ]

    send(dev, cmd)
    expect(dev, REPLY_DONE)

    release_controller(dev)


def print_profile_stick(profile):
    dev = get_controller()
    print_profile_stick_ex(dev, profile)
    release_controller(dev)


def print_profile_stick_ex(dev, profile):
    send(dev, (CMD_READMEM, profile, 1, 0x8a, 18))
    result = expect(dev, REPLY_MEM, 22)[4:]
    if bytes(result) == bytes([1, 0, 0, 1, 0, 0, 2, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1]):
        print("stick: RS")
    else:
        print("stick: LS")


def devices():
    device_list = get_devices()
    for idx, d in enumerate(device_list):
        vend, prod, bus, addr = d
        dev = usb.core.find(idVendor=vend, idProduct=prod, bus=bus, address=addr)
        print(f"{idx}: {dev.manufacturer} {dev.product}")


def info():
    dev = get_controller()
    for i in (1, 2, 3, 4):
        print("==============================================")
        print_profile_name_ex(dev, i)
        print_mappings_ex(dev, i)
        print_profile_stick_ex(dev, i)

    release_controller(dev)


def check_profile(profile):
    if profile < 1 or profile > 4:
        sys.stderr.write("<profile> must be between 1 and 4\n")
        sys.exit(1)
    return profile


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "-d":
        try:
            devnum = int(sys.argv[2], 10)
            sys.argv = sys.argv[2:]
        except:
            sys.stderr.write(f"Not a number: {sys.argv[2]}\n")
            sys.exit(1)

    if len(sys.argv) < 2:
        sys.stderr.write('''Usage: hori.py [-d <num>] <command> [<args>...]

-d <num>
  Select the device to operate on, if multiple supported devices are
  connected to the computer.

devices
  Lists all devices supported by this program, together with the <num>
  for use with -d.

hexdump <profile> [<ofs> [<size>]]
  Dump <size> bytes starting at <ofs> of config memory for <profile>

write <profile> <ofs> <data>
  Write <data> bytes to config memory of <profile> starting at <ofs>

profile [<profile>]
  With no argument, print out currently active profile.
  With argument, make <profile> active.

name [<profile> [<name>]]
  With no arguments, lists the names of all profiles.
  With only <profile> as argument, lists that profile's name.
  With <profile> and <name>, renames <profile>.

reset <profile>
  Reset all values of <profile>, except for the name, to default values.

map <profile> [default] [<button>=<function> ...]
  If only <profile> is specified, print the current button mappings.
  If <button>=<function> ... arguments are specified, the respective button
  mappings are modified. Buttons not listed are left unchanged.
  If "default" is specified as argument, all button mappings for <profile>
  are reset to their default values.

stick <profile> [ LS | RS ]
  If only <profile> is specified, print whether the analog stick of <profile>
  is configured as LS or RS.
  If "LS" or "RS" is specified, configure analog stick of <profile> to that.

dpad <profile> [ default | <up>,<down>,<left>,<right>,<upleft>,<upright>,<downleft>,<downright> ]
  If only <profile> is specified, print out the D-Pad dead zone of <profile>.
  If "default" is specified, reset the D-Pad dead zone of <profile> to the default.
  <up>,<down>,<left>,<right> is the dead zone of the cardinals (0 to 228, where 228
  is the maximum, i.e. you have to press really hard to activate the direction).
  <upleft>,<upright>,<downleft>,<downright> is the dead zone of the diagonals
  (30 to 255, where 255 is the maximum).

info
  Print out all information that can be extracted from the controller.

<profile> 1..4
<ofs> 0..
<size> 1..
<data> Sequence of numbers in range 0..255
<name> String with maximum of 16 characters
<button> is the name of a button as printed on the controller. The names of
         the special buttons are SELECT/VIEW, GUIDE/XBOX, SHARE, START/MENU.
         Button names are case-insensitive.
<function> specifies what the <button> is supposed to transmit to the PC/console
         when pressed. Available functions are:
         A, B, X, Y, LB, RB, LT, RT, LSB, RSB,
         SELECT, VIEW, GUIDE, XBOX, SHARE, START, MENU,
         DPAD-UP, DPAD-DOWN, DPAD-LEFT, DPAD-RIGHT,
         LS-UP, LS-DOWN, LS-LEFT, LS-RIGHT,
         RS-UP, RS-DOWN, RS-LEFT, RS-RIGHT,
         DISABLED

''')
        sys.exit(1)

    check_device()

    cmd = sys.argv[1]
    if cmd == "devices":
        devices()
    elif cmd == "hexdump":
        if len(sys.argv) < 3:
            sys.stderr.write("Missing argument: <profile>\n")
            sys.exit(1)
        if len(sys.argv) > 5:
            sys.stderr.write("Too many arguments\n")
            sys.exit(1)

        profile = check_profile(int(sys.argv[2], 0))

        start = None
        sz = None
        if len(sys.argv) > 3:
            start = int(sys.argv[3], 0)
        if len(sys.argv) > 4:
            sz = int(sys.argv[4], 0)

        if start is not None:
            if start < 0:
                sys.stderr.write("<ofs> must be greater equal 0\n")
                sys.exit(1)
        else:
            start = 0

        if sz is not None:
            if sz < 1:
                sys.stderr.write("<size> must be greater equal 1\n")
                sys.exit(1)
        else:
            sz = PROFILE_MEM_SIZE - start
            if sz <= 0: sz = 1

        hexdump(profile, start, sz)

    elif cmd == "write":
        if len(sys.argv) < 5:
            sys.stderr.write("USAGE: write <profile> <ofs> <data>\n")
            sys.exit(1)

        profile = check_profile(int(sys.argv[2], 0))

        start = int(sys.argv[3], 0)

        if start < 0:
            sys.stderr.write("<ofs> must be greater equal 0\n")
            sys.exit(1)

        try:
            data = list(map(lambda x: int(x, 0), sys.argv[4:]))
        except ValueError as err:
            sys.stderr.write(f"Error parsing <data>: {str(err)}\n")
            sys.exit(1)

        if not all(x >= 0 and x <= 255 for x in data):
            sys.stderr.write("All <data> arguments must be between 0 and 255\n")
            sys.exit(1)

        print(f"Writing mem of profile {profile} at offset {hex(start)}: {[hex(x) for x in data]} ")
        write(profile, start, data)

    elif cmd == "profile":
        if len(sys.argv) > 3:
            sys.stderr.write("Too many arguments\n")
            sys.exit(1)

        if len(sys.argv) == 3:
            profile = check_profile(int(sys.argv[2], 0))
            activate_profile(profile)

        print_active_profile_number()

    elif cmd == "map":
        if len(sys.argv) < 3:
            sys.stderr.write("Need <profile> argument\n")
            sys.exit(1)

        profile = check_profile(int(sys.argv[2], 0))

        if len(sys.argv) > 3:
            mappings = check_mappings(sys.argv[3:])
            map_buttons(profile, mappings)

        print_mappings(profile)

    elif cmd == "reset":
        if len(sys.argv) > 3:
            sys.stderr.write("Too many arguments\n")
            sys.exit(1)

        if len(sys.argv) < 3:
            sys.stderr.write("Missing profile number\n")
            sys.exit(1)

        profile = check_profile(int(sys.argv[2], 0))
        reset_profile(profile)

    elif cmd == "name":
        if len(sys.argv) == 2:
            print_profile_names()
        else:
            if len(sys.argv) > 4:
                sys.stderr.write("Too many arguments\n")
                sys.exit(1)

            profile = check_profile(int(sys.argv[2], 0))
            if len(sys.argv) == 4:
                rename_profile(profile, sys.argv[3])

            print_profile_name(profile)

    elif cmd == "stick":
        if len(sys.argv) > 4:
            sys.stderr.write("Too many arguments\n")
            sys.exit(1)

        if len(sys.argv) < 3:
            sys.stderr.write("Missing profile number\n")
            sys.exit(1)

        profile = check_profile(int(sys.argv[2], 0))
        if len(sys.argv) == 4:
            set_stick(profile, sys.argv[3])

        print_profile_stick(profile)

    elif cmd == "info":
        if len(sys.argv) > 2:
            sys.stderr.write("Too many arguments\n")
            sys.exit(1)

        info()

    else:
        sys.stderr.write(f"Invalid command: {cmd}\n")
        sys.exit(1)
