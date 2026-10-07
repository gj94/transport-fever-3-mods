"""Rebuild ICF detail v02 without reading or changing prior source packages.
Blender -b -t 3 --python scripts/build.py -- SL|1A|2A|3A|CC|2S|GS|all
"""
from pathlib import Path
import sys,json,math,types
import bpy
from mathutils import Vector
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import core as g
import icf_shell,icf_coupling,detail_fittings,icf_running_gear
OLD_MATERIAL=g.material
OLD_ROD=g.rod

def material(n,c,metal=0,rough=.45,alpha=1,transmission=0,emit=0):
 if n=='ICF blue enamel':c=(.017,.087,.245);metal=.15;rough=.36
 if n=='ICF pale blue window band':c=(.29,.56,.60);metal=.05;rough=.47
 if n=='Aluminium silver roof':n='Painted steel roof softly weathered';c=(.57,.59,.56);metal=.08;rough=.69
 if n=='Underframe graphite':c=(.049,.055,.057);metal=.33;rough=.53
 if n=='Warm ivory laminate':c=(.68,.70,.61);rough=.47
 if n=='GLASS sealed passenger glazing alpha fallback':c=(.67,.78,.79);alpha=.24;transmission=.95;rough=.105
 if n=='Blue passenger upholstery':c=(.026,.109,.242);rough=.52
 return OLD_MATERIAL(n,c,metal,rough,alpha,transmission,emit)
g.material=material

def rod(name,a,b,r,mat,parent=None,N=12,coll=None):
 o=OLD_ROD(name,a,b,r,mat,parent,max(N,8),coll)
 for p in o.data.polygons[:-2]:p.use_smooth=True
 return o
g.rod=rod
g.path=lambda name,pts,r,m,parent=None,N=12:detail_fittings.tube(g,name,pts,r,m,parent,N)
g.cushion=lambda n,c,s:detail_fittings.upholstery(g,n,c,s)
g.fan=lambda x,y,z:detail_fittings.fan(g,x,y,z)

def material_nodes():
 # Material variation uses vehicle-space position. Shared across split shell panels.
 for m in [g.BLUE,g.CYAN,g.ROOF,g.DARK]:
  nt=m.node_tree;p=nt.nodes.get('Principled BSDF');base=list(p.inputs['Base Color'].default_value)
  geo=nt.nodes.new('ShaderNodeNewGeometry');noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1.65;noise.inputs['Detail'].default_value=3
  nt.links.new(geo.outputs['Position'],noise.inputs['Vector'])
  ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.12;ramp.color_ramp.elements[1].position=.87
  ramp.color_ramp.elements[0].color=tuple(v*.80 for v in base[:3])+(1,);ramp.color_ramp.elements[1].color=tuple(min(1,v*1.08) for v in base[:3])+(1,)
  nt.links.new(noise.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs['Color'],p.inputs['Base Color'])
  fine=nt.nodes.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=145;fine.inputs['Detail'].default_value=2;nt.links.new(geo.outputs['Position'],fine.inputs['Vector'])
  bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.13;bump.inputs['Distance'].default_value=.00028;nt.links.new(fine.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],p.inputs['Normal'])
  rough=nt.nodes.new('ShaderNodeMapRange');rough.inputs['From Min'].default_value=0;rough.inputs['From Max'].default_value=1;rough.inputs['To Min'].default_value=max(.08,p.inputs['Roughness'].default_value-.06);rough.inputs['To Max'].default_value=min(.9,p.inputs['Roughness'].default_value+.08);nt.links.new(noise.outputs['Fac'],rough.inputs['Value']);nt.links.new(rough.outputs['Result'],p.inputs['Roughness'])

def shell(cfg):
 g.BRASS=g.material('Valve brass',(.31,.18,.065),.78,.35)
 g.RUST=g.material('Restrained oxide fastener',(.12,.057,.028),.42,.77)
 g.SEAM=g.material('Upholstery tailored seam',(.105,.16,.22) if g.V!='1A' else (.19,.063,.065),0,.69)
 material_nodes()
 return icf_shell.build(g,cfg)
g.shell=shell

def gear():
 def cylinder(n,loc,r,depth,m,axis='Z',parent=None,vertices=32):
  d={'X':(depth/2,0,0),'Y':(0,depth/2,0),'Z':(0,0,depth/2)}[axis]
  return g.rod(n,tuple(loc[i]-d[i] for i in range(3)),tuple(loc[i]+d[i] for i in range(3)),r,m,parent,N=vertices)
 api=types.SimpleNamespace(cube=lambda n,c,s,m,bevel=0,parent=None:g.box(n,c,s,m,parent,bevel),cylinder=cylinder,pipe=lambda n,p,r,m,parent=None:g.path(n,p,r,m,parent),mesh=lambda n,v,f,m,parent=None:g.mesh(n,v,f,m,parent),empty=g.empty,collection=g.C,root=g.ROOT,body=g.BODY,materials={'steel':g.STEEL,'dark':g.DARK,'rubber':g.RUBBER,'rust':g.RUST,'brass':g.BRASS,'paint_blue':g.BLUE})
 result=icf_running_gear.build(api,ac=g.CFG['ac'])
 out=g.OUT/'qa';out.mkdir(exist_ok=True);(out/f'{g.V}_running_gear.json').write_text(json.dumps(result,indent=2))
g.underframe=lambda ac:None
g.bogies=gear
g.coupling=lambda:icf_coupling.build(g)
g.DETAIL_HOOK=lambda:detail_fittings.finish(g)

if __name__=='__main__':
 args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['SL']
 variants=list(g.VARIANTS) if args[0]=='all' else [args[0]]
 manifests=[]
 for v in variants:
  d=g.build(v,False)
  d['revision']='icf_detail_v02';d['hardware']='Conventional screw coupling and side buffers; static uncoupled configuration'
  d['detail_scope']=['True full-height door apertures','Radiused glazing and separate rubber/aluminium frames','Non-AC raised louvred shutters and security bars','Detailed all-coil ICF bogies with tread brakes and axle driven alternators','Fabricated screw coupling and dished buffers','Class-specific physical interior and tailored cushions','Wire fan cages, berth hardware, sanitary fittings and service equipment']
  d['known_limits']=[x for x in d['known_limits'] if 'No LODs' not in x]+['Source geometry is detailed authoring quality, not a new native game build. LOD/UV bake/animation/runtime conversion remains separate.','Markings and small fitting positions are illustrative; no numbered coach is claimed as an exact replica.','Screw coupling is shown hanging and uncoupled. Rake linkage and locomotive transition-coupler compatibility are unvalidated.']
  (g.OUT/v/'manifest.json').write_text(json.dumps(d,indent=2));manifests.append(d)
 if len(manifests)==7:(g.OUT/'family_manifest.json').write_text(json.dumps(manifests,indent=2))
