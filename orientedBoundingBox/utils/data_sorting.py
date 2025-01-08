import os
from pathlib import Path
import shutil

def move_unpaired_images(image_dir, label_dir, unpaired_dir):
    """Move images that don't have corresponding label files to a separate directory"""
    # Check if directories exist
    if not os.path.exists(image_dir) or not os.path.exists(label_dir):
        print("Error: Image or label directory does not exist")
        return

    # Create unpaired directory if it doesn't exist
    os.makedirs(unpaired_dir, exist_ok=True)

    # Get list of label files without extension
    label_files = {Path(f).stem for f in os.listdir(label_dir) if f.endswith('.txt')}
    moved_count = 0

    # Check each image file
    for img_file in os.listdir(image_dir):
        if img_file.endswith(('.jpg', '.jpeg', '.png')):
            img_name = Path(img_file).stem
            if img_name not in label_files:
                src_path = os.path.join(image_dir, img_file)
                dst_path = os.path.join(unpaired_dir, img_file)
                shutil.move(src_path, dst_path)
                print(f"Moved: {img_file}")
                moved_count += 1

    print(f"Total images moved: {moved_count}")

if __name__ == "__main__":
    # Assuming images and labels are in these directories
    image_dir = "../original-datasets/original-images"
    label_dir = "../original-datasets/original-labels"
    unpaired_dir = "../original-datasets/unpaired-images"  # New directory for unpaired images
    move_unpaired_images(image_dir, label_dir, unpaired_dir)