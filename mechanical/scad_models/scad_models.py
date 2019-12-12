# <--------------------------------------- 100 characters ---------------------------------------> #

"""Code to genarate and openscad model of the Pololu Romi Base."""

# Pumpkin Pi: 104mm x 70mm.  Holes are the same as the Raspberry Pi with the upper left
# hole in the upper left corner of the PCB.  The extra PCB space goes to the right and
# down on the Pumpkin Pi.

# http://docplayer.net/42910792-
# Hardware-assisted-tracing-on-arm-with-coresight-and-opencsd-mathieu-poirier.html
from scad_models.scad import Circle, LinearExtrude, P2D, Polygon, Scad, SimplePolygon, Square, Union
from typing import Any, Dict, IO, List, Tuple
from math import asin, atan2, cos, degrees, nan, pi, sin, sqrt


# Romi:
class Romi:
    """A helper class for modeling the Pololu Romi robot platform."""

    # Romi.__init__():
    def __init__(self) -> None:
        """Initialize and create the Romi Platform."""
        # Figuring out where everything is located is done with a combination of reading
        # drawing in section 6 of the "Pololu Romi Chassis User's Guide" and extracting
        # values from the `romi-chassis.dxf` file available from the Pololu web site.
        # `romi-chassis.dxf` is also stored in the git repository to make sure it does
        # not go away.
        #
        # It is important to notice that the section 6 drawings are upside-down from
        # the `romi-chassis.dxf`.  For the modeling of this platform, the `.dxf` file
        # orientation is used.  Sigh.  Also, the `.dxf` file seems to be in units of
        # inches rather than millimeters.  The rest of this code uses millimeters, so we
        # multiply inches coordinate values by *inches2mm* as soon as possible.
        #
        # Finally, the origin of the `.dxf` is off  to the lower right rather that in the
        # traditional center for differential drive robots.  There are various "locate"
        # methods that take values in inches from the `.dxf` file and generate an
        # appropriate data structure (usuually a *Polygon*.)  All of these "locate"
        # methods need to have *offset_origin* to convert to a robot center in millimeters.

        # Set *debugging* to *True* to print out debugging messages:
        debugging: bool = False  # True

        # Let's get started computing *origin_offet*:
        #
        # It is pretty clear that the motor axles are intended to go through the center of the
        # Romi platform along the X axis.  By reading the values for the top and bottom of the
        # axle (in inches) from the `.dxf` file we can compute *y_origin_offset*:
        # *y_origin_offset* in millimeters:
        inches2mm: float = 25.4
        axel_y_above: float = 2.967165 * inches2mm
        axel_y_below: float = 2.908110 * inches2mm
        y_origin_offset: float = (axel_y_above + axel_y_below) / 2.0

        # The *x_origin_offset* is computed using the upper castor hole location:
        upper_castor_x_left: float = -3.930756 * inches2mm
        upper_castor_x_right: float = -3.805256 * inches2mm
        x_origin_offset: float = (upper_castor_x_left + upper_castor_x_right) / 2.0

        # Finally we have *origin_offset* in millimeters and can save it back into *romi*
        # (i.e. *self*):
        origin_offset = P2D(x_origin_offset, y_origin_offset)
        self.debugging = debugging
        self.inches2mm: float = inches2mm
        self.origin_offset: P2D = origin_offset
        if debugging:  # pragma: no cover
            print(f"origin_offset={origin_offset}")

    # Romi.base_outline_polygon_get():
    def base_outline_polygon_get(self) -> SimplePolygon:
        """Return the outline of the Romi Base."""
        # Grab some values from *romi* (i.e. *self*):
        romi: Romi = self
        debugging: bool = romi.debugging

        # These other dimensions are read off of the drawings in section 6 of the
        # the "Pololu Romi Chasis User's Guide":
        diameter: float = 163.0  # mm
        radius: float = diameter / 2.0
        overall_width: float = 149.0  # mm
        wheel_well_dx: float = 125.0  # mm
        wheel_well_dy: float = 72.0  # mm
        half_wheel_well_dx: float = wheel_well_dx / 2.0
        half_wheel_well_dy: float = wheel_well_dy / 2.0

        # Perform any requested *debugging*:
        if debugging:  # pragma: no cover
            print(f"diameter={diameter}mm radius={radius}mm")
            print(f"overall_width={overall_width}mm")
            print(f"wheel_well_dx={wheel_well_dx}mm")
            print(f"wheel_well_dy={wheel_well_dy}mm")

        # The outer edge of the wheel well points are on the circle of *radius*.
        # We need to compute the X/Y coordinates using trigonometry.  Using math:
        #
        #     (x, y) = (r * cos(angle), r * sin(angle)                   (1)
        #     x = r * cos(angle)                                         (2)
        #     y = r * sin(angle)                                         (3)
        #     y/r = sin(angle)                                           (4)
        #     asin(y/r) = angle                                          (5)
        #     x = r * sin(acos(y/r))                                     (6)
        #
        wheel_well_angle: float = asin(half_wheel_well_dy / radius)  # radians
        wheel_well_x: float = radius * cos(wheel_well_angle)  # mm (upper right)
        wheel_well_y: float = radius * sin(wheel_well_angle)  # mm (upper right)
        wheel_well_corner: P2D = P2D(wheel_well_x, wheel_well_y)

        # Perform any requested *debugging*:
        if debugging:  # pragma: no cover
            print(f"wheel_well_angle={wheel_well_angle}={degrees(wheel_well_angle)}deg")
            print(f"wheel_well_corner={wheel_well_corner}")

        # Verify that the *distance* from the *origin* to the *wheel_well_corner* matches *radius*:
        origin: P2D = P2D(0.0, 0.0)
        wheel_well_radius: float = origin.distance(wheel_well_corner)
        assert abs(radius - wheel_well_radius) < .00001, "Something is not right"

        # Now we can draw the *outline_polygon* of the Romi platform.  It conists of two arcs
        # with some straight line segments to form the wheel well.  Start by creating
        # an empty *outline_polygon*:
        outline_polygon: SimplePolygon = SimplePolygon("Romi Base Exterior")

        # Create the upper arc:
        upper_start_angle: float = wheel_well_angle
        upper_end_angle: float = pi - wheel_well_angle
        arc_count = 21
        outline_polygon.arc_append(origin, radius, upper_start_angle, upper_end_angle, arc_count)

        # Create the left wheel well:
        outline_polygon.point_append(P2D(-half_wheel_well_dx, half_wheel_well_dy))
        outline_polygon.point_append(P2D(-half_wheel_well_dx, -half_wheel_well_dy))

        # Create the lower arc:
        lower_start_angle: float = wheel_well_angle + pi
        lower_end_angle: float = upper_end_angle + pi
        outline_polygon.arc_append(origin, radius, lower_start_angle, lower_end_angle, arc_count)

        # Create the right wheel well:
        outline_polygon.point_append(P2D(half_wheel_well_dx, -half_wheel_well_dy))
        outline_polygon.point_append(P2D(half_wheel_well_dx, half_wheel_well_dy))
        assert len(outline_polygon) == 2 * arc_count + 4

        # Lock and return *outline_polygon*:
        outline_polygon.lock()
        return outline_polygon

    # Romi.base_scad_polygon_generate()
    def base_scad_polygon_generate(self) -> Polygon:
        """TODO."""
        # Grabe some values from *romi* (i.e. *self*):
        romi: Romi = self
        debugging: bool = romi.debugging

        # Grab the *base_outline_polygon*:
        base_outline_polygon: SimplePolygon = romi.base_outline_polygon_get()

        # Grab the *battery_polygons*:
        battery_polygons: List[SimplePolygon] = romi.battery_polygons_get()

        # Grab the *upper_hex_polygons*:
        upper_hex_polygons: List[SimplePolygon] = romi.upper_hex_polygons_get()
        if debugging:  # pragma: no cover
            print("************************")
            print(f"len(upper_hex_polygons)={len(upper_hex_polygons)}")

        # Grab the *lower_hex_polygons* and *lower_hex_table*:
        lower_hex_polygons: List[SimplePolygon]
        lower_hex_table: Dict[str, P2D]
        lower_hex_polygons, lower_hex_table = romi.lower_hex_polygons_table_get()
        if debugging:  # pragma: no cover
            print(f"len(lower_hex_polygons)={len(lower_hex_polygons)}")

        line_hole_polygons: List[SimplePolygon] = romi.line_hole_polygons_get(lower_hex_table)
        lower_arc_holes_rectangles: List[SimplePolygon] = romi.lower_arc_holes_rectangles_get()
        upper_arc_holes_rectangles: List[SimplePolygon] = romi.upper_arc_holes_rectangles_get()
        miscellaneous_holes: List[Circle] = romi.miscellaneous_holes_get()
        vertical_rectangles: List[Square] = romi.vertical_rectangles_get()

        # Concatenate all of the polygons together into *all_polygons* with *base_outline_polygon*
        # being the required first *Polygon*:
        mirrorable_polygons: List[SimplePolygon] = []
        mirrorable_polygons.extend(upper_hex_polygons)
        mirrorable_polygons.extend(lower_hex_polygons)
        mirrorable_polygons.extend(line_hole_polygons)
        mirrorable_polygons.extend(lower_arc_holes_rectangles)
        mirrorable_polygons.extend(upper_arc_holes_rectangles)
        mirrorable_polygons.extend(miscellaneous_holes)
        mirrorable_polygons.extend(vertical_rectangles)

        mirrorable_polygon: SimplePolygon
        mirrored_polygons: List[SimplePolygon] = [mirrorable_polygon.y_mirror("RIGHT:", "LEFT:")
                                                  for mirrorable_polygon in mirrorable_polygons]
        all_internal_polygons: List[SimplePolygon] = (battery_polygons +
                                                      mirrorable_polygons + mirrored_polygons)
        all_polygons: List[SimplePolygon] = ([base_outline_polygon] + all_internal_polygons)

        internal_polygon: SimplePolygon

        if debugging:  # pragma: no cover
            print(f"len(all_polygons)={len(all_polygons)}")

        # Create the final *base_scad_polygon*, write it out to disk and return it.
        base_scad_polygon: Polygon = Polygon("Romi Base ScadPolygon", all_polygons, lock=True)
        return base_scad_polygon

    # Romi.battery_polygons_get():
    def battery_polygons_get(self) -> List[SimplePolygon]:
        """Return the holes for the Romi battery case."""
        # Grab some values from *romi* (i.e. *self*):
        romi: Romi = self
        # debugging: bool = romi.debugging
        inches2mm: float = romi.inches2mm
        origin_offset: P2D = romi.origin_offset

        # All of the battery holes are done relative to the *battery_reference_hole*
        # indicated on the drawing of the dimensions and mounting holes seciont of the
        # "Pololu Romi Chassis User's Guide".
        reference_hole: Circle = romi.hole_locate("ZILCH: Battery Hole",
                                                  -3.913146, 3.376610, -3.822591, 3.286051)

        # The battery holes have an upper and lower group.  The lower group resides between
        # the motors and the upper group is above the motors.  The lower group is organized
        # in 3 rows by 9 columns and not all holes are poplulated.  We create a
        # *lower_battery_pattenrs* list to specify which of the holes need to be poputlated.
        # Remember, the `.dxf` orientation is being used and move down from the
        # *battery_reference_hole_center*:
        lower_battery_y_offsets: Tuple[float, ...] = (0.0, -12.3, -12.3 - 12.3)
        lower_battery_patterns: Tuple[str, ...] = (
            "*-**O**-*",  # Row with reference hole in the middle (at the 'O' location)
            "*-*****-*",  # Row below reference hole
            "*-*****-*")  # Two rows below referene hole
        simple_polygons: List[SimplePolygon] = list()
        reference_hole_center_y: float = reference_hole.center.y
        hole_dx_pitch: float = 10
        column0_x: float = -4.0 * hole_dx_pitch
        x_index: int
        for x_index in range(9):
            x: float = column0_x + x_index * hole_dx_pitch
            y_index: int
            lower_battery_pattern: str
            for y_index, lower_battery_pattern in enumerate(lower_battery_patterns):
                if lower_battery_pattern[x_index] != '-':
                    # We need a hole:
                    y: float = reference_hole_center_y + lower_battery_y_offsets[y_index]
                    lower_hole_center: P2D = P2D(x, y)
                    lower_hole: Circle = reference_hole.copy(("BATTERY: Lower Hole "
                                                             f"({2-x_index}, {y_index})"),
                                                             center=lower_hole_center)
                    simple_polygons.append(lower_hole)

        # The upper battery holes above the lower battery motor holes are organized as
        # 3 rows by 9 columns where all positions are populated:
        upper_battery_y_offsets: Tuple[float, ...] = (7.0, 7.0 + 12.3, 7.0 + 12.3 + 12.3)
        column0_x = -4.5 * hole_dx_pitch
        for x_index in range(10):
            x = column0_x + x_index * hole_dx_pitch
            for y_index in range(3):
                y = reference_hole_center_y + upper_battery_y_offsets[y_index]
                upper_hole_center: P2D = P2D(x, y)
                upper_hole: Circle = reference_hole.copy(("BATTERY: Upper Hole "
                                                         f"({2-x_index}, {y_index})"),
                                                         center=upper_hole_center)
                simple_polygons.append(upper_hole)

        # There are 6 rectangular slots that have a nub on the end to cleverly indicate battery
        # polarity direction.  We will model these as simple rectangular slots and skip the
        # cleverly battery nubs.  There are 4 batteries slots at the top called
        # *upper_left_battery_slot*, *upper_right_battery_slot*, *lower_left_battery_slot*, and
        # *lower_righ_battery_slot*.  Underneath these 4 batteries are 2 more centered battery
        # slots that are called *upper_center_battery_slot* and *lower_center_battery_slot*:
        upper_left_battery_slot: Square = romi.rectangle_locate("BATTERY: Upper Left Battery Slot",
                                                                -5.550937, 4.252594,
                                                                -4.074563, 4.473067)
        upper_right_battery_slot: Square = romi.rectangle_locate(("BATTERY: "
                                                                  "Upper Right Battery Slot"),
                                                                 -3.621799, 4.252594,
                                                                 -2.145425, 4.473067)
        lower_left_battery_slot: Square = romi.rectangle_locate("BATTERY: Lower Left Battery Slot",
                                                                -5.590311, 3.705346,
                                                                -4.113925, 3.925815)
        lower_right_battery_slot: Square = romi.rectangle_locate("BATTERY Lower Right Battery Slot",
                                                                 -3.661173, 3.705346,
                                                                 -2.184799, 3.925815)
        upper_center_battery_slot: Square = romi.rectangle_locate(("BATTERY: Upper Center "
                                                                  "Battery Slot"),
                                                                  -4.58637, 3.012429,
                                                                  -3.109992, 3.232913)
        lower_center_battery_slot: Square = romi.rectangle_locate(("BATTERY: Lower Center "
                                                                   "Battery Slot"),
                                                                  -4.625744, 2.465193,
                                                                  -3.149354, 2.685665)

        # *battery_slot_polygons* list and append them to *polygons*:
        battery_slot_polygons: List[SimplePolygon] = [
            upper_left_battery_slot, upper_right_battery_slot,
            lower_left_battery_slot, lower_right_battery_slot,
            upper_center_battery_slot, lower_center_battery_slot
        ]
        simple_polygons.extend(battery_slot_polygons)

        # There 4 cutouts across the top of the battery case and 3 cutouts along the bottom.
        # The 4 upper cutouts are called *upper_outer_left_cutout*, *upper_inner_left_cutout*,
        # *upper_inner_right_cutout*, and *upper_outer_right_cutout*.
        upper_outer_left_cutout: Square = romi.rectangle_locate("BATTERY: Upper Outer Left Cutout",
                                                                -5.984008, 4.74865,
                                                                -5.302909, 4.965193)
        upper_inner_left_cutout: Square = romi.rectangle_locate("BATTERY: Upper Inner Left Cutout",
                                                                -5.23598, 4.669913,
                                                                -4.861965, 4.858886)
        upper_inner_right_cutout: Square = romi.rectangle_locate(("BATTERY: "
                                                                  "Upper Inner Right Cutout"),
                                                                 -2.873772, 4.669913,
                                                                 -2.499756, 4.858886)
        upper_outer_right_cutout: Square = romi.rectangle_locate(("BATTERY: "
                                                                  "Upper Outer Right Cutout"),
                                                                 -2.432827, 4.74865,
                                                                 -1.751728, 4.965193)

        # There are three cutouts across the bottom of the battery case and they are called
        # *lower_left_cutout*, *lower_center_cutout*, and *lower_right_cutout*:
        lower_left_cutout: Square = romi.rectangle_locate("BATTERY: Lower Left Cutout",
                                                          -5.572591, 1.939594,
                                                          -4.655272, 2.189594)
        lower_center_cutout: Square = romi.rectangle_locate("BATTERY: Lower Center Cutout",
                                                            -4.340311, 2.032122,
                                                            -3.395425, 2.189594)
        lower_right_cutout: Square = romi.rectangle_locate("BATTERY: Lower Right Cutout",
                                                           -3.080465, 1.939594,
                                                           -2.163146, 2.189594)

        # Collect all of the cutouts into *cutout_polygons* and append to *polygons*:
        cutout_polygons: List[SimplePolygon] = [
            upper_outer_left_cutout, upper_inner_left_cutout,
            upper_inner_right_cutout, upper_outer_right_cutout,
            lower_left_cutout, lower_center_cutout, lower_right_cutout
        ]
        simple_polygons.extend(cutout_polygons)

        # There are 4 slots for where the encoder connectors through hole pins land.
        # We will measure two on the right side and mirror them to the left side:
        x1: float = -2.031646 * inches2mm - origin_offset.x - 8.85
        dx: float = 2.5
        x2: float = x1 - dx
        x3: float = x2 - 1.65
        x4: float = x3 - dx
        dy: float = 0.70 * inches2mm

        outer_center: P2D = P2D((x1 + x2) / 2.0, 0.0)
        outer_encoder_slot: Square = Square("RIGHT: Outer Encoder Slot", dx, dy, outer_center,
                                            corner_radius=dx/2.0, corner_count=3)
        inner_center: P2D = P2D((x3 + x4) / 2.0, 0.0)
        inner_encoder_slot: Square = Square("RIGHT: Inner Encoder Slot", dx, dy, inner_center,
                                            corner_radius=dx/2.0, corner_count=3)

        # Collect the encoder slots into *encoder_slots* and append to *polygons*:
        encoder_slots: List[SimplePolygon] = [
            outer_encoder_slot, outer_encoder_slot.y_mirror("RIGHT:", "LEFT:"),
            inner_encoder_slot, inner_encoder_slot.y_mirror("RIGHT:", "LEFT:")
        ]
        simple_polygons.extend(encoder_slots)

        return simple_polygons

    # Romi.hex_pattern_get():
    def hex_pattern_get(self, pattern_rows: Tuple[str, ...], slot_pairs: List[str],
                        hex_origin: P2D, hole_diameter: float,
                        label: str) -> Tuple[List[SimplePolygon], Dict[str, P2D]]:
        """Generate a hexagonal pattern of holes and slots.

        The Romi base and shelf have pattern of holes and slot that are
        hexagonal.  The patterns are quite irregular because that have
        fit within the circular confines of the base and miss other
        feature such as the castor ball assemblies, battery holder, etc.
        This method returns a list of *Polygon*'s that represent each
        hole and slot. It also returns a hole name to location *dict*.

        Args:
            *pattern_rows* (*Tuple*[*str*, ...]): As list of patterns
                that specify where the holes are to be located.  A '-'
                means "no hole", a lower case letter identifies a
                "virtual hole" that is the end-point of a slot, and
                and upper case letter corresponds to an actual hole.
            *slot_pairs* (*List*[*str*]): A list of two letter
                strings, where each letter specifies the end-point of
                a slot.
            *hex_origin (*P*): The known location of one of the
                in the hoes in the pattern.  It is required that
                one of the *pattern_rows* label this locatation with
                an 'O' letter.
            *hole_diameter: (*float*): The diameter of the holes in
                millimeters.
            *label* (*str*): The sub-label for the holes.

        Returns:
            (*List*[*SimplePolygon*], *Dict*[*str*, *P"]): Returns a
                list of hole and slot *SimplePolygons*.  In addition,
                a *dict* that maps each hole letter name to a location
                is returned.

        """
        # Grab some values from *romi* (i.e. *self*):
        romi: Romi = self
        inches2mm: float = romi.inches2mm
        debugging: bool = romi.debugging

        # The hexagonal slots and hole pattern is present on both the top and the
        # bottom of the platform.  The "User's Guide" implies that holes are spaced
        # by 7.5mm vertically.
        #
        # The math for equilateral triagngles is:
        #     b = equilateral triangle base width
        #     h = equalateral triangle height
        #     h = b*sqrt(3)/2
        #     b = 2*h/sqrt(3)
        hex_dy_pitch: float = 7.50
        half_hex_dx_pitch: float = hex_dy_pitch / sqrt(3.0)

        # We need to get the dimensions for one vertical slot and compute the vertical *slot_width*
        # and the *slot_length* which is distance between to centers of the arc end points:
        slot_left_x: float = -2.437146 * inches2mm
        slot_right_x: float = -2.346591 * inches2mm
        slot_top_y: float = 1.339205 * inches2mm
        slot_bottom_y: float = 1.051803 * inches2mm
        slot_dx: float = slot_right_x - slot_left_x
        slot_dy: float = slot_top_y - slot_bottom_y
        # Remember: *slot_length* is from center to center, *NOT* edge to edge:
        slot_length: float = slot_dy - slot_dx
        slot_width: float = slot_dx

        # Perform any requested debugging:
        if debugging:  # pragma: no cover
            print("-------------------")
            print(f"hex_origin={hex_origin}")
            print(f"hole_diameter={hole_diameter}")
            print(f"slot_width={slot_width}")
            print(f"slot_length={slot_length}")
            print(f"half_hex_dx_pitch={half_hex_dx_pitch}")
            print(f"hex_dy_pitch={hex_dy_pitch}")
            print(f"slot_dx={slot_dx}")
            print(f"slot_dy={slot_dy}")
            print(f"slot_length={slot_length}")
            print(f"slot_width={slot_width}")

        # Compute *upper_left_origin_x* and *upper_right_y* which is the X/Y location
        # the upper left location of the *pattern_rows*.  It is computed relative to
        # *hex_origin* base on finding the a hole labeled 'O' in the *pattern_rows*:
        upper_left_origin_x: float = nan
        upper_left_origin_y: float = nan
        y_index: int
        pattern_row: str
        for y_offset, pattern_row in enumerate(pattern_rows):
            x_offset: int = pattern_row.find('O')
            if x_offset >= 0:
                upper_left_origin_x = hex_origin.x - x_offset * half_hex_dx_pitch
                upper_left_origin_y = hex_origin.y + y_offset * hex_dy_pitch
                break
        else:
            assert False, "No origin hole found."  # pragma: no cover
        if debugging:  # pragma: no cover
            print("upper_left_origin_x={upper_left_origin_x}")
            print("upper_left_origin_y={upper_left_origin_y}")

        # The return values are *simple_polygons* and *locations*:
        simple_polygons: List[SimplePolygon] = list()
        locations: Dict[str, P2D] = dict()

        # *pattern_rows* contain the end-point locations for the hex pattern.
        # We iterate across *pattern_rows* in Y first and X second.
        points_count: int = 8
        pattern_index: int
        for y_index, pattern_row in enumerate(pattern_rows):
            y = upper_left_origin_y - (y_index * hex_dy_pitch)
            pattern_character: str
            x_index: float
            for x_index, pattern_character in enumerate(pattern_row):
                # Dispatch on *pattern_character*:
                if pattern_character != '-':
                    # Enter *left_hole_center* into *locations* keyed by *pattern_character*:
                    x = upper_left_origin_x + (x_index * half_hex_dx_pitch)
                    hole_center: P2D = P2D(x, y)
                    locations[pattern_character] = hole_center

                    # Only create holes when *pattern_character* is upper case:
                    if pattern_character.isupper():
                        # Put in the *right_hole*:
                        hole: Circle = Circle(f"RIGHT: {label} Hex Hole ({x_index}, {y_index})",
                                              hole_diameter, points_count, hole_center)
                        simple_polygons.append(hole)

        # Now sweep through *slot_pairs* and install all of the slots:
        corner_radius: float = slot_width / 2.0
        slot_pair: str
        for slot_pair in slot_pairs:
            # Do one slot for each *slot_pair*:
            hole1: P2D = locations[slot_pair[0]]
            hole2: P2D = locations[slot_pair[1]]
            center: P2D = (hole1 + hole2) / 2.0
            slot_angle: float = atan2(hole1.y - hole2.y, hole1.x - hole2.x)
            slot: Square = Square(f"RIGHT: {label} Slot '{slot_pair}'",
                                  slot_length, slot_width, center,
                                  rotate=slot_angle, corner_radius=corner_radius,
                                  corner_count=points_count)
            simple_polygons.append(slot)

        # Return the *simple_polygons* and *locations*:
        return simple_polygons, locations

    # Romi.hole_locate():
    def hole_locate(self, name: str, x1: float, y1: float, x2: float, y2: float) -> Circle:
        """TODO."""
        romi: Romi = self
        origin_offset: P2D = romi.origin_offset
        inches2mm: float = romi.inches2mm
        x1 *= inches2mm
        y1 *= inches2mm
        x2 *= inches2mm
        y2 *= inches2mm

        dx: float = abs(x2 - x1)
        dy: float = abs(y2 - y1)
        center_x: float = (x1 + x2) / 2.0
        center_y: float = (y1 + y2) / 2.0
        diameter: float = (dx + dy) / 2.0
        center: P2D = P2D(center_x, center_y) - origin_offset
        hole: Circle = Circle(name, diameter, 8, center)
        return hole

    # Romi.line_hole_polygons_get():
    def line_hole_polygons_get(self, lower_hex_table: Dict[str, P2D]) -> List[SimplePolygon]:
        """TODO."""
        # Grab some values from *romi* (i.e. *self*):
        romi: Romi = self
        debugging: bool = romi.debugging

        # There is a line of holes along the bottom that have a smaller hole diameter.
        # We locate the smallest hole at the end of the line:
        small_hole: Circle = romi.hole_locate("Small Hole",
                                              -3.289535, 0.256524, -3.198980, 0.165984)
        small_hole_diameter: float = small_hole.diameter
        small_hole_center: P2D = small_hole.center

        if debugging:  # pragma: no cover
            print(f"small_hole_diameter={small_hole_diameter}")
            print(f"small_hole_center={small_hole_center}")

        # Now using *s_center* and *q_center* we compute a "unit" vector along the line.
        # We enter holes that do not over lap with the larger holes.  We wind up skipping
        # one hole in 3:
        line_hole_polygons: List[SimplePolygon] = list()
        s_center: P2D = lower_hex_table["S"]
        q_center: P2D = lower_hex_table["Q"]
        hole_vector: P2D = q_center - s_center
        for vector_hole_index in range(9):
            if vector_hole_index % 3 != 1:
                # Do the hole on the right first:
                hole_center: P2D = (s_center + (vector_hole_index - 1) * hole_vector / 3.0)
                hole: Circle = Circle(f"RIGHT: Vector Hole {vector_hole_index}",
                                      small_hole_diameter, 8, hole_center)
                line_hole_polygons.append(hole)

        return line_hole_polygons

    # Romi.lower_arc_holes_rectangles_get():
    def lower_arc_holes_rectangles_get(self) -> List[SimplePolygon]:
        """TODO."""
        # Grab some values from *romi*:
        romi: Romi = self
        debugging: bool = romi.debugging
        inches2mm: float = romi.inches2mm
        origin_offset: P2D = romi.origin_offset

        # The resulting *Polygon*'s are collected into *lower_arc_holes_rectangles*:
        lower_arc_holes_rectangles: List[SimplePolygon] = []

        # There are arcs of holes and and rectangular slots along the upper and lower rims.
        # Since they are mirrored across the Y axis, we only worry about the right side.
        # The hole closest to the wheel is the "start" hole and the one farthest from the
        # wheel is the "end" hole.  We have to locate each of these holes:
        lower_start: Circle = romi.hole_locate("Lower Start Hole",
                                               -1.483063, 1.348929, -1.357508, 1.223803)
        lower_start_diameter: float = lower_start.diameter
        lower_start_center: P2D = lower_start.center
        lower_arc_start_angle: float = atan2(lower_start_center.y, lower_start_center.x)
        if debugging:  # pragma: no cover
            print(f"lower_start_diameter={lower_start_diameter}")
            print(f"lower_start_center={lower_start_center}")
            print(f"lower_start_angle={degrees(lower_arc_start_angle)}deg")

        # We pick the smallest hole that is next to the hole at the end to get the
        # *small_hole_diameter*:
        lower_end: Circle = romi.hole_locate("Lower End Hole",
                                             -3.144020, 0.125287, -3.053465, 0.034732)
        lower_end_diameter: float = lower_end.diameter
        lower_end_center: P2D = lower_end.center
        small_hole_diameter: float = lower_end_diameter

        lower_arc_end_angle: float = atan2(lower_end_center.y, lower_end_center.x)
        if debugging:  # pragma: no cover
            print(f"lower_start_diameter={lower_start_diameter}")
            print(f"lower_start_center={lower_start_center}")

        # Compute the *lower_arc_radius*:
        origin: P2D = P2D(0.0, 0.0)
        lower_hole_radius: float = origin.distance(lower_start_center)

        # There are two sizes of rectangle -- small and large.  The width appears to
        # be the same for both, so we only need *rectangle_width*, *small_rectangle_length*
        # and *large_rectangle_length*.  Lastly, we need to find one *rectangle_center*
        # so we can determine the *rectangle_radius* from the *origin*:
        large_upper_left_corner: P2D = (P2D(-1.248201 * inches2mm, 1.259484 * inches2mm) -
                                        origin_offset)
        large_lower_left_corner: P2D = (P2D(-1.33137 * inches2mm, 1.136248 * inches2mm) -
                                        origin_offset)
        large_upper_right_corner: P2D = (P2D(-1.205772 * inches2mm, 1.230858 * inches2mm) -
                                         origin_offset)
        large_rectangle_length: float = large_upper_left_corner.distance(large_lower_left_corner)
        rectangle_width: float = large_upper_left_corner.distance(large_upper_right_corner)
        rectangle_center: P2D = (large_upper_right_corner + large_lower_left_corner) / 2.0
        rectangle_radius: float = origin.distance(rectangle_center)
        small_upper_left_corner: P2D = (P2D(-1.368228 * inches2mm, 1.081638 * inches2mm) -
                                        origin_offset)
        small_lower_left_corner: P2D = (P2D(-1.431575 * inches2mm, 0.987760 * inches2mm) -
                                        origin_offset)
        small_rectangle_length: float = small_upper_left_corner.distance(small_lower_left_corner)
        if debugging:  # pragma: no cover
            print(f"lower_hole_radius={lower_hole_radius}")
            print(f"rectangle_radius={rectangle_radius}")
            print(f"rectangle_width={rectangle_width}")
            print(f"large_rectangle_length={large_rectangle_length}")
            print(f"rectangle_center={rectangle_center}")
            print(f"small_rectangle_length={small_rectangle_length}")

        # There are *lower_holes_count* + 1 holes to create along the arc. There are
        # *lower_holes_count* + 3 rectangles to create along the arc:
        lower_holes_count: int = 12
        delta_angle: float = (lower_arc_end_angle - lower_arc_start_angle) / (lower_holes_count - 1)
        lower_hole_index: int
        for lower_hole_index in range(lower_holes_count + 3):
            # The same *lower_arc_hole_diameter* is used for both the left and right arc holes:
            lower_arc_hole_diameter: float = (lower_start_diameter if lower_hole_index % 3 == 0
                                              else small_hole_diameter)

            # Likewise the *lower_rectangle_length* is used both the left and right rectangle arcs:
            lower_rectangle_length: float = (large_rectangle_length if lower_hole_index % 3 == 0
                                             else small_rectangle_length)

            # Do the *lower_right_hole* first:
            lower_hole_angle: float = lower_arc_start_angle + float(lower_hole_index) * delta_angle
            lower_hole_x: float = lower_hole_radius * cos(lower_hole_angle)
            lower_hole_y: float = lower_hole_radius * sin(lower_hole_angle)
            lower_hole_center: P2D = P2D(lower_hole_x, lower_hole_y)
            lower_hole: Circle = Circle(f"RIGHT: Lower hole {lower_hole_index}",
                                        lower_arc_hole_diameter, 8, lower_hole_center)
            if lower_hole_index < lower_holes_count + 1:
                lower_arc_holes_rectangles.append(lower_hole)

            # Next do the *lower_right_rectangle*:
            lower_rectangle_x: float = rectangle_radius * cos(lower_hole_angle)
            lower_rectangle_y: float = rectangle_radius * sin(lower_hole_angle)
            lower_rectangle_center: P2D = P2D(lower_rectangle_x, lower_rectangle_y)
            lower_rectangle: Square = Square(f"RIGHT: Lower left Rectangle {lower_hole_index}",
                                             rectangle_width, lower_rectangle_length,
                                             lower_rectangle_center, lower_hole_angle)
            lower_arc_holes_rectangles.append(lower_rectangle)

        # Return the resuting *arc_hole_rectangle_polygons*:
        return lower_arc_holes_rectangles

    # Romi.lower_hex_polygons_table_get():
    def lower_hex_polygons_table_get(self) -> Tuple[List[SimplePolygon], Dict[str, P2D]]:
        """TODO."""
        # The "User's Guide" identifies the lower hex whole used to reference the hex
        # pattern off of:
        # Grab some values from *romi* (i.e. *self*):
        romi: Romi = self
        debugging: bool = romi.debugging

        # Extract the origin hole information for the lower hexagon pattern:
        lower_hex_hole: Circle = romi.hole_locate("Lower Hex Hole",
                                                  -2.454646, 1.553776, -2.329091, 1.428650)
        lower_hex_hole_center: P2D = lower_hex_hole.center
        lower_hex_hole_diameter: float = lower_hex_hole.diameter
        if debugging:  # pragma: no cover
            print(f"lower_hex_hole_center={lower_hex_hole_center}")
            print(f"lower_hex_hole_diameter={lower_hex_hole_diameter}")

        # Using the `.dxf` image, the pattern below represent the locations of the hex pattern
        # holes in the lower left quadrant.  'O' is at *lower_hex_hole_center*.  Upper case letters
        # indicate the location of a hole.  Lower case letters indicate  the end-point of a slot.
        # There is a weird little half slot above 'O' that is not currently modeled:
        lower_pattern_rows: Tuple[str, ...] = (
            "---A-B-C-D-",  # [-1]
            "----E-O-F-G",  # [0]
            "---a-H-I-J-",  # [1]
            "----K-L-M--",  # [2]
            "---N-Q-----",  # [3]
            "R-S---------"  # [4]
        )

        # *lower_slot_pairs* specifies the holes that bracket a slot.:
        lower_slot_pairs: List[str] = "AO:OD:Aa:aO:JO:DJ:OL:aL:LJ:aN:NL:RN".split(':')

        # Now we can invoke the *hex_pattern* method to fill in the hex pattern and
        # mirror it across the Y axis to the other sise:
        lower_hex_holes_table: Dict[str, P2D]

        lower_hex_polygons: List[SimplePolygon]
        lower_hex_polygons, lower_holes_table = romi.hex_pattern_get(lower_pattern_rows,
                                                                     lower_slot_pairs,
                                                                     lower_hex_hole_center,
                                                                     lower_hex_hole_diameter,
                                                                     "LOWER")
        return lower_hex_polygons, lower_holes_table

    # Romi.miscellaneous_holes_get():
    def miscellaneous_holes_get(self) -> List[Circle]:
        """Return the miscellaneous holes."""
        # Around the lower hex pattern there are a bunch of miscellaneous holes
        # around the periphery of the patten.  This code just picks them off:
        romi: Romi = self
        lower_left_hole: Circle = romi.hole_locate("RIGHT: Misc Small Lower Left",
                                                   -3.119047, 0.658110,
                                                   -3.041756, 0.74865)
        upper_left_hole: Circle = romi.hole_locate("RIGHT: Misc Small Upper Left",
                                                   -3.028492, 1.642358,
                                                   -3.119047, 1.732913)
        upper_right_hole_minus30: Circle = romi.hole_locate("RIGHT: Misc Small Upper Right -30deg",
                                                            -1.755228, 1.642358,
                                                            -1.664673, 1.732913)
        upper_right_hole_30: Circle = romi.hole_locate("RIGHT: Misc Small Upper Right 30deg",
                                                       -1.755228, 1.839205,
                                                       -1.664673, 1.929760)
        upper_right_hole_90: Circle = romi.hole_locate("RIGHT: Misc Small Upper Right 90deg",
                                                       -1.925717, 1.937638,
                                                       -1.835161, 2.028177)
        upper_right_hole_120: Circle = romi.hole_locate("RIGHT: Misc Small Upper Right 120deg",
                                                        -2.096189, 1.839205,
                                                        -2.005634, 1.929760)
        upper_right_large: Circle = romi.hole_locate("RIGHT: Misc Large Upper Right",
                                                     -1.84402, 2.252594,
                                                     -1.71848, 2.127469)

        # Store all of the located holes into a list of *miscellaneous_holes*:
        miscellaneous_holes: List[Circle] = [
            lower_left_hole,
            upper_left_hole,
            upper_right_hole_minus30,
            upper_right_hole_30,
            upper_right_hole_90,
            upper_right_hole_120,
            upper_right_large
        ]
        return miscellaneous_holes

    # Romi.rectangle_locate():
    def rectangle_locate(self, name: str, x1: float, y1: float,
                         x2: float, y2: float) -> Square:
        """Locate a non-rotated rectangle and return it as a Square.

        Args:
            *name* (*str*): The name to assign to the returned
                *Polygon*.
            *x1* (*float*): One of sides of the rectangle in inches.
            *y1* (*float*): Either the top or bottom edge the rectangle
                in inches.
            *x1* (*float*): One of sides of the rectangle in inches.
            *y2* (*float*): The other top/bottom edge of the rectangle
                in inches:

        Returns:
            (*Polygon*) Returns a *Polygon* that represents the
            rectangle.

        """
        # Grab some values from *romi* (i.e. *self*):
        romi: Romi = self
        origin_offset: P2D = romi.origin_offset
        inches2mm: float = romi.inches2mm

        # Convert *x1*, *y1*, *x2*, and *y2* from inches to millimeters:
        x1 *= inches2mm
        y1 *= inches2mm
        x2 *= inches2mm
        y2 *= inches2mm
        dx: float = abs(x2 - x1)
        dy: float = abs(y2 - y1)
        center: P2D = P2D((x1 + x2) / 2.0, (y1 + y2) / 2.0) - origin_offset

        # Create and return the *rectangle* (which is stored in a *Square* object):
        rectangle: Square = Square(name, dx, dy, center)
        return rectangle

    # Romi.upper_arc_holes_rectangles_get():
    def upper_arc_holes_rectangles_get(self) -> List[SimplePolygon]:
        """TODO."""
        # Grab some values from *romi*:
        romi: Romi = self
        debugging: bool = romi.debugging
        inches2mm: float = romi.inches2mm
        origin_offset: P2D = romi.origin_offset

        # The resulting *Polygon*'s are collected into *upper_arc_holes_rectangles*:
        upper_arc_holes_rectangles: List[SimplePolygon] = []

        # There are arcs of holes and and rectangular slots along the upper and lower rims.
        # Since they are mirrored across the Y axis, we only worry about the right side.
        # The hole closest to the wheel is the "start" hole and the one farthest from the
        # wheel is the "end" hole.  We have to locate each of these holes:
        upper_start: Circle = romi.hole_locate("Upper Start Hole",
                                               -1.483063, 4.651469, -1.357508, 4.526346)
        upper_start_diameter: float = upper_start.diameter
        upper_start_center: P2D = upper_start.center
        upper_arc_start_angle: float = atan2(upper_start_center.y, upper_start_center.x)
        if debugging:  # pragma: no cover
            print(f"upper_start_diameter={upper_start_diameter}")
            print(f"upper_start_center={upper_start_center}")
            print(f"upper_start_angle={degrees(upper_arc_start_angle)}deg")

        upper_end: Circle = romi.hole_locate("Upper End Hole",
                                             -3.14402, 5.840524, -3.053465, 5.749969)
        upper_end_diameter: float = upper_end.diameter
        upper_end_center: P2D = upper_end.center
        upper_arc_end_angle: float = atan2(upper_end_center.y, upper_end_center.x)
        if debugging:  # pragma: no cover
            print(f"upper_end_diameter={upper_end_diameter}")
            print(f"upper_end_center={upper_end_center}")

        # Compute the *upper_hole_radius*:
        origin: P2D = P2D(0.0, 0.0)
        upper_hole_radius: float = origin.distance(upper_start_center)

        # There are two sizes of rectangle -- small and large.  The width appears to
        # be the same for both, so we only need *rectangle_width*, *small_rectangle_length*
        # and *large_rectangle_length*.  Lastly, we need to find one *rectangle_center*
        # so we can determine the *rectangle_radius* from the *origin*:
        large_upper_inner_corner: P2D = (P2D(-1.33137 * inches2mm, 4.739012 * inches2mm) -
                                         origin_offset)
        large_lower_inner_corner: P2D = (P2D(-1.248201 * inches2mm, 4.615776 * inches2mm) -
                                         origin_offset)
        large_lower_outer_corner: P2D = (P2D(-1.205772 * inches2mm, 4.644402 * inches2mm) -
                                         origin_offset)
        large_rectangle_length: float = large_upper_inner_corner.distance(large_lower_inner_corner)
        rectangle_width: float = large_lower_inner_corner.distance(large_lower_outer_corner)
        rectangle_center: P2D = (large_upper_inner_corner + large_lower_outer_corner) / 2.0
        rectangle_radius: float = origin.distance(rectangle_center)
        small_upper_inner_corner: P2D = (P2D(-1.431575 * inches2mm, 4.887512 * inches2mm) -
                                         origin_offset)
        small_lower_inner_corner: P2D = (P2D(-1.368228 * inches2mm, 4.793638 * inches2mm) -
                                         origin_offset)
        small_rectangle_length: float = small_upper_inner_corner.distance(small_lower_inner_corner)
        if debugging:  # pragma: no cover
            print(f"upper_hole_radius={upper_hole_radius}")
            print(f"rectangle_radius={rectangle_radius}")
            print(f"rectangle_width={rectangle_width}")
            print(f"large_rectangle_length={large_rectangle_length}")
            print(f"rectangle_center={rectangle_center}")
            print(f"small_rectangle_length={small_rectangle_length}")

        # There *upper_holes_count* holes and rectangles to create along the arc. Not holes are
        # created.  There are *upper_holes_count* + 1 rectangles and all of these are poplulated:
        small_hole_diameter = upper_end_diameter
        upper_holes_count: int = 12
        delta_angle: float = (upper_arc_end_angle - upper_arc_start_angle) / (upper_holes_count - 1)
        upper_hole_index: int
        for upper_hole_index in range(upper_holes_count + 1):
            # The same *upper_arc_hole_diameter* is used for both the left and right arc holes:
            upper_arc_hole_diameter: float = (upper_start_diameter if upper_hole_index % 3 == 0
                                              else small_hole_diameter)

            # Likewise the *lower_rectangle_length* is used both the left and right rectangle arcs:
            upper_rectangle_length: float = (large_rectangle_length if upper_hole_index % 3 == 0
                                             else small_rectangle_length)

            # Do the *lower_right_hole* first:
            upper_hole_angle: float = upper_arc_start_angle + float(upper_hole_index) * delta_angle
            upper_hole_x: float = upper_hole_radius * cos(upper_hole_angle)
            upper_hole_y: float = upper_hole_radius * sin(upper_hole_angle)
            upper_hole_center = P2D(upper_hole_x, upper_hole_y)
            upper_hole: Circle = Circle(f"RIGHT: Upper hole {upper_hole_index}",
                                        upper_arc_hole_diameter, 8, upper_hole_center)

            # Skip 3 of the holes:
            if upper_hole_index not in (2, 3, 12, 13):
                upper_arc_holes_rectangles.append(upper_hole)

            # Next do the *upper_rectangle*:
            upper_rectangle_x: float = rectangle_radius * cos(upper_hole_angle)
            upper_rectangle_y: float = rectangle_radius * sin(upper_hole_angle)
            upper_rectangle_center: P2D = P2D(upper_rectangle_x, upper_rectangle_y)
            upper_rectangle: Square = Square(f"RIGHT: Upper Right Rectangle {upper_hole_index}",
                                             rectangle_width, upper_rectangle_length,
                                             upper_rectangle_center, upper_hole_angle)
            upper_arc_holes_rectangles.append(upper_rectangle)

        # Return the resulting *arc_holes_rectangles*:
        return upper_arc_holes_rectangles

    # Romi.upper_hex_polygons_get():
    def upper_hex_polygons_get(self) -> List[SimplePolygon]:
        """TODO."""
        # Grab some values from *romi* (i.e. *self*):
        romi: Romi = self
        debugging: bool = romi.debugging

        # For the upper hex pattern, the hole that is at the end of the 4 slots is selected
        # as the upper hex hole:
        upper_hex_hole: Circle = romi.hole_locate("Upper Hex Hole",
                                                  -2.749535, 5.441567, -2.629075, 5.316441)
        upper_hex_hole_center: P2D = upper_hex_hole.center
        upper_hex_hole_diameter: float = upper_hex_hole.diameter
        if debugging:  # pragma: no cover
            print(f"upper_hex_hole_center={upper_hex_hole_center}")
            print(f"upper_hex_hole_diameter={upper_hex_hole_diameter}")

        # For the *upper_pattern_rows*, the 'O' marks the *upper_hex_hole_center*:
        upper_pattern_rows: Tuple[str, ...] = (
            "a------",
            "-A-O---",
            "b-B-C-c",
            "---d---",
        )

        # *upper_slot_pairs* specifies which slots to render.  Now we can invoke the *hex_pattern*
        # method to render the hex pattern and mirror it across to the other side:
        upper_slot_pairs: List[str] = "aO:bO:dO:cO".split(':')
        upper_holes_table: Dict[str, P2D]
        upper_hex_polygons: List[SimplePolygon]
        upper_hex_polygons, upper_holes_table = romi.hex_pattern_get(upper_pattern_rows,
                                                                     upper_slot_pairs,
                                                                     upper_hex_hole_center,
                                                                     upper_hex_hole_diameter,
                                                                     "UPPER")

        # The *upper_holes_table* is not needed, we just return *upper_hex_polygons*:
        return upper_hex_polygons

    # Romi.vertical_rectangles_get():
    def vertical_rectangles_get(self) -> List[Square]:
        """Return the vertical wheel well rectangles."""
        romi: Romi = self
        upper_rectangle0: Square = romi.rectangle_locate("RIGHT: UPPER: Rectangle 0",
                                                         -1.511965, 3.569984,
                                                         -1.460783, 3.683232)
        upper_rectangle1: Square = romi.rectangle_locate("RIGHT: UPPER: Rectangle 1",
                                                         -1.511965, 3.749122,
                                                         -1.460783, 3.897803)
        upper_rectangle2: Square = romi.rectangle_locate("RIGHT: UPPER: Rectangle 2",
                                                         -1.511965, 3.963677,
                                                         -1.460783, 4.076929)
        upper_rectangle3: Square = romi.rectangle_locate("RIGHT: UPPER: Rectangle 3",
                                                         -1.511965, 4.142815,
                                                         -1.460783, 4.291496)
        upper_rectangles: List[Square] = [
            upper_rectangle0,
            upper_rectangle1,
            upper_rectangle2,
            upper_rectangle3
        ]
        upper_rectangle: Square
        lower_rectangles: List[Square] = []
        for upper_rectangle in upper_rectangles:
            lower_rectangle: SimplePolygon = upper_rectangle.x_mirror("UPPER:", "LOWER:")
            assert isinstance(lower_rectangle, Square)
            lower_rectangles.append(lower_rectangle)
        vertical_rectangles: List[Square] = upper_rectangles + lower_rectangles
        return vertical_rectangles


