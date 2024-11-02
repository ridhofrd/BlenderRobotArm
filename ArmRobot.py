import bpy
import math
import mathutils
import random
import time



################################################################
# helper functions BEGIN
################################################################


def purge_orphans():
    """
    Remove all orphan data blocks

    see this from more info:
    https://youtu.be/3rNqVPtbhzc?t=149
    """
    if bpy.app.version >= (3, 0, 0):
        # run this only for Blender versions 3.0 and higher
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
    else:
        # run this only for Blender versions lower than 3.0
        # call purge_orphans() recursively until there are no more orphan data blocks to purge
        result = bpy.ops.outliner.orphans_purge()
        if result.pop() != "CANCELLED":
            purge_orphans()


def clean_scene():
    """
    Removing all of the objects, collection, materials, particles,
    textures, images, curves, meshes, actions, nodes, and worlds from the scene

    Checkout this video explanation with example

    "How to clean the scene with Python in Blender (with examples)"
    https://youtu.be/3rNqVPtbhzc
    """
    # make sure the active object is not in Edit Mode
    if bpy.context.active_object and bpy.context.active_object.mode == "EDIT":
        bpy.ops.object.editmode_toggle()

    # make sure non of the objects are hidden from the viewport, selection, or disabled
    for obj in bpy.data.objects:
        obj.hide_set(False)
        obj.hide_select = False
        obj.hide_viewport = False

    # select all the object and delete them (just like pressing A + X + D in the viewport)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    # find all the collections and remove them
    collection_names = [col.name for col in bpy.data.collections]
    for name in collection_names:
        bpy.data.collections.remove(bpy.data.collections[name])

    # in the case when you modify the world shader
    # delete and recreate the world object
    world_names = [world.name for world in bpy.data.worlds]
    for name in world_names:
        bpy.data.worlds.remove(bpy.data.worlds[name])
    # create a new world data block
    bpy.ops.world.new()
    bpy.context.scene.world = bpy.data.worlds["World"]

    purge_orphans()


def active_object():
    """
    returns the active object
    """
    return bpy.context.active_object


def time_seed():
    """
    Sets the random seed based on the time
    and copies the seed into the clipboard
    """
    seed = time.time()
    print(f"seed: {seed}")
    random.seed(seed)

    # add the seed value to your clipboard
    bpy.context.window_manager.clipboard = str(seed)

    return seed


def add_ctrl_empty(name=None):
    bpy.ops.object.empty_add(type="PLAIN_AXES", align="WORLD")
    empty_ctrl = active_object()

    if name:
        empty_ctrl.name = name
    else:
        empty_ctrl.name = "empty.cntrl"

    return empty_ctrl


def make_active(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def track_empty(obj):
    """
    create an empty and add a 'Track To' constraint
    """
    empty = add_ctrl_empty(name=f"empty.tracker-target.{obj.name}")

    make_active(obj)
    bpy.ops.object.constraint_add(type="TRACK_TO")
    bpy.context.object.constraints["Track To"].target = empty

    return empty


def setup_camera(loc, rot, frame_count):
    """
    create and setup the camera
    """
    bpy.ops.object.camera_add(location=loc, rotation=rot)
    camera = active_object()

    # set the camera as the "active camera" in the scene
    bpy.context.scene.camera = camera

    # set the Focal Length of the camera
    camera.data.lens = 70

    camera.data.passepartout_alpha = 0.9

    empty = track_empty(camera)

    camera.data.dof.use_dof = True
    camera.data.dof.focus_object = empty
    camera.data.dof.aperture_fstop = 0.35

    start_value = camera.data.lens
    mid_value = camera.data.lens - 10
    loop_param(camera.data, "lens", start_value, mid_value, frame_count)

    return empty


def set_1080px_square_render_res():
    """
    Set the resolution of the rendered image to 1080 by 1080
    """
    bpy.context.scene.render.resolution_x = 1080
    bpy.context.scene.render.resolution_y = 1080


def set_scene_props(fps, loop_seconds):
    """
    Set scene properties
    """
    frame_count = fps * loop_seconds

    scene = bpy.context.scene
    scene.frame_end = frame_count

    # set the world background to black
    world = bpy.data.worlds["World"]
    if "Background" in world.node_tree.nodes:
        world.node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)

    scene.render.fps = fps

    scene.frame_current = 1
    scene.frame_start = 1

    scene.eevee.use_bloom = True
    scene.eevee.bloom_intensity = 0.005

    # set Ambient Occlusion properties
    scene.eevee.use_gtao = True
    scene.eevee.gtao_distance = 4
    scene.eevee.gtao_factor = 5

    scene.eevee.taa_render_samples = 64

    if bpy.app.version < (4, 0, 0):
        scene.view_settings.look = "Very High Contrast"
    else:
        scene.view_settings.look = "AgX - Very High Contrast"

    set_1080px_square_render_res()


