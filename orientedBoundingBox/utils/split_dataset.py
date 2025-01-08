import os, shutil, random
from pathlib import Path

def split_dataset(img_dir, label_dir, out_dir, train_ratio=0.85):
    """Split dataset into train/val sets with specified ratio"""
    # Create directories
    for split in ['train', 'val']:
        for dtype in ['images', 'labels']:
            Path(f"{out_dir}/{dtype}/{split}").mkdir(parents=True, exist_ok=True)
    
    # Get and shuffle image files
    imgs = [f for f in os.listdir(img_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    random.shuffle(imgs)
    
    # Calculate split index
    train_idx = int(len(imgs) * train_ratio)
    
    # Split files
    splits = {
        'train': imgs[:train_idx],
        'val': imgs[train_idx:]
    }
    
    # Copy files
    for split, files in splits.items():
        for img in files:
            shutil.copy2(f"{img_dir}/{img}", f"{out_dir}/images/{split}/{img}")
            label = f"{Path(img).stem}.txt"
            if os.path.exists(f"{label_dir}/{label}"):
                shutil.copy2(f"{label_dir}/{label}", f"{out_dir}/labels/{split}/{label}")
    
    print(f"Split complete: {len(imgs)} images → {len(splits['train'])} train, {len(splits['val'])} val")

if __name__ == "__main__":
    random.seed(42)  # For reproducibility
    split_dataset("../original-datasets/original-images", 
                 "../original-datasets/original-labels", 
                 "dataset",
                 train_ratio=0.85)  # Adjusted ratio for train/val only 