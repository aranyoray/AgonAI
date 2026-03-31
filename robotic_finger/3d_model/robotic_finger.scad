// ============================================================
// Soft Robotic Finger - TPU Print-in-Place
// Thread Keeper with Servo Motor Control
// ============================================================
// A soft robotics style finger designed for TPU/TPE flexible
// filament. Features bellows joints, integrated tendon channel,
// and print-in-place design requiring NO assembly.
//
// Print Settings:
//   Material: TPU 95A (NinjaFlex, eSUN TPU, Sainsmart TPU)
//   Layer Height: 0.2mm
//   Nozzle: 0.4mm
//   Infill: 15-25% (gyroid pattern recommended)
//   Speed: 20-30 mm/s (slow for TPU)
//   Retraction: Minimal (1-2mm direct drive, OFF for bowden)
//   Supports: NONE needed (designed for supportless print)
//   Fan: 50-80%
//   Temp: 220-235°C (varies by TPU brand)
//   Bed: 50-60°C
//   Orientation: Print flat on bed, finger pointing up (+X)
// ============================================================

/* ===== PARAMETRIC CONFIGURATION ===== */

// --- Overall Finger ---
finger_total_length = 85;     // Total finger length (mm)
finger_width        = 18;     // Width of finger body (mm)
finger_height       = 14;     // Height/thickness of finger (mm)
corner_radius       = 3;      // Body corner rounding (mm)

// --- Soft Bellows Joints ---
bellows_count_mcp   = 5;      // Number of bellows folds at base joint (MCP)
bellows_count_pip   = 4;      // Number of bellows folds at middle joint (PIP)
bellows_count_dip   = 3;      // Number of bellows folds at tip joint (DIP)
bellows_fold_depth  = 3.0;    // How deep each fold cuts in (mm)
bellows_fold_width  = 1.2;    // Width of each fold (mm)
bellows_gap         = 0.6;    // Gap between folds (mm)
bellows_floor       = 1.5;    // Minimum wall at deepest fold (mm) - strain limiter

// --- Segment Proportions ---
// (base_seg + mcp + mid_seg + pip + tip_seg + dip + fingertip = 1.0)
base_seg_ratio      = 0.18;   // Base/mount segment
mcp_joint_ratio     = 0.14;   // MCP bellows joint
mid_seg_ratio       = 0.16;   // Middle rigid segment
pip_joint_ratio     = 0.12;   // PIP bellows joint
tip_seg_ratio       = 0.14;   // Tip segment
dip_joint_ratio     = 0.10;   // DIP bellows joint
fingertip_ratio     = 0.16;   // Fingertip with thread keeper

// --- Tendon Channel ---
tendon_dia          = 2.0;    // Tendon channel diameter (mm) - for fishing line/cable
tendon_offset_z     = -2.0;   // Tendon offset below center (closer to palm side)
tendon_guide_dia    = 3.5;    // Tendon guide tube inner diameter at entry

// --- Strain Limiting ---
strain_layer_thick  = 0.8;    // Inextensible dorsal (back) layer thickness
strain_embed_depth  = 0.5;    // Depth of fabric/paper embedding channel (dorsal side)

// --- Thread Keeper (Fingertip) ---
keeper_hook_radius  = 4.0;    // Thread hook inner radius
keeper_wall         = 1.8;    // Hook wall thickness
keeper_slots        = 3;      // Number of thread guide grooves
keeper_slot_dia     = 1.5;    // Thread groove diameter
keeper_opening_ang  = 70;     // Hook opening angle (degrees)

// --- Grip Texture (Palm Side) ---
grip_bump_dia       = 1.5;    // Micro grip bump diameter
grip_bump_height    = 0.6;    // Bump height
grip_bump_spacing   = 3.0;    // Space between bumps

// --- Servo Mount Base ---
base_width          = 45;
base_depth          = 35;
base_height         = 6;
servo_body_w        = 23.0;   // SG90 body width
servo_body_d        = 12.5;   // SG90 body depth
servo_body_h        = 22.0;   // SG90 body height
servo_tab_w         = 32.0;   // Tab-to-tab width
servo_screw_dia     = 2.2;

// --- Pneumatic Air Chamber (optional) ---
// Set use_pneumatic = true for pneumatic actuation instead of tendon
use_pneumatic       = false;
air_chamber_wall    = 1.5;    // Pneumatic chamber wall thickness
air_channel_dia     = 3.0;    // Air supply tube diameter
air_chamber_expand  = 2.5;    // Max expansion gap per bellows

