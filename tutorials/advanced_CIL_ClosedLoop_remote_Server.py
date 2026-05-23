'''
CORTO Decoupled-In-the-Loop Tutorial — SERVER SIDE
===================================================
This script runs INSIDE Blender/CORTO. It initialises a CORTO rendering scene
and then sits in a loop waiting for camera-pose requests that arrive from a
separate process over the network.  Once a pose is received CORTO positions the
scene, renders one image, and ships the resulting PNG back to whoever asked.

The companion script (advanced_CIL_Client_Decoupled.py) plays the role of the
"mission process" and can run on the same machine or on any machine reachable
on the same network.

Architecture
------------
  Mission Process (Client) ──── UDP pose   ────► CORTO Server  (this script)
  Mission Process (Client) ◄─── TCP image  ──────  CORTO Server  (this script)

Communication protocol
----------------------
  Pose packet  (UDP, Client → Server)
    21 big-endian doubles packed with struct:
      [sun_x, sun_y, sun_z, sun_qw, sun_qx, sun_qy, sun_qz,      # indices  0-6
       cam_x, cam_y, cam_z, cam_qw, cam_qx, cam_qy, cam_qz,      # indices  7-13
       body_x, body_y, body_z, body_qw, body_qx, body_qy, body_qz]  # indices 14-20
    Positions in Blender Units [BU], quaternions in [w, x, y, z] format.

  Image packet  (TCP, Server → Client)
    8-byte little-endian uint64  →  number of PNG bytes that follow
    N bytes                      →  raw PNG file content

Run order
---------
  1. Start this script first:
       blender --python advanced_CIL_Server_Decoupled.py
  2. Then start the companion client script in a separate terminal / process:
       python advanced_CIL_Client_Decoupled.py
'''

import sys
import os
sys.path.append(os.getcwd())

import socket
import struct
import numpy as np
import cortopy as corto


# ============================================================================
# (1) NETWORK CONFIGURATION
#     Must match the values in advanced_CIL_Client_Decoupled.py
# ============================================================================

CORTO_HOST  = "0.0.0.0"   # listen on all interfaces; use a specific IP on multi-NIC machines
PORT_POSE   = 51001        # UDP port: receives incoming pose packets from the client
PORT_IMAGE  = 30001        # TCP port: sends rendered images back to the client
UDP_BUFSIZE = 512          # bytes; enough for 21 doubles (168 bytes)


# ============================================================================
# (2) SCENE SETUP
#     Mirrors the cooperative tutorials (advanced_CIL_ClosedLoop_Coop.py).
#     Adjust scenario_name / scene_name / body_name to your scenario.
# ============================================================================

def corto_scene_setup():
    '''Initialise the CORTO Blender scene and return the ENV, State, and cam handles.'''

    corto.Utils.clean_scene()

    ### Define inputs ###
    scenario_name = "S01_Eros"
    scene_name    = "scene_EEVEE.json"
    body_name     = "433_Eros_512ICQ.obj"

    State = corto.State(scene=scene_name, geometry=None, body=body_name, scenario=scenario_name)
    State.add_path('albedo_path',  os.path.join(State.path["input_path"], 'body', 'albedo',   'Eros grayscale.jpg'))
    State.add_path('uv_data_path', os.path.join(State.path["input_path"], 'body', 'uv data',  'uv_data.json'))

    ### Build scene objects ###
    cam              = corto.Camera('WFOV_Camera', State.properties_cam)
    sun              = corto.Sun('Sun',            State.properties_sun)
    name, _          = os.path.splitext(body_name)
    body             = corto.Body(name,            State.properties_body)
    rendering_engine = corto.Rendering(State.properties_rendering)
    ENV              = corto.Environment(cam, body, sun, rendering_engine)

    ### Material ###
    material = corto.Shading.create_new_material('corto shading')
    corto.Shading.create_branch_albedo_mix(material, State)
    corto.Shading.load_uv_data(body, State)
    corto.Shading.assign_material_to_object(material, body)

    body.set_scale(np.array([0.1, 0.1, 0.1]))

    return ENV, State, cam


