from PIL import Image, ImageDraw
import os

def create_checkmark():
    # Create directory if it doesn't exist
    if not os.path.exists('c:/familytree/resources'):
        os.makedirs('c:/familytree/resources')
        
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
    img.save('c:/familytree/resources/checkmark.png')
    print("Checkmark image created.")

if __name__ == "__main__":
    create_checkmark()
