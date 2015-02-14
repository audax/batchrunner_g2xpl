import re
import sys
import subprocess
from os import path

WIDTH = 1
LOG = 'batch.log'
INI = 'g2xpl.ini'
G2XPL_DIRECTORY = '.'

class G2XPLException(Exception):
    pass

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
        for x in range(x1, x2, step):
                y = y1 + dy * (x-x1) / dx
                yield (x,y)
                for p_x, p_y in surrounds((x,y), width):
                        yield p_x, p_y

def parse_plan(plan):
    lines = filter(None, plan.readlines())
    waypoints = lines[4:]
    for line in waypoints:
        parts = line.split()
        yield int(float(parts[3])), int(float(parts[4]))

def segments(waypoints):
    waypoints = list(waypoints)
    for i in range(1, len(waypoints)):
        yield waypoints[i-1], waypoints[i]

def coordinates_for_segments(segs):
    coords = set()
    for seg in segs:
        coords |= set(generate_coords(seg[0], seg[1], WIDTH))
    return coords

def run_g2xpl(lat, long):
        with open(INI) as f:
                ini = f.read()

        ini = re.sub('plane_long\s*=\s*[-+0-9.]+',
                                 'plane_long='+str(long+0.5), ini)
        ini = re.sub('plane_lat\s*=\s*[-+0-9.]+',
                                 'plane_lat='+str(lat+0.5),  ini)

        with open(path.join(G2XPL_DIRECTORY, 'g2xpl.ini'), 'w') as f:
                f.write(ini)

        ret = subprocess.call(path.join(G2XPL_DIRECTORY, 'g2xpl.exe'),
                              stdout=sys.stdout, stderr=sys.stderr, cwd=G2XPL_DIRECTORY)
        return ret == 0

def main(plan):                        
    with open(plan, 'r') as p:
        route = parse_plan(p)
        coordinates = coordinates_for_segments(segments(route))

    with open(LOG, 'r+') as log:
            points = set(tuple(map(int, line.split(', '))) for line in log.readlines())
            coordinates -= points

    for lat, long in sorted(coordinates):
        if run_g2xpl(lat, long):
            with open(LOG, 'a') as log:
                    log.write("{}, {}\n".format(lat, long))
        else:
            raise G2XPLException('Error running G2XPL, see shell output')

if __name__ == '__main__':
    plan = sys.argv[1]
    try:
        main(plan)
    except KeyboardInterrupt:
        pass

