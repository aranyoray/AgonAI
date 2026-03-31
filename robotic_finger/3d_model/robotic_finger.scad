// ============================================================
// Robotic Finger with Thread Keeper - Servo Motor Controlled
// ============================================================
// A parametric 3D model of a robotic finger designed to hold
// thread and be actuated by a micro servo motor (SG90/MG90S).
//
// Print Settings:
//   Material: PLA or PETG
//   Layer Height: 0.2mm
//   Infill: 30-50%
//   Supports: Yes (for joint areas)
// ============================================================

/* ---- Global Parameters ---- */

// Finger dimensions
finger_length       = 70;    // Total finger length (mm)
finger_width        = 16;    // Width of each phalanx (mm)
finger_thickness    = 12;    // Thickness/depth of phalanx (mm)
wall_thickness      = 2.0;   // Shell wall thickness (mm)

// Phalanx proportions (fraction of total length)
proximal_ratio  = 0.45;
middle_ratio    = 0.30;
distal_ratio    = 0.25;

// Joint parameters
joint_radius        = 4.0;   // Hinge pin radius (mm)
joint_gap           = 1.0;   // Gap between phalanges at joint (mm)
pin_diameter        = 3.0;   // M3 pin/bolt diameter (mm)
pin_clearance       = 0.3;   // Clearance for pin holes (mm)

// Tendon/thread channel
tendon_channel_dia  = 2.5;   // Diameter of tendon routing channel (mm)
thread_slot_width   = 3.0;   // Width of thread keeper slot (mm)
thread_slot_depth   = 2.0;   // Depth of thread keeper slot (mm)

// Servo mount parameters (SG90 micro servo)
servo_body_w        = 23.0;  // Servo body width (mm)
servo_body_d        = 12.5;  // Servo body depth (mm)
servo_body_h        = 22.0;  // Servo body height (mm)
servo_tab_w         = 32.0;  // Width including mounting tabs (mm)
servo_tab_h         = 2.5;   // Tab thickness (mm)
servo_tab_offset    = 16.0;  // Tab position from bottom (mm)
servo_horn_dia      = 7.0;   // Servo horn hub diameter (mm)
servo_screw_dia     = 2.2;   // Servo mounting screw diameter (mm)

// Thread keeper on distal tip
keeper_hook_radius  = 3.0;
keeper_hook_thick   = 2.0;
keeper_slot_count   = 3;     // Number of thread guide slots

// Base/mount plate
base_width          = 50;
base_depth          = 40;
base_height         = 5;

// Resolution
$fn = 48;


/* ---- Derived Values ---- */

proximal_len = finger_length * proximal_ratio;
middle_len   = finger_length * middle_ratio;
distal_len   = finger_length * distal_ratio;


/* ---- Modules ---- */

// Rounded box primitive
module rounded_box(size, radius) {
    hull() {
        for (x = [radius, size[0] - radius])
            for (y = [radius, size[1] - radius])
                translate([x, y, 0])
                    cylinder(r = radius, h = size[2]);
    }
}

// Single phalanx segment
module phalanx(length, width, thickness, has_proximal_joint, has_distal_joint) {
    difference() {
        // Main body
        rounded_box([length, width, thickness], 2);

        // Hollow interior (save material)
        translate([wall_thickness, wall_thickness, wall_thickness])
            rounded_box([length - 2*wall_thickness,
                         width - 2*wall_thickness,
                         thickness - wall_thickness], 1);

        // Tendon channel running through center
        translate([-1, width/2, thickness/2])
            rotate([0, 90, 0])
                cylinder(d = tendon_channel_dia, h = length + 2);

        // Proximal joint socket (female)
        if (has_proximal_joint) {
            translate([0, width/2, thickness/2])
                rotate([0, 90, 0])
                    cylinder(d = pin_diameter + pin_clearance*2, h = wall_thickness + 1);
        }

        // Distal joint pin hole
        if (has_distal_joint) {
            translate([length - wall_thickness - 0.5, width/2, thickness/2])
                rotate([0, 90, 0])
                    cylinder(d = pin_diameter + pin_clearance*2, h = wall_thickness + 1);
        }
    }