def main() -> int:  # pragma: no cover
    """Generate the openscand file."""
    # print("romi_model.main() called")
    romi: Romi = Romi()
    romi_base_polygon: Polygon = romi.base_scad_polygon_generate()
    scad_file: IO[Any]
    with open("romi_base_dxf.scad", "w") as scad_file:
        romi_base_polygon.scad_file_write(scad_file)

    romi_base_extruded_polygon: LinearExtrude = LinearExtrude("Romi Base Extrude",
                                                              romi_base_polygon, 9.6)
    union: Union = Union("Base Union", [romi_base_extruded_polygon])
    with open("romi_base.scad", "w") as scad_file:
        union.scad_file_write(scad_file)

    romi_base_simple_polygons: List[SimplePolygon] = romi_base_polygon.simple_polygons_get()
    romi_base_simple_polygon: SimplePolygon
    # Generate *romi_base_keys* skipping the first *SimplePolygon* which is the outer one:
    romi_base_keys: List[Tuple[Any, ...]] = [romi_base_simple_polygon.key()
                                             for romi_base_simple_polygon
                                             in romi_base_simple_polygons[1:]]
    romi_base_keys.sort()
    csv_file: IO[Any]
    with open("romi_base.csv", "w") as csv_file:
        Scad.keys_csv_file_write(romi_base_keys, csv_file)
    html_file: IO[Any]
    with open("romi_base.html", "w") as html_file:
        Scad.keys_html_file_write(romi_base_keys, html_file, "Romi Base Holes and Rectangles")

    return 0
