from PIL import Image, ImageDraw
import os

def create_cross():
    # Ensure resources directory exists in the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    resources_dir = os.path.join(current_dir, 'resources')
    
    if not os.path.exists(resources_dir):
        os.makedirs(resources_dir)
        
    # Create a transparent image
    size = (16, 16)
    img = Image.new('RGBA', size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw X
    # Points for X
    # Top-left to bottom-right
    draw.line([(3, 3), (12, 12)], fill='#4A90E2', width=2)
    # Top-right to bottom-left
    draw.line([(12, 3), (3, 12)], fill='#4A90E2', width=2)
    
    # Save
    save_path = os.path.join(resources_dir, 'cross.png')
    img.save(save_path)
    print(f"Cross image created at: {save_path}")

if __name__ == "__main__":
    create_cross()
