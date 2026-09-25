// =============================================================================
// microUnit 50mm Modular Self-Reconfigurable Robot (MSRR)
// Parametric 3D CAD Assembly Model (OpenSCAD / FreeCAD Compatible)
// Scale: Millimeters (mm)
// =============================================================================

$fn = 64; // High-resolution mesh facets

// Global Physical Parameters
cube_size = 50.0;
fillet_radius = 1.5;
wall_thickness = 1.0;
face_pocket_thinning = 0.5; // Thinned to 0.5mm at magnetic pole faces
basin_depth = 0.2;          // Self-aligning docking basin
optical_window_dia = 3.0;   // Optical IR quartz window
screw_dia = 1.6;            // M1.6 screw thread diameter
screw_hole_dia = 1.8;       // Clearance hole
screw_pitch_x = 44.0;       // Center-to-center spacing
screw_pitch_y = 44.0;

// Internal Actuator Parameters
flywheel_dia = 27.0;
flywheel_thickness = 3.5;
flywheel_shaft_dia = 1.5;
bearing_od = 5.0;
bearing_id = 2.0;
bearing_w = 2.5;
motor_dia = 14.0;
motor_len = 12.0;
battery_x = 14.0;
battery_y = 33.0;
battery_z = 14.0;

// Refined Electromagnetic Coil & Bobbin Parameters
bobbin_id = 6.2;            // LCP Bobbin Inner Dia (mm)
bobbin_od = 11.2;           // LCP Bobbin Outer Dia (mm)
bobbin_height = 4.5;        // Winding slot height (mm)
magnet_dia = 6.0;           // N52 + AlNiCo5 core dia (mm)
magnet_len = 6.0;           // Core total length (mm)
dt4c_shoe_thickness = 0.5;  // DT4C pure iron pole shoe (mm)
kapton_film_thickness = 0.05; // 50um Kapton wear film (mm)

// Permalloy EMI Shielding Parameters
shield_box_w = 22.0;        // 1J79 shield width (mm)
shield_box_l = 22.0;        // 1J79 shield length (mm)
shield_box_h = 5.0;         // 1J79 shield height (mm)
shield_wall_t = 0.20;       // 1J79 wall thickness 0.20mm

// Helper: Rounded Box Primitive
module rounded_box(size, radius) {
    x = size[0] - 2 * radius;
    y = size[1] - 2 * radius;
    z = size[2] - 2 * radius;
    translate([radius, radius, radius])
        minkowski() {
            cube([x, y, z]);
            sphere(r = radius);
        }
}

// -----------------------------------------------------------------------------
// 1. Upper Enclosure Shell (Somos Taurus SLA Resin)
// -----------------------------------------------------------------------------
module upper_shell() {
    difference() {
        // Outer Shell
        rounded_box([cube_size, cube_size, cube_size / 2], fillet_radius);

        // Internal Hollow Cavity (1.0mm wall thickness)
        translate([wall_thickness, wall_thickness, -0.1])
            cube([cube_size - 2 * wall_thickness, cube_size - 2 * wall_thickness, cube_size / 2 - wall_thickness + 0.1]);

        // Top Face Self-Aligning Shallow Basin (0.2mm depth, R18mm)
        translate([cube_size / 2, cube_size / 2, cube_size / 2 - basin_depth + 0.01])
            cylinder(r = 18.0, h = basin_depth + 0.1);

        // Top Optical Communication Window Pocket
        translate([cube_size / 2, cube_size / 2, cube_size / 2 - 2.0])
            cylinder(r = optical_window_dia / 2, h = 3.0);

        // M1.6 Screw Mounting Holes at 4 Corners
        for (dx = [-screw_pitch_x / 2, screw_pitch_x / 2]) {
            for (dy = [-screw_pitch_y / 2, screw_pitch_y / 2]) {
                translate([cube_size / 2 + dx, cube_size / 2 + dy, -1])
                    cylinder(r = screw_hole_dia / 2, h = cube_size / 2 + 2);
            }
        }
    }
}

