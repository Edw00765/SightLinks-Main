import shutil

def clean_up(dir):
    """Clean up the output directory"""
    shutil.rmtree(dir)
    print(f"Directory cleaned up: {dir}")