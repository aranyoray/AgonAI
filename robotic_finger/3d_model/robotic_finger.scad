// ============================================================
// Soft Robotic Finger - TPU Print-in-Place
// Wire Tendon Driven + Thread Keeper + Servo Control
// ============================================================
//
// A soft robotics finger with a complete WIRE TENDON system:
//   - Dual tendon channels (flexor on palm, extensor on dorsal)
//   - PTFE tube guide seats at each joint for low-friction wire routing
//   - Pulley redirects at every bellows joint
//   - Wire crimp anchor at fingertip
//   - Bowden sheath entry port at base
//   - Servo horn tendon spool with wire clamp
//
// Wire: 0.5-0.8mm stainless steel cable or braided Dyneema
// Guide: 1mm ID PTFE tube (Bowden style)
//
// Print Settings:
//   Material: TPU 95A (NinjaFlex, eSUN TPU, Sainsmart TPU)
//   Layer Height: 0.2mm
//   Nozzle: 0.4mm
//   Infill: 15-25% (gyroid pattern recommended)
//   Speed: 20-30 mm/s (slow for TPU)
//   Retraction: Minimal (1-2mm direct drive, OFF for bowden)
//   Supports: NONE needed
//   Fan: 50-80%
//   Temp: 220-235°C
//   Bed: 50-60°C
//   Orientation: Print flat, finger along X axis
// ============================================================

/* ===== PARAMETRIC CONFIGURATION ===== */

// --- Overall Finger ---
finger_total_length = 85;     // Total finger length (mm)
finger_width        = 18;     // Width of finger body (mm)
finger_height       = 14;     // Height/thickness of finger (mm)
corner_radius       = 3;      // Body corner rounding (mm)

// --- Soft Bellows Joints ---
bellows_count_mcp   = 5;      // Bellows folds at base joint (MCP)
bellows_count_pip   = 4;      // Bellows folds at middle joint (PIP)
bellows_count_dip   = 3;      // Bellows folds at tip joint (DIP)
bellows_fold_depth  = 3.0;    // Depth of each fold cut (mm)
bellows_fold_width  = 1.2;    // Width of each fold slit (mm)
bellows_gap         = 0.6;    // Gap between folds (mm)
bellows_floor       = 1.5;    // Min wall at deepest fold (mm) - strain limit

// --- Segment Proportions ---
base_seg_ratio      = 0.18;
mcp_joint_ratio     = 0.14;
mid_seg_ratio       = 0.16;
pip_joint_ratio     = 0.12;
tip_seg_ratio       = 0.14;
dip_joint_ratio     = 0.10;
fingertip_ratio     = 0.16;

// --- Wire Tendon System ---
// Flexor tendon (palm side) - pulls finger closed
flexor_wire_dia       = 1.0;    // Wire cable diameter (mm)
flexor_channel_dia    = 1.8;    // Channel ID for wire (mm) - clearance for PTFE tube
flexor_offset_z       = -3.5;   // Z offset from center (palm side, negative = bottom)
flexor_offset_y       = 0;      // Y offset (centered)

// Extensor tendon (dorsal side) - pulls finger open / provides return
extensor_wire_dia     = 0.8;    // Thinner wire for return
extensor_channel_dia  = 1.5;    // Channel ID (mm)
extensor_offset_z     = 4.5;    // Z offset from center (dorsal side, positive = top)
extensor_offset_y     = 0;

// PTFE tube guide seats (Bowden tube)
ptfe_tube_od          = 2.0;    // PTFE tube outer diameter (mm)
ptfe_tube_id          = 1.0;    // PTFE tube inner diameter (mm)
ptfe_seat_length      = 4.0;    // Length of tube seat in rigid segments (mm)
ptfe_seat_clearance   = 0.15;   // Press-fit clearance (mm)

// Bowden sheath at base entry
bowden_sheath_od      = 4.0;    // Outer cable sheath diameter (mm)
bowden_sheath_id      = 2.0;    // Inner bore (mm)
bowden_entry_depth    = 6.0;    // How deep sheath inserts into base (mm)

// Wire anchor / crimp
wire_anchor_cavity    = 3.0;    // Anchor cavity diameter at fingertip (mm)
wire_anchor_depth     = 4.0;    // Depth of anchor pocket (mm)
wire_clamp_slot_w     = 1.5;    // Slot for wire clamp/crimp sleeve
wire_clamp_slot_h     = 2.0;

