"""Run in Blender Text Editor on the opened master to show/hide optional context."""
import bpy
SHOW_PLATFORM=True
SHOW_TRACK=True
SHOW_VEHICLES_AND_VEGETATION=True
for name,show in [('06_PLATFORM_CONTEXT_NOT_SURVEYED',SHOW_PLATFORM),('07_TRACK_CONTEXT',SHOW_TRACK),('08_SET_DRESSING',SHOW_VEHICLES_AND_VEGETATION)]:
 c=bpy.data.collections.get(name)
 if c:c.hide_render=not show;c.hide_viewport=not show
