# Image Metadata Extractor

This Python script extracts detailed metadata from image files using the PIL and exifread libraries. It provides comprehensive information about the image, including camera settings, GPS data, and various other properties.

## Features

- Extracts image properties (format, size, color mode, etc.)
- Retrieves camera information (make, model, software, lens model)
- Captures date and time information
- Provides detailed camera settings (exposure time, F-number, ISO speed, etc.)
- Extracts GPS information (if available)
- Includes various other details (orientation, color space, resolution, etc.)

## Requirements

- Python 3.6+
- Pillow
- exifread

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/brendmung/image-metadata-extractor.git
   ```
2. Navigate to the project directory:
   ```
   cd image-metadata-extractor
   ```
3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Place your image file in the same directory as the script.
2. Modify the `file_path` variable in the script to point to your image file.
3. Run the script:
   ```
   python image_metadata_extractor.py
   ```

The script will print out the extracted metadata in a structured format.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
