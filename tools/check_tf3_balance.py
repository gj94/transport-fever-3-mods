"""Compare exported trainsets with installed stock resources and cost rules.

Read-only game inspection; estimates are before global/difficulty cost scales.
No base-game meshes or scripts are copied into the distributable mod.
"""
import argparse,json,math,re,posixpath,zipfile
from pathlib import Path
from tf3_resource_paths import resolve_model_ref

def table(text,key):
 match=re.search(r'\b'+key+r'\s*=\s*\{',text)
 if not match:return ''
 start=match.end()-1;depth=0;quote=False;escape=False
 for i in range(start,len(text)):
  c=text[i]
  if quote:
   if escape:escape=False
   elif c=='\\':escape=True
   elif c=='"':quote=False
  elif c=='"':quote=True
  elif c=='{':depth+=1
  elif c=='}':
   depth-=1
   if depth==0:return text[start:i+1]
 raise ValueError(key)

def number(text,key,default=0):
 match=re.search(r'\b'+key+r'\s*=\s*([-+\d.eE]+)',text)
 return float(match.group(1)) if match else default

def model_stats(text):
 metadata=table(text,'metadata');land=table(metadata,'landVehicle');tv=table(metadata,'transportVehicle')
 capacity=sum(float(v) for v in re.findall(r'\bcapacity\s*=\s*([\d.]+)',tv))
 speed=number(land,'topSpeed')*3.6
 power=sum(float(v) for v in re.findall(r'\bpower\s*=\s*([\d.]+)',land))
 effort=sum(float(v) for v in re.findall(r'\btractiveEffort\s*=\s*([\d.]+)',land))
 extent=table(metadata,'extent')
 lo=re.search(r'bbMin\s*=\s*\{\s*([-+\d.eE]+)',extent);hi=re.search(r'bbMax\s*=\s*\{\s*([-+\d.eE]+)',extent)
 # Matches base/model_metadata_util.lua:addCostMetadata in this installed game.
 average_speed=(speed**.86+10)/3.6;c=3.7*(365*4)/8
 rounding=lambda x:math.floor(x+.5)
 upkeep=rounding(average_speed*(capacity/4)*c*.5)
 if power:upkeep+=rounding(average_speed*(power/speed*12.5)*c*.5)
 cost=table(metadata,'cost');maintenance=table(metadata,'maintenance')
 purchase=number(cost,'price',-1);running=number(maintenance,'runningCosts',-1)
 if purchase<0:purchase=rounding(upkeep*6*number(cost,'priceScale',1))
 if running<0:running=rounding(upkeep*number(maintenance,'runningCostScale',1))
 return {'capacity':int(capacity),'speed_kmh':round(speed,3),'power_kw':power,'tractive_effort_kn':effort,'weight_t':number(land,'weightEmpty')/1000,'length_m':float(hi.group(1))-float(lo.group(1)),'base_purchase':purchase,'base_annual_upkeep':running,'comfort':number(tv,'comfortFactor',-1),'ticket_price_factor':number(tv,'priceFactor',.5)}

def unit_stats(name,vehicles):
 capacity=sum(v['capacity'] for v in vehicles);length=sum(v['length_m'] for v in vehicles)
 result={'name':name,'cars':len(vehicles),'capacity':capacity,'length_m':round(length,3),'seats_per_m':round(capacity/length,3),'speed_kmh':min(v['speed_kmh'] for v in vehicles)}
 # TF3 applies its stock quarter-capacity scale to gameplay; keep the authored
 # capacity for cost comparison and also expose the ordinary depot capacity.
 result['standard_game_capacity']=sum(int(v['capacity']/4) for v in vehicles)
 for k in ('power_kw','tractive_effort_kn','weight_t','base_purchase','base_annual_upkeep'):result[k]=round(sum(v[k] for v in vehicles),3)
 result['purchase_per_seat']=round(result['base_purchase']/capacity)
 result['annual_upkeep_per_seat']=round(result['base_annual_upkeep']/capacity)
 result['purchase_per_game_seat']=round(result['base_purchase']/result['standard_game_capacity'])
 return result

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--game-root',type=Path,required=True);args=parser.parse_args()
 root=Path(__file__).resolve().parents[1];stock=[]
 for key in ('es1_lastochka','twindexx','ice1','fs_etr_450','fuxing_hao','avelia_liberty','shinkansen_0s'):
  with zipfile.ZipFile(args.game_root/'base/content/vehicle/train'/(key+'.zip')) as z:
   unit=next(n for n in z.namelist() if n.endswith('.mu.lua'))
   refs=re.findall(r'name\s*=\s*"([^"\n]+\.mdl)"',z.read(unit).decode())
   stats=[model_stats(z.read(posixpath.normpath(posixpath.join(posixpath.dirname(unit),ref))).decode()) for ref in refs]
   stock.append(unit_stats(key,stats))
 mod=root/'game_build/gj94_indian_rail_pack/content/vehicle/train';vande=[]
 for count in (8,16):
  p=mod/'vande_bharat'/f'vande_bharat_{count}.mu.lua'
  refs=re.findall(r'name="([^"]+\.mdl)"',p.read_text())
  stats=[model_stats(resolve_model_ref(mod.parents[2],p,ref).read_text()) for ref in refs]
  vande.append(unit_stats(f'Vande Bharat {count}',stats))
  assert all(v['ticket_price_factor']==.5 for v in stats),'VB must use the stock ticket-price factor'
  assert all(v['comfort']<=.8 for v in stats),'Do not exceed stock express comfort'
  assert 2<=vande[-1]['seats_per_m']<=4.5,'Capacity density outside modern stock range'
  peers=[s for s in stock if s['speed_kmh']>=159]
  assert min(s['purchase_per_seat'] for s in peers)<=vande[-1]['purchase_per_seat']<=max(s['purchase_per_seat'] for s in peers),'Purchase cost per seat outside stock range'
 report={'basis':'Installed stock MU/model resources and base/model_metadata_util.lua cost formula; before difficulty/global cost scales. capacity is authored metadata; standard_game_capacity applies the stock quarter-capacity scale.','stock':stock,'vande_bharat':vande}
 (root/'game_build/vande_bharat_balance.json').write_text(json.dumps(report,indent=2))
 for s in stock+vande:print(json.dumps(s))

if __name__=='__main__':main()
