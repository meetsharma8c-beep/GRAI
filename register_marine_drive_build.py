"""
GRAI — DEFINITIVE SCANNED DETAILING MASTER FOR MARINE DRIVE & QUEEN'S NECKLACE
Wrapped in bpy.app.timers for non-blocking execution.
"""

def register_marine_drive_build():
    import bpy

    def build_job():
        import bpy
        import bmesh
        import math
        import random
        from mathutils import Vector, Matrix, Euler

        print("Executing Marine Drive Masterpiece build job...")

        def get_col(name):
            col = bpy.data.collections.get(name)
            if not col:
                col = bpy.data.collections.new(name)
                bpy.context.scene.collection.children.link(col)
            return col

        col_props = get_col("Playable_Street_Props")
        col_tetrapods = get_col("Coastline_Marine_Tetrapods")
        col_curbs = get_col("Road_BMC_Curb_Stones")
        col_artdeco = get_col("MarineDrive_ArtDeco_Mansions")
        col_bldg = get_col("Sector_B_MarineDrive_NarimanPoint")

        # 1. CLEAN STRAY ROAD RIBBONS IN BACK BAY
        for r_name in ["MESH_roads_primary", "MESH_roads_secondary", "MESH_roads_tertiary", "MESH_roads_residential", "MESH_roads_service"]:
            r_obj = bpy.data.objects.get(r_name)
            if r_obj and r_obj.type == 'MESH':
                bm_r = bmesh.new()
                bm_r.from_mesh(r_obj.data)
                bm_r.faces.ensure_lookup_table()
                del_f = []
                for f in bm_r.faces:
                    fc = r_obj.matrix_world @ f.calc_center_median()
                    if fc.x < -1080.0 and 100.0 < fc.y < 2600.0:
                        del_f.append(f)
                if del_f:
                    bmesh.ops.delete(bm_r, geom=del_f, context='FACES_ONLY')
                    bm_r.to_mesh(r_obj.data)
                    r_obj.data.update()
                bm_r.free()

        # 2. SEAWALL CURVE LOOKUP
        sw_curve = [
            (0.0, -1300.0), (200.0, -1200.0), (400.0, -1140.0), (600.0, -1090.0),
            (800.0, -1060.0), (1000.0, -1035.0), (1200.0, -1010.0), (1400.0, -990.0),
            (1600.0, -975.0), (1800.0, -960.0), (2000.0, -945.0), (2200.0, -930.0),
            (2400.0, -920.0), (2600.0, -910.0), (2800.0, -905.0), (3000.0, -905.0)
        ]
        def get_sw_x(y):
            if y <= sw_curve[0][0]: return sw_curve[0][1]
            if y >= sw_curve[-1][0]: return sw_curve[-1][1]
            for i in range(len(sw_curve) - 1):
                y1, x1 = sw_curve[i]
                y2, x2 = sw_curve[i + 1]
                if y1 <= y <= y2:
                    t = (y - y1) / (y2 - y1)
                    return x1 + t * (x2 - x1)
            return -1000.0

        terrain = bpy.data.objects.get("TERRAIN_SRTM_Mumbai_Peninsula_30M")
        
        # Fast elevation lookup table by sampling once per 50m Y
        elev_cache = {}
        def get_elev(y):
            y_key = int(y / 50.0) * 50
            if y_key not in elev_cache:
                if terrain:
                    mw = terrain.matrix_world
                    imw = mw.inverted()
                    tx = get_sw_x(float(y_key)) + 15.0
                    orig = imw @ Vector((tx, float(y_key), 100.0))
                    dir_vec = imw.to_3x3() @ Vector((0, 0, -1.0))
                    hit, loc, norm, idx = terrain.ray_cast(orig, dir_vec)
                    if hit:
                        elev_cache[y_key] = (mw @ loc).z
                    else:
                        elev_cache[y_key] = 6.0
                else:
                    elev_cache[y_key] = 6.0
            return elev_cache[y_key]

        # 3. PBR MATERIALS FOR ROAD, CURBS, PROMENADE & TETRAPODS
        mat_curb_yellow = bpy.data.materials.get("MAT_BMC_Curb_Yellow")
        if not mat_curb_yellow:
            mat_curb_yellow = bpy.data.materials.new("MAT_BMC_Curb_Yellow")
            mat_curb_yellow.use_nodes = True
        cy_bsdf = mat_curb_yellow.node_tree.nodes.get("Principled BSDF")
        if cy_bsdf:
            cy_bsdf.inputs['Base Color'].default_value = (0.96, 0.78, 0.08, 1.0)
            cy_bsdf.inputs['Roughness'].default_value = 0.70

        mat_curb_black = bpy.data.materials.get("MAT_BMC_Curb_Black")
        if not mat_curb_black:
            mat_curb_black = bpy.data.materials.new("MAT_BMC_Curb_Black")
            mat_curb_black.use_nodes = True
        cb_bsdf = mat_curb_black.node_tree.nodes.get("Principled BSDF")
        if cb_bsdf:
            cb_bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.06, 1.0)
            cb_bsdf.inputs['Roughness'].default_value = 0.75

        mat_road_marked = bpy.data.materials.get("MAT_MarineDrive_Asphalt_Striped")
        if not mat_road_marked:
            mat_road_marked = bpy.data.materials.new("MAT_MarineDrive_Asphalt_Striped")
            mat_road_marked.use_nodes = True
            n_rd = mat_road_marked.node_tree.nodes
            l_rd = mat_road_marked.node_tree.links
            n_rd.clear()
            out_rd = n_rd.new("ShaderNodeOutputMaterial")
            bsdf_rd = n_rd.new("ShaderNodeBsdfPrincipled")
            l_rd.new(bsdf_rd.outputs['BSDF'], out_rd.inputs['Surface'])
            bsdf_rd.inputs['Base Color'].default_value = (0.12, 0.13, 0.14, 1.0)
            bsdf_rd.inputs['Roughness'].default_value = 0.72

        mat_prom_stone = bpy.data.materials.get("MAT_MarineDrive_Promenade_Pavers")
        if not mat_prom_stone:
            mat_prom_stone = bpy.data.materials.new("MAT_MarineDrive_Promenade_Pavers")
            mat_prom_stone.use_nodes = True
            np = mat_prom_stone.node_tree.nodes
            lp = mat_prom_stone.node_tree.links
            np.clear()
            out_p = np.new("ShaderNodeOutputMaterial")
            bsdf_p = np.new("ShaderNodeBsdfPrincipled")
            lp.new(bsdf_p.outputs['BSDF'], out_p.inputs['Surface'])
            bsdf_p.inputs['Base Color'].default_value = (0.45, 0.38, 0.34, 1.0)
            bsdf_p.inputs['Roughness'].default_value = 0.65

        # 4. REBUILD DRAPED ROAD, PROMENADE & SEAWALL
        for old_n in ["ROAD_MarineDrive_NetajiSubhashRoad", "PROMENADE_MarineDrive_QueensNecklace", "SEAWALL_MarineDrive_Barrier"]:
            old_o = bpy.data.objects.get(old_n)
            if old_o:
                bpy.data.objects.remove(old_o, do_unlink=True)

        for o in list(bpy.data.objects):
            if o.name.startswith("BMC_Curb_MD_") or o.name.startswith("TETRA_MarineDrive_") or o.name.startswith("VEHICLE_MD_"):
                bpy.data.objects.remove(o, do_unlink=True)

        rd_mesh = bpy.data.meshes.new("ROAD_MarineDrive_NetajiSubhashRoad_Mesh")
        rd_obj = bpy.data.objects.new("ROAD_MarineDrive_NetajiSubhashRoad", rd_mesh)
        col_bldg.objects.link(rd_obj)
        bm_rd = bmesh.new()

        pr_mesh = bpy.data.meshes.new("PROMENADE_MarineDrive_QueensNecklace_Mesh")
        pr_obj = bpy.data.objects.new("PROMENADE_MarineDrive_QueensNecklace", pr_mesh)
        col_bldg.objects.link(pr_obj)
        bm_pr = bmesh.new()

        sw_mesh = bpy.data.meshes.new("SEAWALL_MarineDrive_Barrier_Mesh")
        sw_obj = bpy.data.objects.new("SEAWALL_MarineDrive_Barrier", sw_mesh)
        col_bldg.objects.link(sw_obj)
        bm_sw = bmesh.new()

        y_steps = 100
        for i in range(y_steps):
            y1 = 100.0 + (i / float(y_steps)) * 2400.0
            y2 = 100.0 + ((i + 1) / float(y_steps)) * 2400.0
            
            sw_x1 = get_sw_x(y1)
            sw_x2 = get_sw_x(y2)
            
            z1 = get_elev(y1)
            z2 = get_elev(y2)

            # Seawall
            sw_v1 = bm_sw.verts.new(Vector((sw_x1 - 0.4, y1, z1 + 1.2)))
            sw_v2 = bm_sw.verts.new(Vector((sw_x1 + 0.4, y1, z1 + 1.2)))
            sw_v3 = bm_sw.verts.new(Vector((sw_x2 + 0.4, y2, z2 + 1.2)))
            sw_v4 = bm_sw.verts.new(Vector((sw_x2 - 0.4, y2, z2 + 1.2)))
            bm_sw.faces.new((sw_v1, sw_v2, sw_v3, sw_v4))

            # Promenade
            pr_v1 = bm_pr.verts.new(Vector((sw_x1 + 0.4, y1, z1 + 0.30)))
            pr_v2 = bm_pr.verts.new(Vector((sw_x1 + 12.0, y1, z1 + 0.30)))
            pr_v3 = bm_pr.verts.new(Vector((sw_x2 + 12.0, y2, z2 + 0.30)))
            pr_v4 = bm_pr.verts.new(Vector((sw_x2 + 0.4, y2, z2 + 0.30)))
            bm_pr.faces.new((pr_v1, pr_v2, pr_v3, pr_v4))

            # Road
            rd_v1 = bm_rd.verts.new(Vector((sw_x1 + 12.0, y1, z1 + 0.18)))
            rd_v2 = bm_rd.verts.new(Vector((sw_x1 + 40.0, y1, z1 + 0.18)))
            rd_v3 = bm_rd.verts.new(Vector((sw_x2 + 40.0, y2, z2 + 0.18)))
            rd_v4 = bm_rd.verts.new(Vector((sw_x2 + 12.0, y2, z2 + 0.18)))
            bm_rd.faces.new((rd_v1, rd_v2, rd_v3, rd_v4))

        bm_rd.to_mesh(rd_mesh)
        bm_pr.to_mesh(pr_mesh)
        bm_sw.to_mesh(sw_mesh)
        bm_rd.free(); bm_pr.free(); bm_sw.free()

        rd_obj.data.materials.append(mat_road_marked)
        pr_obj.data.materials.append(mat_prom_stone)
        
        mat_sw_concrete = bpy.data.materials.get("MAT_MarineDrive_SeawallConcrete")
        if mat_sw_concrete:
            sw_obj.data.materials.append(mat_sw_concrete)

        # 5. BMC CURB STONES
        curb_mesh = bpy.data.meshes.new("BMC_Curb_Stone_Unit_Mesh")
        bm_cb = bmesh.new()
        bmesh.ops.create_cube(bm_cb, size=1.0, matrix=Matrix.Diagonal(Vector((0.45, 1.2, 0.32, 1.0))))
        bm_cb.to_mesh(curb_mesh)
        bm_cb.free()

        for c_idx in range(100):
            c_y = 600.0 + c_idx * 8.0
            c_x = get_sw_x(c_y) + 12.0
            c_z = get_elev(c_y) + 0.34
            
            c_obj = bpy.data.objects.new(f"BMC_Curb_MD_{c_idx}", curb_mesh)
            col_curbs.objects.link(c_obj)
            c_obj.location = Vector((c_x, c_y, c_z))
            
            if c_idx % 2 == 0:
                c_obj.data.materials.append(mat_curb_yellow)
            else:
                c_obj.data.materials.append(mat_curb_black)

        # 6. TETRAPODS ALONG SEAWALL
        tetra_master = bpy.data.meshes.get("Tetrapod_Master_Core_Mesh")
        mat_tetra = bpy.data.materials.get("MAT_Concrete_Tetrapod_Marine")
        if tetra_master and mat_tetra:
            random.seed(101)
            for t_step in range(60):
                t_y = 600.0 + t_step * 20.0
                sw_x = get_sw_x(t_y)
                for row in range(3):
                    t_x = sw_x - 1.8 - row * 2.8 + random.uniform(-0.5, 0.5)
                    t_z = 0.3 + row * 0.45 + random.uniform(-0.2, 0.2)
                    
                    t_obj = bpy.data.objects.new(f"TETRA_MarineDrive_{t_step}_{row}", tetra_master)
                    col_tetrapods.objects.link(t_obj)
                    t_obj.location = Vector((t_x, t_y, t_z))
                    t_obj.rotation_euler = Euler((random.uniform(0, 6.28), random.uniform(0, 6.28), random.uniform(0, 6.28)), 'XYZ')
                    t_obj.scale = Vector((1.3, 1.3, 1.3))
                    t_obj.data.materials.append(mat_tetra)

        # 7. ART DECO BUILDINGS WITH STREAMLINE CURVED BALCONIES
        artdeco_names = [
            ("ARTDECO_MarineDrive_Kapoor_Mahal", "MAT_ArtDeco_CreamIvory", -985.0, 750.0, 32.0),
            ("ARTDECO_MarineDrive_Zaver_Mahal", "MAT_ArtDeco_SeafoamGreen", -975.0, 850.0, 34.0),
            ("ARTDECO_MarineDrive_Keval_Mahal", "MAT_ArtDeco_MaladOchre", -965.0, 950.0, 35.0),
            ("ARTDECO_MarineDrive_Soona_Mahal", "MAT_ArtDeco_PalePeach", -955.0, 1050.0, 36.0),
            ("ARTDECO_MarineDrive_Empress_Court", "MAT_ArtDeco_CreamIvory", -945.0, 1150.0, 33.0),
            ("ARTDECO_MarineDrive_Shiv_Shanti_Bhuvan", "MAT_ArtDeco_MaladOchre", -935.0, 1250.0, 35.0),
        ]
        for name, mat_name, ax, ay, ah in artdeco_names:
            old_ad = bpy.data.objects.get(name)
            if old_ad:
                bpy.data.objects.remove(old_ad, do_unlink=True)

            ad_mesh = bpy.data.meshes.new(f"{name}_Mesh")
            ad_obj = bpy.data.objects.new(name, ad_mesh)
            col_artdeco.objects.link(ad_obj)
            
            gz = get_elev(ay)
            ad_obj.location = Vector((ax, ay, gz))

            bm_ad = bmesh.new()
            bmesh.ops.create_cube(bm_ad, size=1.0, matrix=Matrix.Translation(Vector((0, 0, ah / 2.0))) @ Matrix.Diagonal(Vector((24.0, 32.0, ah, 1.0))))
            floors = int(ah / 3.8)
            for fl in range(1, floors):
                fz = fl * 3.8
                bmesh.ops.create_cube(bm_ad, size=1.0, matrix=Matrix.Translation(Vector((-13.5, 0, fz))) @ Matrix.Diagonal(Vector((3.0, 26.0, 0.45, 1.0))))
                for s_line in range(3):
                    lz = fz + 0.35 + s_line * 0.28
                    bmesh.ops.create_cube(bm_ad, size=1.0, matrix=Matrix.Translation(Vector((-14.9, 0, lz))) @ Matrix.Diagonal(Vector((0.15, 26.0, 0.12, 1.0))))
                bmesh.ops.create_cube(bm_ad, size=1.0, matrix=Matrix.Translation(Vector((-13.8, 0, fz + 2.8))) @ Matrix.Diagonal(Vector((2.2, 28.0, 0.20, 1.0))))

            bmesh.ops.create_cube(bm_ad, size=1.0, matrix=Matrix.Translation(Vector((2.0, 0, ah + 2.5))) @ Matrix.Diagonal(Vector((8.0, 10.0, 5.0, 1.0))))
            for tx_i in [-4.0, 4.0]:
                bmesh.ops.create_cone(bm_ad, cap_ends=True, cap_tris=False, segments=12, radius1=1.2, radius2=1.2, depth=2.4, matrix=Matrix.Translation(Vector((tx_i, 8.0, ah + 1.2))))

            bm_ad.to_mesh(ad_mesh)
            bm_ad.free()

            ad_mat = bpy.data.materials.get(mat_name)
            if ad_mat:
                ad_obj.data.materials.append(ad_mat)

        # 8. KAALI-PEELI TAXIS & BEST BUS
        taxi_master = bpy.data.meshes.get("KaaliPeeli_Taxi_Detailed_Mesh")
        if taxi_master:
            taxi_traffic = [
                (Vector((-1015.0, 950.0, get_elev(950) + 0.25)), math.radians(5.0)),
                (Vector((-1008.0, 1020.0, get_elev(1020) + 0.25)), math.radians(5.0)),
                (Vector((-1018.0, 1100.0, get_elev(1100) + 0.25)), math.radians(5.0)),
                (Vector((-998.0, 1080.0, get_elev(1080) + 0.25)), math.radians(185.0)),
                (Vector((-1004.0, 1180.0, get_elev(1180) + 0.25)), math.radians(185.0)),
            ]
            for idx, (t_pos, t_rot) in enumerate(taxi_traffic):
                t_obj = bpy.data.objects.new(f"VEHICLE_MD_Taxi_{idx}", taxi_master)
                col_props.objects.link(t_obj)
                t_obj.location = t_pos
                t_obj.rotation_euler = Euler((0, 0, t_rot), 'XYZ')

        # 9. REPOSITION DRIVER CAMERA
        cam_md = bpy.data.objects.get("Cam_MarineDrive_Playable_Driver")
        if cam_md:
            cam_x = -1016.0
            cam_y = 1040.0
            cam_z = get_elev(cam_y) + 1.45
            cam_md.location = Vector((cam_x, cam_y, cam_z))
            
            target_x = -1010.0
            target_y = 1180.0
            target_z = get_elev(target_y) + 2.0
            dir_vec = Vector((target_x, target_y, target_z)) - cam_md.location
            rot_quat = dir_vec.to_track_quat('-Z', 'Y')
            cam_md.rotation_euler = rot_quat.to_euler()
            cam_md.data.lens = 32.0

        bpy.ops.wm.save_mainfile(filepath="/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend")
        print("Marine Drive Masterpiece job complete!")
        with open("/tmp/md_job_done.txt", "w") as f:
            f.write("DONE")
        return None

    bpy.app.timers.register(build_job, first_interval=0.05)
    print("Registered Marine Drive build job in timer")

register_marine_drive_build()
