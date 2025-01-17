from bpy.types import NodeSocket
from bpy.props import FloatProperty

from .ainodesocket import AiNodeSocket
from .constants import Color

import math

class AiNodeSocketFloat(AiNodeSocket):
    default_type = 'FLOAT'
    color = Color.float_texture

    def export_default(self):
        return self.default_value, self.default_type

class AiNodeSocketFloatUnbounded(NodeSocket, AiNodeSocketFloat):
    default_value: FloatProperty(
        soft_min=-5,
        soft_max=5
        )

class AiNodeSocketFloatPositive(NodeSocket, AiNodeSocketFloat):
    default_value: FloatProperty(
        min=0,
        soft_max=5
        )

class AiNodeSocketFloatAboveOne(NodeSocket, AiNodeSocketFloat):
    default_value: FloatProperty(
        min=1,
        soft_max=5
        )

class AiNodeSocketFloatNormalized(NodeSocket, AiNodeSocketFloat):
    default_value: FloatProperty(
        min=0,
        max=1
        )

class AiNodeSocketFloatPositiveToTen(NodeSocket, AiNodeSocketFloat):
    default_value: FloatProperty(
        min=0,
        max=10
    )

# I need a better name for this
# Covers the -1 to 1 range
class AiNodeSocketFloatNormalizedAlt(NodeSocket, AiNodeSocketFloat):
    default_value: FloatProperty(
        min=-1,
        max=1
        )

# Special socket for AiPhysicalSky. It's limited to the range 0-90deg.
class AiNodeSocketFloatHalfRotation(NodeSocket, AiNodeSocketFloat):
    default_value: FloatProperty(
        min=0,
        max=math.pi,
        unit='ROTATION'
    )

    def export_default(self):
        value = math.degrees(self.default_value)
        return value, self.default_type

# Special socket for AiPhysicalSky. It's limited to the range 0-360deg.
class AiNodeSocketFloatFullRotation(NodeSocket, AiNodeSocketFloat):
    default_value: FloatProperty(
        min=0,
        max=(math.pi * 2),
        unit='ROTATION'
    )

    def export_default(self):
        value = math.degrees(self.default_value)
        return value, self.default_type

classes = (
    AiNodeSocketFloatUnbounded,
    AiNodeSocketFloatPositive,
    AiNodeSocketFloatAboveOne,
    AiNodeSocketFloatNormalized,
    AiNodeSocketFloatNormalizedAlt,
    AiNodeSocketFloatHalfRotation,
    AiNodeSocketFloatFullRotation,
    AiNodeSocketFloatPositiveToTen
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)