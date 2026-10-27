"""
GRAI Mumbai Digital Twin — Real-time Playable Character & Map Controller
========================================================================
Implements full interactive gameplay in Blender 3D Viewport:
1. WASD + Arrow Keys character locomotion and steering across Mumbai.
2. Smooth over-the-shoulder third-person camera tracking.
3. First-person eyes view, neighborhood drone follow, and master map view.
4. M / TAB instant Map View toggle (whole city overview).
5. 1-5 Fast-Travel Teleportation to Mumbai landmarks.
6. Persistent N-Panel UI in Blender's 3D Viewport under the "GRAI" tab.
"""
import bpy
import math
from mathutils import Vector, Matrix

# ----------------------------------------------------------------------
# 1. LANDMARKS & LOCATIONS
# ----------------------------------------------------------------------
LANDMARKS = {
    "MARINEDRIVE": {
        "name": "Marine Drive Promenade & Queen's Necklace",
        "pos": Vector((-1007.0, 1100.0, 7.24)),
        "rot_z": 0.0,
        "description": "Art Deco beachfront boulevard along Back Bay"
    },
    "GATEWAY": {
        "name": "Gateway of India & Taj Mahal Palace",
        "pos": Vector((236.0, -135.0, 2.2)),
        "rot_z": math.radians(90.0),
        "description": "Historic Apollo Bunder basalt plaza and harbor"
    },
    "SEALINK": {
        "name": "Bandra-Worli Sea Link Expressway",
        "pos": Vector((-1420.0, 11950.0, 26.5)),
        "rot_z": 0.0,
        "description": "8-lane cable-stayed expressway crossing Mahim Bay"
    },
    "FORT": {
        "name": "CSMT & Fort Heritage District",
        "pos": Vector((-680.0, 720.0, 8.5)),
        "rot_z": math.radians(-45.0),
        "description": "Victorian Gothic & heritage architecture hub"
    },
    "CHOWPATTY": {
        "name": "Girgaon Chowpatty Beach",
        "pos": Vector((-915.0, 2150.0, 4.2)),
        "rot_z": math.radians(-30.0),
        "description": "Northern tip of the Marine Drive crescent bay"
    }
}

def get_closest_landmark(pos):
    closest = "Marine Drive"
    min_dist = float('inf')
    for key, data in LANDMARKS.items():
        dist = (data['pos'] - pos).length
        if dist < min_dist:
            min_dist = dist
            closest = data['name']
    return closest

# ----------------------------------------------------------------------
# 2. FAST TELEPORT OPERATOR
# ----------------------------------------------------------------------
class GRAI_OT_Teleport(bpy.types.Operator):
    """Teleport Raghunath and active camera to an iconic Mumbai landmark"""
    bl_idname = "grai.teleport"
    bl_label = "Teleport to Landmark"
    bl_options = {'REGISTER', 'UNDO'}

    destination: bpy.props.StringProperty(name="Destination", default="MARINEDRIVE")

    def execute(self, context):
        dest_data = LANDMARKS.get(self.destination)
        if not dest_data:
            self.report({'WARNING'}, f"Unknown destination: {self.destination}")
            return {'CANCELLED'}

        root = bpy.data.objects.get("Character_Raghunath_Root")
        if root:
            root.location = dest_data['pos']
            root.rotation_euler.z = dest_data['rot_z']

        # Ensure third person camera is active
        cam = bpy.data.objects.get("Cam_Player_ThirdPerson_Road")
        if cam:
            context.scene.camera = cam

        # Set 3D views to camera perspective
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.region_3d.view_perspective = 'CAMERA'
                        space.shading.type = 'MATERIAL'
                area.tag_redraw()

        self.report({'INFO'}, f"Teleported to {dest_data['name']}")
        return {'FINISHED'}

# ----------------------------------------------------------------------
# 3. CAMERA SWITCH OPERATOR
# ----------------------------------------------------------------------
class GRAI_OT_SwitchCamera(bpy.types.Operator):
    """Switch active viewport camera to a player or map perspective"""
    bl_idname = "grai.switch_camera"
    bl_label = "Switch View Camera"
    bl_options = {'REGISTER', 'UNDO'}

    camera_name: bpy.props.StringProperty(name="Camera Name", default="Cam_Player_ThirdPerson_Road")

    def execute(self, context):
        cam = bpy.data.objects.get(self.camera_name)
        if not cam or cam.type != 'CAMERA':
            self.report({'WARNING'}, f"Camera not found: {self.camera_name}")
            return {'CANCELLED'}

        context.scene.camera = cam
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.region_3d.view_perspective = 'CAMERA'
                        space.shading.type = 'MATERIAL'
                area.tag_redraw()

        self.report({'INFO'}, f"Switched active view to {self.camera_name}")
        return {'FINISHED'}

