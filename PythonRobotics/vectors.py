#!/usr/bin/env python
"""
Simple vector classes. (Python3)

Why not use numpy instead? A couple of reasons:
1. performance, working with small numpy arrays introduces a lot of overhead
2. .x and .y class properties
3. clear implementation for readability and porting to other languages.

 Copyright (c) 2021 AIGRO B.V. - Jev Kuznetsov
 License: BSD

Special thanks for these information sources and references:

* [vector.py](https://gist.github.com/mostley/3819375)
* [StackOverflow](https://stackoverflow.com/a/43542669)
* [vector.py](https://github.com/betados/vector_2d/blob/develop/vector_2d/vector.py)

"""
import numpy as np
from math import atan2, hypot, pi, acos, sin, cos


class Vector:
    """ 2d vector, compatible with numpy """

    def __init__(self, *args):
        """ create from x,y or xy """
        try:
            self.x, self.y = float(args[0]), float(args[1])
        except:
            self.x = float(args[0][0])
            self.y = float(args[0][1])

    def __repr__(self):
        return f"{self.__class__.__name__}(x={self.x}, y={self.y})"

    def __add__(self, other):
        return Vector(self.x+other.x, self.y+other.y)

    def __sub__(self, other):
        return Vector(self.x-other.x, self.y-other.y)

    def __eq__(self, other):
        return (self.x == other.x) & (self.y == other.y)

    def cross(self, other):
        return (self.x * other.y) - (self.y * other.x)

    def inner(self, other):
        return self.x * other.x + self.y * other.y

    def angle(self, other):
        """ angle between vector, *relative* to other, range (-pi..pi)  """
        return -atan2(self.cross(other), self.inner(other))

    def __mul__(self, scalar):
        """ scalar multiplification """
        return Vector(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):  # note __div__ was removed in Python3
        return Vector(self.x / scalar, self.y / scalar)

    def __neg__(self):
        return Vector(-self.x, -self.y)

    def __abs__(self):
        return hypot(self.x, self.y)

    @classmethod
    def from_polar(cls,r, theta):
        return Vector(r * cos(theta), r * sin(theta))

    def __array__(self, dtype=None) -> np.array:
        """ make this class compatable with numpy operations """
        if dtype:
            return np.array([self.x, self.y], dtype=dtype)
        else:
            return np.array([self.x, self.y])
