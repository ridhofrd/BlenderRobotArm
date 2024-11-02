import bpy
import math
import mathutils
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

def resize_object(obj, scale_x, scale_y, scale_z):
    if obj:
        obj.scale = (scale_x, scale_y, scale_z)
        bpy.context.view_layer.update()
        
def parent_objects(parent_obj, child_obj):
    """
    Set one object as the parent of another.
    """
    child_obj.parent = parent_obj
    
    
# Example usage:
if __name__ == "__main__":
    
    # Duplicate the object and optionally specify a collection
    plate = duplicate_object("PLATE", "plate", "Collection")
    if plate:
        set_location(plate, -1.90249, -0.935105, 0.490659)
        rotate_object(plate, x_degrees=0, y_degrees=0, z_degrees=0)
        resize_object(plate, 0.029202, 0.029202, 0.029202)
    
    rotor = duplicate_object("ROTOR", "rotor", "Collection")
    if plate:
        set_location(rotor, -0.067378, 1.27627, 1.14376)
        rotate_object(rotor, x_degrees=0, y_degrees=0, z_degrees=45)
        resize_object(rotor, -0.026674, -0.026674, -0.026674)
    
    rotationaxis = duplicate_object("ROTATIONAXIS", "rotationaxis", "Collection")
    if rotationaxis:
        set_location(rotationaxis, -0.082457, 1.26177, 1.03893)
        rotate_object(rotationaxis, x_degrees=0, y_degrees=0, z_degrees=0)
        resize_object(rotationaxis, -0.079003, -0.094633, 0.028991)
        
    cube2 = duplicate_object("CUBE.002", "cube2", "Collection")
    if cube2:
        set_location(cube2, 0.076949, 0.940057, 1.69695)
        rotate_object(cube2, x_degrees=180, y_degrees=0, z_degrees=0)
        resize_object(cube2, -0.020435, -0.044361, 0.043016)
        
    angle2 = duplicate_object("ANGLE.002", "angle2", "Collection")
    if angle2:
        set_location(angle2, -0.358202, 0.926703, 1.91278)
        rotate_object(angle2, x_degrees=223.887, y_degrees=0, z_degrees=180)
        resize_object(angle2, 0.022659, 0.022659, 0.022659)
        
    shaft = duplicate_object("SHAFT", "shaft", "Collection")
    if shaft:
        set_location(shaft, -0.092524, 0.446057, 2.11501)
        rotate_object(shaft, x_degrees=35.8352, y_degrees=40, z_degrees=313.85)
        resize_object(shaft, 0.02375, 0.02375, 0.02375)
        
    angle = duplicate_object("ANGLE", "angle", "Collection")
    if angle:
        set_location(angle, -0.358202, -0.029123, 2.42568)
        rotate_object(angle, x_degrees=40.158, y_degrees=0, z_degrees=180)
        resize_object(angle, 0.022659, 0.022659, 0.022659)
        
    cube = duplicate_object("CUBE", "cube", "Collection")
    if cube:
        set_location(cube, 0.076949, -0.450501, 2.66975)
        rotate_object(cube, x_degrees=-137.333, y_degrees=0, z_degrees=0)
        resize_object(cube, -0.020394, -0.043908, -0.020394)
        
    shaft001 = duplicate_object("SHAFT.001", "shaft001", "Collection")
    if shaft001:
        set_location(shaft001, -0.092524, 0.164382, 3.42365)
        rotate_object(shaft001, x_degrees=-33.431, y_degrees=-33.431, z_degrees=323.4)
        resize_object(shaft001, 0.02375, 0.02375, 0.02375)
        
    cube001 = duplicate_object("CUBE.001", "cube001", "Collection")
    if cube001:
        set_location(cube001, 0.076949, 0.550098, 3.63451)
        rotate_object(cube001, x_degrees=-137.333, y_degrees=0, z_degrees=0)
        resize_object(cube001, -0.020394, -0.043908, -0.020394)
        
    angle001 = duplicate_object("ANGLE.001", "angle001", "Collection")
    if angle001:
        set_location(angle001, -0.358202, 1.05752, 3.47314)
        rotate_object(angle001, x_degrees=40.1576, y_degrees=0, z_degrees=-180)
        resize_object(angle001, 0.022659, 0.022659, 0.022659)
        
    rotor001 = duplicate_object("ROTOR.001", "rotor001", "Collection")
    if rotor001:
        set_location(rotor001, -0.072524, 1.56643, 3.17345)
        rotate_object(rotor001, x_degrees=-145.664, y_degrees=-29.1768, z_degrees=35.5155)
        resize_object(rotor001, -0.019042, -0.019042, -0.019042)
        
    gripper = duplicate_object("GRIPPER", "gripper", "Collection")
    if gripper:
        set_location(gripper, -0.355968, 1.53367, 3.2287)
        rotate_object(gripper, x_degrees=214.081, y_degrees=0, z_degrees=0)
        resize_object(gripper, 0.021216, 0.021216, 0.021216)
        
    gripper001 = duplicate_object("GRIPPER.001", "gripper001", "Collection")
    if gripper001:
        set_location(gripper001, 0.215339, 1.59303, 3.16052)
        rotate_object(gripper001, x_degrees=-38.9312, y_degrees=0, z_degrees=180)
        resize_object(gripper001, 0.021216, 0.021216, 0.021216)