    // Joint knuckle (male) at distal end
    if (has_distal_joint) {
        translate([length + joint_gap/2, width/2, thickness/2])
            difference() {
                // Knuckle cylinder
                rotate([0, 90, 0])
                    cylinder(r = joint_radius, h = 3, center = true);
                // Pin hole
                rotate([0, 90, 0])
                    cylinder(d = pin_diameter + pin_clearance, h = 5, center = true);
            }
    }

    // Joint socket (female) at proximal end
    if (has_proximal_joint) {
        difference() {
            translate([-joint_gap/2 - 1.5, width/2, thickness/2])
                rotate([0, 90, 0])
                    cylinder(r = joint_radius + wall_thickness, h = 3, center = true);
            translate([-joint_gap/2 - 1.5, width/2, thickness/2])
                rotate([0, 90, 0])
                    cylinder(r = joint_radius + pin_clearance, h = 4, center = true);
            // Pin hole through socket
            translate([-joint_gap/2 - 1.5, width/2, thickness/2])
                rotate([0, 90, 0])
                    cylinder(d = pin_diameter + pin_clearance*2, h = 10, center = true);
        }
    }
}

// Thread keeper hook on the fingertip
module thread_keeper() {
    // Hook shape for thread retention
    difference() {
        union() {
            // Main hook body
            translate([0, 0, 0])
                cylinder(r = keeper_hook_radius + keeper_hook_thick, h = finger_width);

            // Guide arm
            translate([0, -keeper_hook_radius - keeper_hook_thick, 0])
                cube([keeper_hook_radius * 3, keeper_hook_thick, finger_width]);
        }

        // Hook opening
        cylinder(r = keeper_hook_radius, h = finger_width + 1);

        // Opening slot
        translate([-keeper_hook_radius - keeper_hook_thick - 1, 0, -0.5])
            cube([keeper_hook_radius * 2 + keeper_hook_thick + 1,
                  keeper_hook_radius + keeper_hook_thick + 1,
                  finger_width + 1]);

        // Thread guide grooves
        for (i = [0 : keeper_slot_count - 1]) {
            slot_z = (finger_width / (keeper_slot_count + 1)) * (i + 1);
            translate([0, 0, slot_z])
                rotate_extrude()
                    translate([keeper_hook_radius + keeper_hook_thick/2, 0, 0])
                        circle(d = thread_slot_width);
        }
    }
}

// Distal phalanx with thread keeper integrated
module distal_phalanx() {
    union() {
        phalanx(distal_len, finger_width, finger_thickness,
                has_proximal_joint = true, has_distal_joint = false);

        // Thread keeper at fingertip
        translate([distal_len + 2, finger_width/2, finger_thickness/2])
            rotate([90, 0, 0])
                translate([0, 0, -finger_width/2])
                    thread_keeper();

        // Grip texture pads on inner surface
        for (i = [0 : 3]) {
            translate([distal_len * 0.2 + i * (distal_len * 0.2),
                       finger_width/2, -0.5])
                cylinder(d = 2, h = 1.5);
        }
    }
}

// Servo mounting bracket
module servo_mount() {
    difference() {
        union() {
            // Base plate
            rounded_box([base_width, base_depth, base_height], 3);

            // Servo cradle walls
            translate([(base_width - servo_body_w) / 2, (base_depth - servo_body_d) / 2, base_height])
            difference() {
                cube([servo_body_w + wall_thickness*2,
                      servo_body_d + wall_thickness*2,
                      servo_body_h]);
                translate([wall_thickness, wall_thickness, -1])
                    cube([servo_body_w, servo_body_d, servo_body_h + 2]);
            }

            // Servo tab supports
            translate([(base_width - servo_tab_w) / 2,
                       (base_depth - servo_body_d) / 2 - wall_thickness,
                       base_height + servo_tab_offset])
                cube([servo_tab_w, servo_body_d + wall_thickness*4, servo_tab_h]);
        }

        // Servo mounting screw holes
        for (x_off = [(base_width - servo_tab_w) / 2 + 2,
                       (base_width + servo_tab_w) / 2 - 2]) {
            translate([x_off, base_depth / 2,
                       base_height + servo_tab_offset - 1])
                cylinder(d = servo_screw_dia, h = servo_tab_h + 2);
        }

        // Base mounting holes (M3)
        for (x = [6, base_width - 6])
            for (y = [6, base_depth - 6])
                translate([x, y, -1])
                    cylinder(d = 3.2, h = base_height + 2);

        // Wire routing channel
        translate([base_width / 2, -1, base_height / 2])
            rotate([-90, 0, 0])
                cylinder(d = 5, h = base_depth + 2);
    }
}

