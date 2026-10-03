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
