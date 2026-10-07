"""Reference-informed LHB fabricated shell and opening details, SI units.
Every glazing panel occupies a real rounded through-aperture. No photo assets.
"""
import bpy, math
from mathutils import Vector

def build(g,k,c):
 box,mesh,rod,text,empty=[g[n] for n in ['box','mesh','rod','text','empty']]
 paint,grey,steel,rubber,ivory,white,blue,glass,wood=[g[n] for n in ['paint','grey','steel','rubber','ivory','white','blue','glass','wood']]
 root,body,inter,roof,glasscoll=[g[n] for n in ['root','body','inter','roof','glasscoll']]
 wcglass=g['material']('WC_privacy_frosted_glass',(.72,.78,.77),0,.40)
 wp=wcglass.node_tree.nodes.get('Principled BSDF');wp.inputs['Transmission Weight'].default_value=.75;wp.inputs['IOR'].default_value=1.45
 wcglass['export_note']='Frosted privacy glass; diffuse opaque fallback in FBX, not clear passenger glazing'
 def rounded(w,h,r,n=8):
  p=[]
  for cx,cz,start in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
   for i in range(n+1):
    a=math.radians(start+i*90/n);p.append((cx+r*math.cos(a),cz+r*math.sin(a)))
  return p
 def slab(name,x,y,z,w,h,t,r,mat,coll=None,parent=None):
  ring=rounded(w,h,r);N=len(ring);vs=[(x+xx,y+dy,z+zz) for dy in [-t/2,t/2] for xx,zz in ring]
  fs=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
  ob=mesh(name,vs,fs,mat,parent=parent,coll=coll)
  for p in ob.data.polygons[2:]:p.use_smooth=True
  return ob
 def ring(name,x,y,z,w,h,t,r,border,mat,coll=None,parent=None):
  a=rounded(w,h,r);b=rounded(w-2*border,h-2*border,max(.012,r-border));N=len(a)
  vs=[(x+xx,y+dy,z+zz) for dy in [-t/2,t/2] for points in [a,b] for xx,zz in points];fs=[]
  for i in range(N):
   j=(i+1)%N
   fs += [(i,j,j+N,i+N),(i+2*N,i+3*N,j+3*N,j+2*N),(i,i+2*N,j+2*N,j),(i+N,j+N,j+3*N,i+3*N)]
  ob=mesh(name,vs,fs,mat,parent=parent,coll=coll)
  for i,p in enumerate(ob.data.polygons):p.use_smooth=(i%4>=2)
  md=ob.modifiers.new('Soft manufactured gasket edge','BEVEL');md.width=.0012;md.segments=2
  return ob
 def pierced(name,x,y,z,outerw,outerh,w,h,t,r,mat,coll=None):
  inner=rounded(w,h,r);N=len(inner);outer=[(outerw/2,outerh/2),(-outerw/2,outerh/2),(-outerw/2,-outerh/2),(outerw/2,-outerh/2)];points=inner+outer;M=len(points)
  base=[];n=8
  for corner in range(4):
   start=corner*(n+1);oc=N+corner
   for j in range(n):base.append((oc,start+j,start+j+1))
   nex=(corner+1)%4;base.append((oc,N+nex,nex*(n+1),start+n))
  vs=[(x+xx,y+dy,z+zz) for dy in [-t/2,t/2] for xx,zz in points];fs=base+[tuple(v+M for v in reversed(f)) for f in base]
  for i in range(N):j=(i+1)%N;fs.append((i,j,j+M,i+M))
  for i in range(4):a=N+i;b=N+(i+1)%4;fs.append((a,a+M,b+M,b))
  ob=mesh(name,vs,fs,mat,coll=coll)
  if name.startswith(('BODYSIDE_rounded_aperture','DOOR_leaf_glazed_portal')):
   ob.data.materials.append(ivory)
   for face in list(ob.data.polygons)[2*len(base):2*len(base)+N]:face.material_index=1
  return ob
 # Measured selected drawing families. Exact window pitches remain an interpretation.
 if k=='1A':
  lens=[2.50,1.73,2.50,1.73,1.73,2.50,1.73,2.50];cur=-sum(lens)/2;cab=[]
  for length in lens:cab.append((cur+length/2,1.10));cur+=length
  rhythms={-1:cab,1:[(-8.35+i*1.855,1.10) for i in range(10)]}
 elif k=='2A':rhythms={s:[(-7.57+j*1.88,1.18) for j in range(9)] for s in [-1,1]}
 elif k=='3A':rhythms={s:[(-7.4+j*1.85,1.18) for j in range(9)] for s in [-1,1]}
 elif k=='SL':rhythms={s:[(-8.1+j*1.8+q*.38,.55) for j in range(10) for q in [-1,1]] for s in [-1,1]}
 elif k=='GS':rhythms={s:sorted([(e*(1.25+j*1.68)+q*.35,.53) for e in [-1,1] for j in range(5) for q in [-1,1]]) for s in [-1,1]}
 else:rhythms={s:[(-8.12+j*1.16,.78 if k=='2S' else 1.06) for j in range(15)] for s in [-1,1]}
 root['sealed_window_outer_glass_mm']=8.4 if c['ac'] else 0;root['sealed_window_inner_glass_mm']=4.0 if c['ac'] else 0;root['sealed_window_air_gap_mm']=6.0 if c['ac'] else 0
 root['window_openings_by_side']=str({str(s):len(v) for s,v in rhythms.items()})
 doors=[-10.07,10.07]+([0] if k=='GS' else [])
 for s in [-1,1]:
  wins=sorted(rhythms[s]);root['window_openings_per_side']=len(wins)
  # Each sidewall section is bounded by door portals. Window skins are actual rounded holes.
  edges=[-11.77]+[q for x in sorted(doors) for q in [x-.52,x+.52]]+[11.77]
  for j in range(0,len(edges)-1,2):
   lo,hi=edges[j:j+2];length=hi-lo;x=(lo+hi)/2
   box('BODYSIDE_sill',(x,s*1.578,1.705),(length,.084,.75),grey)
   box('BODYSIDE_header',(x,s*1.578,3.2475),(length,.084,.665),paint)
   box('INTERIOR_sill_liner',(x,s*1.528,1.715),(length,.018,.72),ivory,coll=inter)
   box('INTERIOR_header_liner',(x,s*1.528,3.2475),(length,.018,.665),ivory,coll=inter)
   # Thin red stripe defines the painted belt just beneath the window sill.
   box('LIVERY_belt_pinstripe',(x,s*1.62010,2.032),(length,.00015,.024),paint)
   section=[(wx,w,False) for wx,w in wins if lo<wx<hi]
   for wx in [-11.21,11.21]:
    if lo<wx<hi:section.append((wx,.57,True))
   section.sort()
   cursor=lo
   for idx,(wx,w,wc) in enumerate(section):
    left=max(lo,wx-w/2-.07);right=min(hi,wx+w/2+.07)
    if left>cursor:
     box('BODYSIDE_window_pier',((cursor+left)/2,s*1.578,2.495),(left-cursor,.084,.84),paint)
     box('INTERIOR_window_pier',((cursor+left)/2,s*1.528,2.495),(left-cursor,.02,.84),ivory,coll=inter)
    center=(left+right)/2;ow=right-left
    pierced('BODYSIDE_rounded_aperture',wx,s*1.578,2.495,ow,.84,w,.73,.084,.10,paint)
    pierced('INTERIOR_rounded_aperture_liner',wx,s*1.528,2.495,ow,.84,w,.73,.018,.10,ivory,inter)
    ring('WINDOW_recessed_EPDM_seal',wx,s*1.614,2.495,w+.008,.738,.022,.102,.029,rubber)
    ring('WINDOW_inner_trim',wx,s*1.522,2.495,w+.042,.772,.02,.118,.021,ivory,inter)
    if c['ac'] or wc:
     slab('GLASS_WC_frosted' if wc else 'GLASS_WINDOW',wx,s*1.602,2.495,w-.038,.692,.008 if wc else .0084,.078,wcglass if wc else glass,glasscoll)
     if not wc:
      slab('GLASS_WINDOW_inner_tempered',wx,s*1.5898,2.495,w-.038,.692,.004,.078,glass,glasscoll)
     if not wc:
      box('WINDOW_sill_table_edge',(wx,s*1.475,2.104),(w+.09,.09,.032),ivory,.012,coll=inter)
      rod('CURTAIN_rail',(wx-w/2,s*1.462,2.916),(wx+w/2,s*1.462,2.916),.008,steel,coll=inter)
    else:
     slab('GLASS_WINDOW_upper_sliding',wx,s*1.59,2.65,w-.04,.366,.008,.063,glass,glasscoll)
     box('WINDOW_horizontal_slide_rail',(wx,s*1.591,2.475),(w-.05,.025,.025),steel,.005)
     for zz in [2.19,2.31,2.43,2.55,2.67]:rod('WINDOW_security_bar',(wx-w/2+.015,s*1.615,zz),(wx+w/2-.015,s*1.615,zz),.008,steel,12)
     box('WINDOW_shutter_stack',(wx,s*1.511,2.964),(w,.042,.122),grey,.01,coll=inter)
     for z in [2.930,2.956,2.982]:box('WINDOW_shutter_louvre',(wx,s*1.481,z),(w-.032,.014,.012),steel,.003,coll=inter)
     box('WINDOW_shutter_pull',(wx,s*1.461,2.900),(.12,.018,.017),steel,.004,coll=inter)
     for dx in [-w/2+.018,w/2-.018]:box('WINDOW_slide_channel',(wx+dx,s*1.49,2.495),(.019,.022,.72),steel,.004,coll=inter)
    cursor=right
   if hi>cursor:
    box('BODYSIDE_window_pier',((cursor+hi)/2,s*1.578,2.495),(hi-cursor,.084,.84),paint)
    box('INTERIOR_window_pier',((cursor+hi)/2,s*1.528,2.495),(hi-cursor,.02,.84),ivory,coll=inter)
  # Door leaves have genuine glazing, separately nested hardware and hinges.
  for di,x in enumerate(doors):
   box('DOOR_portal_header',(x,s*1.578,3.4975),(1.04,.084,.165),paint)
   box('INTERIOR_door_portal_header',(x,s*1.528,3.4975),(1.04,.018,.165),ivory,coll=inter)
   for jamb in [-1,1]:box('DOOR_portal_jamb',(x+jamb*.50,s*1.578,2.3725),(.04,.084,2.085),paint)
   dp=empty('DOOR_'+('L' if s>0 else 'R')+'_'+str(di+1)+'_PIVOT',(x-.48,s*1.59,1.34),body)
   box('DOOR_bottom_leaf',(.48,0,.43),(.96,.055,.86),paint,.001,parent=dp)
   box('DOOR_top_leaf',(.48,0,1.99),(.96,.055,.17),paint,.001,parent=dp)
   o=pierced('DOOR_leaf_glazed_portal',.48,0,1.432,.96,1.144,.34,.94,.055,.10,paint);o.parent=dp
   ring('DOOR_EPDM_glazing',.48,0,1.432,.36,.96,.067,.108,.025,rubber,parent=dp)
   slab('GLASS_DOOR',.48,s*.008,1.432,.31,.91,.008,.084,glass,glasscoll,dp)
   for child in list(dp.children):
    if child.type=='MESH' and child.name.startswith(('DOOR_bottom_leaf','DOOR_top_leaf','DOOR_leaf_glazed_portal')):
     child.data.materials.append(ivory);inneridx=len(child.data.materials)-1
     for face in child.data.polygons:
      if face.normal.y*s<-.5:face.material_index=inneridx
   for xx in [.025,.935]:box('DOOR_edge_rebate',(xx,s*.031,1.035),(.024,.012,2.055),grey,.003,parent=dp)
   for hside in [-1,1]:
    rod('DOOR_handle',(.82,hside*.061,.70),(.82,hside*.061,1.01),.013,steel,20,parent=dp)
    for zz in [.70,1.01]:rod('DOOR_handle_mount',(.82,hside*.061,zz),(.82,hside*.027,zz),.012,steel,16,parent=dp)
    rod('DOOR_lock_barrel',(.82,hside*.028,.61),(.82,hside*.039,.61),.024,steel,24,parent=dp)
    box('DOOR_key_slot',(.82,hside*.041,.61),(.004,.003,.024),rubber,parent=dp)
   for zz in [.30,1.05,1.81]:
    rod('DOOR_hinge_pin',(.006,s*.031,zz-.045),(.006,s*.031,zz+.045),.016,steel,parent=dp)
    box('DOOR_hinge_leaf',(.031,s*.028,zz),(.062,.011,.053),steel,.003,parent=dp)
   for z in [.59,.86,1.13]:
    box('ENTRY_step',(x,s*1.48,z),(1.08,.27,.032),steel,.006)
    for q in range(13):box('ENTRY_step_antislip',(x-.47+q*.079,s*1.48,z+.018),(.012,.22,.008),rubber,.002)
   for xx in [x-.59,x+.59]:
    rod('ENTRY_handrail',(xx,s*1.663,1.58),(xx,s*1.663,2.94),.017,steel,16)
    for zz in [1.58,2.94]:rod('ENTRY_handrail_return',(xx,s*1.663,zz),(xx,s*1.616,zz),.017,steel,16)
   box('DOOR_threshold',(x,s*1.533,1.32),(1.04,.22,.035),steel,.006)
  # Railway reference markings; individual tiny stencils add hierarchy without invented serial IDs.
  text('CLASS_MARKING',c['label'],(0 if k!='GS' else 4.8,s*1.627,3.245),.14,rot=(math.pi/2,0,0 if s<0 else math.pi))
  text('RAILWAY_MARKING','INDIAN RAILWAYS',(-5.6,s*1.629,1.865),.105,rot=(math.pi/2,0,0 if s<0 else math.pi))
  text('COACH_CODE',c['code'],(5.6,s*1.629,1.865),.105,rot=(math.pi/2,0,0 if s<0 else math.pi))
  for e in [-1,1]:
   box('DESTINATION_BOARD_frame',(e*3.8,s*1.63,3.03),(1.52,.018,.16),steel,.01)
   box('DESTINATION_BOARD_face',(e*3.8,s*1.642,3.03),(1.46,.008,.118),ivory,.007)
   text('DESTINATION_BOARD_text','INDIAN RAILWAYS',(e*3.8,s*1.649,2.998),.066,rot=(math.pi/2,0,0 if s<0 else math.pi),m=rubber)
   text('SAFETY_stencil','LIFT HERE',(e*6.08,s*1.633,1.420),.047,rot=(math.pi/2,0,0 if s<0 else math.pi),m=rubber)
   box('LIFTING_arrow_stem',(e*6.08,s*1.635,1.382),(.014,.003,.055),rubber)
   for xx in [-.023,.023]:rod('LIFTING_arrow',(e*6.08,s*1.636,1.404),(e*6.08+xx,s*1.636,1.378),.003,rubber,6)
   box('EMERGENCY_brake_indicator_back',(e*8.9,s*1.638,3.03),(.19,.027,.09),rubber,.011)
   for dx,mat in [(-.046,white),(.046,paint)]:slab('EMERGENCY_indicator',e*8.9+dx,s*1.657,3.03,.052,.047,.013,.01,mat)
 # Smooth elliptical arch follows 4.039 m reference crown, no faceted nine-edge roof.
 profile=[(1.62*math.cos(math.pi*i/40),3.545+.494*math.sin(math.pi*i/40)) for i in range(41)]
 profile+= [(y,3.545+.494*math.sqrt(1-(y/1.62)**2)) for y in [-1.27,1.27]]
 profile.sort(key=lambda q:q[0],reverse=True)
 ringp=profile+[(y,z-.05) for y,z in reversed(profile)];N=len(ringp)
 sections=[(-11.77,0),(-11.69,.045),(-11.57,.145),(-11.43,.265),(-8.50,.265),(-8.31,.21),(-8.13,.08),(-8,0),(8,0),(8.13,.08),(8.31,.21),(8.50,.265),(11.43,.265),(11.57,.145),(11.69,.045),(11.77,0)] if c['ac'] else [(-11.77,0),(11.77,0)]
 def deck_height(y,z,drop):
  ay=abs(y);arch=3.545+.494*math.sqrt(max(0,1-(y/1.62)**2))
  deck=3.705 if ay<=1.27 else 3.545+(1.62-ay)/.35*.160
  return z-(drop/.265)*(arch-deck)
 vs=[(x,y,deck_height(y,z,drop)) for x,drop in sections for y,z in ringp]
 fs=[tuple(range(N-1,-1,-1)),tuple(range((len(sections)-1)*N,len(sections)*N))]
 for j in range(len(sections)-1):fs.extend([(j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i) for i in range(N)])
 ob=mesh('ROOF_arch',vs,fs,grey,coll=roof)
 for p in ob.data.polygons[2:]:p.use_smooth=True
 # Long seam beads and rainsheds sit on the crown; no fake corrugated sidewall.
 for yy in [-1.40,-1.02,-.52,0,.52,1.02,1.40]:
  zz=3.545+.494*math.sqrt(max(0,1-(yy/1.62)**2))
  rod('ROOF_longitudinal_seam',(-7.96,yy,zz+.004),(7.96,yy,zz+.004),.004,grey,8,coll=roof)
 for s in [-1,1]:
  box('ROOF_rain_gutter',(0,s*1.61,3.573),(23.54,.042,.024),steel,.009,coll=roof)
 box('CEILING_main',(0,0,3.615),(19.1,3.04,.036),ivory,coll=roof)
 for e in [-1,1]:
  # Endcap above vestibule, closed curved skin.
  end_profile=profile
  cap=[(-1.62,3.535)]+list(reversed(end_profile))+[(1.62,3.535)];nn=len(cap)
  vs=[(e*x,y,z) for x in [11.689,11.769] for y,z in cap]
  fs=[tuple(range(nn-1,-1,-1)),tuple(range(nn,2*nn))]+[(i,(i+1)%nn,(i+1)%nn+nn,i+nn) for i in range(nn)]
  mesh('ROOF_endcap',vs,fs,grey,coll=roof)
  if c['ac']:
   import lhb_hvac_detail
   lhb_hvac_detail.build(g,e)
  else:
   for xx in [e*2.3,e*5.7,e*9.3]:
    box('VENTURI_roof_vent_base',(xx,0,4.025),(.49,.30,.05),grey,.055,coll=roof)
    box('VENTURI_roof_vent_hood',(xx,0,4.083),(.42,.26,.072),grey,.06,coll=roof)
    for s in [-1,1]:box('VENTURI_roof_vent_slot',(xx,s*.128,4.070),(.26,.008,.026),rubber,.01,coll=roof)
  # Four end service compartments; 1A has three toilets and a linen room.
  for s in [-1,1]:
   box('WC_end_wall',(e*11.64,s*1.,2.37),(.08,.99,2.1),ivory,coll=inter)
   box('WC_corridor_wall',(e*11.13,s*.56,2.37),(1.08,.06,2.10),ivory,coll=inter)
   box('WC_door',(e*10.57,s*1.055,2.33),(.05,.91,2.02),ivory,.013,coll=inter)
   rod('WC_handle',(e*10.525,s*.79,2.13),(e*10.525,s*.79,2.31),.012,steel,coll=inter)
   text('WC_sign','LINEN' if k=='1A' and e<0 and s<0 else 'WC',(e*10.52,s*1.06,2.97),.08,rot=(math.pi/2,0,e*math.pi/2),m=rubber,coll=inter)
  for y in [-1.0,1.0]:box('END_wall',(e*11.73,y,2.46),(.08,1.13,2.27),grey,.013)
  box('END_header',(e*11.73,0,3.50),(.08,1.03,.23),grey,.015)
  for x in [11.77,11.82,11.87,11.92,11.97]:
   for y in [-.57,.57]:box('GANGWAY_bellows_side',(e*x,y,2.38),(.028,.10,2.13),rubber,.009)
   box('GANGWAY_bellows_top',(e*x,0,3.445),(.028,1.24,.10),rubber,.009)
  box('GANGWAY_bridge',(e*11.83,0,1.31),(.28,1.02,.06),steel,.008)
 # Helpers reusable for interior service refinements.
 g['detail_rounded_slab']=slab;g['detail_rounded_ring']=ring
