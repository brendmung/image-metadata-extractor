import logging
from PIL import Image
import exifread
import os
from fractions import Fraction

# Suppress debug logs from exifread
logging.basicConfig(level=logging.WARNING)

def extract_clean_image_info(file_path):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    info = {}
    
    with Image.open(file_path) as img:
        info['Image Properties'] = {
            'Format': img.format,
            'Size': f"{img.size[0]} x {img.size[1]} pixels",
            'Color Mode': img.mode,
            'File Size': os.path.getsize(file_path),  # Size in bytes
            'DPI': img.info.get('dpi', 'N/A'),
            'Duration': img.info.get('duration', 'N/A')
        }
    
    with open(file_path, 'rb') as img_file:
        tags = exifread.process_file(img_file)
        
        info['Camera Information'] = {
            'Make': str(tags.get('Image Make', 'N/A')),
            'Model': str(tags.get('Image Model', 'N/A')),
            'Software': str(tags.get('Image Software', 'N/A')),
            'Lens Model': str(tags.get('EXIF LensModel', 'N/A')),
            'Camera Serial Number': str(tags.get('EXIF CameraSerialNumber', 'N/A')),
            'Date of Manufacture': str(tags.get('EXIF DateTimeOriginal', 'N/A'))
        }
        
        info['Date and Time'] = {
            'Taken': str(tags.get('EXIF DateTimeOriginal', 'N/A')),
            'Digitized': str(tags.get('EXIF DateTimeDigitized', 'N/A')),
            'DateTime': str(tags.get('EXIF DateTime', 'N/A')),
            'Time Zone Offset': str(tags.get('EXIF OffsetTimeOriginal', 'N/A'))
        }
        
        info['Camera Settings'] = {
            'Exposure Time': _fraction_to_readable(tags.get('EXIF ExposureTime'), 'N/A'),
            'F-Number': _fraction_to_readable(tags.get('EXIF FNumber'), 'N/A'),
            'ISO Speed': str(tags.get('EXIF ISOSpeedRatings', 'N/A')),
            'Focal Length': _fraction_to_readable(tags.get('EXIF FocalLength'), 'N/A ') + 'mm',
            'Focal Length (35mm equivalent)': str(tags.get('EXIF FocalLengthIn35mmFilm', 'N/A ')) + 'mm',
            'Exposure Mode': _get_exposure_mode(tags),
            'White Balance': _get_white_balance(tags),
            'Flash': _get_flash_info(tags),
            'Metering Mode': _get_metering_mode(tags),
            'Exposure Program': _get_exposure_program(tags),
            'Brightness Value': _fraction_to_readable(tags.get('EXIF BrightnessValue'), 'N/A'),
            'Exposure Bias': _fraction_to_readable(tags.get('EXIF ExposureBiasValue'), 'N/A'),
            'Max Aperture Value': _fraction_to_readable(tags.get('EXIF MaxApertureValue'), 'N/A'),
            'Digital Zoom Ratio': _fraction_to_readable(tags.get('EXIF DigitalZoomRatio'), 'N/A'),
            'Scene Capture Type': _get_scene_capture_type(tags),
            'Shutter Speed Value': _fraction_to_readable(tags.get('EXIF ShutterSpeedValue'), 'N/A'),
            'Aperture Value': _fraction_to_readable(tags.get('EXIF ApertureValue'), 'N/A'),
            'Color Space': _get_color_space(tags),
            'Focus Mode': _get_focus_mode(tags),
            'Shooting Mode': _get_shooting_mode(tags),
            'Noise Reduction': _get_noise_reduction(tags),
            'Subject Area': _get_subject_area(tags)
        }
        
        info['GPS Information'] = _extract_gps_info(tags)
        
        info['Other Details'] = {
            'Orientation': _get_orientation(tags),
            'YCbCr Positioning': _get_ycbcr_positioning(tags),
            'Resolution': _get_resolution(tags),
            'Unique Image ID': str(tags.get('EXIF ImageUniqueID', 'N/A')),
            'Exif Version': str(tags.get('EXIF ExifVersion', 'N/A')),
            'Compression': str(tags.get('EXIF Compression', 'N/A')),
            'Image Width': str(tags.get('EXIF ExifImageWidth', 'N/A')),
            'Image Length': str(tags.get('EXIF ExifImageLength', 'N/A')),
            'Subject Distance': _fraction_to_readable(tags.get('EXIF SubjectDistance'), 'N/A'),
            'Metering Mode': _get_metering_mode(tags),
            'File Name': os.path.basename(file_path),
            'File Path': file_path
        }
    
    return info