// -----------------------------------------------------------------------------
// 2. Lower Enclosure Shell (With Bottom EPM Pocket & Pogo-Pin Debug Base)
// -----------------------------------------------------------------------------
module lower_shell() {
    difference() {
        // Outer Shell
        rounded_box([cube_size, cube_size, cube_size / 2], fillet_radius);

        // Internal Cavity
        translate([wall_thickness, wall_thickness, wall_thickness])
            cube([cube_size - 2 * wall_thickness, cube_size - 2 * wall_thickness, cube_size / 2]);

        // Bottom Self-Aligning Basin
        translate([cube_size / 2, cube_size / 2, -0.01])
            cylinder(r = 18.0, h = basin_depth + 0.01);

        // Bottom Optical Window
        translate([cube_size / 2, cube_size / 2, -1.0])
            cylinder(r = optical_window_dia / 2, h = 3.0);

        // 6-Pin Magnetic Pogo Pin Interface Recess (12mm x 4mm)
        translate([cube_size / 2 - 6.0, cube_size / 2 - 12.0, -0.1])
            cube([12.0, 4.0, 2.0]);

        // M1.6 Screw Counterbore Bosses
        for (dx = [-screw_pitch_x / 2, screw_pitch_x / 2]) {
            for (dy = [-screw_pitch_y / 2, screw_pitch_y / 2]) {
                translate([cube_size / 2 + dx, cube_size / 2 + dy, -1])
                    cylinder(r = screw_dia / 2 * 0.9, h = cube_size / 2); // Tapping pilot hole
            }
        }
    }
}

// -----------------------------------------------------------------------------
// 3. Central Internal Structural Bracket (PA12 SLS Nylon)
// -----------------------------------------------------------------------------
module internal_bracket() {
    difference() {
        // Core Mounting Block
        translate([cube_size / 2 - 20.0, cube_size / 2 - 20.0, -18.0])
            cube([40.0, 40.0, 36.0]);

        // Center 1S LiPo Battery Pocket (14x33x14mm)
        translate([cube_size / 2 - battery_x / 2, cube_size / 2 - battery_y / 2, -battery_z / 2])
            cube([battery_x, battery_y, battery_z]);

        // 1104 Brushless Motor Mounting Cavity
        translate([cube_size / 2, cube_size / 2, 0])
            rotate([90, 0, 0])
                cylinder(r = motor_dia / 2, h = motor_len, center = true);

        // MR52ZZ Bearing Pockets (Dia 5.0mm, Depth 2.5mm)
        translate([cube_size / 2, cube_size / 2 + motor_len / 2 + 1.25, 0])
            rotate([90, 0, 0])
                cylinder(r = bearing_od / 2, h = bearing_w, center = true);
        translate([cube_size / 2, cube_size / 2 - motor_len / 2 - 1.25, 0])
            rotate([90, 0, 0])
                cylinder(r = bearing_od / 2, h = bearing_w, center = true);

        // Flywheel Swept Envelope Cavity (Dia 28.0mm, Width 5.0mm)
        translate([cube_size / 2, cube_size / 2, 0])
            rotate([90, 0, 0])
                cylinder(r = (flywheel_dia + 1.0) / 2, h = flywheel_thickness + 1.5, center = true);

        // Weight-reduction cutouts
        translate([cube_size / 2 - 16, cube_size / 2 - 16, -15])
            cube([8, 8, 30]);
        translate([cube_size / 2 + 8, cube_size / 2 - 16, -15])
            cube([8, 8, 30]);
    }
}