// Tendon anchor point (attaches servo horn to tendon)
module tendon_anchor() {
    difference() {
        union() {
            cylinder(d = servo_horn_dia + 4, h = 3);
            translate([0, 0, 3])
                cylinder(d = 4, h = 5);
        }
        // Servo horn center hole
        translate([0, 0, -1])
            cylinder(d = servo_horn_dia, h = 5);
        // Tendon tie-off hole
        translate([0, 0, 5])
            rotate([90, 0, 0])
                cylinder(d = tendon_channel_dia, h = servo_horn_dia + 6, center = true);
    }
}

// Joint pin (printable)
module joint_pin() {
    difference() {
        union() {
            cylinder(d = pin_diameter - 0.2, h = finger_width + 2);
            // Head
            cylinder(d = pin_diameter + 2, h = 1);
        }
    }
}

// Return spring channel guide
module spring_guide() {
    difference() {
        cube([8, 4, finger_thickness]);
        translate([1, 1, 1])
            cube([6, 2, finger_thickness - 1]);
    }
}


/* ---- Assembly ---- */

module finger_assembly() {
    // Proximal phalanx (connects to servo)
    color("SteelBlue")
        phalanx(proximal_len, finger_width, finger_thickness,
                has_proximal_joint = false, has_distal_joint = true);

    // Middle phalanx
    color("CornflowerBlue")
        translate([proximal_len + joint_gap*2, 0, 0])
            phalanx(middle_len, finger_width, finger_thickness,
                    has_proximal_joint = true, has_distal_joint = true);

    // Distal phalanx with thread keeper
    color("LightSkyBlue")
        translate([proximal_len + middle_len + joint_gap*4, 0, 0])
            distal_phalanx();
}

module full_assembly() {
    // Servo mount base
    color("DimGray")
        translate([-base_width/2 + finger_width/2, -base_depth + finger_width, -base_height - 5])
            servo_mount();

    // Finger
    finger_assembly();

    // Joint pins (shown in place)
    color("Silver") {
        translate([proximal_len + joint_gap, 0, finger_thickness/2])
            rotate([-90, 0, 0])
                translate([0, 0, -1])
                    joint_pin();

        translate([proximal_len + middle_len + joint_gap*3, 0, finger_thickness/2])
            rotate([-90, 0, 0])
                translate([0, 0, -1])
                    joint_pin();
    }

    // Tendon anchor (on servo horn)
    color("Orange")
        translate([finger_width/2, finger_width/2, -10])
            tendon_anchor();
}


/* ---- Render Selection ---- */

// Uncomment the desired output:

// Full assembled view (for visualization)
full_assembly();

// Individual parts for printing (uncomment one at a time):
// translate([0, 30, 0]) phalanx(proximal_len, finger_width, finger_thickness, false, true);
// translate([0, 60, 0]) phalanx(middle_len, finger_width, finger_thickness, true, true);
// translate([0, 90, 0]) distal_phalanx();
// translate([0, 130, 0]) servo_mount();
// translate([0, 180, 0]) tendon_anchor();
// translate([0, 200, 0]) joint_pin();

// Print plate (all parts laid flat):
// module print_plate() {
//     phalanx(proximal_len, finger_width, finger_thickness, false, true);
//     translate([0, 25, 0]) phalanx(middle_len, finger_width, finger_thickness, true, true);
//     translate([0, 50, 0]) distal_phalanx();
//     translate([0, 80, 0]) servo_mount();
//     translate([60, 0, 0]) tendon_anchor();
//     translate([60, 20, 0]) joint_pin();
//     translate([60, 30, 0]) joint_pin();
// }
// print_plate();
