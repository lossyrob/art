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

########## DEFINITIONS

DIM = 1000 # in mm
THICKNESS = 10
OFFSET_X = DIM / 2
OFFSET_Y = DIM / 2
OFFSET_Z = DIM / 2
OUTERDIM = DIM + (THICKNESS*2)

# Spell out each point in the lined tesseract
# Number designates each cube: 1 is bottom cube, 2 is top cube
# t = top, b = bottom, L = left, R = right, F = front, B = back

# Rules for overlap:
# Z: Top and bottom flair out along x and y, along with thickness in Z
# X: left and right flair out along y, along with thickness in X
# Y: front and back do not flair except for thickness in Y

# Cube 1 bottom
LFb1 = Base.Vector(0,0,0)
RFb1 = Base.Vector(DIM,0,0)
LBb1 = Base.Vector(0,DIM,0)
RBb1 = Base.Vector(DIM,DIM,0)

#Cube 1 top
LFt1 = Base.Vector(0,0,DIM)
RFt1 = Base.Vector(DIM,0,DIM)
LBt1 = Base.Vector(0,DIM,DIM)
RBt1 = Base.Vector(DIM,DIM,DIM)

#Cube 2 bottom
LFb2 = Base.Vector(OFFSET_X,OFFSET_Y,OFFSET_Z)
RFb2 = Base.Vector(OFFSET_X + DIM,OFFSET_Y,OFFSET_Z)
LBb2 = Base.Vector(OFFSET_X,OFFSET_Y + DIM,OFFSET_Z)
RBb2 = Base.Vector(OFFSET_X + DIM,OFFSET_Y + DIM,OFFSET_Z)

#Cube 2 top
LFt2 = Base.Vector(OFFSET_X,OFFSET_Y,OFFSET_Z + DIM)
RFt2 = Base.Vector(OFFSET_X + DIM,OFFSET_Y,OFFSET_Z + DIM)
LBt2 = Base.Vector(OFFSET_X,OFFSET_Y + DIM,OFFSET_Z + DIM)
RBt2 = Base.Vector(OFFSET_X + DIM,OFFSET_Y + DIM,OFFSET_Z + DIM)

########## UTIL

# Develop a system that takes a set of faces,
# and some indication of their directionality.
# Create a solid that is a makeBox call that is essentially
# the convex 3D hull of the given point set.
# Then iterate through each face, creating an extrusion. Oh.
# I might be able to make an extrusion with angle. Let me check.
#...
# I can, but, I don't think that solves the problem in a more elegant way.
# I want an API function that takes a list of faces, with possibly
# information about their direction of outward vs inward, 
# and returns me a solid of those faces, correctly able to cut other solids.
# FreeCAD should already have this? I think I've sufficiently checked.
# So create a set of makeBox's for the face and direction. Then create the solid
# that is the convex hull. Then cut that solid by each solid in the face\direction
# pair method.

class SolidFace():
    def __init__(self,face,outVector):
        self.face = face
        self.outVector = outVector

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

def makeSolid(solidFaces):
    vertices = [v for v in face.Vertexes for face in map(lambda x: x.face, solidFaces)]

    head = vertices[0]
    xmin = head.x
    xmax = head.x
    ymin = head.y
    ymax = head.y
    zmin = head.z
    zmax = head.z
    for v in vertices[1:]:
        xmin = math.min(v.x,xmin)
        ymin = math.min(v.y,ymin)
        xmax = math.max(v.x,xmax)
        ymax = math.max(v.y,ymax)

    
        
class Piece():
    @staticmethod
    def fromFaces(name,faces):
        shell = Part.makeShell(faces)
        shape = Part.makeSolid(shell)
        return Piece(name,shape)

    def __init__(self,name,shape):
        self.name = name
        self.shape = shape

    def cut(self,piece):
        print "CUTTING %s WITH %s" % (self.name, piece.name)
        return Piece(self.name,self.shape.cut(piece.shape))

    def copy(self):
        return Piece(self.name, self.shape.copy())

def tX(d,v):
    o = d * THICKNESS
    return Base.Vector(v.x + o, v.y, v.z)

def tY(d,v):
    o = d * THICKNESS
    return Base.Vector(v.x, v.y + o, v.z)

def tZ(d,v):
    o = d * THICKNESS
    return Base.Vector(v.x, v.y, v.z + o)

def tFront(v):
    return tY(-1,v)

def tBack(v):
    return tY(1,v)

def tLeft(v):
    return tX(-1,v)

def tRight(v):
    return tX(1,v)

def tBottom(v):
    return tZ(-1,v)

def tTop(v):
    return tZ(1,v)

def add_shape(doc,piece):
    part = doc.addObject("Part::Feature", piece.name)
    part.Shape = piece.shape
    FreeCADGui.activeDocument().getObject(piece.name).Transparency = 75


########## CUBES

