# Desk test

The first step of the build: four load cells, the Combinator, an HX711 and an ESP32-S3 on the desk, no plates, jacks or cable. **Goal:** press each cell and watch the raw count move.

**Contents:** [Wiring](#wiring) · [Cells to Combinator](#cells-to-combinator) · [Combinator to HX711](#combinator-to-hx711) · [HX711 to ESP32-S3](#hx711-to-esp32-s3) · [Bridge check](#bridge-check) · [Flash](#flash) · [Press test](#press-test)

## Wiring

![Desk test wiring](images/05-wiring-desk.svg)

This uses the **generic green HX711** that comes in the load cell kits. The pad build in [wiring.md](wiring.md) uses the SparkFun HX711, which is powered differently.

## Cells to Combinator

The Combinator has three pads per corner (UL, UR, LL, LR), marked **C**, **+** and **−**. C is the cell's center wire. Each cell is two resistors in a row: a wire at each end and one in the middle.

Wire colors vary by seller, so find the center with a multimeter on Ω:

| Pair (kit cells) | Reading | Meaning |
| --- | --- | --- |
| red–black | ~2 kΩ | the two ends |
| red–yellow | ~1 kΩ | |

The wire not in the ~2 kΩ pair is the center. On the kit cells: **yellow → C, red → +, black → −**, the same on all four corners.

## Combinator to HX711

The Combinator's output holes are labelled with colors on the front. The back of the board shows what they are:

| Combinator | Back of board | Generic HX711 |
| --- | --- | --- |
| RED | E+ | E+ |
| BLK | E− | E− |
| GRN | A+ | A+ |
| WHT | A− | A− |
| YLW | shield | — (unused on the desk) |

The two boards list A+ and A− in opposite orders, so two wires cross. B+ and B− on the HX711 stay empty. Solder these wires straight to the Combinator; loose push-on jumpers make the readings jumpy.

## HX711 to ESP32-S3

| Generic HX711 | ESP32-S3 |
| --- | --- |
| VCC | **3V3** (not 5V) |
| GND | GND |
| DT | GPIO4 |
| SCK | GPIO5 |

The generic board has a single power pin, which also sets its logic level. On 5 V it would send 5 V signals into the ESP32.

On a breadboard, the ESP32-S3 DevKitC straddles the center gap; run solid-core wire from a hole in the same column as each pin.

## Bridge check

Before power-on, measure at the HX711's terminals with the meter on Ω:

| Between | Expect |
| --- | --- |
| E+ and E− | ~2 kΩ |
| A+ and A− | ~2 kΩ, close to E+/E− |

Near 0 Ω is a short (a solder bridge or a stray strand). Open (OL) is a broken joint. Very different readings mean a cell is on the wrong pads. Also check that neighbouring HX711 pins don't beep in continuity mode.

## Flash

Many ESP32-S3 boards have two unlabelled USB-C ports. One is the chip's native USB; the other goes through a USB-serial chip (CH343 or CP2102), and that's the one the console runs on. On macOS, the native port shows up as an Espressif device; if `cargo run` connects but the console stays silent, try the other port.

Build and flash as in [firmware/README.md](../firmware/README.md), then type `status`. A working HX711 shows a raw count (any sign), `stable`, and 0 dropped samples.

## Press test

```sh
python3 tools/press-test.py
```

It asks you to press UL, UR, LL and LR in turn and prints the range of raw counts while you hold each one, with a hands-off step at the start and end. Close any serial monitor first.

```text
Hands off, then hit Enter...
  hands off: -614274 to -614060  (range 214)

Press and hold UL, then hit Enter...
  UL: -711531 to -666484  (range 45047)
...
Hands off, then hit Enter...
  hands off: -614177 to -613997  (range 180)
```

**Pass:** every cell moves the count far more than the hands-off range, all in the same direction, and hands-off comes back to the same baseline. A cell that moves it the other way has + and − swapped. A cell that barely moves it has a bad joint or is on the wrong pads.

Next: mount the cells between plates ([assembly.md](assembly.md)) and calibrate ([test-protocol.md](test-protocol.md)).
