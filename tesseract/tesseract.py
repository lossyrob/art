# FreeCAD python script for creating the tesseract
import sys

# Import FreeCAD if we're running somewhere it's not already loaded
if not 'FreeCAD' in sys.modules:
    FREECADPATH='/usr/lib/freecad/lib/' 
    sys.path.append(FREECADPATH)

    import FreeCAD

from FreeCAD import Base
import Part


DIM = 1000 # in mm
THICKNESS = 10
OFFSET_X = DIM / 2
OFFSET_Y = DIM / 2
OFFSET_Z = DIM / 2

"""
The piece 'tesseract' will be a 3D projection of a tesseract,
made of plexiglass. It will include two identical looking cubes
of inner dimension DIM,
offset in the Z and Y dimensions by some amount less than DIM,
so that they intersect each other. This will require that the 
cubes be made up of separate pieces of plexiglass so that
the intersection is seemless and visually one piece.

The location of the bottom left front corner will be on the origin.
This is facing the front side of the piece:
The x direction moves to the right
The y direction away from the viewer
The z direction moves up
The piece will move to the left with the bottom cube. The piece moves 
to the right, with the 
second cube (top cube, Cube 2) offset in the positive x, y, and z
directions.
"""

#### CUBE 1
"""
This is the cube is the one that rests on the floor. If possible,
I want the piece to be freestanding, with Cube 2 raised and offset
in the Y direction, but the weight balanced out by the weight of 
Cube 1 such that it does not easily tip.

This cube will be made of THICKESS thick plexiglass. It will
contain 6 flat pieces of glass. A decision is to be made
about which pieces will be larger than the DIMxDIM glass pieces
as to compensate for the thickness, and to make the inner cube
DIMxDIMxDIM.
"""

class Cube1():
    def __init__(self,dim,thickness):
        self.dim = dim
        self.thickness = thickness
        self.outer_dim = self.dim + (self.thickness / 2)
        """
        Need 6 pieces:
        Bottom piece and Top Piece -
          Dimension x:(DIM+(THICKNESS/2)),y:(DIM+(THICKNESS/2))
        Two side pieces:
          Dimension y:(DIM+(THICKNESS),z:DIM)
        Two Front and back pieces:
          Dimension x:DIM, y:DIM
        """

    def bottom(self):
        """
        Sketch from xy view
        """
        outer_dim = self.outer_dim
        v1 = Base.Vector(0,0,0)
        v2 = Base.Vector(outer_dim,0,0)
        v3 = Base.Vector(outer_dim,outer_dim,0)
        v4 = Base.Vector(0,outer_dim,0)

        l1 = Part.Line(v1,v2)
        l2 = Part.Line(v2,v3)
        l3 = Part.Line(v3,v4)
        l4 = Part.Line(v4,v1)

        shape = Part.Shape([l1,l2,l3,l4])
        wire = Part.Wire(shape.edges)
        face = Part.makeFace(wire)
        return face.extrude(Base.Vector(0,0,self.thickness))

    def left_side(self):
        
        