def makeTop(v):
    return Part.makeBox(OUTERDIM,OUTERDIM,THICKNESS,tLeft(tFront(v)))    

def makeTop1():
    shape = makeTop(LFt1)
    return Piece("Top1",shape)

def makeTop2():
    shape = makeTop(LFt2)
    return Piece("Top2",shape)

def makeFront(v):
    return Part.makeBox(DIM,THICKNESS,DIM,tFront(v))    

def makeFront1():
    shape = makeFront(LFb1)
    return Piece("Front1",shape)

def makeFront2():
    shape = makeFront(LFb2)
    return Piece("Front2",shape)

def makeRight(v):
    return Part.makeBox(THICKNESS,OUTERDIM,DIM,tFront(v))

def makeRight1():
    shape = makeRight(RFb1)
    return Piece("Right2",shape)

def makeRight2():
    shape = makeRight(RFb2)
    return Piece("Right2",shape)

def makeLeft(v):
    return Part.makeBox(THICKNESS,OUTERDIM,DIM,tLeft(tFront(v)))

def makeLeft1():
    return Piece("Left1",makeLeft(LFb1))

def makeLeft2():
    return Piece("Left2",makeLeft(LFb2))

def makeBottom(v):
    return Part.makeBox(OUTERDIM,OUTERDIM,THICKNESS,tLeft(tFront(tBottom(v))))

def makeBottom1():
    return Piece("Bottom1",makeBottom(LFb1))

def makeBottom2():
    return Piece("Bottom2",makeBottom(LFb2))

def makeBack(v):
    return Part.makeBox(DIM,THICKNESS,DIM,v)

def makeBack1():
    return Piece("Back1",makeBack(LBb1))

def makeBack2():
    return Piece("Back2",makeBack(LBb2))

"""
FourD pieces are 6 sided base faces.
Where the turn is inside the intersection of that dimension of the two cubes,
there is no flat side. Where it is outside of the intersection, there is one
extra vertex to account for 3D edge.
"""

########## TOP SLANTS

def makeTopFront():
    topFrontL1 = tTop(tFront(LFt1))
    topFrontL2 = tTop(tFront(LFt2))
    topFrontR2 = tTop(tFront(RFt2))
    topFrontR1 = tTop(tFront(RFt1))

    topFront = get_face(topFrontL1,topFrontL2,topFrontR2,topFrontR1)

    frontLt = topFrontL1
    frontRt = topFrontR1
    frontLb = tBottom(frontLt)
    frontRb = tBottom(frontRt)

    front = get_face(frontLt,frontLb,frontRb,frontRt)

    leftFt = topFrontL1
    leftBt = tBack(leftFt)
    leftBb = tBottom(leftBt)
    leftFb = tFront(leftBb)

    left = get_face(leftFt,leftBt,leftBb,leftFb)

    bottomBL = LFt1
    bottomFL = tFront(bottomBL)    
    bottomBR = RFt1
    bottomFR = tFront(bottomBR)

    bottom = get_face(bottomFL,bottomBL,bottomBR,bottomFR)

    leftTopFL = topFrontL1
    leftTopBL = tBack(leftTopFL)
    leftTopFR = topFrontL2
    leftTopBR = tBack(leftTopFR)

    leftTop = get_face(leftTopFL,leftTopBL,leftTopBR,leftTopFR)

    leftBackLb = LFt1
    leftBackLt = tTop(leftBackLb)
    leftBackRb = LFt2
    leftBackRt = tTop(leftBackRb)

    leftBack = get_face(leftBackLb,leftBackLt,leftBackRt,leftBackRb)
    
    bottomBackL1 = LFt1
    bottomBackL2 = LFt2
    bottomBackR1 = RFt1
    bottomBackR2 = RFt2

    bottomBack = get_face(bottomBackR1,bottomBackL1,bottomBackL2,bottomBackR2)

    topRF = tFront(tTop(LFt2))
    topRB = tBack(topRF)
    topLF = tFront(tTop(RFt2))
    topLB = tBack(topLF)

    top = get_face(topRF,topRB,topLB,topLF)

    backLt = tTop(LFt2)
    backLb = tBottom(backLt)
    backRt = tTop(RFt2)
    backRb = tBottom(backRt)

    back = get_face(backLt,backLb,backRb,backRt)

    rightBb = RFt2
    rightBt = tTop(rightBb)
    rightFb = tFront(rightBb)
    rightFt = tTop(rightFb)

    right = get_face(rightBb,rightBt,rightFt,rightFb)

    rightBottomBt = RFt2
    rightBottomFt = tFront(rightBottomBt)
    rightBottomBb = RFt1
    rightBottomFb = tFront(rightBottomBb)
    
    rightBottom = get_face(rightBottomBt,rightBottomFt,rightBottomFb,rightBottomBb)

    rightFrontBb = tFront(RFt2)
    rightFrontBt = tTop(rightFrontBb)
    rightFrontFb = tFront(RFt1)
    rightFrontFt = tTop(rightFrontFb)

    rightFront = get_face(rightFrontBb,rightFrontBt,rightFrontFt,rightFrontFb)

    faces = [front,rightFront,rightBottom,
             bottomBack,leftBack,leftTop,
             topFront,right,back,
             top,bottom]

    return Piece.fromFaces("TopFront",faces)

