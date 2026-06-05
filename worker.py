import os
from PIL import Image, ImageFilter

def process_single_image(args):
    """Fungsi target yang akan dijalankan oleh core CPU secara paralel"""
    image_path, output_folder = args
    try:
        img = Image.open(image_path)
        # Memberikan efek blur berulang kali untuk mensimulasikan beban kerja berat
        for _ in range(15):
            img = img.filter(ImageFilter.GaussianBlur(radius=10))
        
        output_path = os.path.join(output_folder, os.path.basename(image_path))
        img.save(output_path)
        return True
    except Exception as e:
        return False