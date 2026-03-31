# Soft Robotic Finger - TPU Print-in-Place

A soft robotics style 3D-printable finger for thread keeping, controlled by servo motor. **Prints as a single piece in TPU - no assembly required!**

## Overview

```
  DORSAL (back) - strain limiting layer
  ┌──────────────────────────────────────────────────────────────────┐
  │ ┌──────┐╔══╗┌──────┐╔══╗┌─────┐╔═╗┌──────────╮                │
  │ │ Base ││MCP││Middle││PIP││ Tip ││D││Fingertip │⊃ ← Thread     │
  │ │ Seg  ││   ││ Seg  ││   ││ Seg ││I││  + Hook  │⊃   Keeper     │
  │ └──────┘╚══╝└──────┘╚══╝└─────┘╚═╝└──────────╯                │
  └──────────────────────────────────────────────────────────────────┘
  PALM (bottom) - bellows cuts allow bending
           ═══ ← tendon runs through center

  ╔══╗ = Bellows joints (accordion folds in TPU)
  ⊃    = Thread keeper C-hook with guide grooves
```

## Key Soft Robotics Features

| Feature | Description |
|---------|-------------|
| **Bellows Joints** | Accordion-style folds that compress when tendon pulls, allowing natural bending |
| **Asymmetric Cuts** | Palm-side cuts are deeper than dorsal - finger curls inward only |
| **Strain Limiting** | Thin reinforced dorsal layer prevents over-extension |
| **Print-in-Place** | Entire finger is ONE piece - zero assembly |
| **Tendon Channel** | Internal tube runs full length for fishing line/cable |
| **Grip Texture** | Biomimetic micro-bumps on palm side |
| **Thread Keeper** | C-shaped hook with guide grooves at fingertip |

## Structure

```
robotic_finger/
├── 3d_model/
│   ├── robotic_finger.scad              # Main parametric 3D model (OpenSCAD)
│   └── robotic_finger_stl_export.scad   # STL export helper
├── servo_control/
│   ├── finger_servo_control.ino         # Arduino servo controller
│   └── finger_servo_control.py          # Python controller (RPi / Serial)
└── README.md
```

## TPU Printing Guide

### Recommended TPU Filaments
- **NinjaFlex 85A** - Most flexible, best bellows action
- **eSUN TPU 95A** - Good balance of flex and printability
- **Sainsmart TPU 95A** - Budget-friendly, reliable
- **Overture TPU 95A** - Widely available

### Print Settings

| Setting | Value | Notes |
|---------|-------|-------|
| **Layer Height** | 0.2mm | 0.16mm for finer bellows |
| **Nozzle** | 0.4mm | |
| **Infill** | 15-25% | Gyroid pattern recommended |
| **Print Speed** | 20-30 mm/s | Slower = better for TPU |
| **Travel Speed** | 100 mm/s | |
| **Retraction** | 1-2mm direct / OFF bowden | TPU jams with too much retraction |
| **Temperature** | 220-235°C | Check your filament specs |
| **Bed Temp** | 50-60°C | |
| **Cooling Fan** | 50-80% | |
| **Supports** | **NONE** | Designed supportless! |
| **Brim** | 5-8mm | Helps TPU bed adhesion |
| **Flow Rate** | 100-105% | Slight over-extrusion helps seal |

### Print Order (Recommended)
1. **Print bellows test piece first** (`PART = 2` in export helper)
   - Test that folds flex properly
   - Adjust speed/temp if folds fuse together
2. **Print full finger** (`PART = 0`)
3. **Print servo mount** (`PART = 1`)

### Troubleshooting TPU

| Problem | Solution |
|---------|----------|
| Bellows folds fused shut | Lower temp 5°C, increase fan, slow down |
| Stringing between folds | Reduce retraction to 0.5mm, enable coasting |
| Poor bed adhesion | Use glue stick, increase brim to 10mm |
| Tendon channel blocked | Thread fishing line during print (pause at 50%) |
| Finger too stiff | Reduce infill to 10%, use 85A TPU |
| Finger too floppy | Increase infill to 30%, use 95A TPU |

## How It Works

### Tendon-Driven Bending
```
    RELAXED (tendon slack)          GRIPPING (tendon pulled)
    ┌─────────────────┐              ┌─────────╮
    │ ═══════════════ │              │ ════╗   │
    │ bellows open    │    ──►       │     ║ ╔═╝
    └─────────────────┘              └─────╚═╝
         ═ tendon                    bellows compress
                                     on palm side
```

1. Servo pulls tendon (fishing line running through internal channel)
2. Bellows folds **compress on palm side** (where cuts are deepest)
3. Dorsal strain layer prevents stretching on back side
4. Result: finger **curls inward** naturally - just like a real finger!
5. Release tendon → TPU elasticity returns finger to straight

### Thread Keeping
1. Servo moves finger to open position
2. Thread is placed across the C-hook at fingertip
3. Servo pulls tendon → finger curls and **pinches thread** against hook
4. Guide grooves prevent thread from slipping sideways
5. Release: servo relaxes → finger opens → thread released

## Hardware

| Component | Specification |
|-----------|--------------|
| Servo Motor | SG90 or MG90S micro servo |
| Tendon | 0.5mm braided fishing line (PE braid) |
| Controller | Arduino Uno/Nano or Raspberry Pi |
| Strain Layer | (Optional) Strip of paper/fabric glued on dorsal side |
| Thread | Any sewing/craft thread |

**No bolts, pins, or springs needed!** The TPU flexibility replaces all mechanical joints.

## Assembly (Minimal!)

1. **Print the finger** (single piece!)
2. **Thread the tendon**: Push fishing line through the internal channel from base to tip. Tie a knot at the fingertip anchor cavity.
3. **Attach to servo**: Loop tendon around servo horn or use a crimp
4. **Mount servo** in the TPU servo cradle (snap-fit, no screws needed)
5. **(Optional)** Glue a thin paper/fabric strip along the dorsal surface for extra strain limiting
6. Done!

## Servo Control

Same control code works for both rigid and soft versions.

### Arduino
Upload `finger_servo_control.ino` - serial commands: `o`pen, `c`lose, `t`hread hold, `k` auto sequence.

### Python
```bash
pip install pyserial
python finger_servo_control.py --mode serial --port /dev/ttyUSB0
```

## Customization

All dimensions are parametric in `robotic_finger.scad`:

| Parameter | Default | Effect |
|-----------|---------|--------|
| `finger_total_length` | 85mm | Overall finger size |
| `bellows_count_mcp` | 5 | More folds = more flex at base joint |
| `bellows_fold_depth` | 3.0mm | Deeper = more bend range |
| `bellows_floor` | 1.5mm | Min wall at fold - structural safety |
| `strain_layer_thick` | 0.8mm | Dorsal stiffness (thicker = less backbend) |
| `keeper_hook_radius` | 4.0mm | Thread hook size |
| `use_pneumatic` | false | Set true for air-powered instead of tendon |

## Optional: Pneumatic Actuation

Set `use_pneumatic = true` in the SCAD file to generate internal air chambers instead of tendon-only actuation. Connect a small air pump or syringe to inflate the bellows chambers for bending.