// -----------------------------------------------------------------------------
// 4. High-Inertia Brass Flywheel Rotor (H62 Brass)
// -----------------------------------------------------------------------------
module brass_flywheel() {
    color([0.85, 0.75, 0.2, 1.0])
    difference() {
        // Outer Rim (Dia 27.0mm, Thickness 3.5mm)
        cylinder(r = flywheel_dia / 2, h = flywheel_thickness, center = true);

        // Center Shaft Bore (Dia 1.5mm H7)
        cylinder(r = flywheel_shaft_dia / 2, h = flywheel_thickness + 1, center = true);

        // Web Relieving Groove (Leaving Rim for Max Polar Inertia J_yy)
        difference() {
            cylinder(r = flywheel_dia / 2 - 2.5, h = flywheel_thickness + 0.1, center = true);
            cylinder(r = 3.5, h = flywheel_thickness + 0.2, center = true); // Center hub
        }
    }
}

// -----------------------------------------------------------------------------
// 4B. 1J79 Permalloy EMI Shielding Box (0.20mm Wall, 22x22x5mm)
// -----------------------------------------------------------------------------
module permalloy_shield_box() {
    color([0.72, 0.75, 0.80, 0.85]) // Mu-metal nickel luster
    difference() {
        cube([shield_box_w, shield_box_l, shield_box_h], center = true);
        translate([0, 0, -shield_wall_t])
            cube([shield_box_w - 2 * shield_wall_t, shield_box_l - 2 * shield_wall_t, shield_box_h], center = true);
    }
}

// -----------------------------------------------------------------------------
// 4C. LCP Bobbin with QZY-2/180 Coil & Composite Magnet Assembly
// -----------------------------------------------------------------------------
module lcp_epm_coil_module() {
    // 1. Central Composite Magnet (N52 + AlNiCo5)
    color([0.35, 0.35, 0.40, 1.0])
        cylinder(r = magnet_dia / 2, h = magnet_len, center = true);

    // 2. LCP Bobbin Frame (Celanese Vectra E130i, Tan)
    color([0.80, 0.70, 0.55, 0.85])
    difference() {
        cylinder(r = bobbin_od / 2, h = bobbin_height, center = true);
        cylinder(r = bobbin_id / 2, h = bobbin_height + 0.2, center = true);
    }

    // 3. Copper Enamelled Wire Windings (120 Turns QZY-2, Copper)
    color([0.85, 0.45, 0.15, 0.95])
    difference() {
        cylinder(r = (bobbin_od + bobbin_id) / 4 + 1.2, h = bobbin_height - 0.6, center = true);
        cylinder(r = bobbin_id / 2 + 0.3, h = bobbin_height, center = true);
    }

    // 4. DT4C Pure Iron Pole Shoe Outer Face Plate (30x30x0.5mm)
    color([0.65, 0.15, 0.15, 0.90])
    translate([0, 0, magnet_len / 2])
    difference() {
        cube([30.0, 30.0, dt4c_shoe_thickness], center = true);
        cylinder(r = optical_window_dia / 2, h = dt4c_shoe_thickness + 0.2, center = true);
    }
}

// -----------------------------------------------------------------------------
// 5. Complete Single Unit Assembly
// -----------------------------------------------------------------------------
module single_micro_unit(unit_id = 0, show_flywheel = true) {
    // Lower Shell
    color([0.85, 0.55, 0.2, 0.85])
        lower_shell();

    // Upper Shell
    color([0.85, 0.55, 0.2, 0.85])
        upper_shell();

    // Central Bracket
    translate([0, 0, cube_size / 2])
        color([0.25, 0.25, 0.3, 0.9])
            internal_bracket();

    // Brass Flywheel Rotor
    if (show_flywheel) {
        translate([cube_size / 2, cube_size / 2, cube_size / 2])
            rotate([90, 0, 0])
                brass_flywheel();
    }

    // Central 1J79 Permalloy Shield Can protecting MCU & IMU
    translate([cube_size / 2, cube_size / 2, cube_size / 2 + 8.0])
        permalloy_shield_box();

