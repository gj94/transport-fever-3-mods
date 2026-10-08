# Ground-to-platform-height entries, without altering established interior plans.
col('24_FORECOURT_ENTRY_STEPS_AND_BOOKING_RAMP')
for lo,hi in [(-77,-2.0),(2.0,59)]:
 for k in range(5):
  h=.17*(k+1);box('Heritage wing entry step',((lo+hi)/2,-1.35+k*.30,h/2),(hi-lo,.30,h),tile)
  box('Entry stair nosing',((lo+hi)/2,-1.485+k*.30,h+.007),(hi-lo,.025,.014),cream)
# Booking front door at(113,-7) shares the station's .85m floor datum.
# A 1:13.75 visual access ramp approaches the door through a clear fence opening.
vs=[(112.28,-18,.05),(113.72,-18,.05),(113.72,-7,.85),(112.28,-7,.85),(112.28,-18,-.08),(113.72,-18,-.08),(113.72,-7,.65),(112.28,-7,.65)]
add('Booking street-entry ramp',vs,[(0,1,2,3),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0),(4,7,6,5)],tile)
for x in(112.12,113.88):
 rod('Booking ramp handrail',(x,-18,1.02),(x,-7,1.82),.033,steel)
 for k in range(7):
  y=-18+k*11/6;z=.05+k*.8/6;rod('Booking ramp upright',(x,y,z),(x,y,z+.98),.025,steel)
flush()
