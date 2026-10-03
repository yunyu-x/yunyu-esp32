#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Command-line interface for spatial kinematics mini"""
import sys
import argparse
from pathlib import Path

# Add local path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from spatial_core.models import Point3D
from spatial_core.transform import KinematicsTransformer


def main():
    parser = argparse.ArgumentParser(description="Spatial Kinematics CLI Runner")
    parser.add_argument("--x", type=float, default=1.0, help="Initial X coordinate")
    parser.add_argument("--y", type=float, default=0.0, help="Initial Y coordinate")
    parser.add_argument("--z", type=float, default=0.0, help="Initial Z coordinate")
    parser.add_argument("--yaw-deg", type=float, default=0.0, help="Yaw rotation in degrees")
    args = parser.parse_args()

    import math
    yaw_rad = math.radians(args.yaw_deg)
    transformer = KinematicsTransformer(yaw=yaw_rad)
    pt = Point3D(args.x, args.y, args.z)
    res = transformer.rotate_point(pt)
    print(f"Original Point: ({pt.x}, {pt.y}, {pt.z})")
    print(f"Transformed Point (Yaw {args.yaw_deg} deg): ({res.x:.4f}, {res.y:.4f}, {res.z:.4f})")


if __name__ == "__main__":
    main()