# ============================================================================
# (3) HELPER FUNCTIONS
# ============================================================================

def unpack_pose(data: bytes):
    '''
    Decode a 17-double UDP pose packet.

    Returns
    -------
    P_Sun  : np.ndarray, shape (3,)  – [x, y, z]
    PQ_Cam  : np.ndarray, shape (7,)  – [x, y, z, qw, qx, qy, qz]
    PQ_Body : np.ndarray, shape (7,)  – [x, y, z, qw, qx, qy, qz]
    '''
    n_vals = len(data) // 8
    values  = struct.unpack('>' + 'd' * n_vals, data)
    P_Sun  = np.array(values[0:3])
    PQ_Cam  = np.array(values[3:10])
    PQ_Body = np.array(values[10:17])
    return P_Sun, PQ_Cam, PQ_Body


def send_image(conn: socket.socket, img_path: str) -> None:
    '''
    Read a PNG from disk and send it over a connected TCP socket.

    The packet format is:
      [8-byte little-endian uint64 = file size] + [raw PNG bytes]
    '''
    with open(img_path, 'rb') as f:
        img_bytes = f.read()
    header = struct.pack('<Q', len(img_bytes))
    conn.sendall(header + img_bytes)


# ============================================================================
# (4) MAIN — OPEN SOCKETS AND ENTER RENDER LOOP
# ============================================================================

## 01. SETUP CORTO SCENE
print("[CORTO Server] Setting up scene...")
ENV, State, cam = corto_scene_setup()
print("[CORTO Server] Scene ready.")

## 02. OPEN UDP SOCKET (receives incoming pose requests)
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.bind((CORTO_HOST, PORT_POSE))
print(f"[CORTO Server] Listening for poses on UDP {CORTO_HOST}:{PORT_POSE}")

## 03. OPEN TCP SOCKET (sends rendered images back)
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_sock.bind((CORTO_HOST, PORT_IMAGE))
tcp_sock.listen(1)
print(f"[CORTO Server] Waiting for client to connect on TCP {CORTO_HOST}:{PORT_IMAGE} ...")
conn, client_addr = tcp_sock.accept()
print(f"[CORTO Server] Client connected from {client_addr}")

## 04. RENDER LOOP
print("[CORTO Server] Entering render loop. Waiting for pose requests...\n")

ii = 0
while True:

    # (a) Block until a new pose packet arrives over UDP
    data, sender = udp_sock.recvfrom(UDP_BUFSIZE)
    P_Sun, PQ_Cam, PQ_Body = unpack_pose(data)

    print(f"[CORTO Server] Request #{ii}")
    print(f"  SUN   pos={P_Sun[0:3]}")
    print(f"  CAM   pos={PQ_Cam[0:3]}  q={PQ_Cam[3:7]}")
    print(f"  BODY  pos={PQ_Body[0:3]}  q={PQ_Body[3:7]}")

    # (b) Position the scene using the cortopy API.
    #     poses_input order: [cam_pos, cam_quat, body_pos, body_quat, sun_pos]
    poses_input = [PQ_Cam[0:3], PQ_Cam[3:7], PQ_Body[0:3], PQ_Body[3:7], P_Sun[0:3]]
    ENV.PositionAll(State, index=None, poses=poses_input)

    # (c) Render one image.  The PNG is saved to State.path["output_path"]/img/{ii:06d}.png
    ENV.RenderOne(cam, State, index=ii)
    img_path = os.path.join(State.path["output_path"], 'img', '{:06d}.png'.format(ii))
    print(f"  Rendered → {img_path}")

    # (d) Send the resulting PNG back to the client over TCP
    send_image(conn, img_path)
    print(f"  Image transmitted to {client_addr}\n")

    ii += 1
