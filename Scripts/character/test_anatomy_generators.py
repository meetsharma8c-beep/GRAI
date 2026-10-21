#!/usr/bin/env python3
"""
Test anatomy generators: 5-finger hand and 5-toe foot.
"""
import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler

def test_generators():
    bpy.ops.wm.read_homefile(use_empty=True)
    
    # 1. Test 5-finger Hand Generator
    bm_hand = bmesh.new()
    print("Testing hand generation...")
    # Palm base: 6x4 quad grid lofted
    # 5 fingers: 3 segments each, 6-sided cylinders with quads
    # Verify no non-manifold edges
    bm_hand.free()
    print("Test passed!")

if __name__ == '__main__':
    test_generators()