// --- Wire Insertion Holes ---
// Open side slots and top/bottom access holes for threading real wire
wire_insert_slot_w    = 1.5;    // Side slot width for wire insertion (mm)
wire_insert_slot_d    = 3.0;    // Slot depth into body (mm)
wire_exit_hole_dia    = 2.5;    // Hole at fingertip end to pull wire through (mm)
wire_base_entry_dia   = 3.0;    // Entry hole diameter at finger base (mm)

// --- Pulley System at Joints ---
pulley_radius         = 2.5;    // Tendon redirect pulley radius (mm)
pulley_width          = 3.0;    // Pulley groove width (mm)
pulley_groove_depth   = 0.8;    // V-groove depth for wire (mm)
pulley_axle_dia       = 1.5;    // Pulley axle hole diameter (mm)

// --- Strain Limiting ---
strain_layer_thick    = 0.8;    // Dorsal (back) inextensible layer thickness
strain_embed_depth    = 0.5;    // Fabric/paper embedding channel depth

// --- Thread Keeper (Fingertip) ---
keeper_hook_radius    = 4.0;
keeper_wall           = 1.8;
keeper_slots          = 3;
keeper_slot_dia       = 1.5;
keeper_opening_ang    = 70;

// --- Grip Texture (Palm Side) ---
grip_bump_dia         = 1.5;
grip_bump_height      = 0.6;
grip_bump_spacing     = 3.0;

// --- Servo Mount Base ---
base_width            = 50;
base_depth            = 40;
base_height           = 6;
servo_body_w          = 23.0;   // SG90 body width
servo_body_d          = 12.5;   // SG90 body depth
servo_body_h          = 22.0;   // SG90 body height
servo_tab_w           = 32.0;
servo_screw_dia       = 2.2;
servo_horn_radius     = 10.0;   // Servo horn arm length

// --- Tendon Spool on Servo Horn ---
spool_radius          = 5.0;    // Wire wraps around this
spool_width           = 6.0;
spool_flange_dia      = 14.0;   // Flange to keep wire on spool
spool_hub_dia         = 7.0;    // Fits onto servo horn spline
wire_clamp_screw_dia  = 2.0;    // Screw to clamp wire on spool

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
flexor_z  = H/2 + flexor_offset_z;
extensor_z = H/2 + extensor_offset_z;


/* ===== PRIMITIVE MODULES ===== */

module rounded_rect_2d(w, h, r) {
    offset(r) offset(-r) square([w, h], center = true);
}

module rounded_box(lx, ly, lz, r) {
    translate([0, 0, lz/2])
        hull() {
            for (x = [-lx/2 + r, lx/2 - r])
                for (y = [-ly/2 + r, ly/2 - r])
                    translate([x, y, 0])
                        cylinder(r = r, h = lz, center = true);
        }
}


/* ===== WIRE TENDON CHANNELS ===== */
// Dual tendon routing through any segment

module tendon_channels(length) {
    // Flexor channel (palm side - pulls finger closed)
    translate([-1, flexor_offset_y, flexor_z])
        rotate([0, 90, 0])
            cylinder(d = flexor_channel_dia, h = length + 2);

    // Extensor channel (dorsal side - returns finger open)
    translate([-1, extensor_offset_y, extensor_z])
        rotate([0, 90, 0])
            cylinder(d = extensor_channel_dia, h = length + 2);
}

// PTFE tube press-fit seats in rigid segments
module ptfe_tube_seats(length) {
    // Flexor PTFE seats at each end of segment
    for (x_pos = [1, length - ptfe_seat_length - 1]) {
        translate([x_pos, flexor_offset_y, flexor_z])
            rotate([0, 90, 0])
                cylinder(d = ptfe_tube_od + ptfe_seat_clearance * 2,
                         h = ptfe_seat_length);
    }
    // Extensor PTFE seats
    for (x_pos = [1, length - ptfe_seat_length - 1]) {
        translate([x_pos, extensor_offset_y, extensor_z])
            rotate([0, 90, 0])
                cylinder(d = ptfe_tube_od + ptfe_seat_clearance * 2,
                         h = ptfe_seat_length);
    }
}


/* ===== PULLEY REDIRECT AT JOINTS ===== */
// Printed-in-place pulley nubs that redirect wire around the bend point
// These keep the wire close to the joint center for efficient moment arm

