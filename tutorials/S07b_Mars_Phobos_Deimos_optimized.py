"""Tutorial script: S07_Mars_Phobos_Deimos — Optimized Render

To run this tutorial, you first need to put data in the input folder. 
You can download the tutorial data from:

https://drive.google.com/drive/folders/1K3e5MyQin6T9d_EXLG_gFywJt3I18r6H?usp=sharing
"""

# TODO: move the shading tree as a method in the Shading class instead
# TODO: coefficient loading from scene and not from a separate JSON (to avoid duplication)
# TODO: atmosphere loading standardized 

import sys
import os
sys.path.append(os.getcwd())
import cortopy as corto
import numpy as np

#TODO: libraries to remove: json, math, bpy (keep only if needed for optimized shader setup or atmosphere creation)
import json
import math
import bpy

## Clean all existing/Default objects in the scene 
corto.Utils.clean_scene()

### (1) DEFINE INPUT ### 
scenario_name = "S07_Mars_Phobos_Deimos" # Name of the scenario folder
scene_name = "scene_optimized.json" # name of the scene input
geometry_name = "geometry_optimized.json" # name of the geometry input
setup_fidelity = 'lowres' # "lowres" or "hires"

if setup_fidelity == 'lowres': # LOW-RES setup
    body_name = ["g_phobos_287m_spc_0000n00000_v002.obj",
                "Mars_65k.obj",
                "g_deimos_162m_spc_0000n00000_v001.obj"] # name of the body input
    # Load inputs and settings into the State object
    State = corto.State(scene = scene_name, geometry = geometry_name, body = body_name, scenario = scenario_name)
    # Add extra inputs 
    State.add_path('albedo_path_1',os.path.join(State.path["input_path"],'body','albedo','Phobos grayscale.jpg'))
    State.add_path('uv_data_path_1',os.path.join(State.path["input_path"],'body','uv data','g_phobos_287m_spc_0000n00000_v002.json'))
    State.add_path('albedo_path_2',os.path.join(State.path["input_path"],'body','albedo','Mars_MOC_f32.tif'))
    State.add_path('uv_data_path_2',os.path.join(State.path["input_path"],'body','uv data','Mars_65k.json'))
    State.add_path('displacement_path_2', os.path.join(State.path["input_path"], 'body', 'displacement', 'Mars_MOLA_DEM_f32.tif'))
    State.add_path('albedo_path_3',os.path.join(State.path["input_path"],'body','albedo','Deimos grayscale.jpg'))
    State.add_path('uv_data_path_3',os.path.join(State.path["input_path"],'body','uv data','g_deimos_162m_spc_0000n00000_v001.json'))
elif setup_fidelity == 'hires': # HIGH-RES setup (run at your own risk)
    body_name = ["g_phobos_018m_spc_0000n00000_v002.obj",
                "Mars_65k.obj",
                "g_deimos_020m_spc_0000n00000_v001.obj"] # name of the body input
    # Load inputs and settings into the State object
    State = corto.State(scene = scene_name, geometry = geometry_name, body = body_name, scenario = scenario_name)
    # Add extra inputs 
    State.add_path('albedo_path_1',os.path.join(State.path["input_path"],'body','albedo','Phobos grayscale.jpg'))
    State.add_path('uv_data_path_1',os.path.join(State.path["input_path"],'body','uv data','g_phobos_018m_spc_0000n00000_v002.json'))
    State.add_path('albedo_path_2',os.path.join(State.path["input_path"],'body','albedo','Mars_MOC_f32.tif'))
    State.add_path('uv_data_path_2',os.path.join(State.path["input_path"],'body','uv data','Mars_65k.json'))
    State.add_path('displacement_path_2', os.path.join(State.path["input_path"], 'body', 'displacement', 'Mars_MOLA_DEM_f32.tif'))
    State.add_path('albedo_path_3',os.path.join(State.path["input_path"],'body','albedo','Deimos grayscale.jpg'))
    State.add_path('uv_data_path_3',os.path.join(State.path["input_path"],'body','uv data','g_deimos_020m_spc_0000n00000_v001.json'))