def makeTopLeft():
    topFrontL1 = tTop(tFront(LFt1))
    topFrontL2 = tTop(tFront(LFt2))
    topFrontR2 = tTop(tFront(RFt2))
    topFrontR1 = tTop(tFront(RFt1))

    topFront = get_face(topFrontL1,topFrontL2,topFrontR2,topFrontR1)

    frontLt = topFrontL1
    frontRt = topFrontR1
    frontLb = tBottom(frontLt)
    frontRb = tBottom(frontRt)

    front = get_face(frontLt,frontLb,frontRb,frontRt)

    leftFt = topFrontL1
    leftBt = tBack(leftFt)
    leftBb = tBottom(leftBt)
    leftFb = tFront(leftBb)

    left = get_face(leftFt,leftBt,leftBb,leftFb)

    bottomBL = LFt1
    bottomFL = tFront(bottomBL)    
    bottomBR = RFt1
    bottomFR = tFront(bottomBR)

    bottom = get_face(bottomFL,bottomBL,bottomBR,bottomFR)

    leftTopFL = topFrontL1
    leftTopBL = tBack(leftTopFL)
    leftTopFR = topFrontL2
    leftTopBR = tBack(leftTopFR)

    leftTop = get_face(leftTopFL,leftTopBL,leftTopBR,leftTopFR)

    leftBackLb = LFt1
    leftBackLt = tTop(leftBackLb)
    leftBackRb = LFt2
    leftBackRt = tTop(leftBackRb)

    leftBack = get_face(leftBackLb,leftBackLt,leftBackRt,leftBackRb)
    
    bottomBackL1 = LFt1
    bottomBackL2 = LFt2
    bottomBackR1 = RFt1
    bottomBackR2 = RFt2

    bottomBack = get_face(bottomBackL1,bottomBackL2,bottomBackR2,bottomBackR1)

    topRF = tFront(tTop(LFt2))
    topRB = tBack(topRF)
    topLF = tFront(tTop(RFt2))
    topLB = tBack(topLF)

    top = get_face(topRF,topRB,topLB,topLF)

    backLt = tTop(LFt2)
    backLb = tBottom(backLt)
    backRt = tTop(RFt2)
    backRb = tBottom(backRt)

    back = get_face(backLt,backLb,backRb,backRt)

    rightBb = RFt2
    rightBt = tTop(rightBb)
    rightFb = tFront(rightBb)
    rightFt = tTop(rightFb)

    right = get_face(rightBb,rightBt,rightFt,rightFb)

    rightBottomBt = RFt2
    rightBottomFt = tFront(rightBottomBt)
    rightBottomBb = RFt1
    rightBottomFb = tFront(rightBottomBb)
    
    rightBottom = get_face(rightBottomBt,rightBottomFt,rightBottomFb,rightBottomBb)

    rightFrontBb = tFront(RFt2)
    rightFrontBt = tTop(rightFrontBb)
    rightFrontFb = tFront(RFt1)
    rightFrontFt = tTop(rightFrontFb)

    rightFront = get_face(rightFrontBb,rightFrontBt,rightFrontFt,rightFrontFb)

    faces = [front,rightFront,rightBottom,
             bottomBack,leftBack,leftTop,
             topFront,right,back,
             top,bottom]


    return Piece.fromFaces("TopFront4",faces)

#### MAIN ####

if __name__ == "__main__":
    doc = FreeCAD.newDocument()
    
    # d4s = [makeTopFront(),
    #        makeTopLeft()]
    d4s = [makeTopFront()]

    cube1 = [makeTop1(),
             makeBottom1(),
             makeFront1(),
             makeBack1(),
             makeRight1(),
             makeLeft1()]

    cube2uncut = [makeTop2(),
                  makeBottom2(),
                  makeFront2(),
                  makeBack2(),
                  makeRight2(),
                  makeLeft2()]

    # do cutting
    def cut(p,cutters):
        cp = p
        for c in cutters:
            cp = cp.cut(c)
        return cp

    cube2 = map(lambda p: cut(p,cube1),cube2uncut)
    cubes = map(lambda p: cut(p,d4s),cube1 + cube2)
#    cubes = cube1+cube2

    # Add to GUI
    for x in d4s + cubes:
        add_shape(doc,x)
    doc.recompute()

    FreeCADGui.SendMsgToActiveView("ViewFit")
    FreeCADGui.activeDocument().activeView().viewAxometric()
