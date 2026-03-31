# Robotic Finger - Thread Keeper with Servo Control

A 3D-printable robotic finger designed to hold thread, controlled by a micro servo motor (SG90/MG90S).

## Overview

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  ┌──────────┐  ┌────────┐  ┌───────┬──╮            │
│  │ Proximal │──│ Middle │──│Distal │◎ │← Thread    │
│  │ Phalanx  │  │Phalanx │  │       │  │  Keeper    │
│  └────┬─────┘  └────────┘  └───────┴──╯            │
│       │                                             │
│       │ tendon                                      │
│       │                                             │
│  ┌────┴─────────────┐                               │
│  │   Servo Mount    │                               │
│  │  ┌─────────┐     │                               │
│  │  │  SG90   │     │                               │
│  │  │  Servo  │     │                               │
│  │  └─────────┘     │                               │
│  └──────────────────┘                               │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Structure

```
robotic_finger/
├── 3d_model/
│   ├── robotic_finger.scad          # Main parametric 3D model (OpenSCAD)
│   └── robotic_finger_stl_export.scad  # STL export helper
├── servo_control/
│   ├── finger_servo_control.ino     # Arduino servo controller
│   └── finger_servo_control.py      # Python controller (RPi / Serial)
└── README.md
```

## 3D Model

### Parts List

| Part | Quantity | Description |
|------|----------|-------------|
| Proximal Phalanx | 1 | Base segment, connects to servo |
| Middle Phalanx | 1 | Middle joint segment |
| Distal Phalanx | 1 | Fingertip with thread keeper hook |
| Servo Mount | 1 | Base plate with SG90 cradle |
| Tendon Anchor | 1 | Connects servo horn to tendon |
| Joint Pin | 2 | M3 hinge pins |

### Print Settings

- **Software**: OpenSCAD (free, open-source)
- **Material**: PLA or PETG
- **Layer Height**: 0.2mm
- **Infill**: 30-50%
- **Supports**: Yes (for joint areas)
- **Nozzle**: 0.4mm

### How to Export STL

1. Open `robotic_finger_stl_export.scad` in OpenSCAD
2. Set the `PART` variable (0-6) to select which part to export
3. Press F6 to render
4. File > Export > Export as STL

## Hardware Required

| Component | Specification |
|-----------|--------------|
| Servo Motor | SG90 or MG90S micro servo |
| Controller | Arduino Uno/Nano or Raspberry Pi |
| Tendon | Braided fishing line (0.5-1.0mm) or thin steel cable |
| Joint Pins | M3 x 20mm bolts (2x) |
| Screws | M2 x 8mm for servo mount (2x) |
| Return Spring | Small extension spring or elastic band |
| Thread | Any sewing/craft thread for testing |

## Assembly

1. **Print all parts** using the STL export helper
2. **Insert joint pins** (M3 bolts) through the phalanx joints
3. **Route the tendon** through the tendon channels in each phalanx
4. **Attach tendon anchor** to the servo horn
5. **Mount servo** in the servo cradle on the base plate
6. **Connect tendon** from anchor through proximal → middle → distal phalanx
7. **Add return spring/elastic** on the back side of the finger for extension
8. **Thread the keeper** - pass thread through the hook slots on the fingertip

## Servo Control

### Arduino

Upload `finger_servo_control.ino` to your Arduino.

**Wiring:**
```
Servo Signal → Pin 9
Potentiometer → A0 (optional)
Button → Pin 2 (optional)
```

**Serial Commands** (9600 baud):
- `o` - Open finger
- `c` - Close/grip
- `t` - Thread hold position
- `r` - Rest position
- `k` - Thread keeping sequence (automated)
- `0-180` - Set exact angle

### Python (Raspberry Pi or Serial to Arduino)

```bash
pip install pyserial   # For serial mode

# Serial control (Arduino via USB)
python finger_servo_control.py --mode serial --port /dev/ttyUSB0

# Direct GPIO (Raspberry Pi)
python finger_servo_control.py --mode gpio
```

## Thread Keeping Sequence

The automated thread keeping sequence (`k` command):

1. **Open** - Finger opens fully to receive thread
2. **Position** - Moves to catch position
3. **Grip** - Slowly closes to grip the thread
4. **Secure** - Gentle oscillation to ensure secure hold
5. **Hold** - Maintains steady grip until release command

## Customization

All dimensions in `robotic_finger.scad` are parametric. Key parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `finger_length` | 70mm | Total finger length |
| `finger_width` | 16mm | Width of phalanges |
| `finger_thickness` | 12mm | Depth of phalanges |
| `joint_radius` | 4mm | Hinge joint radius |
| `tendon_channel_dia` | 2.5mm | Tendon routing channel diameter |
| `keeper_hook_radius` | 3mm | Thread keeper hook size |
| `keeper_slot_count` | 3 | Number of thread guide grooves |