// --- Resolution ---
$fn = 64;


/* ===== DERIVED DIMENSIONS ===== */

L = finger_total_length;
base_len     = L * base_seg_ratio;
mcp_len      = L * mcp_joint_ratio;
mid_len      = L * mid_seg_ratio;
pip_len      = L * pip_joint_ratio;
tip_len      = L * tip_seg_ratio;
dip_len      = L * dip_joint_ratio;
ftip_len     = L * fingertip_ratio;

W = finger_width;
H = finger_height;
tendon_z = H/2 + tendon_offset_z;


/* ===== PRIMITIVE MODULES ===== */

// Rounded rectangle cross-section (2D)
module rounded_rect_2d(w, h, r) {
    offset(r) offset(-r) square([w, h], center = true);
}

// Rounded box (3D)
module rounded_box(lx, ly, lz, r) {
    translate([0, 0, lz/2])
        hull() {
            for (x = [-lx/2 + r, lx/2 - r])
                for (y = [-ly/2 + r, ly/2 - r])
                    translate([x, y, 0])
                        cylinder(r = r, h = lz, center = true);
        }
}

// Soft body segment (rigid-ish section between bellows)
module soft_segment(length, width, height) {
    difference() {
        // Outer body
        translate([length/2, 0, height/2])
            rounded_box(length, width, height, corner_radius);

        // Tendon channel
        translate([-1, 0, tendon_z])
            rotate([0, 90, 0])
                cylinder(d = tendon_dia, h = length + 2);

        // Pneumatic chamber (if enabled)
        if (use_pneumatic) {
            translate([length/2, 0, height/2 + 1])
                rounded_box(length - air_chamber_wall*2,
                           width - air_chamber_wall*2,
                           height - air_chamber_wall*2 - 2,
                           corner_radius - 1);
        }
    }
}


/* ===== BELLOWS JOINT MODULE ===== */
// The core soft robotics element - accordion-style folds that
// allow bending when tendon is pulled. Asymmetric design:
// - Palm side (bottom): deep cuts allow compression/bending
// - Dorsal side (top): thin strain-limiting layer prevents over-extension

module bellows_joint(length, width, height, num_folds) {
    fold_pitch = length / num_folds;

    difference() {
        // Solid block for the joint region
        translate([length/2, 0, height/2])
            rounded_box(length, width, height, min(corner_radius, fold_pitch/3));

        // Bellows cuts from PALM SIDE (bottom) - allows bending
        for (i = [0 : num_folds - 1]) {
            x_pos = fold_pitch * (i + 0.5);

            // V-shaped bellows cut from bottom
            translate([x_pos, 0, -0.1])
                linear_extrude(height = height - bellows_floor - strain_layer_thick)
                    rounded_rect_2d(bellows_fold_width, width - bellows_floor * 2,
                                    bellows_fold_width / 4);

            // Widen the cut at the bottom for better flex
            translate([x_pos, 0, -0.1])
                linear_extrude(height = bellows_fold_depth)
                    rounded_rect_2d(bellows_fold_width * 1.8,
                                    width - bellows_floor,
                                    bellows_fold_width / 3);
        }

        // Side relief cuts for lateral compliance
        for (i = [0 : num_folds - 1]) {
            x_pos = fold_pitch * (i + 0.5);
            for (side = [-1, 1]) {
                translate([x_pos, side * (width/2 + 0.1), height * 0.3])
                    rotate([0, 0, 0])
                        linear_extrude(height = height * 0.4)
                            rounded_rect_2d(bellows_fold_width * 0.8,
                                            bellows_fold_depth, 0.3);
            }
        }

        // Tendon channel passes through joint
        translate([-1, 0, tendon_z])
            rotate([0, 90, 0])
                cylinder(d = tendon_dia, h = length + 2);

        // Pneumatic expansion chambers between folds
        if (use_pneumatic) {
            for (i = [0 : num_folds - 2]) {
                x_pos = fold_pitch * (i + 1);
                translate([x_pos, 0, height/2])
                    rounded_box(fold_pitch - bellows_fold_width,
                               width - air_chamber_wall*2,
                               height - air_chamber_wall*3,
                               1);
            }
        }
    }

    // Strain-limiting dorsal ridge (top surface reinforcement)
    translate([length/2, 0, height - strain_layer_thick/2])
        rounded_box(length, width * 0.6, strain_layer_thick, 1);
}


