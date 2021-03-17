from bpy.types import Node
from bpy.props import IntProperty

from ..base import ArnoldNode
from .. import constants

class AiCarPaint(Node, ArnoldNode):
    '''A simple-to-use car paint shader. Outputs RGB.'''
    bl_label = "Car Paint"
    bl_width_default = constants.BL_NODE_WIDTH_DEFAULT
    bl_icon = 'MATERIAL'

    ai_name = "car_paint"

    flake_layers: IntProperty(
        name="Flake Layers",
        min=1,
        default=1
    )

    # flake_coord_space enum property

    def init(self, context):
        self.inputs.new('AiNodeSocketFloatNormalized', "Base Weight", identifier="base").default_value = 1
        self.inputs.new('AiNodeSocketRGB', "Base Color", identifier="base_color")
        self.inputs.new('AiNodeSocketFloatNormalized', "Base Roughness", identifier="base_roughness")

        self.inputs.new('AiNodeSocketFloatNormalized', "Specular Weight", identifier="specular").default_value = 1
        self.inputs.new('AiNodeSocketRGB', "Specular Color", identifier="specular_color")
        self.inputs.new('AiNodeSocketRGB', "Specular Flip Flop", identifier="specular_flip_flop")
        self.inputs.new('AiNodeSocketRGB', "Specular Light Facing", identifier="specular_light_facing")
        self.inputs.new('AiNodeSocketFloatNormalized', "Specular Falloff", identifier="specular_falloff")
        self.inputs.new('AiNodeSocketFloatNormalized', "Specular Roughness", identifier="specular_roughness").default_value = 0.2
        self.inputs.new('AiNodeSocketFloatAboveOne', "Specular IOR", identifier="specular_IOR").default_value = 1.52

        self.inputs.new('AiNodeSocketRGB', "Transmission Color", identifier="transmission_color")
        self.inputs.new('AiNodeSocketRGB', "Flake Color", identifier="flake_color")
        self.inputs.new('AiNodeSocketRGB', "Flake Flip Flop", identifier="flake_flip_flop")
        self.inputs.new('AiNodeSocketRGB', "Flake Light Facing", identifier="flake_light_facing")
        self.inputs.new('AiNodeSocketFloatNormalized', "Flake Falloff", identifier="flake_falloff")
        self.inputs.new('AiNodeSocketFloatNormalized', "Flake Roughness", identifier="flake_roughness").default_value = 0.4
        self.inputs.new('AiNodeSocketFloatAboveOne', "Flake IOR", identifier="flake_IOR")
        self.inputs.new('AiNodeSocketFloatNormalized', "Flake Scale", identifier="flake_scale").default_value = 0.001
        self.inputs.new('AiNodeSocketFloatNormalized', "Flake Density", identifier="flake_density")
        self.inputs.new('AiNodeSocketFloatNormalized', "Flake Normal Randomize", identifier="flake_normal_randomize").default_value = 0.2
        self.inputs.new("AiNodeSocketCoord", "Flake Coords", identifier="flake_coord_space")

        self.inputs.new('AiNodeSocketFloatNormalized', "Coat", identifier="coat")
        self.inputs.new('AiNodeSocketRGB', "Coat Color", identifier="coat_color")
        self.inputs.new('AiNodeSocketFloatNormalized', "Coat Roughness", identifier="coat_roughness")
        self.inputs.new('AiNodeSocketFloatAboveOne', "Coat IOR", identifier="coat_IOR").default_value = 1.5
        self.inputs.new('AiNodeSocketVector', name="Coat Normal", identifier="coat_normal")

        self.outputs.new('AiNodeSocketSurface', name="RGB", identifier="output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "flake_layers")

    def sub_export(self, node):
        node.set_int("flake_layers", self.flake_layers)

def register():
    from bpy.utils import register_class
    register_class(AiCarPaint)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(AiCarPaint)
    