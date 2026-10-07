"""Reference-placed Indian Railways livery accents and editable coach-position boards.
Position numbers are representative formation slots, not verified real coach serials.
"""
import bpy,bmesh,math
from mathutils import Vector

def apply(g,k,c):
 box,mesh,rod,text,material=[g[n] for n in ['box','mesh','rod','text','material']]
 body=g['body'];grey=g['grey'];ivory=g['ivory'];rubber=g['rubber'];white=g['white'];steel=g['steel']
 yellow=material('Coach_position_board_ochre',(.70,.42,.045),0,.46)
 charcoal=material('Railway_identification_ink',(.014,.020,.024),0,.45)
 slot={'1A':'H1','2A':'A1','3A':'B1','2S':'D1','CC':'C1','SL':'S1','GS':'GS'}[k]
 root=g['root'];root['coach_position_board']=slot;root['coach_position_board_scope']='Representative editable formation position; not a verified train formation or real serial number'
 # End wedge follows the broad layout seen in the railway manual's 3A photograph.
 # Bisect actual metal faces, so the two-colour boundary cannot cover a glazing opening.
 for ob in list(bpy.data.objects):
  if ob.type!='MESH' or not ob.name.startswith(('BODYSIDE_header','BODYSIDE_rounded_aperture','BODYSIDE_window_pier')):continue
  if not ob.data.vertices:continue
  xs=[v.co.x for v in ob.data.vertices]
  if min(xs)>10.58:sign=1
  elif max(xs)<-10.58:sign=-1
  else:continue
  slope=(3.46-2.08)/(11.77-10.60)
  bm=bmesh.new();bm.from_mesh(ob.data)
  bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000001,plane_co=(sign*10.60,0,2.08),plane_no=(-sign*slope,0,1),clear_inner=False,clear_outer=False)
  bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(ob.data);bm.free()
  if grey.name not in ob.data.materials:ob.data.materials.append(grey)
  idx=list(ob.data.materials).index(grey)
  for p in ob.data.polygons:
   center=sum((ob.data.vertices[i].co for i in p.vertices),Vector())/len(p.vertices)
   if center.z < 2.08+slope*(abs(center.x)-10.60)+.00001:p.material_index=idx
 for ob in bpy.data.objects:
  if ob.type=='FONT' and ob.name.startswith('CLASS_MARKING'):ob.data.size=.18;ob.location.z=3.25
 for side in [-1,1]:
  rotation=(math.pi/2,0,0 if side<0 else math.pi)
  for end in [-1,1]:
   x=end*9.33;y=side*1.637
   box('COACH_POSITION_board_frame',(x,y,3.065),(.265,.022,.325),steel,.011)
   box('COACH_POSITION_board_face',(x,side*1.652,3.065),(.232,.009,.288),yellow,.008)
   text('COACH_POSITION_number',slot,(x,side*1.660,3.008),.16,rot=rotation,m=charcoal)
   text('CAPACITY_marking',str(c['capacity'])+(' BERTHS' if k in ['1A','2A','3A','SL'] else ' SEATS'),(end*8.96,side*1.635,1.867),.065,rot=rotation,m=charcoal)
   # Region initials reflect the representative NR livery pictured in CAMTECH, not fleet assignment.
   text('REGION_initials_representative','N R',(end*11.46,side*1.635,3.205),.14,rot=rotation,m=charcoal)
   text('END_equipment_stencil','CBC  /  EOG',(end*11.36,side*1.635,1.627),.042,rot=rotation,m=charcoal)
   # Narrow caution edge along the end structure, leaving the end toilet window unobstructed.
   box('END_visibility_yellow_band',(end*11.713,side*1.625,2.45),(.052,.007,2.11),yellow,.003)
   # Small individual seat-range plaques on entry vestibule at readable modelling scale.
   text('ENTRY_capacity_plaque',c['code'],(end*10.065,side*1.629,1.623),.049,rot=rotation,m=white)
 root['region_livery_note']='NR lettering and grey end wedges are representative reference-informed livery, not a real numbered coach reproduction'