/* ===== THREAD KEEPER FINGERTIP ===== */

module thread_keeper_tip(length, width, height) {
    union() {
        // Fingertip body (slightly tapered)
        difference() {
            hull() {
                // Base
                translate([0, 0, height/2])
                    rounded_box(2, width, height, corner_radius);
                // Tip (narrower)
                translate([length * 0.7, 0, height/2])
                    rounded_box(2, width * 0.7, height * 0.85, corner_radius * 0.7);
            }

            // Tendon channel to anchor point
            translate([-1, 0, tendon_z])
                rotate([0, 90, 0])
                    cylinder(d = tendon_dia, h = length * 0.8);

            // Tendon anchor cavity (tie-off point)
            translate([length * 0.65, 0, tendon_z])
                sphere(d = tendon_dia * 2.5);
        }

        // Thread keeper hook
        translate([length * 0.75, 0, height/2])
            thread_hook(width);

        // Soft grip texture on palm side
        grip_texture(length * 0.6, width * 0.65, 0);
    }
}

// C-shaped hook for thread retention
module thread_hook(width) {
    rotate([90, 0, 0])
    translate([0, 0, -width/2])
    linear_extrude(height = width)
    difference() {
        // Outer hook
        circle(r = keeper_hook_radius + keeper_wall);

        // Inner opening
        circle(r = keeper_hook_radius);

        // Hook mouth opening
        rotate([0, 0, -keeper_opening_ang/2])
            translate([0, 0])
                polygon([
                    [0, 0],
                    [(keeper_hook_radius + keeper_wall + 1) * cos(0),
                     (keeper_hook_radius + keeper_wall + 1) * sin(0)],
                    [(keeper_hook_radius + keeper_wall + 1) * cos(keeper_opening_ang),
                     (keeper_hook_radius + keeper_wall + 1) * sin(keeper_opening_ang)]
                ]);
    }

    // Thread guide grooves (slots cut into the hook)
    for (i = [0 : keeper_slots - 1]) {
        y_pos = -width/2 + (width / (keeper_slots + 1)) * (i + 1);
        translate([0, y_pos, 0])
            rotate([90, 0, 0])
                translate([keeper_hook_radius + keeper_wall/2, 0, 0])
                    cylinder(d = keeper_slot_dia, h = keeper_wall + 1, center = true);
    }
}


/* ===== GRIP TEXTURE ===== */
// Biomimetic micro-bumps on palm side for better thread/object grip

module grip_texture(length, width, z_offset) {
    cols = floor(length / grip_bump_spacing);
    rows = floor(width / grip_bump_spacing);

    for (ix = [0 : cols - 1]) {
        for (iy = [0 : rows - 1]) {
            // Offset every other row for hexagonal packing
            x_off = ix * grip_bump_spacing + (iy % 2) * (grip_bump_spacing / 2);
            y_off = iy * grip_bump_spacing - width/2;

            translate([x_off + grip_bump_spacing/2, y_off + grip_bump_spacing/2, z_offset])
                sphere(d = grip_bump_dia);
        }
    }
}


/* ===== TENDON GUIDE TUBES ===== */
// Small tubes at each joint to keep tendon aligned during bending

module tendon_guide(height) {
    difference() {
        cylinder(d = tendon_guide_dia + 1.5, h = height);
        translate([0, 0, -0.5])
            cylinder(d = tendon_guide_dia, h = height + 1);
    }
}


/* ===== STRAIN LIMIT CHANNEL ===== */
// Dorsal (back) channel for embedding inextensible layer
// (paper, fabric strip, or fishing line) to prevent over-extension

module strain_limit_channel(length, width) {
    translate([length/2, 0, H - strain_embed_depth/2])
        cube([length, width * 0.5, strain_embed_depth], center = true);
}


/* ===== SERVO MOUNT (TPU compatible) ===== */