### (2) SETUP THE SCENE ###
cam = corto.Camera('WFOV_Camera', State.properties_cam)
sun = corto.Sun('Sun', State.properties_sun)
name_1, _ = os.path.splitext(body_name[0])
name_2, _ = os.path.splitext(body_name[1])
name_3, _ = os.path.splitext(body_name[2])
body_1 = corto.Body(name_1, State.properties_body_1)
body_2 = corto.Body(name_2, State.properties_body_2)
body_3 = corto.Body(name_3, State.properties_body_3)
# Setup rendering engine
rendering_engine = corto.Rendering(State.properties_rendering)
# Setup environment
ENV = corto.Environment(cam, [body_1, body_2, body_3], sun, rendering_engine)

### (3) MATERIAL PROPERTIES ###
material_1 = corto.Shading.create_new_material('Phobos_Optimized')
material_2 = corto.Shading.create_new_material('Mars_Standard')
material_3 = corto.Shading.create_new_material('Deimos_Standard')

### --- Phobos --- ### # TODO: remove this and bring it into a method
corto.Shading.create_branch_albedo_mix(material_1, State, 1)

# Hybrid upgrade: intercept TexImage→Principled link, add RGBtoBW+Value+MixFloat
_tex1 = next(n for n in material_1.node_tree.nodes if n.bl_idname == 'ShaderNodeTexImage')
_dif1 = next(n for n in material_1.node_tree.nodes if n.bl_idname == 'ShaderNodeBsdfDiffuse')
_pri1 = next(n for n in material_1.node_tree.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled')
_mix1 = next(n for n in material_1.node_tree.nodes if n.bl_idname == 'ShaderNodeMixShader')
for link in list(material_1.node_tree.links):
    if link.from_node == _tex1 and link.to_node == _pri1:
        material_1.node_tree.links.remove(link)

_rgbbw1 = corto.Shading.create_node("ShaderNodeRGBToBW", material_1, (-300, 100))
_val1   = corto.Shading.create_node("ShaderNodeValue", material_1, (-300, -100))
_mixf1  = corto.Shading.create_node("ShaderNodeMix", material_1, (0, 0))
_mixf1.data_type = 'FLOAT'

corto.Shading.link_nodes(material_1, _tex1.outputs['Color'],   _rgbbw1.inputs['Color'])
corto.Shading.link_nodes(material_1, _rgbbw1.outputs['Val'],   _mixf1.inputs['A'])
corto.Shading.link_nodes(material_1, _val1.outputs['Value'],   _mixf1.inputs['B'])
corto.Shading.link_nodes(material_1, _mixf1.outputs['Result'], _dif1.inputs['Color'])
corto.Shading.link_nodes(material_1, _mixf1.outputs['Result'], _pri1.inputs['Base Color'])

# Apply optimized Phobos values from coefficients.json
p = State.properties_rendering['phobos_optimized_shader']
_val1.outputs[0].default_value = p['base_gray']
_mixf1.inputs['Factor'].default_value = p['tex_mix']
_dif1.inputs['Roughness'].default_value = p['oren_rough']
_pri1.inputs['Roughness'].default_value = p['princ_rough']
_pri1.inputs['IOR'].default_value = p['ior']
_mix1.inputs[0].default_value = p['shader_mix']

corto.Shading.load_uv_data(body_1, State, 1)
corto.Shading.assign_material_to_object(material_1, body_1)

### --- Mars (matching optimizer's node tree exactly) --- ###
if 'displacement_path_2' in State.path and os.path.exists(State.path['displacement_path_2']):
    _mars_settings = {
        'displacement': {'scale': 0.001, 'mid_level': 6690.0, 'colorspace_name': 'Non-Color'},
        'albedo': {'weight_diffuse': 0.95}
    }
    corto.Shading.create_branch_albedo_and_displacement_mix(material_2, State, settings=_mars_settings, id_body=2)
    material_2.cycles.displacement_method = 'BOTH'
    bpy.context.scene.cycles.feature_set = 'EXPERIMENTAL'
    bpy.context.scene.cycles.dicing_rate = 1.0
    _mars_obj = bpy.data.objects.get(name_2)
    if _mars_obj:
        _subsurf = _mars_obj.modifiers.new('Mars_Adaptive', 'SUBSURF')
        _subsurf.subdivision_type = 'SIMPLE'
        _subsurf.levels = 0
        _subsurf.render_levels = 0
    print("  Mars displacement enabled")
else:
    corto.Shading.create_branch_albedo_mix(material_2, State, 2)

# Fix albedo colorspace: CORTO defaults to sRGB, must be Non-Color
for _akey in ['albedo_path_2', 'albedo_path_3']:
    _img_name = os.path.basename(State.path.get(_akey, ''))
    if _img_name and _img_name in bpy.data.images:
        bpy.data.images[_img_name].colorspace_settings.name = 'Non-Color'
        print(f"  Albedo colorspace → Non-Color: {_img_name}")

# Mars hybrid shader upgrade (exact optimizer node tree)
_mars_nodes = material_2.node_tree.nodes
_mars_links = material_2.node_tree.links

_tex2 = next(n for n in _mars_nodes if n.bl_idname == 'ShaderNodeTexImage'
             and 'displacement' not in (n.image.name if n.image else '').lower())

# Remove old CORTO-generated shader nodes (Diffuse, MixShader, Principled)
_old_dif = next((n for n in _mars_nodes if n.bl_idname == 'ShaderNodeBsdfDiffuse'), None)
_old_mix = next((n for n in _mars_nodes if n.bl_idname == 'ShaderNodeMixShader'), None)
_old_pri = next((n for n in _mars_nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled'), None)
for _old in [_old_dif, _old_mix, _old_pri]:
    if _old:
        _mars_nodes.remove(_old)

# BrightContrast (mars_contrast — optimizer has this!)
_bc2 = _mars_nodes.new('ShaderNodeBrightContrast')
_bc2.location = (-450, 100)
_bc2.inputs['Contrast'].default_value = 0.4  # default, overridden below

# RGB→BW
_rgbbw2 = _mars_nodes.new('ShaderNodeRGBToBW')
_rgbbw2.location = (-300, 100)

# Value (mars_base_gray)
_val2 = _mars_nodes.new('ShaderNodeValue')
_val2.location = (-300, -100)
_val2.outputs['Value'].default_value = 0.15

# MixFloat (mars_tex_mix)
_mixf2 = _mars_nodes.new('ShaderNodeMix')
_mixf2.data_type = 'FLOAT'
_mixf2.location = (0, 0)
_mixf2.inputs['Factor'].default_value = 0.8

# Albedo multiplier (VectorMath MULTIPLY — optimizer has this!)
_mul2 = _mars_nodes.new('ShaderNodeVectorMath')
_mul2.operation = 'MULTIPLY'
_mul2.location = (200, 100)
_mul2.inputs[1].default_value = (1.0, 1.0, 1.0)  # set by mars_albedo_mul

# OrenNayar BSDF
_dif2 = corto.Shading.diffuse_BSDF(material_2, location=(450, 200))
_dif2.inputs['Roughness'].default_value = 0.9

# Principled BSDF
_pri2 = corto.Shading.principled_BSDF(material_2, location=(450, -200))
_pri2.inputs['Roughness'].default_value = 0.85
if 'IOR' in _pri2.inputs:
    _pri2.inputs['IOR'].default_value = 1.50
for _sp in ('Specular IOR Level', 'Specular'):
    if _sp in _pri2.inputs:
        _pri2.inputs[_sp].default_value = 0.50
        break
for _sl in ('Metallic', 'Clearcoat', 'Sheen', 'Coat Weight'):
    if _sl in _pri2.inputs:
        _pri2.inputs[_sl].default_value = 0.0

# MixShader (mars_shader_mix)
_mix2 = corto.Shading.mix_node(material_2, location=(700, 0))
_mix2.inputs[0].default_value = 0.1

# Find material output
_mat_out2 = next(n for n in _mars_nodes if n.bl_idname == 'ShaderNodeOutputMaterial')

# --- Link nodes (exact optimizer chain) ---
# Texture → BrightContrast → RGB→BW
_mars_links.new(_tex2.outputs['Color'], _bc2.inputs['Color'])
_mars_links.new(_bc2.outputs['Color'], _rgbbw2.inputs['Color'])
# RGB→BW → MixFloat.A
_mars_links.new(_rgbbw2.outputs['Val'], _mixf2.inputs['A'])
# Value → MixFloat.B
_mars_links.new(_val2.outputs['Value'], _mixf2.inputs['B'])
# MixFloat → Albedo multiplier
_mars_links.new(_mixf2.outputs['Result'], _mul2.inputs[0])
# Albedo multiplier → OrenNayar + Principled
_mars_links.new(_mul2.outputs['Vector'], _dif2.inputs['Color'])
_mars_links.new(_mul2.outputs['Vector'], _pri2.inputs['Base Color'])
# OrenNayar → MixShader.1, Principled → MixShader.2
_mars_links.new(_dif2.outputs['BSDF'], _mix2.inputs[1])
_mars_links.new(_pri2.outputs['BSDF'], _mix2.inputs[2])
# MixShader → Material Output (remove old surface link)
for _lnk in list(_mars_links):
    if _lnk.to_node == _mat_out2 and getattr(_lnk.to_socket, 'name', '') == 'Surface':
        _mars_links.remove(_lnk)
_mars_links.new(_mix2.outputs['Shader'], _mat_out2.inputs['Surface'])

# Apply optimized Mars values from coefficients.json
m = State.properties_rendering['mars_optimized_shader']
_val2.outputs[0].default_value = m['base_gray']
_mixf2.inputs['Factor'].default_value = m['tex_mix']
_dif2.inputs['Roughness'].default_value = m['oren_rough']
_pri2.inputs['Roughness'].default_value = m['princ_rough']
_pri2.inputs['IOR'].default_value = m['ior']
_mix2.inputs[0].default_value = m['shader_mix']
_bc2.inputs['Contrast'].default_value = m.get('contrast', 0.157)
_mul2.inputs[1].default_value = (m.get('albedo_mul', 4.282),) * 3

corto.Shading.load_uv_data(body_2, State, 2)
corto.Shading.assign_material_to_object(material_2, body_2)

### --- Deimos (standard CORTO) --- ###
corto.Shading.create_branch_albedo_mix(material_3, State, 3)
corto.Shading.load_uv_data(body_3, State, 3)
corto.Shading.assign_material_to_object(material_3, body_3)


### (4) COMPOSITING PROPERTIES ###

tree = corto.Compositing.create_compositing()
render_node = corto.Compositing.rendering_node(tree, (0, 0)) # Create Render node
corto.Compositing.create_img_denoise_branch(tree, render_node) # Create img_denoise branch
corto.Compositing.create_depth_branch(tree, render_node) # Create depth branch
corto.Compositing.create_slopes_branch(tree, render_node, State) # Create slopes branch
corto.Compositing.create_maskID_branch(tree, render_node, State) # Create ID mask branch

# ============================================================================
# (6) Atmosphere — Python only (helpers/atmosphere.py) # TODO: remove this
# ============================================================================
helpers_path = os.path.join(os.getcwd(), 'helpers')
if os.path.isdir(helpers_path):
    if helpers_path not in sys.path:
        sys.path.insert(0, helpers_path)
    try:
        from atmosphere import create_atmosphere
        a = State.properties_rendering['mars_atm_optimized_shader']

        create_atmosphere(
            name='Mars_Atmosphere',
            center_object=name_2,
            body_radius=3389.5,
            atmosphere_ratio=1.0177,
            beta0=a['beta0'],
            scale_height=a['scale_height'],
            anisotropy=a['anisotropy'],
            color=(a['color_r'], a['color_g'], a['color_b']),
        )
        print("  Mars atmosphere created")
    except Exception as e:
        print(f"  Atmosphere skipped: {e}")

# ============================================================================
# (7) Render quality overrides
# ============================================================================
cycles = bpy.context.scene.cycles
#TODO: move all of them into the scene_optimized settings. 
cycles.diffuse_bounces = 4
cycles.volume_bounces = 2
cycles.max_bounces = 8
cycles.glossy_bounces = 2
cycles.transparent_max_bounces = 8

### (5) GENERATION OF IMG-LBL PAIRS ###
body_1.set_scale(np.array([1, 1, 1]))
body_2.set_scale(np.array([1, 1, 1]))
body_3.set_scale(np.array([1, 1, 1]))




# Per-frame Sun energy (inverse-square law, matching optimizer pipeline)
AU_KM = 149597870.7
W_1AU = 427.815 # Solar irradiance at 1 AU in Blender units
SUN_BLENDER_SCALER = 1.0
geom = json.load(open(os.path.join('input', scenario_name, 'geometry', geometry_name)))
def sun_energy_for_frame(idx):
    """Calculate Sun lamp energy from Sun position (inverse-square law)."""
    sun_pos = np.array(geom['sun']['position'][idx])
    solar_dist_km = float(np.linalg.norm(sun_pos))
    dist_au = solar_dist_km / AU_KM if solar_dist_km > 0 else 1.0
    irradiance = W_1AU / (dist_au ** 2)
    return SUN_BLENDER_SCALER * irradiance

# OSIRIS NAC camera config (from mission_config.py)
OSIRIS_FOV_DEG = 2.0 * math.degrees(math.atan(27.648 / (2.0 * 712.4)))  # 2.2226 deg # TODO, bring it into config file of the scene
HRSC_FOV = cam.CAM_Blender.data.angle  # save original HRSC FOV #TODO: remove this and set it directly in the scene_optimized.json

# Import post-processor once (if enabled)
from post_processor_for_tutorial import post_process_single# TODO: remove?
tv = State.properties_rendering['threshold_value']
# COEFF.get('threshold_value', 0.000127)
print(f"Post-processing enabled: threshold={tv:.6f}")

n_img = 8 # 0-5: HRSC, 6-7: OSIRIS
for idx in range(0, n_img):
    if idx == 6:
        # Switch to OSIRIS NAC camera
        cam.CAM_Blender.data.angle = math.radians(OSIRIS_FOV_DEG)
        print(f"  Camera switched to OSIRIS NAC (FOV={OSIRIS_FOV_DEG:.4f} deg)")

    # Set Sun energy per frame (solar distance varies)
    energy = sun_energy_for_frame(idx)
    sun.set_energy(energy)

    ENV.PositionAll(State, index=idx)
    ENV.RenderOne(cam, State, index=idx, depth_flag=True)

    # Post-process immediately after render
    render_png = os.path.join(State.path['output_path'], 'img', f'{idx:06d}.png')
    processed_tif = os.path.join(State.path['output_path'], 'img', f'{idx:06d}_processed.tif')
    if os.path.exists(render_png):
        post_process_single(render_png, processed_tif, threshold_value=tv)
        print(f"  Post-processed: {idx:06d}.png -> {idx:06d}_processed.tif")

# Restore HRSC FOV
cam.CAM_Blender.data.angle = HRSC_FOV

corto.Utils.save_blend(State)
print("Done!")