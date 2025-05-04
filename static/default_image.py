from PIL import Image, ImageDraw, ImageFont

# Create a new image with blue background
img = Image.new('RGB', (400, 500), color=(73, 109, 137))
d = ImageDraw.Draw(img)

# Add text
d.text((10, 10), "Default Image - No Criminal Image Found", fill=(255, 255, 0))

# Save the image
img.save('default_image.png')

print("Default image created successfully!")
