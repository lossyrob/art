# FreeCAD python script for creating the tesseract
import sys

# Import FreeCAD if we're running somewhere it's not already loaded
if not 'FreeCAD' in sys.modules:
    FREECADPATH='/usr/lib/freecad/lib/' 
    sys.path.append(FREECADPATH)

    import FreeCAD

from FreeCAD import Base
import Part
import FreeCADGui

import math

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

def add_shape(doc,name,shape):
    part = doc.addObject("Part::Feature", name)
    part.Shape = shape
    FreeCADGui.activeDocument().getObject(name).Transparency = 75

def get_face(*vs):
    """
    Takes a sequence of vectors and returns a face
    """
    s = vs[0:-1]
    e = vs[1:]
    l = []
    for i in range(0,len(s)):
        l.append(Part.Line(s[i],e[i]))

    l.append(Part.Line(vs[-1],vs[0]))

    shape = Part.Shape(l)
    wire = Part.Wire(shape.Edges)
    return Part.makeFilledFace(shape.Edges)


class Cube1():
    def __init__(self,dim,thickness,offsetX,offsetY,offsetZ):
        self.dim = dim
        self.thickness = thickness
        self.outer_dim = self.dim + (self.thickness / 2)
        self.offsetX = offsetX
        self.offsetY = offsetY
        self.offsetZ = offsetZ
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
        od = self.outer_dim
        v1 = Base.Vector(0,0,0)
        v2 = Base.Vector(od,0,0)
        v3 = Base.Vector(od,od,0)
        v4 = Base.Vector(0,od,0)

        face = get_face(v1,v2,v3,v4)
        return face.extrude(Base.Vector(0,0,self.thickness))

    def left_side(self):
        od = self.outer_dim
        t = self.thickness
        v1 = Base.Vector(0,0,t)
        v2 = Base.Vector(0,od,t)
        v3 = Base.Vector(0,od,od-t)
        v4 = Base.Vector(0,0,od-t)

        face = get_face(v1,v2,v3,v4)
        return face.extrude(Base.Vector(self.thickness,0,0))

    def right_side(self):
        od = self.outer_dim
        t = self.thickness
        v1 = Base.Vector(od,0,t)
        v2 = Base.Vector(od,od,t)
        v3 = Base.Vector(od,od,od-t)
        v4 = Base.Vector(od,0,od-t)

        face = get_face(v1,v2,v3,v4)
        return face.extrude(Base.Vector(-self.thickness,0,0))
    
    def front_side(self):
        od = self.outer_dim
        t = self.thickness
        v1 = Base.Vector(t,0,t)
        v2 = Base.Vector(od-t,0,t)
        v3 = Base.Vector(od-t,0,od-t)
        v4 = Base.Vector(t,0,od-t)

        face = get_face(v1,v2,v3,v4)
        return face.extrude(Base.Vector(0,self.thickness,0))

    def back_side(self):
        od = self.outer_dim
        t = self.thickness
        v1 = Base.Vector(t,od,t)
        v2 = Base.Vector(od-t,od,t)
        v3 = Base.Vector(od-t,od,od-t)
        v4 = Base.Vector(t,od,od-t)

        face = get_face(v1,v2,v3,v4)
        return face.extrude(Base.Vector(0,-self.thickness,0))

    def top(self):
        od = self.outer_dim
        t = self.thickness
        v1 = Base.Vector(0,0,od)
        v2 = Base.Vector(0,od,od)
        v3 = Base.Vector(od,od,od)
        v4 = Base.Vector(od,0,od)

        face = get_face(v1,v2,v3,v4)
        solid = face.extrude(Base.Vector(0,0,-self.thickness))
        
        # Cut out piece for connector
        x = (self.offsetY / self.offsetZ) * t
        
        v1 = Base.Vector(0,0,od-t)
        v2 = Base.Vector(0,0,od)
        v3 = Base.Vector(0,x,od)

        face = get_face(v1,v2,v3)
        cut_solid = face.extrude(Base.Vector(od,0,0))

        return solid.cut(cut_solid)


    def show(self, doc):
        add_shape(doc,"Cube1_Bottom",self.bottom())
        add_shape(doc,"Cube1_Left",self.left_side())
        add_shape(doc,"Cube1_Right",self.right_side())
        add_shape(doc,"Cube1_Front",self.front_side())
        add_shape(doc,"Cube1_Back",self.back_side())
        add_shape(doc,"Cube1_Top",self.top())
        doc.recompute()

