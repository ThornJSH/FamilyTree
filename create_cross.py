from PIL import Image, ImageDraw
import os

def create_cross():
    # Create directory if it doesn't exist
    if not os.path.exists('c:/familytree/resources'):
        os.makedirs('c:/familytree/resources')
        
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
    img.save('c:/familytree/resources/cross.png')
    print("Cross image created.")

if __name__ == "__main__":
    create_cross()
