import bpy
node = bpy.context.object.active_material.arnold.node_tree.get_output_node().inputs["Surface"].links[0].from_node

node.inputs[0].default_value = 1.0
node.inputs[1].default_value = (0.8309999704360962, 0.4259999990463257, 0.0)
node.inputs[2].default_value = 0.0
node.inputs[3].default_value = 0.0
node.inputs[4].default_value = 1.0
node.inputs[5].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929)
node.inputs[6].default_value = 0.20000000298023224
node.inputs[7].default_value = 1.399999976158142
node.inputs[8].default_value = 0.0
node.inputs[9].default_value = 0.0
node.inputs[10].default_value = 0.0
node.inputs[11].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929)
node.inputs[12].default_value = 0.10000000149011612
node.inputs[13].default_value = (0.0, 0.0, 0.0)
node.inputs[14].default_value = 0.0
node.inputs[15].default_value = 0.0
node.inputs[16].default_value = 0.0
node.inputs[17].default_value = 0
node.inputs[18].default_value = 1.0
node.inputs[19].default_value = (0.8309999704360962, 0.4259999990463257, 0.0)
node.inputs[20].default_value = (0.10999999940395355, 0.0560000017285347, 0.0)
node.inputs[21].default_value = 0.10000000149011612
node.inputs[22].default_value = 0.0
node.inputs[23].default_value = (0.0, 0.0, 0.0)
node.inputs[24].default_value = (0.0, 0.0, 0.0)
node.inputs[25].default_value = 0.0
node.inputs[26].default_value = (0.0, 0.0, 0.0)
node.inputs[27].default_value = 0.30000001192092896
node.inputs[28].default_value = 0.0
node.inputs[29].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929)
node.inputs[30].default_value = 0.10000000149011612
node.inputs[31].default_value = 1.5
node.inputs[32].default_value = 0.0
node.inputs[33].default_value = 0.0
node.inputs[34].default_value = (0.0, 0.0, 0.0)
node.inputs[35].default_value = 0.0
node.inputs[36].default_value = 0.0
node.inputs[37].default_value = 0.0
node.inputs[38].default_value = 1.5
node.inputs[39].default_value = 0.0
node.inputs[40].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929)
node.inputs[41].default_value = (1.0, 1.0, 1.0)
node.transmit_aovs = True
node.thin_walled = False
node.caustics = False
node.internal_reflections = False
node.exit_to_background = False
node.subsurface_type = '1'
