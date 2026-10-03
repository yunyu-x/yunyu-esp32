# -*- coding: utf-8 -*-
"""Kinematics Transformation Engine"""
import math
from typing import Tuple
from .models import Point3D, Quaternion


class KinematicsTransformer:
    """
    Solves rigid-body translation, Euler rotation, and point transformation.
    """
    def __init__(self, roll: float = 0.0, pitch: float = 0.0, yaw: float = 0.0):
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw

    def set_euler_angles(self, roll: float, pitch: float, yaw: float):
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw

    def rotate_point(self, point: Point3D) -> Point3D:
        """Applies Z-Y-X Tait-Bryan rotation sequence."""
        cr = math.cos(self.roll)
        sr = math.sin(self.roll)
        cp = math.cos(self.pitch)
        sp = math.sin(self.pitch)
        cy = math.cos(self.yaw)
        sy = math.sin(self.yaw)

        # 3x3 Rotation matrix entries
        r11 = cy * cp
        r12 = cy * sp * sr - sy * cr
        r13 = cy * sp * cr + sy * sr

        r21 = sy * cp
        r22 = sy * sp * sr + cy * cr
        r23 = sy * sp * cr - cy * sr

        r31 = -sp
        r32 = cp * sr
        r33 = cp * cr

        new_x = r11 * point.x + r12 * point.y + r13 * point.z
        new_y = r21 * point.x + r22 * point.y + r23 * point.z
        new_z = r31 * point.x + r32 * point.y + r33 * point.z

        return Point3D(new_x, new_y, new_z)

    def translate_point(self, point: Point3D, offset: Tuple[float, float, float]) -> Point3D:
        dx, dy, dz = offset
        return Point3D(point.x + dx, point.y + dy, point.z + dz)

    def transform_full(self, point: Point3D, offset: Tuple[float, float, float]) -> Point3D:
        rotated = self.rotate_point(point)
        return self.translate_point(rotated, offset)
