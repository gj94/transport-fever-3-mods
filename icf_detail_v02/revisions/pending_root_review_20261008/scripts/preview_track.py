"""Plain original 1,676 mm gauge inspection track; studio-only, never asset export."""
import bpy,math

def build(scene,length=32):
 coll=bpy.data.collections.get('STUDIO_render_only') or scene.collection
 def mat(n,c,metal,rough):
  m=bpy.data.materials.new(n);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
 steel=mat('STUDIO rail running steel',(.18,.20,.20),.8,.32);web=mat('STUDIO rail oxidised web',(.12,.086,.065),.5,.7);concrete=mat('STUDIO concrete sleeper',(.22,.23,.225),0,.86);clip=mat('STUDIO rail clip steel',(.10,.105,.105),.55,.64)
 def box(n,c,size,m):
  x,y,z=c;a,b,d=[q/2 for q in size];vv=[(x+i*a,y+j*b,z+k*d) for i,j,k in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]];ff=[(2,6,4,0),(5,7,3,1),(4,5,1,0),(3,7,6,2),(1,3,2,0),(6,7,5,4)];me=bpy.data.meshes.new(n);me.from_pydata(vv,[],ff);me.materials.append(m);ob=bpy.data.objects.new(n,me);coll.objects.link(ob);return ob
 ground=bpy.data.objects.get('STUDIO ground')
 if ground:ground.location.z=-.30
 # Head inner edges y=±0.838 establish broad gauge. Rail running surface is z=0.
 for y in [-.871,.871]:
  box('STUDIO rail head',(0,y,-.021),(length,.066,.042),steel)
  box('STUDIO rail web',(0,y,-.094),(length,.015,.104),web)
  box('STUDIO rail base',(0,y,-.158),(length,.14,.028),web)
 count=2*int(length/.65/2)+1
 for i in range(count):
  x=(i-(count-1)/2)*.65;box('STUDIO sleeper',(x,0,-.256),(.235,2.75,.168),concrete)
  for y in [-.871,.871]:
   box('STUDIO rail pad',(x,y,-.176),(.25,.20,.010),clip)
   for dy in [-.102,.102]:box('STUDIO fastening clip',(x,y+dy,-.158),(.065,.042,.047),clip)
 scene['preview_track_gauge_m']=1.676;scene['preview_rail_top_m']=0.0
