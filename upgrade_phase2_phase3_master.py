#!/usr/bin/env python3
"""
GRAI Mumbai Digital Twin — Phase 2 & Phase 3 Master Execution
1. Populates and unifies authoritative OSM building footprints into GRAI_MUMBAI_MASTER_BUILDINGS.
2. Drapes all 7 polygonal road networks onto the real SRTM 30m terrain elevation.
3. Upgrades Mat_Asphalt_Road and Mat_Mumbai_Building_Facade to photorealistic PBR shaders.
4. Organizes master collections: GRAI_MUMBAI_MASTER_BUILDINGS, GRAI_MUMBAI_MASTER_ROADS, GRAI_MUMBAI_MASTER_LANDMARKS.
"""
def main():
    import bpy
    import gzip
    import struct
    import math
    import mathutils

    print(">>> Starting Phase 2 & 3: Authoritative Buildings & Road Network Draping...")

    # -------------------------------------------------------------
    # 1. TransverseMercator Projection & SRTM Elevation Sampler
    # -------------------------------------------------------------
    class TransverseMercator:
        def __init__(self, lat=18.923, lon=72.833, k=1.0, radius=6378137.0):
            self.lat0 = math.radians(lat)
            self.lon0 = math.radians(lon)
            self.k = k
            self.radius = radius

        def toGeographic(self, x, y):
            D = y / (self.k * self.radius) + self.lat0
            x_norm = x / (self.k * self.radius)
            lat = math.asin(math.sin(D) / math.cosh(x_norm))
            dlon = math.atan(math.sinh(x_norm) / math.cos(D))
            lon = self.lon0 + dlon
            return math.degrees(lat), math.degrees(lon)

    tm = TransverseMercator()

    with gzip.open('/Users/ms/Downloads/blosm_assets/terrain/N18E072.hgt.gz', 'rb') as f:
        raw_dem = f.read()

    def get_elevation_bilinear(lat, lon):
        if lat < 18.0 or lon < 72.0 or lon > 73.0:
            return 0.0
        if lat >= 19.0:
            col_f = (lon - 72.0) * 3600.0
            c0 = max(0, min(3600, int(math.floor(col_f))))
            c1 = min(3600, c0 + 1)
            fc = col_f - c0
            val0 = struct.unpack('>h', raw_dem[c0*2 : c0*2+2])[0]
            val1 = struct.unpack('>h', raw_dem[c1*2 : c1*2+2])[0]
            base_val = (1.0 - fc) * val0 + fc * val1
            return max(2.5, base_val)

        row_f = (19.0 - lat) * 3600.0
        col_f = (lon - 72.0) * 3600.0
        r0 = max(0, min(3600, int(math.floor(row_f))))
        r1 = min(3600, r0 + 1)
        c0 = max(0, min(3600, int(math.floor(col_f))))
        c1 = min(3600, c0 + 1)
        fr = row_f - r0
        fc = col_f - c0

        off00 = (r0 * 3601 + c0) * 2
        off01 = (r0 * 3601 + c1) * 2
        off10 = (r1 * 3601 + c0) * 2
        off11 = (r1 * 3601 + c1) * 2

        v00 = struct.unpack('>h', raw_dem[off00:off00+2])[0]
        v01 = struct.unpack('>h', raw_dem[off01:off01+2])[0]
        v10 = struct.unpack('>h', raw_dem[off10:off10+2])[0]
        v11 = struct.unpack('>h', raw_dem[off11:off11+2])[0]

        val = (1.0 - fr) * ((1.0 - fc) * v00 + fc * v01) + fr * ((1.0 - fc) * v10 + fc * v11)
        return max(0.0, float(val))

    # Helper: get or create collection
    def get_or_create_col(name, parent_col=None):
        if name in bpy.data.collections:
            return bpy.data.collections[name]
        col = bpy.data.collections.new(name)
        if parent_col:
            parent_col.children.link(col)
        else:
            bpy.context.scene.collection.children.link(col)
        return col

    # -------------------------------------------------------------
    # 2. Phase 2: Building Footprint Consolidation & Shader Upgrade
    # -------------------------------------------------------------
    col_master_bldgs = get_or_create_col("GRAI_MUMBAI_MASTER_BUILDINGS")

    # Link authoritative Colaba buildings
    auth_bldgs = bpy.data.objects.get("SECTOR_A_Authoritative_Colaba_Buildings")
    if auth_bldgs:
        if auth_bldgs.name not in col_master_bldgs.objects:
            col_master_bldgs.objects.link(auth_bldgs)
        print("Linked SECTOR_A_Authoritative_Colaba_Buildings to GRAI_MUMBAI_MASTER_BUILDINGS.")

    # Link raw OSM Colaba buildings
    osm_bldgs = bpy.data.objects.get("mumbai_colaba.osm_buildings")
    if osm_bldgs:
        if osm_bldgs.name not in col_master_bldgs.objects:
            col_master_bldgs.objects.link(osm_bldgs)
        print("Linked mumbai_colaba.osm_buildings to GRAI_MUMBAI_MASTER_BUILDINGS.")

    # Upgrade Mat_Mumbai_Building_Facade with procedural architectural fenestration
    mat_facade = bpy.data.materials.get("Mat_Mumbai_Building_Facade")
    if mat_facade:
        mat_facade.use_nodes = True
        nodes = mat_facade.node_tree.nodes
        links = mat_facade.node_tree.links
        nodes.clear()

        out_node = nodes.new("ShaderNodeOutputMaterial")
        out_node.location = (600, 0)

        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.location = (300, 0)

        tex_coord = nodes.new("ShaderNodeTexCoord")
        tex_coord.location = (-600, 0)

        # Brick texture for window fenestration
        brick = nodes.new("ShaderNodeTexBrick")
        brick.location = (-300, 100)
        brick.inputs['Scale'].default_value = 14.0
        brick.inputs['Mortar Size'].default_value = 0.09
        brick.inputs['Bias'].default_value = -0.2
        brick.inputs['Color1'].default_value = (0.16, 0.22, 0.28, 1.0) # Reflective window pane
        brick.inputs['Color2'].default_value = (0.20, 0.26, 0.32, 1.0)
        brick.inputs['Mortar'].default_value = (0.68, 0.62, 0.54, 1.0) # Malad sandstone / limestone facade

        links.new(tex_coord.outputs['Object'], brick.inputs['Vector'])
        links.new(brick.outputs['Color'], bsdf.inputs['Base Color'])

        # Roughness: high for stone mortar, low for glass windows
        mix_rough = nodes.new("ShaderNodeMix")
        mix_rough.data_type = 'FLOAT'
        mix_rough.location = (50, -100)
        mix_rough.inputs[2].default_value = 0.85 # Stone roughness
        mix_rough.inputs[3].default_value = 0.15 # Glass roughness
        links.new(brick.outputs['Fac'], mix_rough.inputs['Factor'])
        links.new(mix_rough.outputs[0], bsdf.inputs['Roughness'])

        # Subtle metallic for window reflection
        mix_met = nodes.new("ShaderNodeMix")
        mix_met.data_type = 'FLOAT'
        mix_met.location = (50, -250)
        mix_met.inputs[2].default_value = 0.0
        mix_met.inputs[3].default_value = 0.65
        links.new(brick.outputs['Fac'], mix_met.inputs['Factor'])
        links.new(mix_met.outputs[0], bsdf.inputs['Metallic'])

        # Bump map for mortar masonry relief
        bump = nodes.new("ShaderNodeBump")
        bump.location = (100, 150)
        bump.inputs['Strength'].default_value = 0.25
        bump.inputs['Distance'].default_value = 0.5
        links.new(brick.outputs['Fac'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

        links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])
        print("Upgraded Mat_Mumbai_Building_Facade with architectural window fenestration.")

    # -------------------------------------------------------------
    # 3. Phase 3: Road Network Draping onto SRTM 30m Elevation Grid
    # -------------------------------------------------------------
    col_master_roads = get_or_create_col("GRAI_MUMBAI_MASTER_ROADS")

    road_mesh_names = [
        "MESH_roads_motorway",
        "MESH_roads_trunk",
        "MESH_roads_primary",
        "MESH_roads_secondary",
        "MESH_roads_tertiary",
        "MESH_roads_residential",
        "MESH_roads_service"
    ]

    total_draped_verts = 0
    for r_name in road_mesh_names:
        r_obj = bpy.data.objects.get(r_name)
        if not r_obj:
            continue

        if r_obj.name not in col_master_roads.objects:
            col_master_roads.objects.link(r_obj)

        mesh = r_obj.data
        mw = r_obj.matrix_world
        inv_mw = mw.inverted()

        for v in mesh.vertices:
            w_co = mw @ v.co
            lat, lon = tm.toGeographic(w_co.x, w_co.y)
            elev = get_elevation_bilinear(lat, lon)
            # Elevate road 0.25m above terrain for crisp rendering without z-fighting
            target_z = max(0.35, elev + 0.25)
            w_new = mathutils.Vector((w_co.x, w_co.y, target_z))
            v.co = inv_mw @ w_new

        mesh.update()
        total_draped_verts += len(mesh.vertices)
        print(f"Draped {r_name} ({len(mesh.vertices)} verts) to physical SRTM terrain.")

    print(f"Completed road draping: {total_draped_verts} vertices successfully draped.")

    # -------------------------------------------------------------
    # 4. Photorealistic PBR Asphalt Shader Upgrade
    # -------------------------------------------------------------
    mat_asphalt = bpy.data.materials.get("Mat_Asphalt_Road")
    if mat_asphalt:
        mat_asphalt.use_nodes = True
        nodes = mat_asphalt.node_tree.nodes
        links = mat_asphalt.node_tree.links
        nodes.clear()

        out_node = nodes.new("ShaderNodeOutputMaterial")
        out_node.location = (600, 0)

        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.location = (300, 0)

        tex_coord = nodes.new("ShaderNodeTexCoord")
        tex_coord.location = (-700, 0)

        # Micro-asphalt aggregate noise
        noise_micro = nodes.new("ShaderNodeTexNoise")
        noise_micro.location = (-400, 150)
        noise_micro.inputs['Scale'].default_value = 180.0
        noise_micro.inputs['Detail'].default_value = 6.0
        noise_micro.inputs['Roughness'].default_value = 0.75
        links.new(tex_coord.outputs['Object'], noise_micro.inputs['Vector'])

        # Macro road wear & tire tracks noise
        noise_macro = nodes.new("ShaderNodeTexNoise")
        noise_macro.location = (-400, -150)
        noise_macro.inputs['Scale'].default_value = 8.0
        noise_macro.inputs['Detail'].default_value = 3.0
        noise_macro.inputs['Roughness'].default_value = 0.5
        links.new(tex_coord.outputs['Object'], noise_macro.inputs['Vector'])

        # Mix asphalt dark tones
        # Bitumen fresh: (0.08, 0.08, 0.09)
        # Weathered coastal asphalt: (0.16, 0.16, 0.17)
        color_ramp = nodes.new("ShaderNodeValToRGB")
        color_ramp.location = (-150, 150)
        color_ramp.color_ramp.elements[0].position = 0.2
        color_ramp.color_ramp.elements[0].color = (0.08, 0.08, 0.09, 1.0)
        color_ramp.color_ramp.elements[1].position = 0.8
        color_ramp.color_ramp.elements[1].color = (0.17, 0.17, 0.18, 1.0)
        links.new(noise_micro.outputs['Fac'], color_ramp.inputs['Fac'])
        links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])

        # Roughness variation from macro noise
        map_rough = nodes.new("ShaderNodeMapRange")
        map_rough.location = (-150, -150)
        map_rough.inputs['From Min'].default_value = 0.2
        map_rough.inputs['From Max'].default_value = 0.8
        map_rough.inputs['To Min'].default_value = 0.68
        map_rough.inputs['To Max'].default_value = 0.88
        links.new(noise_macro.outputs['Fac'], map_rough.inputs['Value'])
        links.new(map_rough.outputs['Result'], bsdf.inputs['Roughness'])

        # Bump from micro noise
        bump = nodes.new("ShaderNodeBump")
        bump.location = (50, -300)
        bump.inputs['Strength'].default_value = 0.12
        bump.inputs['Distance'].default_value = 0.1
        links.new(noise_micro.outputs['Fac'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

        bsdf.inputs['Specular IOR Level'].default_value = 0.35
        links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])
        print("Upgraded Mat_Asphalt_Road with photorealistic coastal asphalt PBR.")

    # -------------------------------------------------------------
    # 5. Master Landmarks Collection Consolidation
    # -------------------------------------------------------------
    col_master_landmarks = get_or_create_col("GRAI_MUMBAI_MASTER_LANDMARKS")
    landmark_names = [
        "LANDMARK_Gateway_of_India",
        "LANDMARK_Taj_Mahal_Palace",
        "LANDMARK_CSMT_GrandFacade",
        "LANDMARK_CSMT_CentralDome",
        "LANDMARK_BSE_PhirozeTowers"
    ]
    for lm_name in landmark_names:
        lm_obj = bpy.data.objects.get(lm_name)
        if lm_obj and lm_obj.name not in col_master_landmarks.objects:
            col_master_landmarks.objects.link(lm_obj)
            print(f"Linked {lm_name} to GRAI_MUMBAI_MASTER_LANDMARKS.")

    # Sea Link objects
    sealink_deck = bpy.data.objects.get("SEALINK_RoadDeck_8Lanes")
    if sealink_deck and sealink_deck.name not in col_master_landmarks.objects:
        col_master_landmarks.objects.link(sealink_deck)

    print(">>> Phase 2 & 3 Execution Complete!")

main()
