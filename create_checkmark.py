from PIL import Image, ImageDraw
import os

def create_checkmark():
    # Ensure resources directory exists in the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    resources_dir = os.path.join(current_dir, 'resources')
    
    if not os.path.exists(resources_dir):
        os.makedirs(resources_dir)
        
    # Create a transparent image
    size = (16, 16)
    img = Image.new('RGBA', size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw checkmark
    # Points for a checkmark shape
    points = [(3, 8), (7, 12), (13, 4)]
    
    # Draw lines with thickness
    draw.line(points, fill='#4A90E2', width=2)
    
    # Save
    save_path = os.path.join(resources_dir, 'checkmark.png')
    img.save(save_path)
    print(f"Checkmark image created at: {save_path}")

if __name__ == "__main__":
    create_checkmark()