module soft_servo_mount() {
    difference() {
        union() {
            // Flexible base plate
            rounded_box(base_width, base_depth, base_height, 4);

            // Servo cradle with snap-fit walls
            translate([0, 0, base_height]) {
                difference() {
                    rounded_box(servo_body_w + 4, servo_body_d + 4, servo_body_h, 2);
                    // Servo cavity
                    translate([0, 0, -0.5])
                        cube([servo_body_w, servo_body_d, servo_body_h + 1], center = true);
                }

                // Snap-fit tabs (TPU flex allows snap insertion)
                for (side = [-1, 1]) {
                    translate([side * (servo_body_w/2 + 1), 0, servo_body_h * 0.6])
                        rotate([0, side * 15, 0])
                            cube([1.5, servo_body_d * 0.4, 3], center = true);
                }
            }

            // Tendon routing post
            translate([servo_body_w/2 + 5, 0, base_height])
                difference() {
                    cylinder(d = 8, h = 10);
                    translate([0, 0, -1])
                        cylinder(d = tendon_guide_dia, h = 12);
                    // Side slot for tendon insertion
                    translate([0, -0.8, 3])
                        cube([10, 1.6, 12]);
                }

            // Finger attachment tab
            translate([base_width/2 - 2, 0, base_height + servo_body_h])
                rounded_box(10, W, 4, 2);
        }

        // Base screw holes
        for (x = [-base_width/2 + 5, base_width/2 - 5])
            for (y = [-base_depth/2 + 5, base_depth/2 - 5])
                translate([x, y, -1])
                    cylinder(d = 3.2, h = base_height + 2);

        // Servo tab screw holes
        for (x = [-servo_tab_w/2 + 2, servo_tab_w/2 - 2])
            translate([x, 0, base_height + 15])
                rotate([90, 0, 0])
                    cylinder(d = servo_screw_dia, h = base_depth, center = true);

        // Wire pass-through
        translate([0, 0, base_height/2])
            rotate([90, 0, 0])
                cylinder(d = 5, h = base_depth + 2, center = true);

        // Pneumatic air inlet (if enabled)
        if (use_pneumatic) {
            translate([-base_width/2 + 5, 0, base_height/2])
                rotate([0, 90, 0])
                    cylinder(d = air_channel_dia, h = 15, center = true);
        }
    }
}


/* ===== FULL SOFT FINGER - MONOLITHIC PRINT-IN-PLACE ===== */
// Single piece - no assembly needed!

module soft_finger() {
    x = 0;

    // 1. Base mounting segment
    color("SteelBlue", 0.9)
    translate([x, 0, 0])
        soft_segment(base_len, W, H);

    // Tendon entry guide
    color("Silver")
    translate([1, 0, tendon_z])
        rotate([0, 90, 0])
            tendon_guide(3);

    // 2. MCP Joint (base knuckle - most flex)
    color("CornflowerBlue", 0.85)
    translate([base_len, 0, 0])
        bellows_joint(mcp_len, W, H, bellows_count_mcp);

    // 3. Middle rigid segment
    color("SteelBlue", 0.9)
    translate([base_len + mcp_len, 0, 0])
        soft_segment(mid_len, W, H);

    // 4. PIP Joint (middle knuckle)
    color("CornflowerBlue", 0.85)
    translate([base_len + mcp_len + mid_len, 0, 0])
        bellows_joint(pip_len, W, H, bellows_count_pip);

    // 5. Tip segment
    color("SteelBlue", 0.9)
    translate([base_len + mcp_len + mid_len + pip_len, 0, 0])
        soft_segment(tip_len, W, H);

    // 6. DIP Joint (tip knuckle - least flex)
    color("CornflowerBlue", 0.85)
    translate([base_len + mcp_len + mid_len + pip_len + tip_len, 0, 0])
        bellows_joint(dip_len, W, H, bellows_count_dip);

    // 7. Fingertip with thread keeper
    color("LightSkyBlue", 0.9)
    translate([base_len + mcp_len + mid_len + pip_len + tip_len + dip_len, 0, 0])
        thread_keeper_tip(ftip_len, W, H);

    // Strain limit channel along entire dorsal surface
    color("DarkSlateGray", 0.5)
    translate([0, 0, 0])
        strain_limit_channel(L * 0.85, W);
}


/* ===== FULL ASSEMBLY WITH SERVO ===== */

module full_soft_assembly() {
    // Servo mount
    color("DimGray", 0.8)
    translate([-base_width/2, 0, -base_height - servo_body_h - 2])
        soft_servo_mount();

    // Soft finger
    soft_finger();
}


/* ===== RENDER SELECTION ===== */
// Uncomment desired output:

// Full assembly (visualization)
full_soft_assembly();

// Just the finger (for printing)
// soft_finger();

// Just the servo mount (for printing)
// soft_servo_mount();

// Individual bellows joint test piece (print this first to test TPU settings!)
// bellows_joint(15, W, H, 4);

// Thread keeper test
// thread_keeper_tip(ftip_len, W, H);
