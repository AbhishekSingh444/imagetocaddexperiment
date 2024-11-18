from pyautocad import Autocad, APoint
from PIL import Image, ImageChops
import os
from datetime import datetime
import traceback

def remove_background_and_create_editable(acad, image_path, output_path):
    try:
        print(f"Processing image: {image_path}")
        with Image.open(image_path) as img:
            # Convert image to RGBA (to manage transparency)
            img = img.convert("RGBA")
            bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
            diff = ImageChops.difference(img, bg)
            diff = ImageChops.add(diff, diff, 2.0, -100)
            mask = diff.convert("L")
            img.putalpha(mask)

            img.save(output_path, "PNG")
            print(f"Transparent image saved at {output_path}")

        # Step 2: Insert the image into AutoCAD
        print(f"Inserting image into AutoCAD: {output_path}")
        insert_image_with_correct_scale(acad, output_path)
        convert_background_to_editable(acad, img)

    except Exception as e:
        print(f"Error during image processing: {e}")
        traceback.print_exc()  # Prints full traceback for better diagnosis

def insert_image_with_correct_scale(acad, image_path):
    try:
        print(f"Opening image to insert into AutoCAD: {image_path}")
        with Image.open(image_path) as img:
            width, height = img.size  # Get dimensions in pixels

        scale_x = width
        scale_y = height
        insertion_point = APoint(0, 0)

        raster = acad.doc.ModelSpace.AddRaster(image_path, insertion_point, scale_x / 100, scale_y / 100)
        print(f"Image inserted into Model Space at {insertion_point} with scale ({scale_x}, {scale_y}).")

    except Exception as e:
        print(f"Failed to insert image into AutoCAD: {e}")
        traceback.print_exc()

def convert_image_to_dwg(image_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"The image file {image_path} does not exist.")
    
    image_dir, image_name = os.path.split(image_path)
    base_name, _ = os.path.splitext(image_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    transparent_image_path = os.path.join(image_dir, f"{base_name}_transparent.png")
    dwg_path = os.path.join(image_dir, f"{base_name}_{timestamp}.dwg")

    acad = Autocad(create_if_not_exists=True)
    print("AutoCAD instance started.")

    try:
        remove_background_and_create_editable(acad, image_path, transparent_image_path)

        acad.doc.SaveAs(dwg_path)
        print(f"DWG file saved at {dwg_path}")

        acad.Application.Documents.Open(dwg_path)
        print(f"DWG file opened in AutoCAD: {dwg_path}")

    except Exception as e:
        print(f"Error during conversion: {e}")
        traceback.print_exc()
    finally:
        acad.doc.Close(False)
        print("AutoCAD instance closed.")

if __name__ == "__main__":
    image_path = r"D:\Imagetocadd\C1.jpg"  # Update this path to your .jpg file

    try:
        convert_image_to_dwg(image_path)
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