def _fraction_to_readable(fraction, default_value='Unknown'):
    if not fraction:
        return default_value
    if isinstance(fraction.values[0], Fraction):
        return str(fraction.values[0])
    return f"{fraction.values[0]}/{fraction.values[1]}"

def _get_exposure_mode(tags):
    modes = {0: 'Auto', 1: 'Manual', 2: 'Auto bracket'}
    exposure_mode_tag = tags.get('EXIF ExposureMode')
    if exposure_mode_tag:
        return modes.get(exposure_mode_tag.values[0], 'Unknown')
    else:
        return 'N/A'

def _get_white_balance(tags):
    modes = {0: 'Auto', 1: 'Manual'}
    white_balance_tag = tags.get('EXIF WhiteBalance')
    if white_balance_tag:
        return modes.get(white_balance_tag.values[0], 'Unknown')
    else:
        return 'N/A'

def _get_flash_info(tags):
    flash_info = tags.get('EXIF Flash', None)
    if flash_info is not None:
        flash_value = flash_info.values[0]
        if flash_value == 0:
            return 'Flash did not fire'
        elif flash_value == 1:
            return 'Flash fired'
        else:
            return 'Unknown'
    else:
        return 'N/A'

def _extract_gps_info(tags):
    def _convert_to_degrees(value):
        d = float(value.values[0].num) / float(value.values[0].den)
        m = float(value.values[1].num) / float(value.values[1].den)
        s = float(value.values[2].num) / float(value.values[2].den)
        return d + (m / 60.0) + (s / 3600.0)

    lat = tags.get('GPS GPSLatitude')
    lat_ref = tags.get('GPS GPSLatitudeRef')
    lon = tags.get('GPS GPSLongitude')
    lon_ref = tags.get('GPS GPSLongitudeRef')
    alt = tags.get('GPS GPSAltitude')
    
    gps_info = {}
    if lat and lat_ref and lon and lon_ref:
        latitude = _convert_to_degrees(lat)
        longitude = _convert_to_degrees(lon)
        
        # Adjust for hemisphere
        if lat_ref.values[0] == 'S':
            latitude *= -1
        if lon_ref.values[0] == 'W':
            longitude *= -1
        
        gps_info['Latitude'] = f"{latitude:.5f}° {'S' if lat_ref.values[0] == 'S' else 'N'}"
        gps_info['Longitude'] = f"{longitude:.5f}° {'W' if lon_ref.values[0] == 'W' else 'E'}"
        # Create Google Maps link
        gps_info['Google Maps Link'] = f"https://www.google.com/maps?q={latitude},{longitude}"
    
    if alt:
        gps_info['Altitude'] = f"{float(alt.values[0].num) / float(alt.values[0].den):.2f} meters"
    
    return gps_info if gps_info else 'N/A'

def _get_orientation(tags):
    orientations = {
        1: "Normal",
        2: "Mirrored horizontally",
        3: "Rotated 180 degrees",
        4: "Mirrored vertically",
        5: "Mirrored horizontally and rotated 270 degrees CW",
        6: "Rotated 90 degrees CW",
        7: "Mirrored horizontally and rotated 90 degrees CW",
        8: "Rotated 270 degrees CW"
    }
    orientation_tag = tags.get('Image Orientation')
    if isinstance(orientation_tag, exifread.classes.IfdTag):
        orientation = orientation_tag.values[0]
        return orientations.get(orientation, 'N/A')
    else:
        return 'N/A'

def _get_color_space(tags):
    color_spaces = {1: 'sRGB', 2: 'Adobe RGB'}
    color_space_tag = tags.get('EXIF ColorSpace')
    if isinstance(color_space_tag, exifread.classes.IfdTag):
        color_space = color_space_tag.values[0]
        return color_spaces.get(color_space, 'N/A')
    else:
        return 'N/A'

