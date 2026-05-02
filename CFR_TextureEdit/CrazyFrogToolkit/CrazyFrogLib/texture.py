import os
import struct
from PIL import Image

class PS2Texture:
    @staticmethod
    def unswizzle_palette(palette_data):
        """Unswizzles a 1024-byte PS2 TIM2 palette (BGRA)."""
        colors = []
        for i in range(0, 1024, 4):
            colors.append(tuple(palette_data[i:i+4]))
            
        unswizzled = [(0,0,0,0)] * 256
        for i in range(256):
            blk = i // 32
            sub = (i % 32) // 8
            off = i % 8
            disk = blk * 32 + [0, 2, 1, 3][sub] * 8 + off
            unswizzled[i] = colors[disk]
            
        # Convert BGRA to RGBA and fix alpha (0x80 -> 255)
        pal_bytes = bytearray()
        for (b, g, r, a) in unswizzled:
            rgba_a = min(255, a * 2) if a <= 128 else a
            pal_bytes.extend([r, g, b, rgba_a])
        return pal_bytes, unswizzled

    @staticmethod
    def swizzle_palette(rgba_palette, original_unswiz=None):
        """Swizzles an RGBA palette back to PS2 TIM2 BGRA."""
        # rgba_palette is a list of (r, g, b, a) or similar
        # If original_unswiz is provided, we can use it to maintain original values for non-target colors
        
        swizzled = [(0, 0, 0, 0)] * 256
        for i in range(256):
            r, g, b, a = rgba_palette[i]
            # Convert RGBA to BGRA and fix alpha (255 -> 0x80)
            ps2_a = a // 2 if a <= 254 else 0x80
            
            blk = i // 32
            sub = (i % 32) // 8
            off = i % 8
            disk = blk * 32 + [0, 2, 1, 3][sub] * 8 + off
            swizzled[disk] = (b, g, r, ps2_a)
            
        pal_bytes = bytearray()
        for (b, g, r, a) in swizzled:
            pal_bytes.extend([b, g, r, a])
        return pal_bytes

    @staticmethod
    def extract(data, offset, size, pitch, bit_depth=8):
        """Extracts texture data to a PIL Image."""
        pal_bytes, unswiz = PS2Texture.unswizzle_palette(data[offset:offset+1024])
        pixel_data = data[offset+1024:offset+size]
        
        w = pitch
        h = (len(pixel_data) * (8 // bit_depth)) // w
        
        if bit_depth == 4:
            expanded = bytearray()
            for b in pixel_data:
                expanded.append(b & 0xF)
                expanded.append(b >> 4)
            img_data = bytes(expanded[:w*h])
        else:
            img_data = bytes(pixel_data[:w*h])
            
        img = Image.frombytes('P', (w, h), img_data)
        img.putpalette(pal_bytes, 'RGBA')
        return img, unswiz

    @staticmethod
    def pack(img, original_unswiz, bit_depth=8):
        """Packs a PIL Image and its palette back to PS2 format."""
        img = img.convert('P')
        
        # Palette reconstruction
        # Pull palette colors from the PIL image
        flat = img.palette.palette if img.palette else []
        mode = img.palette.mode if img.palette else 'RGB'
        
        new_colors = []
        for i in range(256):
            if mode == 'RGBA' and (i*4+3) < len(flat):
                new_colors.append(tuple(flat[i*4:i*4+4]))
            elif mode == 'RGB' and (i*3+2) < len(flat):
                r, g, b = flat[i*3:i*3+3]
                new_colors.append((r, g, b, 255))
            else:
                # Fallback to original if out of range
                new_colors.append(original_unswiz[i] if original_unswiz else (0,0,0,0))
        
        swizzled_pal = PS2Texture.swizzle_palette(new_colors)
        
        # Pixel reconstruction
        pixels = list(img.getdata())
        if bit_depth == 4:
            packed = bytearray()
            for i in range(0, len(pixels), 2):
                p1 = pixels[i] & 0xF
                p2 = pixels[i+1] & 0xF if i+1 < len(pixels) else 0
                packed.append(p1 | (p2 << 4))
            return swizzled_pal, packed
        else:
            return swizzled_pal, bytearray(pixels)
