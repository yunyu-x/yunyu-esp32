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
