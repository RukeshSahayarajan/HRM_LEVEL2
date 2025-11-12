# ============================================================
# FILE: modules/text_extractor.py
# ============================================================
"""
Text Extractor Module
Handles extraction from PDF, DOCX, and Images (with OCR)
"""

import os
import glob
from pdfminer.high_level import extract_text
import docx2txt
from PIL import Image
from config import SUPPORTED_EXTENSIONS


def extract_text_from_file(file_path_or_obj):
    """
    Extract text from PDF, DOCX, or Image

    Args:
        file_path_or_obj: File path (string) or file object (uploaded file)

    Returns:
        str: Extracted text or None if failed
    """
    try:
        # Check if it's a file path (string) or file object
        if isinstance(file_path_or_obj, str):
            return _extract_from_path(file_path_or_obj)
        else:
            return _extract_from_uploaded_file(file_path_or_obj)
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None


def _extract_from_path(file_path):
    """Extract text from file path"""
    file_extension = file_path.lower().split('.')[-1]

    if file_extension == 'pdf':
        return extract_text(file_path)

    elif file_extension in ['docx', 'doc']:
        return docx2txt.process(file_path)

    elif file_extension in ['png', 'jpg', 'jpeg', 'bmp']:
        print("⚠️ Image OCR not supported with Groq. Please use PDF/DOCX format.")
        return None

    return None


def _extract_from_uploaded_file(file_obj):
    """Extract text from uploaded file object"""
    file_extension = file_obj.name.lower().split('.')[-1]

    if file_extension == 'pdf':
        with open("temp_file.pdf", "wb") as f:
            f.write(file_obj.getbuffer())
        text = extract_text("temp_file.pdf")
        os.remove("temp_file.pdf")
        return text

    elif file_extension in ['docx', 'doc']:
        with open("temp_file.docx", "wb") as f:
            f.write(file_obj.getbuffer())
        text = docx2txt.process("temp_file.docx")
        os.remove("temp_file.docx")
        return text

    elif file_extension in ['png', 'jpg', 'jpeg', 'bmp']:
        print("⚠️ Image OCR not supported with Groq. Please use PDF/DOCX format.")
        return None

    return None


def get_files_from_folder(folder_path):
    """
    Get all supported files from a folder

    Args:
        folder_path: Path to folder containing files

    Returns:
        list: List of file paths
    """
    files = []

    for ext in SUPPORTED_EXTENSIONS:
        files.extend(glob.glob(os.path.join(folder_path, f'*.{ext}')))
        files.extend(glob.glob(os.path.join(folder_path, f'*.{ext.upper()}')))

    return files


def validate_file_format(filename):
    """
    Check if file format is supported

    Args:
        filename: Name of the file

    Returns:
        bool: True if supported, False otherwise
    """
    extension = filename.lower().split('.')[-1]
    return extension in SUPPORTED_EXTENSIONS