def _get_metering_mode(tags):
    modes = {
        0: 'Unknown',
        1: 'Average',
        2: 'Center-weighted average',
        3: 'Spot',
        4: 'Multi-spot',
        5: 'Pattern',
        6: 'Partial'
    }
    metering_mode_tag = tags.get('EXIF MeteringMode')
    if metering_mode_tag:
        return modes.get(metering_mode_tag.values[0], 'Unknown')
    else:
        return 'N/A'

def _get_exposure_program(tags):
    programs = {
        0: 'Not defined',
        1: 'Manual',
        2: 'Normal program',
        3: 'Aperture priority',
        4: 'Shutter priority',
        5: 'Creative program',
        6: 'Action program',
        7: 'Portrait mode',
        8: 'Landscape mode'
    }
    exposure_program_tag = tags.get('EXIF ExposureProgram')
    if exposure_program_tag:
        return programs.get(exposure_program_tag.values[0], 'Unknown')
    else:
        return 'N/A'

def _get_scene_capture_type(tags):
    types = {
        0: 'Standard',
        1: 'Landscape',
        2: 'Portrait',
        3: 'Night scene'
    }
    scene_capture_type_tag = tags.get('EXIF SceneCaptureType')
    if scene_capture_type_tag:
        return types.get(scene_capture_type_tag.values[0], 'Unknown')
    else:
        return 'N/A'

def _get_resolution(tags):
    x_resolution = _fraction_to_readable(tags.get('Image XResolution'), 'N/A')
    y_resolution = _fraction_to_readable(tags.get('Image YResolution'), 'N/A')
    resolution_unit = _get_resolution_unit(tags)
    return f"{x_resolution} x {y_resolution} {resolution_unit}"

def _get_resolution_unit(tags):
    units = {
        1: 'No absolute unit of measurement',
        2: 'Inches',
        3: 'Centimeters'
    }
    resolution_unit_tag = tags.get('Image ResolutionUnit')
    if resolution_unit_tag:
        return units.get(resolution_unit_tag.values[0], 'Unknown')
    else:
        return 'N/A'

def _get_ycbcr_positioning(tags):
    positions = {
        1: 'Centered',
        2: 'Co-sited'
    }
    ycbcr_positioning_tag = tags.get('Image YCbCrPositioning')
    if ycbcr_positioning_tag:
        return positions.get(ycbcr_positioning_tag.values[0], 'Unknown')
    else:
        return 'N/A'

def _get_focus_mode(tags):
    focus_modes = {0: 'Manual', 1: 'Auto'}
    focus_mode_tag = tags.get('EXIF FocusMode')
    if focus_mode_tag:
        return focus_modes.get(focus_mode_tag.values[0], 'Unknown')
    else:
        return 'N/A'

def _get_shooting_mode(tags):
    shooting_modes = {0: 'Normal', 1: 'Portrait', 2: 'Landscape'}
    shooting_mode_tag = tags.get('EXIF ShootingMode')
    if shooting_mode_tag:
        return shooting_modes.get(shooting_mode_tag.values[0], 'Unknown')
    else:
        return 'N/A'

def _get_noise_reduction(tags):
    noise_reduction_tag = tags.get('EXIF NoiseReduction')
    if noise_reduction_tag:
        return 'On' if noise_reduction_tag.values[0] == 1 else 'Off'
    else:
        return 'N/A'

def _get_subject_area(tags):
    subject_area_tag = tags.get('EXIF SubjectArea')
    if subject_area_tag:
        return f"{subject_area_tag.values}"
    else:
        return 'N/A'

def print_clean_image_info(info):
    for category, data in info.items():
        print(f"\n{category}:")
        if isinstance(data, dict):
            for key, value in data.items():
                print(f"  {key}: {value}")
        else:
            print(f"  {data}")

if __name__ == "__main__":
    file_path = 'my_pic.jpg'  # Replace with the actual path to your image
    image_info = extract_clean_image_info(file_path)
    print_clean_image_info(image_info)