    // 6-Face Refined LCP EPM Coil & Pole Shoe Assemblies (Embedded & Flush-Mounted)
    // Front Face (+X)
    translate([cube_size - (magnet_len / 2 + dt4c_shoe_thickness / 2), cube_size / 2, cube_size / 2])
        rotate([0, 90, 0])
            lcp_epm_coil_module();

    // Back Face (-X)
    translate([magnet_len / 2 + dt4c_shoe_thickness / 2, cube_size / 2, cube_size / 2])
        rotate([0, -90, 0])
            lcp_epm_coil_module();

    // Right Face (+Y)
    translate([cube_size / 2, cube_size - (magnet_len / 2 + dt4c_shoe_thickness / 2), cube_size / 2])
        rotate([-90, 0, 0])
            lcp_epm_coil_module();

    // Left Face (-Y)
    translate([cube_size / 2, magnet_len / 2 + dt4c_shoe_thickness / 2, cube_size / 2])
        rotate([90, 0, 0])
            lcp_epm_coil_module();

    // Top Face (+Z)
    translate([cube_size / 2, cube_size / 2, cube_size - (magnet_len / 2 + dt4c_shoe_thickness / 2)])
        lcp_epm_coil_module();

    // Bottom Face (-Z)
    translate([cube_size / 2, cube_size / 2, magnet_len / 2 + dt4c_shoe_thickness / 2])
        rotate([180, 0, 0])
            lcp_epm_coil_module();
}

// -----------------------------------------------------------------------------
// 5B. Option B Solid-State Micro-Unit (Flywheel-Free, 1300mAh Battery, Potted IP68)
// -----------------------------------------------------------------------------
module solid_state_micro_unit(unit_id = 0) {
    single_micro_unit(unit_id = unit_id, show_flywheel = false);

    // Expanded 1300mAh High-Density LiPo Battery (42x30x9.5mm) occupying center cavity
    color([0.2, 0.4, 0.8, 0.9])
        translate([cube_size / 2 - 15.0, cube_size / 2 - 21.0, cube_size / 2 - 4.75])
            cube([30.0, 42.0, 9.5]);

    // Transparent Heat-Conductive Potted Silicone Encapsulation Block
    color([0.4, 0.8, 0.9, 0.25])
        translate([wall_thickness + 1.0, wall_thickness + 1.0, wall_thickness + 1.0])
            cube([cube_size - 2 * wall_thickness - 2.0, cube_size - 2 * wall_thickness - 2.0, cube_size - 2 * wall_thickness - 2.0]);
}

// -----------------------------------------------------------------------------
// 6. Dual-Unit Docked Assembly (Face-to-Face Latching)
// -----------------------------------------------------------------------------
module dual_unit_docked_assembly() {
    // Unit A: Base Unit at Origin
    single_micro_unit(unit_id = 0);

    // Unit B: Docked along +X Face
    translate([cube_size, 0, 0])
        single_micro_unit(unit_id = 1);
}

// -----------------------------------------------------------------------------
// 7. Dual-Unit Climbing Transition (Edge Rolling onto Top Face)
// -----------------------------------------------------------------------------
module dual_unit_climbing_transition(climb_angle_deg = 45.0) {
    // Unit A: Ground-Anchored Base
    single_micro_unit(unit_id = 0);

    // Unit B: Pivoting around Unit A's Top-Right Edge [cube_size, 0, cube_size]
    translate([cube_size, 0, cube_size])
        rotate([0, -climb_angle_deg, 0])
            translate([0, 0, -cube_size])
                single_micro_unit(unit_id = 1);
}

// -----------------------------------------------------------------------------
// 8. Multi-Unit Chain Assembly (3 to 5 Units in Peristaltic Configuration)
// -----------------------------------------------------------------------------
module multi_unit_chain_assembly(n = 3) {
    for (i = [0 : n - 1]) {
        translate([i * cube_size, 0, 0])
            single_micro_unit(unit_id = i);
    }
}

// Default View: Multi-Unit Docked Chain (3 Units)
multi_unit_chain_assembly(n = 3);

