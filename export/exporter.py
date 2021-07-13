from .array import ArnoldArray
from .colormanager import ArnoldColorManager
from .node import ArnoldNode
from .polymesh import ArnoldPolymesh
from .constants import BTOA_CONVERTIBLE_TYPES, BTOA_LIGHT_SHAPE_CONVERSIONS
from . import utils as export_utils

class Exporter:
    def __init__(self, session):
        self.session = session

    def __get_target_frame(self, motion_step):
        frame_flt = frame_current + motion_step
        frame_int = math.floor(frame_flt)
        subframe = frame_flt - frame_int

        return frame_int, subframe

    def __evaluate_mesh(self, ob):
        pass

    def __get_static_mesh_data(self, mesh):
        vlist_data = numpy.ndarray(len(mesh.vertices) * 3, dtype=numpy.float32)
        mesh.vertices.foreach_get("co", vlist_data)

        nlist_data = numpy.ndarray(len(mesh.loops) * 3, dtype=numpy.float32)
        mesh.loops.foreach_get("normal", nlist_data)

        return vlist_data, nlist_data

    def create_polymesh(self, object_instance):
        scene = self.session.depsgraph.scene
        data = scene.arnold

        # Evaluate geometry at current frame

        ob = utils.get_object_data_from_instance(object_instance)
        mesh = self.__evaluate_mesh(ob)

        if mesh is None:
            return None

        # Calculate matrix data
        vlist_data = None
        nlist_data = None

        if data.enable_motion_blur:
            motion_steps = numpy.linspace(data.shutter_start, data.shutter_end, data.motion_keys)
            frame_current = scene.frame_current

            # Transform motion blur
            # TODO: I think this needs to be `transform_motion_blur`

            if data.camera_motion_blur:
                matrix = ArnoldArray()
                matrix.allocate(1, data.motion_keys, 'MATRIX')
                
                for i in range(0, motion_steps.size):
                    frame, subframe = self.__get_target_frame(motion_step[i])

                    self.session.engine.frame_set(frame, subframe=subframe)
                    
                    m = utils.flatten_matrix(object_instance.matrix_world)
                    matrix.set_matrix(i, m)

                self.session.engine.frame_set(frame_current, subframe=0)
            else:
                matrix = utils.flatten_matrix(object_instance.matrix_world)

            # Deformation motion blur

            if data.deformation_motion_blur:
                for i in range(0, motion_steps.size):
                    frame, subframe = self.__get_target_frame(motion_step[i])

                    self.session.engine.frame_set(frame, subframe=subframe)
                    _mesh = self.__evaluate_mesh(ob)

                    # vlist data

                    a = numpy.ndarray(len(mesh.vertices) * 3, dtype=numpy.float32)
                    _mesh.vertices.foreach_get("co", a)

                    vlist_data = a if vlist_data is None else numpy.concatenate((vlist_data, a))

                    # nlist data

                    a = numpy.ndarray(len(mesh.loops) * 3, dtype=numpy.float32)
                    _mesh.loops.foreach_get("normal", a)

                    nlist_data = a if nlist_data is None else numpy.concatenate((nlist_data, a))
            else:
                vlist_data, nlist_data = self.__get_static_mesh_data(mesh)

            # Compile vlist and nlist

            vlist = ArnoldArray()
            vlist.convert_from_buffer(
                len(mesh.vertices),
                data.motion_keys,
                'VECTOR',
                ctypes.c_void_p(vlist_data.ctypes.data)
            )

            nlist = ArnoldArray()
            nlist.convert_from_buffer(
                len(mesh.loops),
                data.motion_keys,
                'VECTOR',
                ctypes.c_void_p(nlist_data.ctypes.data)
            )

        # Calculate without motion blur

        else:
            vlist_data, nlist_data = self.__get_static_mesh_data(mesh)

            vlist = ArnoldArray()
            vlist.convert_from_buffer(
                len(mesh.vertices),
                1,
                'VECTOR',
                ctypes.c_void_p(vlist_data.ctypes.data)
            )

            nlist = ArnoldArray()
            nlist.convert_from_buffer(
                len(mesh.loops),
                1,
                'VECTOR',
                ctypes.c_void_p(nlist_data.ctypes.data)
            )

        # Polygons

        nsides_data = numpy.ndarray(len(mesh.polygons), dtype=numpy.uint32)
        mesh.polygons.foreach_get("loop_total", nsides_data)

        nsides = ArnoldArray()
        nsides.convert_from_buffer(
            len(mesh.polygons),
            1,
            'UINT',
            ctypes.c_void_p(nsides.ctypes.data)
        )

        vidxs_data = numpy.ndarray(len(mesh.loops), dtype=numpy.uint32)
        mesh.polygons.foreach_get("vertices", vidxs_data)

        vidxs = ArnoldArray()
        vidxs.convert_from_buffer(
            len(mesh.loops),
            1,
            'UINT',
            ctypes.c_void_p(vidxs_data.ctypes.data)
        )

        # TODO: I feel like this is missing a line...
        a = numpy.arange(len(mesh.loops), dtype=numpy.uint32)
        
        nidxs = ArnoldArray()
        nidxs.convert_from_buffer(
            len(mesh.loops),
            1,
            'UINT',
            ctypes.c_void_p(nidxs_data.ctypes.data)
        )

        # Create polymesh object
        
        name = utils.get_unique_name(object_instance)
        node = ArnoldPolymesh(name)

        if data.enable_motion_blur and data.camera_motion_blur:
            node.set_array("matrix", matrix)
        else:
            node.set_matrix("matrix", matrix)
        
        node.set_bool("smoothing", True)
        node.set_array("vlist", vlist)
        node.set_array("nlist", nlist)
        node.set_array("nsides", nsides)
        node.set_array("vidxs", vidxs)
        node.set_array("nidxs", nidxs)
        node.set_float("motion_start", settings.shutter_start)
        node.set_float("motion_end", settings.shutter_end)

        # UV's
        for i, uvt in enumerate(mesh.uv_layers):
            if uvt.active_render:
                uv_data = mesh.uv_layers[i].data
                
                uvidxs_data = numpy.arange(len(uv_data), dtype=numpy.uint32)
                uvidxs = ArnoldArray()
                uvidxs.convert_from_buffer(
                    len(uv_data),
                    1,
                    'UINT',
                    ctypes.c_void_p(uvidxs_data.ctypes.data)
                )

                uvlist_data = numpy.ndarray(len(uv_data) * 2, dtype=numpy.float32)
                uv_data.foreach_get("uv", a)

                uvlist = ArnoldArray()
                uvlist.convert_from_buffer(
                    len(data),
                    1,
                    'VECTOR2',
                    ctypes.c_void_p(uvlist_data.ctypes.data)
                )

                node.set_array("uvidxs", uvidxs)
                node.set_array("uvlist", uvlist)

                break

        # Materials
        # This should really be in a for loop, but for now we're only
        # looking for the material in the first slot.
        # for slot in ob.material_slots:
        try:
            slot = ob.material_slots[0]
            if slot.material is not None:
                unique_name = utils.get_unique_name(slot.material)

                if slot.material.arnold.node_tree is not None:
                    shader = engine.session.get_node_by_name(unique_name)

                    if shader.is_valid():
                        node.set_pointer("shader", shader)
                    else:
                        surface, volume, displacement = slot.material.arnold.node_tree.export()
                        surface[0].set_string("name", unique_name)
                        node.set_pointer("shader", surface[0])

        except:
            print("WARNING: {} has no material slots assigned!".format(ob.name))

        return node

    def create_world(self, world):
        data = world.arnold.data
        
        surface, volume, displacement = world.arnold.node_tree.export()
        node = surface[0]
        
        unique_name = utils.get_unique_name(world)
        node.set_string("name", unique_name)

        # Flip image textures in the U direction
        image = node.get_link("color")
        if image.is_valid() and image.type_is("image"):
            sflip = image.get_bool("sflip")
            image.set_bool("sflip", not sflip)

        node.set_int("samples", data.samples)
        node.set_bool("normalize", data.normalize)

        node.set_bool("cast_shadows", data.cast_shadows)
        node.set_bool("cast_volumetric_shadows", data.cast_volumetric_shadows)
        node.set_rgb("shadow_color", *data.shadow_color)
        node.set_float("shadow_density", data.shadow_density)

        node.set_float("camera", data.camera)
        node.set_float("diffuse", data.diffuse)
        node.set_float("specular", data.specular)
        node.set_float("transmission", data.transmission)
        node.set_float("sss", data.sss)
        node.set_float("indirect", data.indirect)
        node.set_float("volume", data.volume)
        node.set_int("max_bounces", data.max_bounces)

        return node

    def create_camera(self, object_instance):
        node = ArnoldNode("persp_camera")
        self.sync_camera(node, object_instance)

        return node

    def create_light(self, object_instance):
        ob = utils.get_object_data_from_instance(object_instance)

        ntype = BTOA_LIGHT_SHAPE_CONVERSIONS[ob.data.shape] if ob.data.type == 'AREA' else btoa.BT_LIGHT_CONVERSIONS[ob.data.type]
        node = ArnoldNode(ntype)
        self.sync_light(node, object_instance)

        return node

    def sync_camera(self, btnode, object_instance):
        ob = utils.get_object_data_from_instance(object_instance)
        data = ob.data
        arnold = data.arnold
        settings = self.session.settings

        btnode.set_string("name", utils.get_unique_name(object_instance))

        if settings.enable_motion_blur and settings.camera_motion_blur:
            matrix = self.get_transform_blur_matrix(object_instance)
            btnode.set_array("matrix", matrix)
        else:
            matrix = utils.flatten_matrix(object_instance.matrix_world)
            btnode.set_matrix("matrix", matrix)

        fov = utils.calc_horizontal_fov(ob)
        btnode.set_float("fov", math.degrees(fov))
        btnode.set_float("exposure", arnold.exposure)

        if data.dof.focus_object:
            distance = mathutils.geometry.distance_point_to_plane(
                ob.matrix_world.to_translation(),
                data.dof.focus_object.matrix_world.to_translation(),
                ob.matrix_world.col[2][:3]
            )
        else:
            distance = data.dof.focus_distance

        aperture_size = arnold.aperture_size if arnold.enable_dof else 0

        btnode.set_float("focus_distance", distance)
        btnode.set_float("aperture_size", aperture_size)
        btnode.set_int("aperture_blades", arnold.aperture_blades)
        btnode.set_float("aperture_rotation", arnold.aperture_rotation)
        btnode.set_float("aperture_blade_curvature", arnold.aperture_blade_curvature)
        btnode.set_float("aperture_aspect_ratio", arnold.aperture_aspect_ratio)

        btnode.set_float("near_clip", data.clip_start)
        btnode.set_float("far_clip", data.clip_end)

        if settings.enable_motion_blur:
            btnode.set_float("shutter_start", settings.shutter_start)
            btnode.set_float("shutter_end", settings.shutter_end)
            #btnode.set_string("shutter_type", arnold.shutter_type)
            #btnode.set_string("rolling_shutter", arnold.rolling_shutter)
            #btnode.set_float("rolling_shutter_duration", arnold.rolling_shutter_duration)

    def sync_light(self, btnode, object_instance):    
        ob = utils.get_object_data_from_instance(object_instance)

        data = ob.data
        arnold = data.arnold

        btnode.set_string("name", utils.get_unique_name(object_instance))

        # Set matrix for everything except cylinder lights
        if not hasattr(data, "shape") or data.shape != 'RECTANGLE':
            btnode.set_matrix(
                "matrix",
                utils.flatten_matrix(ob.matrix_world)
            )
        
        btnode.set_rgb("color", *data.color)
        btnode.set_float("intensity", arnold.intensity)
        btnode.set_float("exposure", arnold.exposure)
        btnode.set_int("samples", arnold.samples)
        btnode.set_bool("normalize", arnold.normalize)

        btnode.set_bool("cast_shadows", arnold.cast_shadows)
        btnode.set_bool("cast_volumetric_shadows", arnold.cast_volumetric_shadows)
        btnode.set_rgb("shadow_color", *arnold.shadow_color)
        btnode.set_float("shadow_density", arnold.shadow_density)

        btnode.set_float("camera", arnold.camera)
        btnode.set_float("diffuse", arnold.diffuse)
        btnode.set_float("specular", arnold.specular)
        btnode.set_float("transmission", arnold.transmission)
        btnode.set_float("sss", arnold.sss)
        btnode.set_float("indirect", arnold.indirect)
        btnode.set_float("volume", arnold.volume)
        btnode.set_int("max_bounces", arnold.max_bounces)

        if data.type in ('POINT', 'SPOT'):
            btnode.set_float("radius", data.shadow_soft_size)

        if data.type == 'SUN':
            btnode.set_float("angle", arnold.angle)

        if data.type == 'SPOT':
            btnode.set_float("cone_angle", math.degrees(data.spot_size))
            btnode.set_float("penumbra_angle", math.degrees(arnold.penumbra_angle))
            btnode.set_float("roundness", arnold.spot_roundness)
            btnode.set_float("aspect_ratio", arnold.aspect_ratio)
            btnode.set_float("lens_radius", arnold.lens_radius)

        if data.type == 'AREA':
            btnode.set_float("roundness", arnold.area_roundness)
            btnode.set_float("spread", arnold.spread)
            btnode.set_int("resolution", arnold.resolution)
            btnode.set_float("soft_edge", arnold.soft_edge)
            
            if data.shape == 'SQUARE':
                smatrix = mathutils.Matrix.Diagonal((
                    data.size / 2,
                    data.size / 2,
                    data.size / 2
                )).to_4x4()
                
                tmatrix = ob.matrix_world @ smatrix
            
                btnode.set_matrix(
                    "matrix",
                    utils.flatten_matrix(tmatrix)
                )
            elif data.shape == 'DISK':
                s = ob.scale.x if ob.scale.x > ob.scale.y else ob.scale.y
                btnode.set_float("radius", 0.5 * data.size * s)
            elif data.shape == 'RECTANGLE':
                d = 0.5 * data.size_y * ob.scale.y
                top = utils.get_position_along_local_vector(ob, d, 'Y')
                bottom = utils.get_position_along_local_vector(ob, -d, 'Y')

                btnode.set_vector("top", *top)
                btnode.set_vector("bottom", *bottom)

                s = ob.scale.x if ob.scale.x > ob.scale.z else ob.scale.z
                btnode.set_float("radius", 0.5 * data.size * s)

    def run(self, engine, depsgraph):
        self.engine = engine
        self.depsgraph = depsgraph

        scene = depsgraph.scene
        options = engine.session.options

        # Set resolution settings

        options.set_render_resolution(*utils.get_render_resolution(scene))

        if scene.render.use_border:
            min_x = int(x * render.border_min_x)
            min_y = int(math.ceil(y * (1 - render.border_max_y)))
            max_x = int(x * render.border_max_x) - 1 # I don't know why, but subtracting 1px here avoids weird render artifacts
            max_y = int(math.ceil(y * (1 - render.border_min_y)))

            options.set_render_region(min_x, min_y, max_x, max_y)
        
        # Set global render settings

        self.options.set_int("render_device", int(scene.arnold.render_device))

        self.options.set_int("AA_samples", scene.arnold.aa_samples)
        self.options.set_int("GI_diffuse_samples", scene.arnold.diffuse_samples)
        self.options.set_int("GI_specular_samples", scene.arnold.specular_samples)
        self.options.set_int("GI_transmission_samples", scene.arnold.transmission_samples)
        self.options.set_int("GI_sss_samples", scene.arnold.sss_samples)
        self.options.set_int("GI_volume_samples", scene.arnold.volume_samples)
        self.options.set_float("AA_sample_clamp", scene.arnold.sample_clamp)
        self.options.set_bool("AA_sample_clamp_affects_aovs", scene.arnold.clamp_aovs)
        self.options.set_float("indirect_sample_clamp", scene.arnold.indirect_sample_clamp)
        self.options.set_float("low_light_threshold", scene.arnold.low_light_threshold)

        self.options.set_bool("enable_adaptive_sampling", scene.arnold.use_adaptive_sampling)
        self.options.set_int("AA_samples_max", scene.arnold.adaptive_aa_samples_max)
        self.options.set_float("adaptive_threshold", scene.arnold.adaptive_threshold)

        if scene.arnold.aa_seed > 0:
            self.options.set_int("AA_seed", scene.arnold.aa_seed)

        self.options.set_int("GI_total_depth", scene.arnold.total_depth)
        self.options.set_int("GI_diffuse_depth", scene.arnold.diffuse_depth)
        self.options.set_int("GI_specular_depth", scene.arnold.specular_depth)
        self.options.set_int("GI_transmission_depth", scene.arnold.transmission_depth)
        self.options.set_int("GI_volume_depth", scene.arnold.volume_depth)
        self.options.set_int("auto_transparency_depth", scene.arnold.transparency_depth)

        self.options.set_int("bucket_size", scene.arnold.bucket_size)
        self.options.set_string("bucket_scanning", scene.arnold.bucket_scanning)
        self.options.set_bool("parallel_node_init", scene.arnold.parallel_node_init)
        self.options.set_int("threads", scene.arnold.threads)

        # Export scene objects

        for object_instance in self.depsgraph.object_instances:
            ob = utils.get_object_data_from_instance(object_instance)
            ob_unique_name = utils.get_unique_name(object_instance)

            node = self.get_node_by_name(ob_unique_name)

            if not node.is_valid():
                if ob.type in BTOA_CONVERTIBLE_TYPES:
                    node = self.create_polymesh(engine, depsgraph, object_instance)
                elif ob.name == scene.camera.name:
                    node = self.create_camera(object_instance)
                    self.options.set_pointer("camera", node)
                
                #if ob.type == 'LIGHT':
                #    node = self.create_light(object_instance)

        # Export world settings

        #if depsgraph.scene.world.arnold.node_tree is not None:
        #    self.create_world(depsgraph.scene.world)

        # Add final required nodes

        default_filter = ArnoldNode("gaussian_filter")
        default_filter.set_string("name", "gaussianFilter")

        outputs = ArnoldArray()
        outputs.allocate(1, 1, 'STRING')
        outputs.set_string(0, "RGBA RGBA gaussianFilter __display_driver")
        options.set_array("outputs", outputs)

        color_manager = ArnoldColorManager()
        color_manager.set_string("config", os.getenv("OCIO"))
        options.set_pointer("color_manager", color_manager)

        cb = btoa.AtDisplayCallback(display_callback)
        
        display_node = session.get_node_by_name("__display_driver")
        
        if not display_node.is_valid():
            display_node = ArnoldNode("driver_display_callback")
            display_node.set_string("name", "__display_driver")
        
        display_node.set_pointer("callback", cb)
    
    def update_render_result(self, x, y, width, height, buffer, data):
        session = self.engine.session
        min_x, min_y, max_x, max_y = session.options.get_render_region()

        x = x - min_x
        y = max_y - y - height

        if buffer:
            try:
                result = self.buckets.pop((x, y), None)

                if result is None:
                    result = engine.begin_result(x, y, width, height)

                b = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_float))
                rect = numpy.ctypeslib.as_array(b, shape=(width * height, 4))

                result.layers[0].passes["Combined"].rect = rect
                engine.end_result(result)
            
            finally:
                session.free_buffer(buffer)
        else:
            self.buckets[(x, y)] = engine.begin_result(x, y, width, height)

        if engine.test_break():
            session.abort()
            while self.buckets:
                (x, y), result = self.buckets.popitem()
                engine.end_result(result, cancel=True)