class Cube2():
    def __init__(self,dim,thickness,offsetX,offsetY,offsetZ):
        self.dim = dim
        self.thickness = thickness
        self.outer_dim = self.dim + (self.thickness / 2)
        self.offsetX = offsetX
        self.offsetY = offsetY
        self.offsetZ = offsetZ

    def bottom_out(self):
        od = self.outer_dim
        ox = self.offsetX
        oy = self.offsetY
        oz = self.offsetZ

        vs = [
          Base.Vector(od,oy,oz),
          Base.Vector(od,od,oz),
          Base.Vector(ox,od,oz),
          Base.Vector(ox,od+oy,oz),
          Base.Vector(ox+od,oy+od,oz),
          Base.Vector(ox+od,oy,oz),
        ]

        face = get_face(*vs)
        return face.extrude(Base.Vector(0,0,self.thickness))

    def bottom_in(self):
        od = self.outer_dim
        t = self.thickness
        ox = self.offsetX
        oy = self.offsetY
        oz = self.offsetZ

        vs = [
          Base.Vector(ox,oy,oz),
          Base.Vector(od-t,oy,oz),
          Base.Vector(od-t,od-t,oz),
          Base.Vector(ox,od-t,oz),
        ]

        face = get_face(*vs)
        return face.extrude(Base.Vector(0,0,self.thickness))

    def left_side_out(self):
        od = self.outer_dim
        t = self.thickness
        ox = self.offsetX
        oy = self.offsetY
        oz = self.offsetZ
        
        vs = [
            Base.Vector(ox,od,od),
            Base.Vector(ox,oy,od),
            Base.Vector(ox,oy,od+oz-t),
            Base.Vector(ox,od+oy,od+oz-t),
            Base.Vector(ox,od+oy,oz+t),
            Base.Vector(ox,od,oz+t),
        ]

        face = get_face(*vs)
        return face.extrude(Base.Vector(self.thickness,0,0))
    
    def left_side_in(self):
        od = self.outer_dim
        t = self.thickness
        ox = self.offsetX
        oy = self.offsetY
        oz = self.offsetZ

        vs = [
            Base.Vector(ox,oy,oz+t),
            Base.Vector(ox,od-t,oz+t),
            Base.Vector(ox,od-t,od-t),
            Base.Vector(ox,oy,od-t),
        ]

        face = get_face(*vs)
        return face.extrude(Base.Vector(self.thickness,0,0))

    def right_side(self):
        od = self.outer_dim
        t = self.thickness
        ox = self.offsetX
        oy = self.offsetY
        oz = self.offsetZ
        v1 = Base.Vector(od+ox,oy,t+oz)
        v2 = Base.Vector(od+ox,od+oy,t+oz)
        v3 = Base.Vector(od+ox,od+oy,od+oz-t)
        v4 = Base.Vector(od+ox,oy,od+oz-t)

        face = get_face(v1,v2,v3,v4)
        return face.extrude(Base.Vector(-self.thickness,0,0))
    
    def front_side_out(self):
        od = self.outer_dim
        t = self.thickness
        ox = self.offsetX
        oy = self.offsetY
        oz = self.offsetZ
        
        vs = [
            Base.Vector(od,oy,od),
            Base.Vector(od,oy,oz+t),
            Base.Vector(od+ox-t,oy,oz+t),
            Base.Vector(od+ox-t,oy,od+oz-t),
            Base.Vector(ox+t,oy,od+oz-t),
            Base.Vector(ox+t,oy,od),
        ]

        face = get_face(*vs)
        return face.extrude(Base.Vector(0,self.thickness,0))

    def top_front_cut_lower(self):
        od = self.outer_dim
        t = self.thickness
        ox = self.offsetX
        oy = self.offsetY
        oz = self.offsetZ

        x = (self.offsetY / self.offsetZ) * t + oy
        
        v1 = Base.Vector(ox,oy,od+oz-t)
        v2 = Base.Vector(ox,oy,od+oz-t-t)
        v3 = Base.Vector(ox,x,od+oz-t)

        face = get_face(v1,v2,v3)
        return face.extrude(Base.Vector(od,0,0))

    def front_side_in(self):
        od = self.outer_dim
        t = self.thickness
        ox = self.offsetX
        oy = self.offsetY
        oz = self.offsetZ
        v1 = Base.Vector(ox+t,oy,oz+t)
        v2 = Base.Vector(od-t,oy,oz+t)
        v3 = Base.Vector(od-t,oy,od-t)
        v4 = Base.Vector(ox+t,oy,od-t)

        face = get_face(v1,v2,v3,v4)
        return face.extrude(Base.Vector(0,self.thickness,0))        

    def back_side(self):
        od = self.outer_dim
        t = self.thickness
        ox = self.offsetX
        oy = self.offsetY
        oz = self.offsetZ
        v1 = Base.Vector(ox+t,od+oy,t+oz)
        v2 = Base.Vector(od+ox-t,od+oy,t+oz)
        v3 = Base.Vector(od+ox-t,od+oy,t+od+oz)
        v4 = Base.Vector(ox+t,od+oy,t+od+oz)

        face = get_face(v1,v2,v3,v4)
        return face.extrude(Base.Vector(0,-self.thickness,0))

    def top(self):
        od = self.outer_dim
        t = self.thickness
        ox = self.offsetX
        oy = self.offsetY
        oz = self.offsetZ
        v1 = Base.Vector(ox,oy,od+oz)
        v2 = Base.Vector(ox,od+oy,od+oz)
        v3 = Base.Vector(od+ox,od+oy,od+oz)
        v4 = Base.Vector(od+ox,oy,od+oz)

        face = get_face(v1,v2,v3,v4)
        solid = face.extrude(Base.Vector(0,0,-self.thickness))

        # Cut out piece for connector
        od = self.outer_dim
        t = self.thickness
        ox = self.offsetX
        oy = self.offsetY
        oz = self.offsetZ

        x = (self.offsetY / self.offsetZ) * t + oy
        
        v1 = Base.Vector(ox,oy,od+oz)
        v2 = Base.Vector(ox,oy,od+oz-t)
        v3 = Base.Vector(ox,x,od+oz-t)

        face = get_face(v1,v2,v3)
        cut_solid = face.extrude(Base.Vector(od,0,0))

        return solid.cut(cut_solid)

    def show(self, doc):
        add_shape(doc,"Cube2_Bottom_Out",self.bottom_out())
        add_shape(doc,"Cube2_Bottom_In",self.bottom_in())
        add_shape(doc,"Cube2_Left_In",self.left_side_in())

        add_shape(doc,"Cube2_Front_In",self.front_side_in())
        add_shape(doc,"Cube2_Back",self.back_side())
        add_shape(doc,"Cube2_Top",self.top())
        front_out = self.front_side_out()
        right = self.right_side()
        left_out = self.left_side_out()

        top_front_cut_lower = self.top_front_cut_lower()
        
        add_shape(doc,"Cube2_Front_Out",front_out.cut(top_front_cut_lower))
        add_shape(doc,"Cube2_Right",right.cut(top_front_cut_lower))
        add_shape(doc,"Cube2_Left_Out",left_out.cut(top_front_cut_lower))
        doc.recompute()