# ----------------------------------------------------------------------
# 4. TOGGLE MAP / CHARACTER VIEW OPERATOR
# ----------------------------------------------------------------------
class GRAI_OT_ToggleMapView(bpy.types.Operator):
    """Toggle between character ground view and high-altitude map overview"""
    bl_idname = "grai.toggle_map_view"
    bl_label = "Toggle Map / Player View"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        current_cam = context.scene.camera
        cam_map = bpy.data.objects.get("Cam_Mumbai_Playable_Map_Master")
        cam_player = bpy.data.objects.get("Cam_Player_ThirdPerson_Road")

        if current_cam == cam_map:
            # Return to player
            if cam_player:
                context.scene.camera = cam_player
                self.report({'INFO'}, "Returned to Player Third-Person View")
        else:
            # Switch to map overview
            if cam_map:
                context.scene.camera = cam_map
                self.report({'INFO'}, "Switched to Mumbai Map Overview View")

        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.region_3d.view_perspective = 'CAMERA'
                        space.shading.type = 'MATERIAL'
                area.tag_redraw()

        return {'FINISHED'}

# ----------------------------------------------------------------------
# 5. REAL-TIME MODAL PLAY CONTROLLER
# ----------------------------------------------------------------------
class GRAI_OT_PlayController(bpy.types.Operator):
    """Real-time playable character and map controller with WASD controls"""
    bl_idname = "grai.play"
    bl_label = "Start Playable Mode"
    bl_options = {'REGISTER', 'UNDO'}

    _timer = None
    keys = {}
    mode = "CHARACTER" # "CHARACTER" or "MAP"
    cam_mode_idx = 0
    cam_names = [
        "Cam_Player_ThirdPerson_Road",
        "Cam_Player_FirstPerson_Eyes",
        "Cam_Player_Drone_Overview",
        "Cam_Mumbai_Playable_Map_Master"
    ]
    walk_phase = 0.0
    base_walk_speed = 7.5   # m/s
    sprint_multiplier = 3.2 # m/s (approx 24 m/s running)
    turn_speed = 2.4        # radians/sec
    map_pan_speed = 450.0   # m/s
    dt = 0.020              # 50 FPS

    def modal(self, context, event):
        # 1. Process Key Press / Release Events
        if event.type in {'W', 'UP_ARROW'}:
            self.keys['W'] = (event.value == 'PRESS')
        elif event.type in {'S', 'DOWN_ARROW'}:
            self.keys['S'] = (event.value == 'PRESS')
        elif event.type in {'A', 'LEFT_ARROW'}:
            self.keys['A'] = (event.value == 'PRESS')
        elif event.type in {'D', 'RIGHT_ARROW'}:
            self.keys['D'] = (event.value == 'PRESS')
        elif event.type in {'LEFT_SHIFT', 'RIGHT_SHIFT'}:
            self.keys['SHIFT'] = (event.value == 'PRESS')
        elif event.type == 'Q':
            self.keys['Q'] = (event.value == 'PRESS')
        elif event.type == 'E':
            self.keys['E'] = (event.value == 'PRESS')

        # 2. Single Key Actions
        if event.value == 'PRESS':
            # Toggle Map View vs Character View
            if event.type in {'M', 'TAB'}:
                if self.mode == "CHARACTER":
                    self.mode = "MAP"
                    cam = bpy.data.objects.get("Cam_Mumbai_Playable_Map_Master")
                    if cam:
                        context.scene.camera = cam
                else:
                    self.mode = "CHARACTER"
                    cam = bpy.data.objects.get(self.cam_names[self.cam_mode_idx % 3])
                    if cam:
                        context.scene.camera = cam
                self.tag_redraw(context)

            # Cycle Camera Perspectives
            elif event.type == 'V':
                if self.mode == "CHARACTER":
                    self.cam_mode_idx = (self.cam_mode_idx + 1) % 3
                    cam = bpy.data.objects.get(self.cam_names[self.cam_mode_idx])
                    if cam:
                        context.scene.camera = cam
                self.tag_redraw(context)

            # Quick Fast-Travel Teleports (1 - 5)
            elif event.type == 'ONE':
                self.teleport_player(context, "MARINEDRIVE")
            elif event.type == 'TWO':
                self.teleport_player(context, "GATEWAY")
            elif event.type == 'THREE':
                self.teleport_player(context, "SEALINK")
            elif event.type == 'FOUR':
                self.teleport_player(context, "FORT")
            elif event.type == 'FIVE':
                self.teleport_player(context, "CHOWPATTY")

            # Exit Game Controller
            elif event.type in {'ESC', 'RIGHTMOUSE'}:
                return self.cancel(context)

        # 3. Timer Tick: Update Physics and Movement
        if event.type == 'TIMER':
            root = bpy.data.objects.get("Character_Raghunath_Root")
            if not root:
                return {'PASS_THROUGH'}

            if self.mode == "CHARACTER":
                # Current heading angle
                rot_z = root.rotation_euler.z

                # Turn left / right
                if self.keys.get('A'):
                    rot_z += self.turn_speed * self.dt
                if self.keys.get('D'):
                    rot_z -= self.turn_speed * self.dt
                root.rotation_euler.z = rot_z

                # Forward / backward movement
                speed = self.base_walk_speed
                if self.keys.get('SHIFT'):
                    speed *= self.sprint_multiplier

                # Direction vector in world space: facing along rotated +Y
                forward = Vector((-math.sin(rot_z), math.cos(rot_z), 0.0))

                moving = False
                if self.keys.get('W'):
                    root.location += forward * (speed * self.dt)
                    moving = True
                if self.keys.get('S'):
                    root.location -= forward * (speed * self.dt * 0.55)
                    moving = True

                # Subtle walking bobbing animation
                if moving:
                    self.walk_phase += 14.0 * self.dt
                else:
                    self.walk_phase = 0.0

                # Update live status bar HUD
                landmark_name = get_closest_landmark(root.location)
                speed_txt = f"{speed*3.6:.0f} km/h" if moving else "Idle"
                hud = (
                    f"GRAI MUMBAI [CHARACTER MODE] | Location: {landmark_name} "
                    f"({root.location.x:.1f}, {root.location.y:.1f}) | Speed: {speed_txt} | "
                    f"[W/A/S/D] Walk/Steer | [Shift] Sprint | [M] Map View | [V] Cam | [1-5] Teleport | [ESC] Exit"
                )
                try:
                    context.workspace.status_text_set(hud)
                except Exception:
                    pass

            elif self.mode == "MAP":
                cam_map = bpy.data.objects.get("Cam_Mumbai_Playable_Map_Master")
                if cam_map:
                    # Pan camera across Mumbai
                    pan = self.map_pan_speed * self.dt
                    if self.keys.get('SHIFT'):
                        pan *= 3.0
                    if self.keys.get('W'):
                        cam_map.location.y += pan
                    if self.keys.get('S'):
                        cam_map.location.y -= pan
                    if self.keys.get('A'):
                        cam_map.location.x -= pan
                    if self.keys.get('D'):
                        cam_map.location.x += pan
                    if self.keys.get('Q'):
                        cam_map.location.z = max(150.0, cam_map.location.z - pan * 1.5)
                    if self.keys.get('E'):
                        cam_map.location.z = min(35000.0, cam_map.location.z + pan * 1.5)

                hud = (
                    f"GRAI MUMBAI [MAP OVERVIEW MODE] | Alt: {cam_map.location.z:.0f}m | "
                    f"[W/A/S/D] Pan Map | [Q/E] Alt Zoom | [M/Tab] Return to Player | [1-5] Teleport | [ESC] Exit"
                )
                try:
                    context.workspace.status_text_set(hud)
                except Exception:
                    pass

            self.tag_redraw(context)

        return {'RUNNING_MODAL'}

    def teleport_player(self, context, landmark_key):
        data = LANDMARKS.get(landmark_key)
        if not data:
            return
        root = bpy.data.objects.get("Character_Raghunath_Root")
        if root:
            root.location = data['pos']
            root.rotation_euler.z = data['rot_z']
        if self.mode == "MAP":
            # Also center map camera above destination
            cam_map = bpy.data.objects.get("Cam_Mumbai_Playable_Map_Master")
            if cam_map:
                cam_map.location.x = data['pos'].x - 1200.0
                cam_map.location.y = data['pos'].y - 1500.0
        self.tag_redraw(context)

    def tag_redraw(self, context):
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()

    def invoke(self, context, event):
        if context.area.type != 'VIEW_3D':
            self.report({'WARNING'}, "View3D not found, please invoke from 3D Viewport")
            return {'CANCELLED'}

        # Ensure Raghunath root exists
        root = bpy.data.objects.get("Character_Raghunath_Root")
        if not root:
            self.report({'ERROR'}, "Character_Raghunath_Root not found in scene")
            return {'CANCELLED'}

        # Setup active camera to third-person follow
        cam = bpy.data.objects.get("Cam_Player_ThirdPerson_Road")
        if cam:
            context.scene.camera = cam

        # Configure 3D view space to camera and material shading
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.region_3d.view_perspective = 'CAMERA'
                        space.shading.type = 'MATERIAL'

        # Initialize keys
        self.keys = {
            'W': False, 'S': False, 'A': False, 'D': False,
            'SHIFT': False, 'Q': False, 'E': False
        }
        self.mode = "CHARACTER"
        self.cam_mode_idx = 0

        # Start 50 FPS timer
        wm = context.window_manager
        self._timer = wm.event_timer_add(time_step=self.dt, window=context.window)
        wm.modal_handler_add(self)

        self.report({'INFO'}, "GRAI Playable Mode Started! Press [W/A/S/D] to move, [M] for Map View, [ESC] to exit.")
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        if self._timer:
            wm.event_timer_remove(self._timer)
            self._timer = None
        try:
            context.workspace.status_text_set(None)
        except Exception:
            pass
        self.report({'INFO'}, "GRAI Playable Mode Stopped.")
        return {'FINISHED'}

