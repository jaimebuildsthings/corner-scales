#!/usr/bin/env python3
"""Press test: press each load cell when asked and print the range of raw counts.

    python3 tools/press-test.py
    python3 tools/press-test.py --port /dev/cu.usbmodem5CE51256791

macOS and Linux, Python 3 standard library only. Close any other serial
monitor first: only one program can hold the port.
"""

import argparse
import glob
import os
import select
import sys
import termios
import time

STEPS = ["hands off", "UL", "UR", "LL", "LR", "hands off"]
RECORD_S = 3.0


def find_port():
    ports = sorted(glob.glob("/dev/cu.usbserial*") + glob.glob("/dev/cu.wchusbserial*")
                   + glob.glob("/dev/cu.usbmodem*") + glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*"))
    if len(ports) == 1:
        return ports[0]
    sys.exit(f"Found {len(ports) or 'no'} serial ports {ports}; pick one with --port.")


def open_port(port):
    fd = os.open(port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    a = termios.tcgetattr(fd)
    a[0] = a[1] = a[3] = 0
    a[2] = termios.CS8 | termios.CREAD | termios.CLOCAL
    a[4] = a[5] = termios.B115200
    termios.tcsetattr(fd, termios.TCSANOW, a)
    return fd


def read_counts(fd, seconds):
    """Raw counts from `stream on` rows (t_ms,ch,raw,...) received in the next `seconds`."""
    buf, counts = b"", []
    end = time.monotonic() + seconds
    while (left := end - time.monotonic()) > 0:
        if select.select([fd], [], [], min(left, 0.05))[0]:
            try:
                buf += os.read(fd, 4096)
            except BlockingIOError:
                pass
        while b"\n" in buf:
            line, buf = buf.split(b"\n", 1)
            parts = line.decode(errors="replace").strip().split(",")
            if len(parts) >= 3 and parts[0].isdigit() and parts[1] == "0":
                counts.append(int(parts[2]))
    return counts


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--port", help="serial port (default: the only one found)")
    fd = open_port(ap.parse_args().port or find_port())
    os.write(fd, b"stream on\r\n")
    try:
        for step in STEPS:
            prompt = "Hands off" if step == "hands off" else f"Press and hold {step}"
            input(f"{prompt}, then hit Enter... ")
            read_counts(fd, 0.3)  # drop rows from before Enter
            c = read_counts(fd, RECORD_S)
            if c:
                print(f"  {step}: {min(c)} to {max(c)}  (range {max(c) - min(c)})\n")
            else:
                print(f"  {step}: no data; is the pad streaming?\n")
    except KeyboardInterrupt:
        print()
    finally:
        os.write(fd, b"stream off\r\n")
        os.close(fd)


if __name__ == "__main__":
    main()
