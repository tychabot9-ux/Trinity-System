// Phone Stand
// Simple angled support design

// Parameters
base_length = 80;   // mm
base_width = 60;    // mm
base_height = 5;    // mm
back_height = 60;   // mm
angle = 65;         // degrees
$fn = 50;

// Base
cube([base_length, base_width, base_height], center=true);

// Angled back support
translate([0, -base_width/4, base_height/2 + back_height/2])
    rotate([angle-90, 0, 0])
        cube([base_length, base_height, back_height], center=true);

// Support triangle
translate([0, 0, base_height + 10])
    rotate([0, 0, 0])
        linear_extrude(height=base_length, center=true, twist=0)
            polygon(points=[[0,0], [30,0], [0,30]]);
