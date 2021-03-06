# HBRC ROS Robot Electical Issues

The organization of this directory is organized around PCB's (Printed Circuit Boards) and
orders (PCB/Part orders.)  The KiCad printed circuit board software is exclusively used.
Each PCB is given PCB specific sub-directory (e.g. `master_board` or `encoder`).  Furthermore,
each PCB has a separate revision directory of the form `rev_` followed by a lower case letter
(e.g. `rev_a`, `rev_b`, etc.)  All of the KiCad files and sub-directories are installed
under these revision sub-directories.  In each, revision sub-directory, there are three
special sub-directories called `pretty`, `sweet` and `kiparts`:

* `pretty`: A sub-directory containing KiCad component footprints.

* `sweet`: A sub-directory contains KiCad schematic symbols.

* `kiparts`: A sub-directory of `.csv` (Comma Separated Values) that are used
  to construct some of the parts in the `sweet` directory.

The `orders` directory is organized PCB and part orders.  Each order has a
separate sub-directory called `orderN`, where N is an integer starting from 1
(e.g. `order1`, `order2`, etc.)  Each `orderN` directory contains a `pretty`, `sweet`,
and `kiparts` sub-directory that contains, KiCad footprints, KiCad Schematic symbols,
and `kipart` `.csv` files respectively.

Here is the punch line.  Each PCB board revision `pretty`, `sweet` and `kiparts`
sub-directory is actually a symbolic link to an order directory.  What this ensures
is that ***ALL*** KiCad footprints/schematic and kiparts are the same and shared
across a single order.  Once an order is made, all of the KiCAD files and order
files are locked down ***HARD*** and never edited again.  This way we can safely
come back and look at older revisions.  This also means that any footprints and
schematic symbols from the KiCad libraries are copied over into the order directories.

In general, you should just use what you want when designing a board.  The order
person will get everything locked down before shipping the board orders and PCB
orders out.

Here is a crufty ASCII art directory tree:

     electrical/
     +- master_board/
     |  +- rev_a/
     |  |  +- pretty => ../../orders/order1/pretty
     |  |  +- sweet -> ../../orders/order1/sweet
     |  |  +- kiparts -> ../../orders/order1/kiparts
     |  +- rev_b/
     |     +- pretty => ../../orders/order2/pretty
     |     +- sweet -> ../../orders/order2/sweet
     |     +- kiparts -> ../../orders/order2/kiparts
     +- encoder/
     |  +- rev_a/
     |     +- pretty => ../../orders/order2/pretty
     |     +- sweet -> ../../orders/order2/sweet
     |     +- kiparts -> ../../orders/order2/kiparts	
     +- orders/
           +- order1/
           |  +- pretty/
           |  +- sweet/
           |  +- kiparts/
           +- order2/
              +- pretty/
              +- sweet/
              +- kiparts/

This is a program called [`kipart`](https://kipart.readthedocs.io/en/latest/)
that takes a `.csv` file and generates a KiCad schematic part file.  Since
many schematics are full of square modules, program generates the square
schematic symbols with the right pin names, numbers, and signal types.  It
is generally easier to use `kipart` to manage KiCad schematic symbols than
to use the KiCad schematic symbol library.  There is a `makefile` that runs
`kipart` over all of the `.csv` files in the `kiparts` sub-directory.

Finally, there is the microcontroller.  The microcontroller is from the
STM Electronics family of microcontrollers.  There is a tool called `STM32CubeMX`
that is used to configure the pin bindings of the microcontroller.  The main
content of the file has a suffix of `.ioc`.  The `STM32CubeMX` program reads
and manipulates the `.ioc` file.  In addition, you can generate a `.csv` file
that has a summary of the pin bindings from the `.ioc` file.  The `kicube32`
program reads this `.csv` file and generates another `.csv` file that contains
the schematic symbols for the processor.

Thus the flow is:

     .ioc => STMCubeMX => .csv => kicbube32 -> .csv -> kipart -> .lib -> KiCad

Whew.  This is all automated using the `make` program and appropriate `Makefile`'s.

The design rules for schematic capture are:

* All text is horizontal (no exceptions) and the same size.
* All net names are upper case letters and digits.  A lower case `n` can be used
  as a prefix indicate an active low logic line.
* No rectangular symbols have wires coming out vertically connections are horizontal.
* All wire are on a rectangular grid.
* When possible try to organize the schematic such that inputs are on the left
  and outputs are on the right.
* Hierarchical design is used to organize the sheets.
* Try to keep "air wires" to a minimum.
* Make all power and ground connections explicit.
* Resistors use the older "3 hump" style.
