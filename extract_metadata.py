#!/usr/bin/env python3
"""
Extract metadata from Wildlife Acoustics WAV files.
The metadata is stored in a custom 'wamd' chunk.
"""

import struct
from datetime import datetime
from pathlib import Path


def parse_wamd_chunk(data):
    """Parse the wamd chunk data containing metadata tags."""
    metadata = {}
    offset = 0

    while offset < len(data) - 6:
        # Read tag ID (1 byte), skip byte (1 byte), and size (4 bytes)
        tag_id = data[offset]
        # offset+1 is a skip byte (usually 0x00)
        tag_size = struct.unpack('<I', data[offset+2:offset+6])[0]
        offset += 6

        # Read tag value
        if offset + tag_size > len(data):
            break

        tag_value = data[offset:offset+tag_size]
        offset += tag_size

        # Decode value as string (removing null terminator if present)
        try:
            value_str = tag_value.decode('utf-8').rstrip('\x00')
        except:
            # For binary data, skip it
            continue

        # Map tag IDs to names
        tag_names = {
            0x01: 'model',
            0x02: 'serial',
            0x03: 'firmware',
            0x04: 'prefix',
            0x05: 'timestamp',
            0x14: 'gps',
            0x10: 'software',
            0x12: 'mic',
            0x13: 'sensitivity',
            0x15: 'temperature',
        }

        tag_name = tag_names.get(tag_id, f'unknown_{tag_id:02x}')
        metadata[tag_name] = value_str

    return metadata


def extract_wav_metadata(wav_path):
    """Extract metadata from a Wildlife Acoustics WAV file."""
    with open(wav_path, 'rb') as f:
        # Read RIFF header
        riff = f.read(12)
        if riff[:4] != b'RIFF' or riff[8:12] != b'WAVE':
            raise ValueError('Not a valid WAV file')

        # Read chunks
        while True:
            chunk_header = f.read(8)
            if len(chunk_header) < 8:
                break

            chunk_id = chunk_header[:4]
            chunk_size = struct.unpack('<I', chunk_header[4:8])[0]
            chunk_data = f.read(chunk_size)

            if chunk_id == b'wamd':
                metadata = parse_wamd_chunk(chunk_data)

                # Parse GPS data
                if 'gps' in metadata:
                    gps_parts = metadata['gps'].split(',')
                    if len(gps_parts) >= 5:
                        metadata['latitude'] = float(gps_parts[1])
                        metadata['longitude'] = float(gps_parts[3])
                        metadata['latitude_dir'] = gps_parts[2]
                        metadata['longitude_dir'] = gps_parts[4]

                        # Convert to signed coordinates
                        if metadata['latitude_dir'] == 'S':
                            metadata['latitude'] = -metadata['latitude']
                        if metadata['longitude_dir'] == 'E':
                            metadata['longitude'] = -metadata['longitude']

                # Parse timestamp
                if 'timestamp' in metadata:
                    # Format: 2025-02-20 17:00:00-06:00
                    timestamp_str = metadata['timestamp']
                    metadata['datetime'] = datetime.fromisoformat(timestamp_str)

                return metadata

            # Handle odd-sized chunks (WAV requires even alignment)
            if chunk_size % 2:
                f.read(1)

    return None


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print('Usage: python extract_metadata.py <wav_file>')
        sys.exit(1)

    wav_file = sys.argv[1]
    metadata = extract_wav_metadata(wav_file)

    if metadata:
        print('Metadata extracted:')
        print(f"  Model: {metadata.get('model', 'N/A')}")
        print(f"  Serial: {metadata.get('serial', 'N/A')}")
        print(f"  Firmware: {metadata.get('firmware', 'N/A')}")
        print(f"  DateTime: {metadata.get('datetime', 'N/A')}")
        print(f"  Latitude: {metadata.get('latitude', 'N/A')} {metadata.get('latitude_dir', '')}")
        print(f"  Longitude: {metadata.get('longitude', 'N/A')} {metadata.get('longitude_dir', '')}")
        print(f"  Temperature: {metadata.get('temperature', 'N/A')}")
        print('\nAll fields:')
        for key, value in sorted(metadata.items()):
            if key not in ['datetime']:  # datetime is already printed
                print(f"  {key}: {value}")
    else:
        print('No metadata found in WAV file')