class TopConnectors():
    """
    These are the pieces that imitate the 4th dimensionality of the tesseract.
    """
    def __init__(self,dim,thickness,offsetX,offsetY,offsetZ):
        self.dim = dim
        self.thickness = thickness
        self.outer_dim = self.dim + (self.thickness / 2)
        self.offsetX = offsetX
        self.offsetY = offsetY
        self.offsetZ = offsetZ

    def front(self):
        od = self.outer_dim
        ox = self.offsetX
        oy = self.offsetY
        oz = self.offsetZ

        vs = [
            Base.Vector(0,0,od),
            Base.Vector(od,0,od),
            Base.Vector(ox+od,oy,od+oz),
            Base.Vector(ox,oy,od+oz),
        ]

        face = get_face(*vs)
        return face.extrude(Base.Vector(0,0,self.thickness))

    def show(self, doc):
        add_shape(doc,"TopConnector_Front",self.front())
        doc.recompute()

if __name__ == "__main__":
    doc = FreeCAD.newDocument()
    cube1 = Cube1(DIM,THICKNESS,OFFSET_X,OFFSET_Y,OFFSET_Z)
    cube2 = Cube2(DIM,THICKNESS,OFFSET_X,OFFSET_Y,OFFSET_Z)
    cube1.show(doc)
    cube2.show(doc)
    FreeCADGui.SendMsgToActiveView("ViewFit")
    FreeCADGui.activeDocument().activeView().viewAxometric()


# execfile("/home/rob/art/tesseract/tesseract.py")
