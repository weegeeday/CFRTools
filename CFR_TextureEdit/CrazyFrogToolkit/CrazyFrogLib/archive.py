import os
import subprocess
import shutil

class PCArchive:
    def __init__(self, bms_exe, bms_script):
        self.bms_exe = bms_exe
        self.bms_script = bms_script

    def decompress(self, pc_path, output_dir):
        """Decompresses a .PC archive using QuickBMS."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        args = [self.bms_exe, "-o", self.bms_script, pc_path, output_dir]
        result = subprocess.run(args, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"QuickBMS decompression failed: {result.stderr}")
        
        # Identify the extracted file (usually same name as .pc without extension)
        base_name = os.path.splitext(os.path.basename(pc_path))[0]
        extracted_path = os.path.join(output_dir, base_name)
        
        if not os.path.exists(extracted_path):
            # Try lowercase if not found
            extracted_path = os.path.join(output_dir, base_name.lower())
            
        return extracted_path

    def reimport(self, pc_path, modified_dir):
        """Reimports modified files back into a .PC archive."""
        # QuickBMS reimport mode is -r
        # -w overwrites the original file
        args = [self.bms_exe, "-r", "-w", "-o", self.bms_script, pc_path, modified_dir]
        
        # We need to provide "force\n" to stdin if the reimported file is larger
        result = subprocess.run(args, input=b"force\n", capture_output=True)
        
        if result.returncode != 0:
            raise Exception(f"QuickBMS reimport failed: {result.stderr.decode()}")
        
        return True
