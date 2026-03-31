# Soft Robotic Finger - Wire Tendon Driven (TPU)

A soft robotics 3D-printable finger with a **wire tendon actuation system** for thread keeping, controlled by servo motor. Prints as a single piece in TPU - minimal assembly!

## Overview

```
  DORSAL (back) - strain limiting layer + extensor wire
  ┌──────────────────────────────────────────────────────────────────┐
  │ ┌──────┐╔══╗┌──────┐╔══╗┌─────┐╔═╗┌──────────╮                │
  │ │ Base ││MCP││Middle││PIP││ Tip ││D││Fingertip │⊃ ← Thread     │
  │ │ Seg  ││   ││ Seg  ││   ││ Seg ││I││  + Hook  │⊃   Keeper     │
  │ └──┬───┘╚══╝└──────┘╚══╝└─────┘╚═╝└────┬─────╯                │
  │    │                                     │                       │
  │ Bowden                             Wire anchor                   │
  │ entry                              (crimp)                       │
  └──────────────────────────────────────────────────────────────────┘
  PALM (bottom) - bellows cuts + flexor wire

  ╔══╗ = Bellows joints with tendon pulleys
  ───  = Wire cable through PTFE tube guides
```

## Wire Tendon System

```
                    ┌─────────────────────────────────┐
                    │         FINGER (TPU)             │
                    │                                  │
  ┌────────┐  Bowden│  PTFE    Pulley   PTFE   Pulley │  Anchor
  │ Servo  │  sheath│  seat   redirect  seat  redirect│  (crimp)
  │ Spool  │════════╪══[==]════◎════[==]══◎═══════════╪══●
  │        │        │  guide         guide             │
  └────────┘        │         FLEXOR WIRE              │
                    └─────────────────────────────────┘

  Servo winds spool → wire pulls through Bowden sheath →
  enters finger base → PTFE tube guides in rigid segments →
  redirects around pulleys at bellows joints →
  anchors at fingertip crimp cavity → finger CURLS
```

### How It Works

1. **Servo spool** winds the wire cable (0.5-0.8mm stainless steel or Dyneema)
2. **Bowden sheath** (1mm PTFE tube) routes wire from servo to finger base
3. **PTFE tube seats** in rigid segments provide low-friction wire guides
4. **Pulley nubs** at each bellows joint redirect wire around the bend axis
5. **Wire anchor** at fingertip holds the cable via crimp sleeve or knot
6. **Bellows compress** on palm side as wire pulls → finger curls inward
7. **TPU elasticity** returns finger to straight when wire is released

### Dual Tendon System

| Tendon | Side | Wire | Function |
|--------|------|------|----------|
| **Flexor** | Palm (bottom) | 0.8mm cable | Pulls finger closed |
| **Extensor** | Dorsal (top) | 0.5mm cable | Returns finger open (backup to TPU spring) |

## Structure

```
robotic_finger/
├── 3d_model/
│   ├── robotic_finger.scad              # Main parametric 3D model (OpenSCAD)
│   └── robotic_finger_stl_export.scad   # STL export helper
├── servo_control/
│   ├── finger_servo_control.ino         # Arduino wire tendon controller
│   └── finger_servo_control.py          # Python controller (RPi / Serial)
└── README.md
```

## Hardware Required

| Component | Specification | Purpose |
|-----------|--------------|---------|
| Servo Motor | SG90 or MG90S | Winds/unwinds wire spool |
| Flexor Wire | 0.5-0.8mm stainless cable or braided Dyneema | Main tendon - closes finger |
| Extensor Wire | 0.3-0.5mm cable (optional) | Return tendon - opens finger |
| Bowden Sheath | 1mm ID / 2mm OD PTFE tube, ~15cm | Routes wire from servo to finger |
| PTFE Tube | 1mm ID, cut to 4mm pieces (x4) | Press-fit guides in rigid segments |
| Crimp Sleeves | 1mm aluminum crimp (x2) | Anchor wire at fingertip |
| Controller | Arduino Uno/Nano or Raspberry Pi | Drives servo |
| Thread | Any sewing/craft thread | For testing thread keeper |

