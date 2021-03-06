import re
import sys
import subprocess as sub
import argparse
from os import path

LOG = 'batch.log'
G2XPL_DIRECTORY = '.'
INI = 'g2xpl.ini'

def surrounds(point, width):
        x, y = point
        for diff in range(1, width+1):
                yield x+diff, y
                yield x-diff, y
                yield x, y+diff
                yield x, y-diff
                yield x+diff, y+diff
                yield x-diff, y-diff

def generate_coords(start, stop, width):
        x1, y1 = start
        x2, y2 = stop
        dx = x2 - x1
        dy = y2 -y1
        step = 1 if x1 < x2 else -1
        yield (x1, y1)
        for p_x, p_y in surrounds((x1,y1), width):
                yield p_x, p_y
				
		yield (x2, y2)
        for p_x, p_y in surrounds((x2,y2), width):
                yield p_x, p_y
				
        for x in range(x1, x2, step):
                y = y1 + dy * (x-x1) / dx
                yield (x,y)
                for p_x, p_y in surrounds((x,y), width):
                        yield p_x, p_y

def parse_plan(plan):
    lines = filter(None, (line.strip() for line in plan.readlines()))
    waypoints = lines[4:]
    for line in waypoints:
        parts = line.split()
        if parts[0] != '0':
            yield int(float(parts[3])), int(float(parts[4]))

def segments(waypoints):
    waypoints = list(waypoints)
    for i in range(1, len(waypoints)):
        yield waypoints[i-1], waypoints[i]

def coordinates_for_segments(segs, width):
    coords = set()
    for seg in segs:
        coords |= set(generate_coords(seg[0], seg[1], width))
    return coords

def run_g2xpl(lat, long):
    ini_path = path.join(G2XPL_DIRECTORY, 'g2xpl.ini')

    with open(ini_path, 'r') as f:
        ini = f.read()

    ini = re.sub('plane_long\s*=\s*[-+0-9.]+',
                             'plane_long='+str(long+0.5), ini)
    ini = re.sub('plane_lat\s*=\s*[-+0-9.]+',
                             'plane_lat='+str(lat+0.5),  ini)
    with open(ini_path, 'w') as f:
        f.write(ini)

    ret = sub.call(path.join(G2XPL_DIRECTORY, 'g2xpl.exe'))
    return ret == 0

def main():
    parser = argparse.ArgumentParser(description='Batchrunner for g2xpl')
    parser.add_argument('plan', metavar='PLAN', type=file, help='Flightplan in .fms format')
    parser.add_argument('--width', metavar='WIDTH', type=int,
        help='Amount of surrounding tiles to render', default=1)
    parser.add_argument('--dummy', action='store_true',
            help='Print the coordinates of the tiles and exit')

    args = parser.parse_args()

    with args.plan as p:
        route = parse_plan(p)
        coordinates = coordinates_for_segments(segments(route), width=args.width)

    try:
        with open(LOG, 'r+') as log:
                points = set(tuple(map(int, line.split(', '))) for line in log.readlines()
                        if not line.startswith('#'))
                coordinates -= points
    except IOError:
        pass

    if args.dummy:
        print sorted(coordinates)
        return

    for lat, long in sorted(coordinates):
        with open(LOG, 'a') as log:
            entry = "{}, {}\n".format(lat, long)
            if not run_g2xpl(lat, long):
                entry = '#'+entry
            log.write(entry)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass

