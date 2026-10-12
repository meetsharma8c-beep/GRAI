#!/usr/bin/env python3
"""
Phase 1: Real Topography & Coastline Draping
Builds continuous SRTM 1-arc-second (30m) physical elevation terrain for the entire Mumbai peninsula.
Coordinates losslessly projected via TransverseMercator (lat=18.923, lon=72.833).
"""
def main():
    import bpy
    import gzip
    import struct
    import math
    import mathutils

    print(">>> Starting Phase 1: Real SRTM Topography Mesh Generation...")

    # 1. TransverseMercator projection matching blosm / scene
    class TransverseMercator:
        def __init__(self, lat=18.923, lon=72.833, k=1.0, radius=6378137.0):
            self.lat0 = math.radians(lat)
            self.lon0 = math.radians(lon)
            self.k = k
            self.radius = radius

        def fromGeographic(self, lat, lon):
            lat = math.radians(lat)
            lon = math.radians(lon)
            B = math.sin(lon - self.lon0) * math.cos(lat)
            x = 0.5 * self.k * self.radius * math.log((1.0 + B) / (1.0 - B))
            y = self.k * self.radius * (math.atan(math.tan(lat) / math.cos(lon - self.lon0)) - self.lat0)
            return x, y

        def toGeographic(self, x, y):
            D = y / (self.k * self.radius) + self.lat0
            x_norm = x / (self.k * self.radius)
            lat = math.asin(math.sin(D) / math.cosh(x_norm))
            dlon = math.atan(math.sinh(x_norm) / math.cos(D))
            lon = self.lon0 + dlon
            return math.degrees(lat), math.degrees(lon)

    tm = TransverseMercator()

    # 2. Read SRTM 30m dataset
    srtm_path = '/Users/ms/Downloads/blosm_assets/terrain/N18E072.hgt.gz'
    print(f"Reading SRTM DEM from {srtm_path}...")
    with gzip.open(srtm_path, 'rb') as f:
        raw_dem = f.read()

    def sample_srtm_raw(r, c):
        r = max(0, min(3600, r))
        c = max(0, min(3600, c))
        offset = (r * 3601 + c) * 2
        val = struct.unpack('>h', raw_dem[offset:offset+2])[0]
        return val

    def get_elevation_bilinear(lat, lon):
        if lat < 18.0 or lon < 72.0 or lon > 73.0:
            return 0.0
        
        # If north of 19.00 (e.g. Bandra/Mahim/Kurla), interpolate with row 0
        if lat >= 19.0:
            col_f = (lon - 72.0) * 3600.0
            c0 = int(math.floor(col_f))
            c1 = min(3600, c0 + 1)
            fc = col_f - c0
            val0 = sample_srtm_raw(0, c0)
            val1 = sample_srtm_raw(0, c1)
            base_val = (1.0 - fc) * val0 + fc * val1
            # Coastal alluvium in north Mumbai is ~3m to 6m
            over_lat = (lat - 19.0) / 0.1 # distance north
            taper = max(0.0, 1.0 - over_lat)
            elev = max(2.5, base_val * taper + 4.0 * (1.0 - taper))
            return max(0.0, elev)

        row_f = (19.0 - lat) * 3600.0
        col_f = (lon - 72.0) * 3600.0

        r0 = int(math.floor(row_f))
        r1 = min(3600, r0 + 1)
        c0 = int(math.floor(col_f))
        c1 = min(3600, c0 + 1)

        fr = row_f - r0
        fc = col_f - c0

        v00 = sample_srtm_raw(r0, c0)
        v01 = sample_srtm_raw(r0, c1)
        v10 = sample_srtm_raw(r1, c0)
        v11 = sample_srtm_raw(r1, c1)

        # Bilinear interpolation
        val = (1.0 - fr) * ((1.0 - fc) * v00 + fc * v01) + fr * ((1.0 - fc) * v10 + fc * v11)
        
        # If in ocean / negative, clamp cleanly
        if val <= 0:
            return -0.25
        return float(val)

    # 3. Define Peninsula Bounding Grid in World Meters
    # X: -5500 to +6500 (12,000m span)
    # Y: -5000 to +15000 (20,000m span)
    # Step: 50m
    x_min, x_max = -5500.0, 6500.0
    y_min, y_max = -5000.0, 15000.0
    step = 50.0

    xs = [x_min + i * step for i in range(int((x_max - x_min) / step) + 1)]
    ys = [y_min + j * step for j in range(int((y_max - y_min) / step) + 1)]

    nx = len(xs)
    ny = len(ys)
    print(f"Generating terrain mesh grid: {nx} x {ny} = {nx * ny} vertices ({nx-1}x{ny-1} quads)...")

    verts = []
    # Build vertices
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            lat, lon = tm.toGeographic(x, y)
            elev = get_elevation_bilinear(lat, lon)
            verts.append((x, y, elev))

    # Build quad faces
    faces = []
    for j in range(ny - 1):
        row_offset = j * nx
        next_row_offset = (j + 1) * nx
        for i in range(nx - 1):
            v0 = row_offset + i
            v1 = row_offset + (i + 1)
            v2 = next_row_offset + (i + 1)
            v3 = next_row_offset + i
            faces.append((v0, v1, v2, v3))

    print(f"Constructed {len(verts)} vertices and {len(faces)} quad polygons.")

    # 4. Create Blender Mesh Object
    mesh_name = "TERRAIN_SRTM_Mumbai_Peninsula_30M"
    if mesh_name in bpy.data.objects:
        old_obj = bpy.data.objects[mesh_name]
        bpy.data.objects.remove(old_obj, do_unlink=True)
    if mesh_name in bpy.data.meshes:
        bpy.data.meshes.remove(bpy.data.meshes[mesh_name])

    mesh_data = bpy.data.meshes.new(mesh_name)
    mesh_data.from_pydata(verts, [], faces)
    mesh_data.update()

    # Shade smooth
    for p in mesh_data.polygons:
        p.use_smooth = True

    terrain_obj = bpy.data.objects.new(mesh_name, mesh_data)

    # 5. Collection Management
    col_name = "GRAI_MUMBAI_MASTER_TERRAIN"
    if col_name not in bpy.data.collections:
        col = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(col)
    else:
        col = bpy.data.collections[col_name]

    col.objects.link(terrain_obj)

    # 6. High-Fidelity PBR Terrain Material
    mat_name = "MAT_Mumbai_Peninsula_SRTM_PBR"
    if mat_name in bpy.data.materials:
        mat = bpy.data.materials[mat_name]
    else:
        mat = bpy.data.materials.new(mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()

        out_node = nodes.new("ShaderNodeOutputMaterial")
        out_node.location = (600, 0)

        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.location = (300, 0)

        # Base color with color ramp based on elevation and noise
        tex_coord = nodes.new("ShaderNodeTexCoord")
        tex_coord.location = (-700, 0)

        sep_xyz = nodes.new("ShaderNodeSeparateXYZ")
        sep_xyz.location = (-500, -100)
        links.new(tex_coord.outputs['Object'], sep_xyz.inputs['Vector'])

        # Elevation Color Ramp
        # 0m -> Coastal shore / sand / basalt grey
        # 5m-20m -> City ground / asphalt tint
        # 25m-55m -> Malabar & Cumballa ridge lush tropical green
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.location = (-250, -100)
        # Normalize Z: 0m to 55m -> 0.0 to 1.0
        map_range = nodes.new("ShaderNodeMapRange")
        map_range.location = (-400, -100)
        map_range.inputs['From Min'].default_value = 0.0
        map_range.inputs['From Max'].default_value = 55.0
        map_range.inputs['To Min'].default_value = 0.0
        map_range.inputs['To Max'].default_value = 1.0
        links.new(sep_xyz.outputs['Z'], map_range.inputs['Value'])
        links.new(map_range.outputs['Result'], ramp.inputs['Fac'])

        # Ramp elements
        ramp.color_ramp.elements[0].position = 0.02
        ramp.color_ramp.elements[0].color = (0.24, 0.22, 0.20, 1.0) # Basalt / shore
        
        el1 = ramp.color_ramp.elements.new(0.15)
        el1.color = (0.32, 0.30, 0.28, 1.0) # City base

        el2 = ramp.color_ramp.elements.new(0.45)
        el2.color = (0.22, 0.32, 0.16, 1.0) # Ridge green

        ramp.color_ramp.elements[1].position = 1.0
        ramp.color_ramp.elements[1].color = (0.16, 0.28, 0.12, 1.0) # Lush hilltop canopy

        # Noise texture for natural detail variation
        noise = nodes.new("ShaderNodeTexNoise")
        noise.location = (-300, 200)
        noise.inputs['Scale'].default_value = 25.0
        noise.inputs['Detail'].default_value = 4.0
        noise.inputs['Roughness'].default_value = 0.6
        links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])

        mix_col = nodes.new("ShaderNodeMix")
        mix_col.data_type = 'RGBA'
        mix_col.location = (50, 50)
        mix_col.inputs['Factor'].default_value = 0.35
        links.new(ramp.outputs['Color'], mix_col.inputs[6])
        links.new(noise.outputs['Color'], mix_col.inputs[7])

        links.new(mix_col.outputs[2], bsdf.inputs['Base Color'])
        bsdf.inputs['Roughness'].default_value = 0.85
        bsdf.inputs['Specular IOR Level'].default_value = 0.2

        # Bump from noise
        bump = nodes.new("ShaderNodeBump")
        bump.location = (100, -200)
        bump.inputs['Strength'].default_value = 0.15
        bump.inputs['Distance'].default_value = 1.0
        links.new(noise.outputs['Fac'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

        links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])

    terrain_obj.data.materials.append(mat)

    # 7. Check and calibrate Arabian Sea water plane
    sea = bpy.data.objects.get("Arabian_Sea")
    if sea:
        # Move sea into GRAI_MUMBAI_MASTER_TERRAIN for clean organization
        for c in list(sea.users_collection):
            c.objects.unlink(sea)
        col.objects.link(sea)
        sea.location.z = -0.25 # Clean water line at -0.25m
        print(f"Aligned Arabian_Sea to collection {col_name} at z=-0.25m.")

    print(f">>> Phase 1 Complete! Generated real SRTM terrain mesh: {mesh_name} with {len(verts)} vertices.")

main()