def setup_scene(i=0):
    fps = 30
    loop_seconds = 12
    frame_count = fps * loop_seconds

    project_name = "stack_spin"
    bpy.context.scene.render.image_settings.file_format = "FFMPEG"
    bpy.context.scene.render.ffmpeg.format = "MPEG4"
    bpy.context.scene.render.filepath = f"/tmp/project_{project_name}/loop_{i}.mp4"

    seed = 0
    if seed:
        random.seed(seed)
    else:
        time_seed()

    # Utility Building Blocks
    clean_scene()
    set_scene_props(fps, loop_seconds)

    loc = (0, 0, 7)
    rot = (0, 0, 0)
    setup_camera(loc, rot, frame_count)

    context = {
        "frame_count": frame_count,
    }

    return context


def make_fcurves_linear():
    for fc in bpy.context.active_object.animation_data.action.fcurves:
        fc.extrapolation = "LINEAR"


def get_random_color():
    return random.choice(
        [
            [0.92578125, 1, 0.0, 1],
            [0.203125, 0.19140625, 0.28125, 1],
            [0.8359375, 0.92578125, 0.08984375, 1],
            [0.16796875, 0.6796875, 0.3984375, 1],
            [0.6875, 0.71875, 0.703125, 1],
            [0.9609375, 0.9140625, 0.48046875, 1],
            [0.79296875, 0.8046875, 0.56640625, 1],
            [0.96484375, 0.8046875, 0.83984375, 1],
            [0.91015625, 0.359375, 0.125, 1],
            [0.984375, 0.4609375, 0.4140625, 1],
            [0.0625, 0.09375, 0.125, 1],
            [0.2578125, 0.9140625, 0.86328125, 1],
            [0.97265625, 0.21875, 0.1328125, 1],
            [0.87109375, 0.39453125, 0.53515625, 1],
            [0.8359375, 0.92578125, 0.08984375, 1],
            [0.37109375, 0.29296875, 0.54296875, 1],
            [0.984375, 0.4609375, 0.4140625, 1],
            [0.92578125, 0.16796875, 0.19921875, 1],
            [0.9375, 0.9609375, 0.96484375, 1],
            [0.3359375, 0.45703125, 0.4453125, 1],
        ]
    )


def render_loop():
    bpy.ops.render.render(animation=True)


def apply_random_color_material(obj):
    color = get_random_color()
    mat = bpy.data.materials.new(name="Material")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = color
    mat.node_tree.nodes["Principled BSDF"].inputs["Specular"].default_value = 0

    obj.data.materials.append(mat)


def add_lights():
    rotation = (math.radians(60), 0.0, math.radians(180))
    bpy.ops.object.light_add(type="SUN", rotation=rotation)
    bpy.context.object.data.energy = 100
    bpy.context.object.data.diffuse_factor = 0.05
    bpy.context.object.data.angle = math.radians(45)


def loop_param(obj, param_name, start_value, mid_value, frame_count):
    frame = 1

    setattr(obj, param_name, start_value)
    obj.keyframe_insert(param_name, frame=frame)

    frame = frame_count / 2
    setattr(obj, param_name, mid_value)
    obj.keyframe_insert(param_name, frame=frame)

    frame = frame_count
    setattr(obj, param_name, start_value)
    obj.keyframe_insert(param_name, frame=frame)


def set_keyframe_to_ease_in_out(obj):
    for fcurve in obj.animation_data.action.fcurves:
        for kf in fcurve.keyframe_points:
            kf.interpolation = "BACK"
            kf.easing = "EASE_IN_OUT"


################################################################
# helper functions END
################################################################