module tendon_pulley_nub(z_pos) {
    // Small ridge inside the channel that acts as a low-friction redirect
    // Wire slides over this smooth TPU bump during bending
    translate([0, 0, z_pos])
        rotate([90, 0, 0])
            difference() {
                // Pulley bump
                cylinder(r = pulley_radius, h = pulley_width, center = true);
                // V-groove for wire
                rotate_extrude()
                    translate([pulley_radius, 0, 0])
                        circle(d = pulley_groove_depth * 2);
                // Hollow center (save material + flexibility)
                cylinder(d = pulley_axle_dia, h = pulley_width + 1, center = true);
            }
}

// Full pulley set at a joint (flexor + extensor)
module joint_pulleys() {
    // Flexor pulley (palm side) - redirects wire around bend
    translate([0, 0, flexor_z + flexor_channel_dia/2 + pulley_radius - 0.5])
        rotate([90, 0, 0])
            difference() {
                cylinder(r = pulley_radius, h = pulley_width, center = true);
                cylinder(d = pulley_axle_dia, h = pulley_width + 1, center = true);
                // Wire groove
                rotate_extrude()
                    translate([pulley_radius - pulley_groove_depth, 0, 0])
                        circle(d = flexor_wire_dia + 0.3);
            }

    // Extensor pulley (dorsal side)
    translate([0, 0, extensor_z - extensor_channel_dia/2 - pulley_radius + 0.5])
        rotate([90, 0, 0])
            difference() {
                cylinder(r = pulley_radius, h = pulley_width, center = true);
                cylinder(d = pulley_axle_dia, h = pulley_width + 1, center = true);
                rotate_extrude()
                    translate([pulley_radius - pulley_groove_depth, 0, 0])
                        circle(d = extensor_wire_dia + 0.3);
            }
}


/* ===== WIRE INSERTION SIDE SLOTS ===== */
// Open slots from the side surface into the tendon channel so you
// can push real wire in from the side, slide it along, then it
// drops into the channel. Slots are narrow enough that the wire
// stays in during operation.

module wire_side_insertion_slot(z_pos, channel_dia, length) {
    // Slot cut from one side of the finger into the tendon channel
    // Located at mid-length of each rigid segment
    translate([length/2, -W/2 - 0.1, z_pos - wire_insert_slot_w/2])
        cube([channel_dia + 1, wire_insert_slot_d + W/2 + 0.1, wire_insert_slot_w]);
}

// Vertical access hole from top or bottom surface to tendon channel
// for inserting wire with a needle or threader tool
module wire_vertical_access(x_pos, z_pos, from_top) {
    if (from_top) {
        // Hole from dorsal (top) surface down to channel
        translate([x_pos, 0, z_pos])
            cylinder(d = wire_exit_hole_dia, h = H, center = false);
    } else {
        // Hole from palm (bottom) surface up to channel
        translate([x_pos, 0, -0.1])
            cylinder(d = wire_exit_hole_dia, h = z_pos + 0.2);
    }
}


/* ===== SOFT BODY SEGMENT WITH TENDON ROUTING ===== */

module soft_segment(length, width, height) {
    difference() {
        // Outer body
        translate([length/2, 0, height/2])
            rounded_box(length, width, height, corner_radius);

        // Dual tendon channels
        tendon_channels(length);

        // PTFE tube seats
        ptfe_tube_seats(length);

        // Wire insertion side slots (one per tendon, at segment midpoint)
        wire_side_insertion_slot(flexor_z, flexor_channel_dia, length);
        wire_side_insertion_slot(extensor_z, extensor_channel_dia, length);
    }
}


/* ===== BELLOWS JOINT WITH TENDON PULLEYS ===== */

module bellows_joint(length, width, height, num_folds) {
    fold_pitch = length / num_folds;

