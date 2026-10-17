"""Write the constant Lua resource tables shared by exporters and metadata updates."""
import json
import math


def lua(value):
    if isinstance(value, dict):
        return '{' + ','.join(k + '=' + lua(v) for k, v in value.items()) + '}'
    if isinstance(value, (list, tuple)):
        return '{' + ','.join(lua(v) for v in value) + '}'
    if isinstance(value, str):
        return json.dumps(value)
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, float):
        assert math.isfinite(value)
        return format(value, '.9g')
    return str(value)


def write_lua(path, value):
    path.write_text('function data()\nreturn ' + lua(value) + '\nend\n', encoding='utf8')
