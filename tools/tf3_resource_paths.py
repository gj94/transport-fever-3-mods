"""Resolve model identifiers without accepting filesystem-only dot segments."""
from pathlib import Path


MOD_ID = 'gj94_indian_rail_pack'


def resolve_model_ref(mod, unit_path, reference):
    # TF3's resource repository does not normalize '../' as pathlib does.
    assert '\\' not in reference, reference
    if '::/' in reference:
        namespace, resource = reference.split('::/', 1)
        assert namespace == MOD_ID, reference
        base = mod / 'content'
    else:
        resource = reference
        base = unit_path.parent
    assert resource and not resource.startswith('/'), reference
    assert all(part not in ('', '.', '..') for part in resource.split('/')), reference
    path = base.joinpath(*resource.split('/'))
    assert path.is_file(), reference
    return path
