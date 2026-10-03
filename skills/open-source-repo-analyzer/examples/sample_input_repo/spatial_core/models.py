# -*- coding: utf-8 -*-
"""Spatial Coordinate and Orientation Data Models"""
import math
from dataclasses import dataclass


@dataclass
class Point3D:
    x: float
    y: float
    z: float

    def magnitude(self) -> float:
        """Computes Euclidean distance from origin."""
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self) -> "Point3D":
        mag = self.magnitude()
        if mag == 0:
            return Point3D(0.0, 0.0, 0.0)
        return Point3D(self.x / mag, self.y / mag, self.z / mag)


@dataclass
class Quaternion:
    w: float
    x: float
    y: float
    z: float

    def is_unit(self, tolerance: float = 1e-6) -> bool:
        norm_sq = self.w**2 + self.x**2 + self.y**2 + self.z**2
        return abs(norm_sq - 1.0) < tolerance
