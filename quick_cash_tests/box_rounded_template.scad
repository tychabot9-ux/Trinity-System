// Parametric Box with Rounded Corners
// Ready for customization

// Parameters
length = 50;  // mm
width = 30;   // mm
height = 20;  // mm
corner_radius = 3;  // mm
wall_thickness = 2; // mm
$fn = 50;

// Model
difference() {
    // Outer shell with rounded corners
    minkowski() {
        cube([length-2*corner_radius, width-2*corner_radius, height/2], center=true);
        sphere(r=corner_radius);
    }
    
    // Hollow interior
    translate([0, 0, wall_thickness])
        minkowski() {
            cube([length-2*corner_radius-2*wall_thickness, 
                  width-2*corner_radius-2*wall_thickness, 
                  height/2], center=true);
            sphere(r=corner_radius);
        }
}