    difference() {
        union() {
            // Solid block for joint region
            translate([length/2, 0, height/2])
                rounded_box(length, width, height, min(corner_radius, fold_pitch/3));

            // Strain-limiting dorsal ridge
            translate([length/2, 0, height - strain_layer_thick/2])
                rounded_box(length, width * 0.6, strain_layer_thick, 1);

            // Tendon pulley redirects at center of each joint
            translate([length/2, 0, 0])
                joint_pulleys();
        }

        // Bellows cuts from PALM SIDE (bottom)
        for (i = [0 : num_folds - 1]) {
            x_pos = fold_pitch * (i + 0.5);

            // Main bellows slit
            translate([x_pos, 0, -0.1])
                linear_extrude(height = height - bellows_floor - strain_layer_thick)
                    rounded_rect_2d(bellows_fold_width, width - bellows_floor * 2,
                                    bellows_fold_width / 4);

            // Wider base cut for better flex
            translate([x_pos, 0, -0.1])
                linear_extrude(height = bellows_fold_depth)
                    rounded_rect_2d(bellows_fold_width * 1.8,
                                    width - bellows_floor,
                                    bellows_fold_width / 3);
        }

        // Side relief cuts
        for (i = [0 : num_folds - 1]) {
            x_pos = fold_pitch * (i + 0.5);
            for (side = [-1, 1]) {
                translate([x_pos, side * (width/2 + 0.1), height * 0.3])
                    linear_extrude(height = height * 0.4)
                        rounded_rect_2d(bellows_fold_width * 0.8,
                                        bellows_fold_depth, 0.3);
            }
        }

        // Dual tendon channels through joint
        tendon_channels(length);

        // Wire access holes at joint center (top/bottom surface)
        // Allows threading a needle down into the channel at each joint
        wire_vertical_access(length/2, flexor_z, false);   // bottom hole to flexor
        wire_vertical_access(length/2, extensor_z, true);   // top hole to extensor
    }
}


/* ===== BOWDEN SHEATH ENTRY PORT ===== */
// Open entry at finger base for inserting wire from outside.
// Wire pushes straight through from the back of the finger
// into the internal tendon channel. Bowden sheath press-fits
// into the socket to guide wire from servo to finger.

module bowden_entry_port() {
    difference() {
        // Port housing
        translate([0, 0, 0])
            rounded_box(bowden_entry_depth + 3, W * 0.5, H * 0.7, 2);

        // Flexor: open entry hole (wire pushes in from outside)
        translate([-(bowden_entry_depth + 2), flexor_offset_y, flexor_z - H/2 + H*0.35])
            rotate([0, 90, 0])
                cylinder(d = wire_base_entry_dia, h = bowden_entry_depth * 4);

        // Flexor: Bowden sheath socket (sheath slides in after wire is threaded)
        translate([-bowden_entry_depth/2 - 1, flexor_offset_y, flexor_z - H/2 + H*0.35])
            rotate([0, 90, 0])
                cylinder(d = bowden_sheath_od + 0.3, h = bowden_entry_depth);

        // Extensor: open entry hole
        translate([-(bowden_entry_depth + 2), extensor_offset_y, extensor_z - H/2 + H*0.35])
            rotate([0, 90, 0])
                cylinder(d = wire_base_entry_dia, h = bowden_entry_depth * 4);

        // Extensor: Bowden sheath socket
        translate([-bowden_entry_depth/2 - 1, extensor_offset_y, extensor_z - H/2 + H*0.35])
            rotate([0, 90, 0])
                cylinder(d = bowden_sheath_od + 0.3, h = bowden_entry_depth);
    }
}


/* ===== WIRE ANCHOR AT FINGERTIP ===== */
// Exit holes at the fingertip so you can:
// 1. Push a needle/threader through from the base
// 2. Pull the wire out through the exit hole at the tip
// 3. Tie a knot or crimp a sleeve on the wire end
// 4. Pull it back so the knot/crimp seats into the anchor cavity

module wire_anchor_cavity() {
    // Flexor wire anchor
    translate([0, flexor_offset_y, flexor_z]) {
        // Anchor pocket (knot or crimp sits here)
        sphere(d = wire_anchor_cavity);
        // Wire channel entry from finger body
        translate([-wire_anchor_depth - 2, 0, 0])
            rotate([0, 90, 0])
                cylinder(d = flexor_channel_dia, h = wire_anchor_depth + 2);
        // EXIT HOLE: wire pull-through to outside of fingertip
        translate([0, 0, 0])
            rotate([0, 90, 0])
                cylinder(d = wire_exit_hole_dia, h = wire_anchor_depth + 5);
        // Clamp slot (insert crimp sleeve from the side)
        translate([0, -wire_clamp_slot_w/2, -wire_clamp_slot_h/2])
            cube([wire_anchor_depth + 3, wire_clamp_slot_w, wire_clamp_slot_h]);
        // Side access slot to drop crimp in
        translate([-wire_clamp_slot_w/2, -W/2 - 0.1, -wire_clamp_slot_h/2])
            cube([wire_clamp_slot_w, wire_insert_slot_d + W/2 + 0.1, wire_clamp_slot_h]);
    }