def importArmRobot():
    #ubah prefix_path ke path dari folder asset kalian
    prefix_path = r"C:\Users\LENOVO\OneDrive - Politeknik Negeri Bandung\Documents\Akademik\semester 3\Komputer Grafik\Praktek\7. Tugas_6\task 3\animasi\BlenderRobotArm\STEAMFY_ASSET"
    ANGLE_path = r"\ANGLE.stl"
    CUBE_path = r"\CUBE.stl"
    GRIPPER_path = r"\GRIPPER.stl"
    PLATE_path = r"\PLATE.stl"
    ROTATIONAXIS_path = r"\ROTATIONAXIS.stl"
    ROTOR_path = r"\ROTOR.stl"
    SHAFT_path = r"\SHAFT.stl"
    
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    bpy.ops.wm.stl_import(filepath=(prefix_path + ANGLE_path))
    bpy.ops.wm.stl_import(filepath=(prefix_path + CUBE_path))
    bpy.ops.wm.stl_import(filepath=(prefix_path + GRIPPER_path))
    bpy.ops.wm.stl_import(filepath=(prefix_path + PLATE_path))
    bpy.ops.wm.stl_import(filepath=(prefix_path + ROTATIONAXIS_path))
    bpy.ops.wm.stl_import(filepath=(prefix_path + ROTOR_path))
    bpy.ops.wm.stl_import(filepath=(prefix_path + SHAFT_path))

    global plate, rotor, rotor1, rotationaxis, cube, angle, shaft, angle1, cube1, shaft001, cube2, angle2, gripper, gripper1, thruster, thruster1, thruster2, thruster3
    
    # Duplicate the object and optionally specify a collection
    plate = duplicate_object("PLATE", "plate", "Collection")
    if plate:
        set_location(plate, -1.90249, -0.935105, 0.490659)
        rotate_object(plate, x_degrees=0, y_degrees=0, z_degrees=0)
        resize_object(plate, 0.029202, 0.029202, 0.029202)
    
    rotor = duplicate_object("ROTOR", "rotor", "Collection")
    if rotor:
        set_location(rotor, -0.067378, 1.27627, 1.14376)
        rotate_object(rotor, x_degrees=0, y_degrees=0, z_degrees=45)
        resize_object(rotor, -0.026674, -0.026674, -0.026674)
    
    rotationaxis = duplicate_object("ROTATIONAXIS", "rotationaxis", "Collection")
    if rotationaxis:
        set_location(rotationaxis, -0.082457, 1.26177, 1.03893)
        rotate_object(rotationaxis, x_degrees=0, y_degrees=0, z_degrees=0)
        resize_object(rotationaxis, -0.079003, -0.094633, 0.028991)
        
    cube = duplicate_object("CUBE", "cube", "Collection")
    if cube:
        set_location(cube, 0.076949, 0.940057, 1.69695)
        rotate_object(cube, x_degrees=180, y_degrees=0, z_degrees=0)
        resize_object(cube, -0.020435, -0.044361, 0.043016)
        
    angle = duplicate_object("ANGLE", "angle", "Collection")
    if angle:
        set_location(angle, -0.358202, 0.926703, 1.91278)
        rotate_object(angle, x_degrees=223.887, y_degrees=0, z_degrees=180)
        resize_object(angle, 0.022659, 0.022659, 0.022659)
        
    shaft = duplicate_object("SHAFT", "shaft", "Collection")
    if shaft:
        set_location(shaft, -0.092524, 0.446057, 2.11501)
        rotate_object(shaft, x_degrees=35.8352, y_degrees=40, z_degrees=313.85)
        resize_object(shaft, 0.02375, 0.02375, 0.02375)
        
    angle1 = duplicate_object("angle", "angle1", "Collection")
    if angle1:
        set_location(angle1, -0.358202, -0.029123, 2.42568)
        rotate_object(angle1, x_degrees=40.158, y_degrees=0, z_degrees=180)
        resize_object(angle1, 0.022659, 0.022659, 0.022659)
        
    cube1 = duplicate_object("cube", "cube1", "Collection")
    if cube1:
        set_location(cube1, 0.076949, -0.450501, 2.66975)
        rotate_object(cube1, x_degrees=-137.333, y_degrees=0, z_degrees=0)
        resize_object(cube1, -0.020394, -0.043908, -0.020394)
        
    shaft001 = duplicate_object("shaft", "shaft001", "Collection")
    if shaft001:
        set_location(shaft001, -0.092524, 0.164382, 3.42365)
        rotate_object(shaft001, x_degrees=-33.431, y_degrees=-33.431, z_degrees=323.4)
        resize_object(shaft001, 0.02375, 0.02375, 0.02375)
        
    cube2 = duplicate_object("cube1", "cube2", "Collection")
    if cube2:
        set_location(cube2, 0.076949, 0.550098, 3.63451)
        rotate_object(cube2, x_degrees=-137.333, y_degrees=0, z_degrees=0)
        resize_object(cube2, -0.020394, -0.043908, -0.020394)
        
    angle2 = duplicate_object("angle1", "angle2", "Collection")
    if angle2:
        set_location(angle2, -0.358202, 1.05752, 3.47314)
        rotate_object(angle2, x_degrees=40.1576, y_degrees=0, z_degrees=-180)
        resize_object(angle2, 0.022659, 0.022659, 0.022659)
        
    rotor1 = duplicate_object("rotor", "rotor1", "Collection")
    if rotor1:
        set_location(rotor1, -0.072524, 1.56643, 3.17345)
        rotate_object(rotor1, x_degrees=-145.664, y_degrees=-29.1768, z_degrees=35.5155)
        resize_object(rotor1, -0.019042, -0.019042, -0.019042)
        
    gripper = duplicate_object("GRIPPER", "gripper", "Collection")
    if gripper:
        set_location(gripper, -0.355968, 1.53367, 3.2287)
        rotate_object(gripper, x_degrees=214.081, y_degrees=0, z_degrees=0)
        resize_object(gripper, 0.021216, 0.021216, 0.021216)
        
    gripper1 = duplicate_object("gripper", "gripper1", "Collection")
    if gripper1:
        set_location(gripper1, 0.215339, 1.59303, 3.16052)
        rotate_object(gripper1, x_degrees=-38.9312, y_degrees=0, z_degrees=180)
        resize_object(gripper1, 0.021216, 0.021216, 0.021216)
        
    thruster = duplicate_object("rotor1","thruster", "Collection")
    if thruster:
        set_location(thruster, 1.76499, -0.977508, -0.002476)
        rotate_object(thruster, x_degrees=176.994, y_degrees=2.9716, z_degrees=44.6315)
        resize_object(thruster, -0.023033, -0.023033, -0.023033)
        
    thruster1 = duplicate_object("thruster","thruster1", "Collection")
    if thruster1:
        set_location(thruster1, -1.88332, -0.968107, -0.00117)
        rotate_object(thruster1, x_degrees=176.994, y_degrees=2.9716, z_degrees=44.6315)
        resize_object(thruster1, -0.023033, -0.023033, -0.023417)
        
    thruster2 = duplicate_object("thruster1","thruster2", "Collection")
    if thruster2:
        set_location(thruster2, -1.86581, 2.66486, 0.006509)
        rotate_object(thruster2, x_degrees=176.994, y_degrees=2.9716, z_degrees=44.6315)
        resize_object(thruster2, -0.023033, -0.023033, -0.023417)
        
    thruster3 = duplicate_object("thruster1","thruster3", "Collection")
    if thruster1:
        set_location(thruster3, 1.76499, 2.6485 , -0.011162)
        rotate_object(thruster3, x_degrees=179.135, y_degrees=0.856294, z_degrees=44.703)
        resize_object(thruster3, -0.023033, -0.023033, -0.023033)
        
    print("After")
    
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects['ANGLE'].select_set(True)
    bpy.data.objects['CUBE'].select_set(True)
    bpy.data.objects['GRIPPER'].select_set(True)
    bpy.data.objects['PLATE'].select_set(True)
    bpy.data.objects['ROTATIONAXIS'].select_set(True)
    bpy.data.objects['ROTOR'].select_set(True)
    bpy.data.objects['SHAFT'].select_set(True)
    bpy.ops.object.delete()
    
    armRobot_object_list = [plate, rotor, rotor1, rotationaxis, cube, angle, shaft, angle1, cube1, shaft001, cube2, angle2, gripper, gripper1, thruster, thruster1, thruster2, thruster3]
    
    return armRobot_object_list
    
    
