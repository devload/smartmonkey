"""Helper utilities for SmartMonkey"""

import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional
from PIL import Image


def ensure_dir(path: str) -> None:
    """
    Ensure directory exists, create if not

    Args:
        path: Directory path
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def get_timestamp() -> str:
    """
    Get current timestamp string

    Returns:
        Timestamp in format YYYY-MM-DD_HH-MM-SS
    """
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def calculate_hash(text: str) -> str:
    """
    Calculate MD5 hash of text

    Args:
        text: Input text

    Returns:
        MD5 hash string
    """
    return hashlib.md5(text.encode()).hexdigest()


def compress_image(image_path: str, quality: int = 80, max_size: Optional[tuple] = None) -> None:
    """
    Compress image file

    Args:
        image_path: Path to image file
        quality: JPEG quality (1-100)
        max_size: Optional max size as (width, height)
    """
    if not os.path.exists(image_path):
        return

    try:
        with Image.open(image_path) as img:
            # Resize if max_size specified
            if max_size:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Convert RGBA to RGB if saving as JPEG
            if img.mode == 'RGBA':
                img = img.convert('RGB')

            # Save with compression
            img.save(image_path, optimize=True, quality=quality)
    except Exception:
        # Silently ignore compression errors
        pass


def calculate_similarity(str1: str, str2: str) -> float:
    """
    Calculate similarity between two strings using simple matching

    Args:
        str1: First string
        str2: Second string

    Returns:
        Similarity score between 0.0 and 1.0
    """
    if not str1 or not str2:
        return 0.0

    if str1 == str2:
        return 1.0

    # Simple character-based similarity
    set1 = set(str1.lower())
    set2 = set(str2.lower())

    intersection = len(set1 & set2)
    union = len(set1 | set2)

    return intersection / union if union > 0 else 0.0