    // Extensor wire anchor
    translate([0, extensor_offset_y, extensor_z]) {
        sphere(d = wire_anchor_cavity * 0.8);
        translate([-wire_anchor_depth - 2, 0, 0])
            rotate([0, 90, 0])
                cylinder(d = extensor_channel_dia, h = wire_anchor_depth + 2);
        // EXIT HOLE for extensor wire
        translate([0, 0, 0])
            rotate([0, 90, 0])
                cylinder(d = wire_exit_hole_dia, h = wire_anchor_depth + 5);
    }
}


/* ===== THREAD KEEPER FINGERTIP ===== */

module thread_keeper_tip(length, width, height) {
    union() {
        difference() {
            // Tapered fingertip body
            hull() {
                translate([0, 0, height/2])
                    rounded_box(2, width, height, corner_radius);
                translate([length * 0.7, 0, height/2])
                    rounded_box(2, width * 0.7, height * 0.85, corner_radius * 0.7);
            }

            // Dual tendon channels
            tendon_channels(length * 0.7);

            // Wire anchor cavities at end of tendons
            translate([length * 0.6, 0, 0])
                wire_anchor_cavity();
        }

        // Thread keeper hook
        translate([length * 0.75, 0, height/2])
            thread_hook(width);

        // Grip texture on palm side
        grip_texture(length * 0.6, width * 0.65, 0);
    }
}

// C-shaped thread hook
module thread_hook(width) {
    rotate([90, 0, 0])
    translate([0, 0, -width/2])
    linear_extrude(height = width)
    difference() {
        circle(r = keeper_hook_radius + keeper_wall);
        circle(r = keeper_hook_radius);
        rotate([0, 0, -keeper_opening_ang/2])
            polygon([
                [0, 0],
                [(keeper_hook_radius + keeper_wall + 1) * cos(0),
                 (keeper_hook_radius + keeper_wall + 1) * sin(0)],
                [(keeper_hook_radius + keeper_wall + 1) * cos(keeper_opening_ang),
                 (keeper_hook_radius + keeper_wall + 1) * sin(keeper_opening_ang)]
            ]);
    }

    // Thread guide grooves
    for (i = [0 : keeper_slots - 1]) {
        y_pos = -width/2 + (width / (keeper_slots + 1)) * (i + 1);
        translate([0, y_pos, 0])
            rotate([90, 0, 0])
                translate([keeper_hook_radius + keeper_wall/2, 0, 0])
                    cylinder(d = keeper_slot_dia, h = keeper_wall + 1, center = true);
    }
}


/* ===== GRIP TEXTURE ===== */

module grip_texture(length, width, z_offset) {
    cols = floor(length / grip_bump_spacing);
    rows = floor(width / grip_bump_spacing);

    for (ix = [0 : cols - 1])
        for (iy = [0 : rows - 1]) {
            x_off = ix * grip_bump_spacing + (iy % 2) * (grip_bump_spacing / 2);
            y_off = iy * grip_bump_spacing - width/2;
            translate([x_off + grip_bump_spacing/2, y_off + grip_bump_spacing/2, z_offset])
                sphere(d = grip_bump_dia);
        }
}


/* ===== STRAIN LIMIT CHANNEL ===== */

module strain_limit_channel(length, width) {
    translate([length/2, 0, H - strain_embed_depth/2])
        cube([length, width * 0.5, strain_embed_depth], center = true);
}


/* ===== SERVO MOUNT WITH TENDON SPOOL ===== */

module tendon_spool() {
    difference() {
        union() {
            // Spool barrel (wire wraps around this)
            cylinder(r = spool_radius, h = spool_width, center = true);

            // Top flange
            translate([0, 0, spool_width/2])
                cylinder(d = spool_flange_dia, h = 1.5);

            // Bottom flange
            translate([0, 0, -spool_width/2 - 1.5])
                cylinder(d = spool_flange_dia, h = 1.5);
        }

        // Servo horn hub hole (cross-shaped spline)
        cylinder(d = spool_hub_dia, h = spool_width + 4, center = true);

        // Wire entry hole (thread wire through this)
        translate([spool_radius - 1, 0, 0])
            rotate([0, 90, 0])
                cylinder(d = flexor_wire_dia + 0.5, h = 4, center = true);

        // Wire clamp screw hole
        translate([spool_radius * 0.6, 0, 0])
            cylinder(d = wire_clamp_screw_dia, h = spool_width + 4, center = true);

        // Second wire entry for extensor (opposite side)
        translate([-(spool_radius - 1), 0, 0])
            rotate([0, 90, 0])
                cylinder(d = extensor_wire_dia + 0.5, h = 4, center = true);
    }