def duplicate_object(original_name, new_name, collection_name=None):
    original_object = bpy.data.objects.get(original_name)
    if original_object is None:
        print("Object not found")
        return None

    new_object_data = original_object.data.copy()
    new_object = bpy.data.objects.new(new_name, new_object_data)

    # Manage collection
    if collection_name:
        # Check if the collection exists
        collection = bpy.data.collections.get(collection_name)
        if not collection:
            # Create new collection if it does not exist
            collection = bpy.data.collections.new(collection_name)
            bpy.context.scene.collection.children.link(collection)
        collection.objects.link(new_object)
    else:

        original_collection = original_object.users_collection[0]  # Assumes the object is in at least one collection
        original_collection.objects.link(new_object)

    return new_object

def rotate_object(obj, x_degrees=0, y_degrees=0, z_degrees=0):
    if obj:
        obj.rotation_euler[0] += math.radians(x_degrees)
        obj.rotation_euler[1] += math.radians(y_degrees)
        obj.rotation_euler[2] += math.radians(z_degrees)
        bpy.context.view_layer.update()

def set_location(obj, x, y, z):
    if obj:
        obj.location = (x, y, z)
        bpy.context.view_layer.update()
        
def translate_object(obj, tx, ty, tz):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[obj.name].select_set(True)
    
    bpy.ops.transform.translate(value=(tx, ty, tz), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)

    bpy.context.view_layer.update()

