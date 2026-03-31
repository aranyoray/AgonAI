// ============================================================
// STL Export Helper - Soft Robotic Finger (TPU)
// ============================================================
// Export parts for TPU 3D printing.
// In OpenSCAD: Design > Render (F6), then File > Export > STL
//
// PART selection:
//   0 = Complete soft finger (single print-in-place piece!)
//   1 = Servo mount base
//   2 = Bellows test piece (print first to calibrate TPU!)
//   3 = Thread keeper test piece
//   4 = Full assembly (visualization only, not for printing)
//   5 = Single bellows joint (5 folds)
//   6 = Single bellows joint (3 folds)
// ============================================================

PART = 0;  // <-- Change this to select part

include <robotic_finger.scad>;

if (PART == 0) {
    // The entire finger prints as ONE piece - no assembly!
    soft_finger();
} else if (PART == 1) {
    soft_servo_mount();
} else if (PART == 2) {
    // Test piece: small bellows section to calibrate your TPU settings
    // Print this FIRST before printing the full finger
    bellows_joint(15, W, H, 4);
} else if (PART == 3) {
    thread_keeper_tip(ftip_len, W, H);
} else if (PART == 4) {
    full_soft_assembly();
} else if (PART == 5) {
    bellows_joint(18, W, H, 5);
} else if (PART == 6) {
    bellows_joint(12, W, H, 3);
}
