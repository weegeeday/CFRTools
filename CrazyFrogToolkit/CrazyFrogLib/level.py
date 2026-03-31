import os
import struct
from .archive import PCArchive
from .texture import PS2Texture

class CFRLevel:
    def __init__(self, data_dir, level_name, bms_exe, bms_script):
        self.data_dir = data_dir
        self.level_name = level_name
        self.lvl_dir = os.path.join(data_dir, level_name)
        self.gfx_pc = os.path.join(self.lvl_dir, f"{level_name}gfx.pc")
        self.tin_pc = os.path.join(self.lvl_dir, f"{level_name}tin.pc")
        
        self.archive = PCArchive(bms_exe, bms_script)
        self.textures = []
        self._temp_dir = None
        self._gfx_data = None

    def load(self, temp_base):
        self._temp_dir = os.path.join(temp_base, self.level_name)
        
        # Decompress tin and gfx
        tin_raw = self.archive.decompress(self.tin_pc, os.path.join(self._temp_dir, "tin"))
        gfx_raw = self.archive.decompress(self.gfx_pc, os.path.join(self._temp_dir, "gfx"))
        
        # Parse tin metadata
        with open(tin_raw, 'rb') as f: tin_data = f.read()
        self.textures = self._parse_tin(tin_data)
        
        with open(gfx_raw, 'rb') as f: self._gfx_data = bytearray(f.read())
        return len(self.textures)

    def _parse_tin(self, tin):
        textures = []
        # Structural search for the 0x80000001 flag (8-bit/4-bit paletted)
        # We start from known headers or do a scan
        for i in range(0, len(tin)-15, 4):
            offset, flags, size = struct.unpack('<III', tin[i+4:i+16])
            if flags == 0x80000001 and size > 0 and size < 10000000 and offset != 0xFFFFFFFF:
                pitch = struct.unpack('<I', tin[i:i+4])[0]
                # Determine bit depth heuristically based on size
                # (size - palette) * (8 / bit_depth) = pixels
                # For small blocks, we assume 4-bit
                bit_depth = 4 if size <= 6500 else 8
                textures.append({
                    'id': len(textures),
                    'pitch': pitch,
                    'offset': offset,
                    'size': size,
                    'bit_depth': bit_depth
                })
        # Remove duplicates
        unique = {}
        for t in textures: unique[t['offset']] = t
        return sorted(unique.values(), key=lambda x: x['offset'])

    def export_all(self, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        for i, t in enumerate(self.textures):
            img, _ = PS2Texture.extract(self._gfx_data, t['offset'], t['size'], t['pitch'], t['bit_depth'])
            img.save(os.path.join(output_dir, f"tex_{i}_{t['pitch']}x{img.height}_{t['bit_depth']}b.png"))

    def replace_all_with_image(self, source_image_path):
        from PIL import Image
        src = Image.open(source_image_path).convert('RGB').quantize(colors=256)
        
        # Pre-build quantized palette parts
        # Extract once to get a reference unswiz list (not strictly needed for full replacement but good for internal consistency)
        _, ref_unswiz = PS2Texture.extract(self._gfx_data, self.textures[0]['offset'], self.textures[0]['size'], self.textures[0]['pitch'], self.textures[0]['bit_depth'])
        
        # Swizzle the new palette
        flat = src.palette.palette
        mode = src.palette.mode
        new_colors = []
        for i in range(256):
            if mode == 'RGB':
                r,g,b = flat[i*3:i*3+3]
                new_colors.append((r,g,b,255))
            else: # RGBA
                new_colors.append(tuple(flat[i*4:i*4+4]))
        
        new_pal_bytes = PS2Texture.swizzle_palette(new_colors)

        for t in self.textures:
            # Scale image
            w = t['pitch']
            h = ( (t['size'] - 1024) * (8 // t['bit_depth']) ) // w
            resized = src.resize((w, h), Image.NEAREST)
            
            # Pack
            pal, pixels = PS2Texture.pack(resized, new_colors, t['bit_depth'])
            
            # Inject
            self._gfx_data[t['offset'] : t['offset']+1024] = pal
            self._gfx_data[t['offset']+1024 : t['offset']+1024+len(pixels)] = pixels

    def save(self):
        gfx_raw = os.path.join(self._temp_dir, "gfx", self.level_name + "gfx")
        with open(gfx_raw, 'wb') as f: f.write(self._gfx_data)
        self.archive.reimport(self.gfx_pc, os.path.join(self._temp_dir, "gfx"))