def rotateObjectOnSelect(objList, radValue, axis):
    bpy.ops.object.select_all(action='DESELECT')
    for i in objList:
        bpy.data.objects[i.name].select_set(True)
    
    bpy.ops.transform.rotate(value=radValue, orient_axis=axis, orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)



    bpy.context.view_layer.update()
    
def rotate_object_on_x_axis(obj_name, rotation_value):
    # Setel nama objek yang akan dirotasi
    obj = bpy.data.objects.get(obj_name)
    if obj is None:
        print(f"Objek {obj_name} tidak ditemukan.")
        return

    # Deselect semua objek & pilih objek yang diinginkan
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # Lakukan rotasi
    bpy.ops.transform.rotate(
        value=rotation_value,  # nilai rotasi dalam radian
        orient_axis='X',  # rotasi pada sumbu X
        orient_type='GLOBAL',  # orientasi global
        orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),  # matriks orientasi global
        orient_matrix_type='GLOBAL',
        constraint_axis=(True, False, False),  # hanya sumbu X yang dirotasi
        mirror=False,
        use_proportional_edit=False,
        proportional_edit_falloff='SMOOTH',
        proportional_size=1,
        use_proportional_connected=False,
        use_proportional_projected=False,
        snap=False,
        snap_elements={'INCREMENT'},
        use_snap_project=False,
        snap_target='CLOSEST',
        use_snap_self=True,
        use_snap_edit=True,
        use_snap_nonedit=True,
        use_snap_selectable=False
    )

    bpy.context.view_layer.update()

def resize_object(obj, scale_x, scale_y, scale_z):
    if obj:
        obj.scale = (scale_x, scale_y, scale_z)
        bpy.context.view_layer.update()
        
def parent_objects(parent_obj, child_obj):
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)

    
def parentRobotArms():
    object_list = [rotor, rotationaxis, cube, angle, shaft, angle1, cube1, shaft001, cube2, angle2, gripper, gripper1, thruster, thruster1, thruster2, thruster3]
    for i in object_list:
        parent_objects(plate, i)
    
    
def transformasiRidho():
    translateList = [plate, rotor, rotor1, rotationaxis, cube, angle, shaft, angle1, cube1, shaft001, cube2, angle2, gripper, gripper1, thruster, thruster1, thruster2, thruster3]
    for i in translateList:
        translate_object(i, 15, 0, 0)
    
    rotationList = [rotor, rotor1, rotationaxis, cube, angle, shaft, angle1, cube1, shaft001, cube2, angle2, gripper, gripper1]
    rotateObjectOnSelect(rotationList, 360, 'Z')
    
def transformasiRidho2():
    translateList = [plate, rotor, rotor1, rotationaxis, cube, angle, shaft, angle1, cube1, shaft001, cube2, angle2, gripper, gripper1, thruster, thruster1, thruster2, thruster3]
    for i in translateList:
        translate_object(i, 0, 10, 0)
    
    rotationList = [rotor, rotor1, rotationaxis, cube, angle, shaft, angle1, cube1, shaft001, cube2, angle2, gripper, gripper1]
    rotateObjectOnSelect(rotationList, 11, 'Z')
    
