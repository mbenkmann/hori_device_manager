# hori_device_manager

Alternative to Hori Device Manager to configure Fighting Commander Octa. This
allows you to use all features of the controller on Linux. You may also want to
use this program on Windows because it permits you to remap buttons that the
Hori Device Manager does not allow you to remap.

This program is based on reverse engineering of the Game Input Protocol (GIP)
commands used by the HDM to communicate with the controller. See
[hori_gip_reverse_eng.md](hori_gip_reverse_eng.md) if you're interested in
details.

## Installation

Just download `hori.py` and copy it wherever you want.

## Usage

You need Python and PyUSB installed. Just execute `hori.py` without arguments
and it will print its usage.