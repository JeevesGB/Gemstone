import numpy as np

class Plane:
    def __init__(self, normal, dist):
        self.normal = np.array(normal, dtype=float)
        self.dist = float(dist)


class Brush:
    """
    Axis-aligned convex brush defined by 6 planes
    """
    def __init__(self, min_pt, max_pt):
        self.min = np.array(min_pt, dtype=float)
        self.max = np.array(max_pt, dtype=float)

        self.planes = [
            Plane(( 1,  0,  0), self.max[0]),
            Plane((-1,  0,  0), -self.min[0]),
            Plane(( 0,  1,  0), self.max[1]),
            Plane(( 0, -1,  0), -self.min[1]),
            Plane(( 0,  0,  1), self.max[2]),
            Plane(( 0,  0, -1), -self.min[2]),
        ]

    def vertices(self):
        """
        Returns 8 corners (AABB)
        """
        x0, y0, z0 = self.min
        x1, y1, z1 = self.max

        return [
            (x0, y0, z0), (x1, y0, z0),
            (x1, y1, z0), (x0, y1, z0),
            (x0, y0, z1), (x1, y0, z1),
            (x1, y1, z1), (x0, y1, z1),
        ]
