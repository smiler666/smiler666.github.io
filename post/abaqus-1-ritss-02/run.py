# -*- coding: mbcs -*-
from math import *
from abaqus import *
from abaqusConstants import *
from odbAccess import *
from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *
import os
import os.path

# part pile
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=100.0)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.sketchOptions.setValues(viewStyle=AXISYM)
s1.setPrimaryObject(option=STANDALONE)
s1.ConstructionLine(point1=(0.0, -50.0), point2=(0.0, 50.0))
s1.FixedConstraint(entity=g[2])
s1.rectangle(point1=(0.0, 50.0), point2=(5.0, 60.0))
p = mdb.models['Model-1'].Part(name='pile', dimensionality=AXISYMMETRIC, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['pile']
p.BaseShell(sketch=s1)
s1.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['pile']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['pile']
v2, e1, d2, n1 = p.vertices, p.edges, p.datums, p.nodes
p.ReferencePoint(point=v2[3])
p = mdb.models['Model-1'].parts['pile']
r = p.referencePoints
refPoints=(r[2], )
p.Set(referencePoints=refPoints, name='RP')
p = mdb.models['Model-1'].parts['pile']
s = p.edges
side1Edges = s.getSequenceFromMask(mask=('[#1 ]', ), )
p.Surface(side1Edges=side1Edges, name='Surf-1')
p = mdb.models['Model-1'].parts['pile']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#1 ]', ), )
p.Set(faces=faces, name='Set-3')

# part soil
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=100.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.sketchOptions.setValues(viewStyle=AXISYM)
s.setPrimaryObject(option=STANDALONE)
s.ConstructionLine(point1=(0.0, -50.0), point2=(0.0, 50.0))
s.FixedConstraint(entity=g[2])
s.rectangle(point1=(0.0, 0.0), point2=(50.0, 50.0))
p = mdb.models['Model-1'].Part(name='soil', dimensionality=AXISYMMETRIC, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['soil']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['soil']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['soil']
s = p.edges
side1Edges = s.getSequenceFromMask(mask=('[#4 ]', ), )
p.Surface(side1Edges=side1Edges, name='Surf-1')

# material
mdb.models['Model-1'].Material(name='Material-1')
mdb.models['Model-1'].materials['Material-1'].Elastic(table=((5000.0, 0.3), ))
mdb.models['Model-1'].materials['Material-1'].MohrCoulombPlasticity(table=((
    0.0, 0.0), ))
mdb.models['Model-1'].materials['Material-1'].mohrCoulombPlasticity.MohrCoulombHardening(
    table=((5.0, 0.0), ))
mdb.models['Model-1'].materials['Material-1'].mohrCoulombPlasticity.TensionCutOff(
    temperatureDependency=OFF, dependencies=0, table=((0.0, 0.0), ))
mdb.models['Model-1'].HomogeneousSolidSection(name='Section-1', 
    material='Material-1', thickness=None)
p = mdb.models['Model-1'].parts['pile']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#1 ]', ), )
region = p.Set(faces=faces, name='Set-2')
p = mdb.models['Model-1'].parts['pile']
p.SectionAssignment(region=region, sectionName='Section-1', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
p = mdb.models['Model-1'].parts['soil']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
p = mdb.models['Model-1'].parts['soil']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#1 ]', ), )
region = p.Set(faces=faces, name='Set-1')
p = mdb.models['Model-1'].parts['soil']
p.SectionAssignment(region=region, sectionName='Section-1', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
    
# assembly
a = mdb.models['Model-1'].rootAssembly
a.DatumCsysByThreePoints(coordSysType=CYLINDRICAL, origin=(0.0, 0.0, 0.0), 
    point1=(1.0, 0.0, 0.0), point2=(0.0, 0.0, -1.0))
p = mdb.models['Model-1'].parts['pile']
a.Instance(name='pile-1', part=p, dependent=ON)
p = mdb.models['Model-1'].parts['soil']
a.Instance(name='soil-1', part=p, dependent=ON)

# step
mdb.models['Model-1'].StaticStep(name='Step-1', previous='Initial')
session.viewports['Viewport: 1'].assemblyDisplay.setValues(step='Step-1')

# constraints
a = mdb.models['Model-1'].rootAssembly
region1=a.instances['pile-1'].surfaces['Surf-1']
a = mdb.models['Model-1'].rootAssembly
region2=a.instances['soil-1'].surfaces['Surf-1']
mdb.models['Model-1'].Tie(name='Constraint-1', master=region1, slave=region2, 
    positionToleranceMethod=COMPUTED, adjust=ON, tieRotations=ON, 
    thickness=ON)
a = mdb.models['Model-1'].rootAssembly
region2=a.instances['pile-1'].sets['Set-2']
a = mdb.models['Model-1'].rootAssembly
region1=a.instances['pile-1'].sets['RP']
mdb.models['Model-1'].RigidBody(name='Constraint-2', refPointRegion=region1, 
    bodyRegion=region2)

# load
a = mdb.models['Model-1'].rootAssembly
e1 = a.instances['soil-1'].edges
edges1 = e1.getSequenceFromMask(mask=('[#a ]', ), )
region = a.Set(edges=edges1, name='Set-1')
mdb.models['Model-1'].DisplacementBC(name='BC-1', createStepName='Step-1', 
    region=region, u1=0.0, u2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, 
    distributionType=UNIFORM, fieldName='', localCsys=None)
a = mdb.models['Model-1'].rootAssembly
e1 = a.instances['soil-1'].edges
edges1 = e1.getSequenceFromMask(mask=('[#1 ]', ), )
region = a.Set(edges=edges1, name='Set-2')
mdb.models['Model-1'].DisplacementBC(name='BC-2', createStepName='Step-1', 
    region=region, u1=UNSET, u2=0.0, ur3=UNSET, amplitude=UNSET, fixed=OFF, 
    distributionType=UNIFORM, fieldName='', localCsys=None)
a = mdb.models['Model-1'].rootAssembly
r1 = a.instances['pile-1'].referencePoints
refPoints1=(r1[2], )
region = a.Set(referencePoints=refPoints1, name='Set-3')
mdb.models['Model-1'].DisplacementBC(name='BC-3', createStepName='Step-1', 
    region=region, u1=0.0, u2=-5.0, ur3=0.0, amplitude=UNSET, fixed=OFF, 
    distributionType=UNIFORM, fieldName='', localCsys=None)

# mesh
p = mdb.models['Model-1'].parts['pile']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
session.viewports['Viewport: 1'].partDisplay.setValues(mesh=ON)
session.viewports['Viewport: 1'].partDisplay.meshOptions.setValues(
    meshTechnique=ON)
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=OFF)
p = mdb.models['Model-1'].parts['pile']
p.seedPart(size=1.0, deviationFactor=0.1, minSizeFactor=0.1)
p = mdb.models['Model-1'].parts['pile']
p.generateMesh()
p = mdb.models['Model-1'].parts['soil']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
p = mdb.models['Model-1'].parts['soil']
p.seedPart(size=5.0, deviationFactor=0.1, minSizeFactor=0.1)
p = mdb.models['Model-1'].parts['soil']
p.seedPart(size=1.0, deviationFactor=0.1, minSizeFactor=0.1)
p = mdb.models['Model-1'].parts['soil']
p.generateMesh()
a = mdb.models['Model-1'].rootAssembly
session.viewports['Viewport: 1'].setValues(displayedObject=a)
a1 = mdb.models['Model-1'].rootAssembly
a1.regenerate()

# job
session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=OFF)
session.viewports['Viewport: 1'].assemblyDisplay.meshOptions.setValues(
    meshTechnique=OFF)
mdb.Job(name='Job-1', model='Model-1', description='', type=ANALYSIS, 
    atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
    memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
    explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
    scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=1, 
    numGPUs=0)
mdb.jobs['Job-1'].submit(consistencyChecking=OFF)