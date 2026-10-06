"""Stable exterior material interface; implementation lives in surface_materials.

This module intentionally does not execute until setup()/apply() is called.
"""
from surface_materials import (apply, setup, basic, image, mapped_paint, setmat,
                               assign_buffer_uv, buffer_contact, machined_steel,
                               assign_windscreen_uv, assign_windscreen_service, VERSION, PREFIX)