**No bolts, pins, or springs needed!** TPU flexibility replaces mechanical joints. Wire + Bowden replaces rigid linkages.

## 3D Printing

### Parts to Print

| Part | Material | PART # | Notes |
|------|----------|--------|-------|
| Soft Finger | **TPU 95A** | 0 | Single print-in-place piece |
| Servo Mount | **TPU 95A** | 1 | Snap-fit servo cradle + Bowden anchor posts |
| Tendon Spool | **PLA** | 2 | Rigid spool - fits on servo horn |
| Bellows Test | **TPU 95A** | 3 | Print first to calibrate settings! |

### TPU Print Settings

| Setting | Value |
|---------|-------|
| Layer Height | 0.2mm |
| Infill | 15-25% gyroid |
| Speed | 20-30 mm/s |
| Retraction | 1-2mm direct / OFF bowden |
| Temp | 220-235°C |
| Bed | 50-60°C |
| Supports | **NONE** |
| Brim | 5-8mm |

### STL Export
1. Open `robotic_finger_stl_export.scad` in OpenSCAD
2. Set `PART` variable (0-5)
3. F6 to render → File > Export > STL

## Assembly

1. **Print** finger (TPU), servo mount (TPU), spool (PLA)
2. **Cut PTFE tube** into 4mm pieces for guide seats + one ~15cm piece for Bowden sheath
3. **Press-fit** PTFE tube pieces into the guide seats in rigid segments
4. **Thread flexor wire**: Push cable from base entry → through PTFE guides → over pulleys → into fingertip anchor cavity. Crimp the end.
5. **Thread extensor wire** (optional): Same route on dorsal side
6. **Insert Bowden sheath** into base entry port. Thread wire through sheath back to servo.
7. **Mount spool** on servo horn
8. **Wrap wire** around spool, clamp with set screw
9. **Snap servo** into mount cradle
10. **Test**: Send `o` (open) and `c` (close) commands to verify wire pull

## Servo Control

### Arduino
Upload `finger_servo_control.ino`. Serial commands (9600 baud):

| Command | Action | Servo Angle |
|---------|--------|-------------|
| `o` | Release wire (open) | 10° |
| `c` | Full pull (close) | 160° |
| `t` | Thread grip tension | 110° |
| `l` | Light curl | 60° |
| `r` | Rest pretension | 45° |
| `k` | Thread keep sequence | auto |
| `+` / `-` | Adjust tension ±15° | current ±15 |
| `0-180` | Exact spool angle | as specified |
| `?` | Show status | - |

### Python
```bash
pip install pyserial
python finger_servo_control.py --mode serial --port /dev/ttyUSB0
```

## Thread Keeping Sequence (`k` command)

```
Step 1: Release wire      → Finger opens fully (place thread in hook)
Step 2: Light pull        → Finger begins to curl around thread
Step 3: Thread grip pull  → Finger closes on thread with medium tension
Step 4: Oscillate ±5°     → Seats thread into guide grooves on hook
Step 5: Hold steady       → Maintains constant grip tension
```

## Customization

Key parameters in `robotic_finger.scad`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `finger_total_length` | 85mm | Overall size |
| `flexor_wire_dia` | 1.0mm | Flexor cable diameter |
| `flexor_channel_dia` | 1.8mm | Channel bore (fits PTFE tube) |
| `bellows_count_mcp` | 5 | More folds = more flex range |
| `bellows_fold_depth` | 3.0mm | Deeper = more bend per fold |
| `pulley_radius` | 2.5mm | Wire redirect radius at joints |
| `bowden_sheath_od` | 4.0mm | Bowden tube outer diameter |
| `spool_radius` | 5.0mm | Wire wrap radius on servo horn |
| `keeper_hook_radius` | 4.0mm | Thread hook size |
