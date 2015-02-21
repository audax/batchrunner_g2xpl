Batch Runner for G2XPL
======================
This tool runs g2xpl for you flightplan, so you can ensure
that your route is covered by nice textures.

## Usage

Call it like this:

    python batch.py EDDVLOWW.fms

The flight plan should be in the same format as the X-Plane
default GNS 430/530 expects.

See

    python batch.py --help

for further information.

## Configuration

Open batch.py and edit the constants at the top.

#### LOG
Path to the log file which is used to ensure that no tiles
are created twice.

#### INI
Path to the g2xpl.ini

#### G2XPL_DIRECTORY
Working directory for g2xpl

### Copyright and License

Code by Jens Kadenbach and released under WTFPL license