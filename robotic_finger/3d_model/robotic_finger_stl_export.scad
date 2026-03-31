// ============================================================
// STL Export Helper - Soft Robotic Finger (TPU + Wire Tendon)
// ============================================================
// Export parts for 3D printing.
// OpenSCAD: Design > Render (F6), then File > Export > STL
//
// PART selection:
//   0 = Complete soft finger (TPU, single print-in-place!)
//   1 = Servo mount base (TPU)
//   2 = Tendon spool (print in PLA for rigidity)
//   3 = Bellows test piece (print first to calibrate TPU!)
//   4 = Thread keeper test piece
//   5 = Full assembly (visualization only, not for print)
// ============================================================

PART = 0;  // <-- Change this to select part

use <robotic_finger.scad>;

if (PART == 0) {
    soft_finger();
} else if (PART == 1) {
    soft_servo_mount();
} else if (PART == 2) {
    tendon_spool();
} else if (PART == 3) {
    bellows_joint(15, 18, 14, 4);
} else if (PART == 4) {
    thread_keeper_tip(13.6, 18, 14);
} else if (PART == 5) {
    full_soft_assembly();
}
