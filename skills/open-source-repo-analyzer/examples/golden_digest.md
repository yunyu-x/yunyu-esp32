# Repository Context Package: sample_input_repo

> 纯确定性打包生成，严格按 POSIX 路径字典序排列以优化 LLM Prompt Caching 命中率。

## 1. 仓库全景指标
- **文件总数**: 10
- **代码总行数**: 238
- **预估 Token 数**: ~1,830
- **脱敏凭据数**: 0

## 2. 目录拓扑结构
```text
sample_input_repo/
  └── README.md (0.3 KB)
  └── cli.py (1.2 KB)
  ├── native/
    └── kinematics.go (0.5 KB)
  └── pyproject.toml (0.2 KB)
  ├── spatial_core/
    └── __init__.py (0.2 KB)
    └── models.py (0.8 KB)
    └── transform.py (1.7 KB)
  ├── tests/
    └── __init__.py (0.0 KB)
    └── test_transform.py (1.0 KB)
  ├── web/
    └── viewer.ts (0.8 KB)
```

## 3. 源文件代码包

### File: `README.md` (8 lines, ~81 tokens)
```md
# Spatial Kinematics Mini

A lightweight pure-Python robotics kinematics library for 3D coordinate transformation and rigid-body orientation calculations.

## Features
- Pure Python with zero external dependencies
- Support for Euler angles, Quaternions, and SE(3) transformation matrices
- Fast deterministic unit test suite

```

### File: `cli.py` (33 lines, ~297 tokens)
```py
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

```

### File: `native/kinematics.go` (23 lines, ~122 tokens)
```go
// Package native provides high-performance CGo / Go native robotics bindings
package native

import (
	"math"
)

type SpatialVector struct {
	X float64
	Y float64
	Z float64
}

func (v *SpatialVector) Magnitude() float64 {
	return math.Sqrt(v.X*v.X + v.Y*v.Y + v.Z*v.Z)
}

func ComputeForwardKinematics(joints []float64) (*SpatialVector, error) {
	if len(joints) == 0 {
		return &SpatialVector{X: 0, Y: 0, Z: 0}, nil
	}
	return &SpatialVector{X: joints[0] * 10.0, Y: 0.0, Z: 5.0}, nil
}

```

### File: `pyproject.toml` (7 lines, ~62 tokens)
```toml
[project]
name = "spatial-kinematics-mini"
version = "0.1.0"
description = "Miniature spatial kinematics and coordinate transformation toolkit"
authors = [{ name = "YunYu", email = "yunyu@example.com" }]
dependencies = []
requires-python = ">=3.10"

```

### File: `spatial_core/__init__.py` (6 lines, ~52 tokens)
```py
# -*- coding: utf-8 -*-
"""Spatial Kinematics Core Package"""
from .models import Point3D, Quaternion
from .transform import KinematicsTransformer

__all__ = ["Point3D", "Quaternion", "KinematicsTransformer"]

```

### File: `spatial_core/models.py` (33 lines, ~197 tokens)
```py
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

```

### File: `spatial_core/transform.py` (56 lines, ~446 tokens)
```py
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

```

### File: `tests/__init__.py` (2 lines, ~11 tokens)
```py
# -*- coding: utf-8 -*-
"""Tests package"""

```

### File: `tests/test_transform.py` (31 lines, ~262 tokens)
```py
# -*- coding: utf-8 -*-
import unittest
import math
from spatial_core.models import Point3D, Quaternion
from spatial_core.transform import KinematicsTransformer


class TestKinematics(unittest.TestCase):
    def test_point_magnitude(self):
        p = Point3D(3.0, 4.0, 0.0)
        self.assertAlmostEqual(p.magnitude(), 5.0)

    def test_translation(self):
        transformer = KinematicsTransformer()
        p = Point3D(1.0, 2.0, 3.0)
        p_trans = transformer.translate_point(p, (10.0, -2.0, 5.0))
        self.assertAlmostEqual(p_trans.x, 11.0)
        self.assertAlmostEqual(p_trans.y, 0.0)
        self.assertAlmostEqual(p_trans.z, 8.0)

    def test_rotation_yaw_90(self):
        transformer = KinematicsTransformer(yaw=math.pi / 2.0)
        p = Point3D(1.0, 0.0, 0.0)
        rotated = transformer.rotate_point(p)
        self.assertAlmostEqual(rotated.x, 0.0, places=5)
        self.assertAlmostEqual(rotated.y, 1.0, places=5)
        self.assertAlmostEqual(rotated.z, 0.0, places=5)


if __name__ == "__main__":
    unittest.main()

```

### File: `web/viewer.ts` (39 lines, ~210 tokens)
```ts
// TypeScript Web 3D Visualization Adapter
import { Point3D } from '../spatial_core/models';

export interface ViewerOptions {
  canvasId: string;
  fps: number;
  enableAntiAliasing: boolean;
}

export class PoseViewer {
  private canvasId: string;
  private isRunning: boolean;

  constructor(options: ViewerOptions) {
    this.canvasId = options.canvasId;
    this.isRunning = false;
  }

  public startRenderLoop(): void {
    this.isRunning = true;
    console.log(`Starting render loop on ${this.canvasId}`);
  }

  public renderAxes(origin: Point3D): boolean {
    if (!this.isRunning) {
      return false;
    }
    // Render X, Y, Z axes
    return true;
  }
}

export function createDefaultViewer(canvasId: string): PoseViewer {
  return new PoseViewer({
    canvasId: canvasId,
    fps: 60,
    enableAntiAliasing: true
  });
}

```