    // Wire guide groove on barrel surface
    difference() {
        cylinder(r = spool_radius + 0.1, h = spool_width, center = true);
        cylinder(r = spool_radius - 0.3, h = spool_width + 1, center = true);
        // Spiral groove (simplified as rings)
        for (z = [-spool_width/2 + 1 : 1.5 : spool_width/2 - 1]) {
            translate([0, 0, z])
                rotate_extrude()
                    translate([spool_radius, 0, 0])
                        circle(d = flexor_wire_dia + 0.2);
        }
    }
}

module soft_servo_mount() {
    difference() {
        union() {
            // Base plate
            rounded_box(base_width, base_depth, base_height, 4);

            // Servo cradle with snap-fit walls
            translate([0, 0, base_height]) {
                difference() {
                    rounded_box(servo_body_w + 4, servo_body_d + 4, servo_body_h, 2);
                    translate([0, 0, -0.5])
                        cube([servo_body_w, servo_body_d, servo_body_h + 1], center = true);
                }

                // Snap-fit tabs
                for (side = [-1, 1]) {
                    translate([side * (servo_body_w/2 + 1), 0, servo_body_h * 0.6])
                        rotate([0, side * 15, 0])
                            cube([1.5, servo_body_d * 0.4, 3], center = true);
                }
            }

            // Bowden sheath anchor posts (wire exits here toward finger)
            for (y_off = [-4, 4]) {
                translate([base_width/2 - 3, y_off, base_height])
                    difference() {
                        cylinder(d = bowden_sheath_od + 4, h = 8);
                        translate([0, 0, -1])
                            cylinder(d = bowden_sheath_od + 0.3, h = 10);
                    }
            }

            // Finger attachment tab
            translate([base_width/2 - 2, 0, base_height + servo_body_h])
                rounded_box(10, W, 4, 2);
        }

        // Base mounting holes
        for (x = [-base_width/2 + 5, base_width/2 - 5])
            for (y = [-base_depth/2 + 5, base_depth/2 - 5])
                translate([x, y, -1])
                    cylinder(d = 3.2, h = base_height + 2);

        // Servo tab screw holes
        for (x = [-servo_tab_w/2 + 2, servo_tab_w/2 - 2])
            translate([x, 0, base_height + 15])
                rotate([90, 0, 0])
                    cylinder(d = servo_screw_dia, h = base_depth, center = true);

        // Wire routing channel under base
        translate([0, 0, base_height/2])
            rotate([90, 0, 0])
                cylinder(d = 5, h = base_depth + 2, center = true);
    }

    // Tendon spool (shown near servo horn position)
    color("Orange")
    translate([0, servo_body_d/2 + 5, base_height + servo_body_h * 0.7])
        rotate([90, 0, 0])
            tendon_spool();
}


/* ===== FULL SOFT FINGER - MONOLITHIC PRINT-IN-PLACE ===== */

module soft_finger() {
    // 1. Base segment with Bowden entry port
    color("SteelBlue", 0.9) {
        soft_segment(base_len, W, H);
        // Bowden sheath entry
        translate([-1, 0, H/2])
            bowden_entry_port();
    }

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

    // 7. Fingertip with thread keeper + wire anchors
    color("LightSkyBlue", 0.9)
    translate([base_len + mcp_len + mid_len + pip_len + tip_len + dip_len, 0, 0])
        thread_keeper_tip(ftip_len, W, H);

    // Strain limit channel on dorsal surface
    color("DarkSlateGray", 0.5)
        strain_limit_channel(L * 0.85, W);
}


/* ===== FULL ASSEMBLY ===== */

module full_soft_assembly() {
    // Servo mount with spool
    color("DimGray", 0.8)
    translate([-base_width/2, 0, -base_height - servo_body_h - 2])
        soft_servo_mount();

    // Soft finger with real wire holes (no dummy wires)
    soft_finger();
}


/* ===== RENDER SELECTION ===== */
// Uncomment desired output:

// Full assembly
full_soft_assembly();

// Just the finger (for printing)
// soft_finger();

// Just the servo mount + spool (for printing)
// soft_servo_mount();

// Individual spool (print separately in PLA for rigidity)
// tendon_spool();

// Bellows test piece
// bellows_joint(15, W, H, 4);

// Thread keeper test
// thread_keeper_tip(ftip_len, W, H);
