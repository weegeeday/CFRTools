"""
CrazyFrogLib - Mesh Module
Handles DLWM 3D geometry extraction from .PC level archives.

Vertex format: 16 bytes per vertex
  [int16 X, int16 Y, int16 Z, int16 W, int16 U, int16 V, int16 A, int16 B]

Face format: 20 bytes per face
  [u16 material, u16 pad, u16 idx1, u16 flag1, u16 idx2, u16 flag2, 
   u16 idx3, u16 flag3, u16 termA, u16 termB]
"""

import struct
import os


class DLWMMesh:
    """Parser for DLWM (Neko Engine) 3D level geometry."""

    VERTEX_STRIDE = 16
    FACE_STRIDE = 20
    HEADER_SIZE = 0x28

    def __init__(self):
        self.vertices = []   # List of (x, y, z) tuples
        self.uvs = []        # List of (u, v) tuples [0-1 range]
        self.faces = []      # List of (idx1, idx2, idx3, material_id) tuples
        self.materials = []  # Sorted unique material IDs
        self.face_count = 0
        self.vert_count = 0

    @classmethod
    def from_file(cls, filepath):
        """Load mesh from a decompressed DLWM level file."""
        with open(filepath, 'rb') as f:
            data = f.read()
        return cls.from_bytes(data)

    @classmethod
    def from_bytes(cls, data):
        """Parse mesh from raw DLWM bytes."""
        mesh = cls()

        # Validate header
        if data[0x0C:0x10] != b'DLWM':
            raise ValueError("Not a DLWM file (missing magic at 0x0C)")

        version = struct.unpack_from('<2I', data, 0)
        if version != (3, 3):
            raise ValueError(f"Unsupported DLWM version: {version}")

        # Parse header fields
        hdr = struct.unpack_from('<6I', data, 0x10)
        mesh.face_count = hdr[1]
        mesh.vert_count = hdr[2]

        # Parse faces
        for i in range(mesh.face_count):
            off = cls.HEADER_SIZE + i * cls.FACE_STRIDE
            vals = struct.unpack_from('<10H', data, off)
            mat = vals[0]
            idx1, idx2, idx3 = vals[2], vals[4], vals[6]
            mesh.faces.append((idx1, idx2, idx3, mat))

        # Parse vertices (immediately after face table)
        vert_start = cls.HEADER_SIZE + mesh.face_count * cls.FACE_STRIDE
        for i in range(mesh.vert_count):
            off = vert_start + i * cls.VERTEX_STRIDE
            x, y, z, w, u, v, a, b = struct.unpack_from('<8h', data, off)
            mesh.vertices.append((x, y, z))
            # UVs are signed int16 fixed-point, 4096 = 1.0
            # Negative/large values indicate texture tiling
            uf = u / 4096.0
            vf = 1.0 - v / 4096.0
            mesh.uvs.append((uf, vf))

        mesh.materials = sorted(set(f[3] for f in mesh.faces))
        return mesh

    def export_obj(self, obj_path, mtl_name=None, texture_dir=None, tex_count=0):
        """
        Export mesh as Wavefront OBJ with optional MTL and textures.
        
        Args:
            obj_path: Output .obj file path
            mtl_name: Optional .mtl filename to reference
            texture_dir: Optional relative path to texture folder
            tex_count: Number of available textures (for material mapping)
        """
        with open(obj_path, 'w') as f:
            f.write(f"# CrazyFrog Racer - DLWM Mesh Export\n")
            f.write(f"# {len(self.vertices)} vertices, {len(self.faces)} faces\n")
            f.write(f"# {len(self.materials)} materials\n\n")

            if mtl_name:
                f.write(f"mtllib {mtl_name}\n\n")

            for v in self.vertices:
                f.write(f"v {v[0]} {v[1]} {v[2]}\n")
            f.write("\n")

            for uv in self.uvs:
                f.write(f"vt {uv[0]:.6f} {uv[1]:.6f}\n")
            f.write("\n")

            # Group faces by material
            by_mat = {}
            for face in self.faces:
                m = face[3]
                if m not in by_mat:
                    by_mat[m] = []
                by_mat[m].append(face)

            for mat in sorted(by_mat.keys()):
                if mtl_name:
                    f.write(f"\nusemtl mat_{mat}\n")
                f.write(f"g group_{mat}\n")
                for face in by_mat[mat]:
                    i1, i2, i3 = face[0] + 1, face[1] + 1, face[2] + 1
                    f.write(f"f {i1}/{i1} {i2}/{i2} {i3}/{i3}\n")

    def export_mtl(self, mtl_path, texture_dir="textures", tex_count=0):
        """Generate an MTL material file mapping materials to textures."""
        with open(mtl_path, 'w') as f:
            f.write("# CrazyFrog Racer - Material Library\n\n")
            for mat in self.materials:
                tex_idx = mat % tex_count if tex_count > 0 else 0
                f.write(f"newmtl mat_{mat}\n")
                f.write(f"Ka 1.0 1.0 1.0\n")
                f.write(f"Kd 1.0 1.0 1.0\n")
                if tex_count > 0:
                    f.write(f"map_Kd {texture_dir}/tex_{tex_idx}.png\n")
                f.write("\n")
