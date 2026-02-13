# Wildlife Acoustics WAV Metadata Extractor

Python script to extract metadata from Wildlife Acoustics WAV files (SM4, SM3, etc.).

## Overview

Wildlife Acoustics recorders embed metadata in a custom `wamd` (Wildlife Acoustics MetaData) RIFF chunk within WAV files. This script parses that format to extract:

- **GPS Coordinates** (latitude/longitude)
- **Recording DateTime** (with timezone)
- Device model, serial number, firmware version
- Microphone settings and sensitivity
- Temperature at recording time

## Usage

```bash
python3 extract_metadata.py <wav_file>
```

Example:
```bash
python3 extract_metadata.py data/S4A02641_20250220_170000.wav
```

Output:
```
Metadata extracted:
  Model: SM4
  Serial: S4A02641
  Firmware: 2.4.9
  DateTime: 2025-02-20 17:00:00-06:00
  Latitude: 46.83631 N
  Longitude: 92.01620 W
  Temperature: -2.50C
```

## Requirements

- Python 3.6+
- No external dependencies (uses only built-in modules)

## How It Works

The script:
1. Opens the WAV file and reads RIFF chunks
2. Locates the custom `wamd` chunk
3. Parses tag-value pairs within the chunk:
   - Tag ID (2 bytes, little-endian)
   - Size (4 bytes, little-endian)
   - Value (variable length)
4. Decodes GPS coordinates from WGS84 format
5. Parses ISO 8601 timestamps with timezone

## WAMD Chunk Format

The `wamd` chunk uses a proprietary Wildlife Acoustics format with these tag IDs:

| Tag ID | Field Name    | Description                          |
|--------|---------------|--------------------------------------|
| 0x01   | model         | Device model (e.g., "SM4")           |
| 0x02   | serial        | Device serial number                 |
| 0x03   | firmware      | Firmware version                     |
| 0x04   | prefix        | Recording prefix                     |
| 0x05   | timestamp     | ISO 8601 datetime with timezone      |
| 0x14   | gps           | WGS84 GPS coordinates                |
| 0x12   | mic           | Microphone configuration             |
| 0x13   | sensitivity   | Microphone sensitivity               |
| 0x15   | temperature   | Temperature at recording time        |

## License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.
