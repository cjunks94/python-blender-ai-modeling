import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Composite scene preview

# Object 1: Object 1 (sphere)
bpy.ops.mesh.primitive_uv_sphere_add(radius=2.0, location=(0.0, 1.5, 0.0))
# Apply material
mat = bpy.data.materials.new(name='Mat_0')
mat.use_nodes = True
bsdf = mat.node_tree.nodes['Principled BSDF']
bsdf.inputs['Base Color'].default_value = (0.7098039215686275, 0.7098039215686275, 0.7098039215686275, 1.0)
bsdf.inputs['Metallic'].default_value = 0.0
bsdf.inputs['Roughness'].default_value = 0.8
obj = bpy.context.active_object
if obj.data.materials:
    obj.data.materials[0] = mat
else:
    obj.data.materials.append(mat)

# Object 2: Object 2 (cylinder)
bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=3.0, location=(0.0, 3.0, 0.0))
# Apply material
mat = bpy.data.materials.new(name='Mat_1')
mat.use_nodes = True
bsdf = mat.node_tree.nodes['Principled BSDF']
bsdf.inputs['Base Color'].default_value = (0.10196078431372549, 0.10196078431372549, 0.10196078431372549, 1.0)
bsdf.inputs['Metallic'].default_value = 0.2
bsdf.inputs['Roughness'].default_value = 0.3
obj = bpy.context.active_object
if obj.data.materials:
    obj.data.materials[0] = mat
else:
    obj.data.materials.append(mat)

# Object 3: Object 3 (cube)
bpy.ops.mesh.primitive_cube_add(size=4.0, location=(0.0, -0.5, 0.0))
# Apply material
mat = bpy.data.materials.new(name='Mat_2')
mat.use_nodes = True
bsdf = mat.node_tree.nodes['Principled BSDF']
bsdf.inputs['Base Color'].default_value = (0.5450980392156862, 0.27058823529411763, 0.07450980392156863, 1.0)
bsdf.inputs['Metallic'].default_value = 0.0
bsdf.inputs['Roughness'].default_value = 0.7
obj = bpy.context.active_object
if obj.data.materials:
    obj.data.materials[0] = mat
else:
    obj.data.materials.append(mat)

# Object 4: Object 4 (cube)
bpy.ops.mesh.primitive_cube_add(size=0.5, location=(0.0, 1.2, 1.0))
bpy.context.object.rotation_euler = (0.0, 0.7853981633974483, 0.0)
# Apply material
mat = bpy.data.materials.new(name='Mat_3')
mat.use_nodes = True
bsdf = mat.node_tree.nodes['Principled BSDF']
bsdf.inputs['Base Color'].default_value = (1.0, 0.0, 0.0, 1.0)
bsdf.inputs['Metallic'].default_value = 0.1
bsdf.inputs['Roughness'].default_value = 0.5
obj = bpy.context.active_object
if obj.data.materials:
    obj.data.materials[0] = mat
else:
    obj.data.materials.append(mat)

# Object 5: Object 5 (sphere)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(3.0, 5.0, 3.0))
# Apply material
mat = bpy.data.materials.new(name='Mat_4')
mat.use_nodes = True
bsdf = mat.node_tree.nodes['Principled BSDF']
bsdf.inputs['Base Color'].default_value = (1.0, 1.0, 1.0, 1.0)
bsdf.inputs['Metallic'].default_value = 0.0
bsdf.inputs['Roughness'].default_value = 0.0
bsdf.inputs['Emission Strength'].default_value = 5.0
obj = bpy.context.active_object
if obj.data.materials:
    obj.data.materials[0] = mat
else:
    obj.data.materials.append(mat)

# Set up camera for scene view
if 'Camera' not in bpy.data.objects:
    bpy.ops.object.camera_add(location=(7, -7, 5))
camera = bpy.data.objects['Camera']
camera.location = (7, -7, 5)
camera.rotation_euler = (1.1, 0, 0.785)  # Point at scene center
    
# Set up lighting
if 'Light' not in bpy.data.objects:
    bpy.ops.object.light_add(type='SUN', location=(4, -4, 6))
light = bpy.data.objects['Light']
light.location = (4, -4, 6)
light.data.energy = 3.0

# Set render settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 32

# Save the file
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

print("Composite scene generated successfully")