# ----------------------------------------------------------------------
# 6. 3D VIEWPORT N-PANEL UI
# ----------------------------------------------------------------------
class GRAI_PT_PlayerController(bpy.types.Panel):
    """GRAI Player & Map Controller UI in 3D Viewport N-Panel"""
    bl_label = "GRAI — Mumbai Digital Twin"
    bl_idname = "GRAI_PT_player_controller"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "GRAI"

    def draw(self, context):
        layout = self.layout

        root = bpy.data.objects.get("Character_Raghunath_Root")
        loc_txt = f"({root.location.x:.0f}, {root.location.y:.0f})" if root else "N/A"
        closest = get_closest_landmark(root.location) if root else "Unknown"

        # Status Box
        box = layout.box()
        row = box.row()
        row.label(text="Protagonist: Raghunath", icon='USER')
        row = box.row()
        row.label(text=f"Location: {closest}", icon='PINNED')
        row.label(text=f"Coords: {loc_txt}")

        # Big Play Button
        col = layout.column(align=True)
        col.scale_y = 1.8
        col.operator("grai.play", text="START PLAYABLE CONTROLLER (WASD)", icon='PLAY')

        # Map View / Player Toggle
        col = layout.column(align=True)
        col.scale_y = 1.3
        col.operator("grai.toggle_map_view", text="TOGGLE MAP VIEW (Whole Mumbai)", icon='RESTRICT_VIEW_OFF')

        # Camera Perspective Switcher
        layout.separator()
        box_cam = layout.box()
        box_cam.label(text="Camera Perspectives", icon='CAMERA_DATA')
        col_c = box_cam.column(align=True)
        col_c.operator("grai.switch_camera", text="3rd Person Follow", icon='OUTLINER_OB_CAMERA').camera_name = "Cam_Player_ThirdPerson_Road"
        col_c.operator("grai.switch_camera", text="1st Person Eyes", icon='HIDE_OFF').camera_name = "Cam_Player_FirstPerson_Eyes"
        col_c.operator("grai.switch_camera", text="Drone Follow", icon='TRACKING').camera_name = "Cam_Player_Drone_Overview"
        col_c.operator("grai.switch_camera", text="City Map Overview", icon='WORLD').camera_name = "Cam_Mumbai_Playable_Map_Master"
        col_c.operator("grai.switch_camera", text="Satellite Topdown Map", icon='IMAGE_DATA').camera_name = "Cam_Mumbai_Full_Map_TopDown"

        # Fast-Travel Teleportation
        layout.separator()
        box_tp = layout.box()
        box_tp.label(text="Fast-Travel (Mumbai Landmarks)", icon='WORKSPACE')
        col_t = box_tp.column(align=True)
        col_t.operator("grai.teleport", text="Marine Drive (Queen's Necklace)").destination = "MARINEDRIVE"
        col_t.operator("grai.teleport", text="Gateway of India & Taj Mahal").destination = "GATEWAY"
        col_t.operator("grai.teleport", text="Bandra-Worli Sea Link").destination = "SEALINK"
        col_t.operator("grai.teleport", text="CSMT & Fort Heritage District").destination = "FORT"
        col_t.operator("grai.teleport", text="Girgaon Chowpatty Beach").destination = "CHOWPATTY"

        # Help / Keybinds Box
        layout.separator()
        box_h = layout.box()
        box_h.label(text="Controls Cheat Sheet", icon='QUESTION')
        col_h = box_h.column(align=True)
        col_h.label(text="• W / A / S / D: Walk & Steer")
        col_h.label(text="• Shift + W: Sprint / Run")
        col_h.label(text="• M or Tab: Toggle Map View")
        col_h.label(text="• V: Cycle Camera Views")
        col_h.label(text="• 1 to 5: Fast Landmark Teleport")
        col_h.label(text="• ESC: Exit Play Mode")

# ----------------------------------------------------------------------
# 7. REGISTRATION
# ----------------------------------------------------------------------
classes = (
    GRAI_OT_Teleport,
    GRAI_OT_SwitchCamera,
    GRAI_OT_ToggleMapView,
    GRAI_OT_PlayController,
    GRAI_PT_PlayerController
)

def register():
    for cls in classes:
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
        bpy.utils.register_class(cls)
    print("GRAI Playable Controller Registered Successfully.")

if __name__ == "__main__":
    register()
