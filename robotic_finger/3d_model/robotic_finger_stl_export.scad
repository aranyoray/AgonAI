// ============================================================
// STL Export Helper - Robotic Finger Parts
// ============================================================
// Use this file to export individual parts as STL files.
// In OpenSCAD: Design > Render (F6), then File > Export > STL
//
// Change the PART variable to export each piece:
//   0 = Proximal phalanx
//   1 = Middle phalanx
//   2 = Distal phalanx (with thread keeper)
//   3 = Servo mount base
//   4 = Tendon anchor
//   5 = Joint pin (print 2x)
//   6 = Full print plate
// ============================================================

PART = 6;  // <-- Change this number to select part

include <robotic_finger.scad>;

if (PART == 0) {
    phalanx(proximal_len, finger_width, finger_thickness, false, true);
} else if (PART == 1) {
    phalanx(middle_len, finger_width, finger_thickness, true, true);
} else if (PART == 2) {
    distal_phalanx();
} else if (PART == 3) {
    servo_mount();
} else if (PART == 4) {
    tendon_anchor();
} else if (PART == 5) {
    joint_pin();
} else if (PART == 6) {
    // Full print plate - all parts
    phalanx(proximal_len, finger_width, finger_thickness, false, true);
    translate([0, 25, 0])
        phalanx(middle_len, finger_width, finger_thickness, true, true);
    translate([0, 50, 0])
        distal_phalanx();
    translate([0, 85, 0])
        servo_mount();
    translate([65, 0, 0])
        tendon_anchor();
    translate([65, 20, 0])
        joint_pin();
    translate([65, 30, 0])
        joint_pin();
}
