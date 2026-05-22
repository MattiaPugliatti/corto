'''
CORTO Decoupled-In-the-Loop Tutorial — CLIENT SIDE
===================================================
This script represents the "mission process": the algorithm or simulation that
lives somewhere else and needs photorealistic images from CORTO.  It does NOT
require Blender, bpy, or cortopy to be installed — only the Python standard
library and NumPy.

The companion script (advanced_CIL_Server_Decoupled.py) must be running inside
Blender on the CORTO machine BEFORE this script is started.

Architecture
------------
  Mission Process (this script) ──── UDP pose   ────► CORTO Server  (Blender)
  Mission Process (this script) ◄─── TCP image  ──────  CORTO Server  (Blender)

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
  1. On the CORTO machine start the server first:
       blender --python advanced_CIL_Server_Decoupled.py
  2. Then start this script (on the same machine or any reachable machine):
       python advanced_CIL_Client_Decoupled.py
'''

import os
import socket
import struct
import numpy as np


# ============================================================================
# (1) NETWORK CONFIGURATION
#     Must match the values in advanced_CIL_ClosedLoop_Server.py
# ============================================================================

CORTO_HOST = "127.0.0.1"  # IP address of the machine running the CORTO server.
                           # Use "127.0.0.1" when both processes run on the same machine.
PORT_POSE  = 51001         # UDP port the CORTO server listens on for pose requests
PORT_IMAGE = 30001         # TCP port the CORTO server uses to send images back


# ============================================================================
# (2) OUTPUT CONFIGURATION
# ============================================================================

OUTPUT_DIR = os.path.join(os.getcwd(), "output", "decoupled_tutorial")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================================
# (3) SCENARIO — DEFINE THE SEQUENCE OF POSES TO REQUEST
#     Each entry is one rendering request sent to CORTO.
#     Positions are in Blender Units [BU].
#     Quaternions follow the [w, x, y, z] convention (same as Blender / cortopy).
# ============================================================================

sun_pos = np.array([0.0, 30000.0, 0.0])
body_pos = np.array([0.0, 0.0, 0.0])
cam_pos = np.array([-3.880436735865625,9.436275094557633,0.2122852153592106])
cam_q = np.array([-0.13848248126035184, -0.13563116230823927, 0.6864425350546722, 0.7008733382449409])

poses_sequence = [
    {
        "body_orientation":   np.array([0.016352521502461803,  0.0, 0.0, 0.999866288580884]),
    },
    {
        "body_orientation":   np.array([-0.49429973225975826, 0.0, 0.0, 0.8692915360728708]),
    },
    {
        "body_orientation":   np.array([-0.5776846363362429, 0.0, 0.0, 0.8162600449250611]),
    },
]

# ============================================================================
# (4) HELPER FUNCTIONS
# ============================================================================

def pack_pose(cam_pos, cam_q, body_pos, body_q, sun_pos) -> bytes:
    '''
    Build a 21-double big-endian UDP pose packet.

    Packet layout: [PQ_Sun (7), PQ_Cam (7), PQ_Body (7)]
    Each PQ vector: [x, y, z, qw, qx, qy, qz]
    '''
    values = np.concatenate([
        sun_pos,
        cam_pos,  cam_q,
        body_pos, body_q,
    ])
    return struct.pack('>' + 'd' * len(values), *values)


def recv_exact(sock: socket.socket, n: int) -> bytes:
    '''Receive exactly n bytes from a TCP socket, blocking until complete.'''
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("CORTO server closed the connection unexpectedly.")
        buf.extend(chunk)
    return bytes(buf)


def recv_image(sock: socket.socket) -> bytes:
    '''
    Receive one image from the CORTO server.

    Protocol: 8-byte little-endian uint64 size header followed by that many
    bytes of raw PNG data.
    '''
    header    = recv_exact(sock, 8)
    img_size  = struct.unpack('<Q', header)[0]
    img_bytes = recv_exact(sock, img_size)
    return img_bytes


# ============================================================================
# (5) MAIN — CONNECT TO CORTO SERVER AND REQUEST IMAGES
# ============================================================================

## 01. OPEN SOCKETS

# UDP socket used to transmit pose requests (fire-and-forget, no connection needed)
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# TCP socket used to receive rendered images (persistent connection)
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print(f"[Mission Client] Connecting to CORTO server at {CORTO_HOST}:{PORT_IMAGE} ...")
tcp_sock.connect((CORTO_HOST, PORT_IMAGE))
print("[Mission Client] Connected.\n")

## 02. REQUEST IMAGES ONE BY ONE

for ii, pose in enumerate(poses_sequence):

    body_q   = pose["body_orientation"]

    print(f"[Mission Client] Sending pose request #{ii}")
    print(f"  BODY q={body_q}")

    # (a) Send pose to CORTO server via UDP
    payload = pack_pose(cam_pos, cam_q, body_pos, body_q, sun_pos)
    udp_sock.sendto(payload, (CORTO_HOST, PORT_POSE))

    # (b) Wait for the rendered image to arrive via TCP
    print(f"  Waiting for image...")
    img_bytes = recv_image(tcp_sock)

    # (c) Save the received PNG to disk
    out_path = os.path.join(OUTPUT_DIR, '{:06d}.png'.format(ii))
    with open(out_path, 'wb') as f:
        f.write(img_bytes)

    print(f"  Image saved to {out_path}  ({len(img_bytes)} bytes)\n")

    # (d) At this point img_bytes is a valid PNG you can pass to any image
    #     processing library (e.g. PIL, OpenCV, scikit-image) for further
    #     analysis — for example feature extraction, pose estimation, etc.

## 03. CLOSE CONNECTIONS

tcp_sock.close()
udp_sock.close()
print("[Mission Client] All images received. Session complete.")
print(f"[Mission Client] Images saved in: {OUTPUT_DIR}")