def transformasiRidho3():
    translateList = [plate, rotor, rotor1, rotationaxis, cube, angle, shaft, angle1, cube1, shaft001, cube2, angle2, gripper, gripper1, thruster, thruster1, thruster2, thruster3]
    for i in translateList:
        translate_object(i, -15, 0, 0)
    
    rotationList = [rotor, rotor1, rotationaxis, cube, angle, shaft, angle1, cube1, shaft001, cube2, angle2, gripper, gripper1]
    rotateObjectOnSelect(rotationList, -360, 'Z')
    
def transformasiRidho4():
    translateList = [plate, rotor, rotor1, rotationaxis, cube, angle, shaft, angle1, cube1, shaft001, cube2, angle2, gripper, gripper1, thruster, thruster1, thruster2, thruster3]
    for i in translateList:
        translate_object(i, 0, -15, 0)
    
    rotationList = [rotor, rotor1, rotationaxis, cube, angle, shaft, angle1, cube1, shaft001, cube2, angle2, gripper, gripper1]
    rotateObjectOnSelect(rotationList, -11, 'Z')
        
    #parent_objects(plate, rotor)
    
def transformasiHarish():
    rotateList = [angle1, cube1, shaft001, cube2, angle2, gripper, gripper1]
    for obj in rotateList:
        rotate_object_on_x_axis(obj.name, -0.268581)

def transformasiHarish2():
    rotateList = [angle1, cube1, shaft001, cube2, angle2, gripper, gripper1]
    for obj in rotateList:
        rotate_object_on_x_axis(obj.name, 0.268581)

def transformasiHarish3():
    rotateList = [angle1, cube1, shaft001, cube2, angle2, gripper, gripper1]
    for obj in rotateList:
        rotate_object_on_x_axis(obj.name, -0.268581)

def insertKeyFrameForObjectTrans(objList, transformation, frameTime):
    for i in objList:
        i.keyframe_insert(transformation, frame=frameTime)
    
def transformasiDhea():
    rotateList = [angle, shaft, angle1, cube1, shaft001, cube2, angle2, gripper, gripper1, thruster, thruster1, thruster2, thruster3]
    for obj in rotateList:
        rotate_object_on_x_axis(obj.name, -0.268581)

def transformasiDhea2():
    rotateList = [angle, shaft, angle1, cube1, shaft001, cube2, angle2, gripper, gripper1, thruster, thruster1, thruster2, thruster3]
    for obj in rotateList:
        rotate_object_on_x_axis(obj.name, 0.268581)
        
def transformasiDhea3():
    rotateList = [angle, shaft, angle1, cube1, shaft001, cube2, angle2, gripper, gripper1, thruster, thruster1, thruster2, thruster3]
    for obj in rotateList:
        rotate_object_on_x_axis(obj.name, -0.268581)

def gen_centerpiece(context):
    RobotArmObj = importArmRobot()
    
    insertKeyFrameForObjectTrans(RobotArmObj, "rotation_euler", 1)
    insertKeyFrameForObjectTrans(RobotArmObj, "location", 1)
    
    transformasiRidho()
    transformasiDhea()
    transformasiHarish()
    
    insertKeyFrameForObjectTrans(RobotArmObj, "rotation_euler", 100)
    insertKeyFrameForObjectTrans(RobotArmObj, "location", 100)
    
    transformasiRidho2()
    transformasiHarish2()
    transformasiDhea2()
    
    insertKeyFrameForObjectTrans(RobotArmObj, "rotation_euler", 200)
    insertKeyFrameForObjectTrans(RobotArmObj, "location", 200)
    
    transformasiRidho3()
    transformasiHarish3()
    transformasiDhea3()
    insertKeyFrameForObjectTrans(RobotArmObj, "rotation_euler", 300)
    insertKeyFrameForObjectTrans(RobotArmObj, "location", 300)
    
    transformasiRidho4()
    transformasiDhea()
    transformasiHarish()
    insertKeyFrameForObjectTrans(RobotArmObj, "rotation_euler", 400)
    insertKeyFrameForObjectTrans(RobotArmObj, "location", 400)
    
    #parentRobotArms()


def main():
    """
    Python code to generate an animation loop
    """
    context = setup_scene()
    gen_centerpiece(context)
    add_lights()

    
    
    
# Example usage:
if __name__ == "__main__":
    main()
    
