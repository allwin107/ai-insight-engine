"""
File validation utilities
"""
import os
import magic
from fastapi import UploadFile, HTTPException, status
from app.config import settings

# MIME types for allowed file formats
ALLOWED_MIME_TYPES = {
    'text/csv': ['.csv'],
    'application/vnd.ms-excel': ['.xls'],
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    'text/plain': ['.csv'],  # Sometimes CSV is detected as text/plain
}

def validate_file_extension(filename: str) -> bool:
    """Check if file extension is allowed"""
    ext = os.path.splitext(filename)[1].lower()
    allowed = settings.allowed_extensions_list
    return ext.lstrip('.') in allowed

def validate_file_size(file: UploadFile) -> bool:
    """Check if file size is within limits"""
    file.file.seek(0, 2)  # Seek to end
    size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024  # Convert to bytes
    return size <= max_size

def validate_file_type(file: UploadFile) -> bool:
    """Validate file type using magic bytes (actual file content)"""
    try:
        # Read first 2048 bytes for magic detection
        file.file.seek(0)
        header = file.file.read(2048)
        file.file.seek(0)  # Reset
        
        # Detect MIME type
        mime = magic.from_buffer(header, mime=True)
        
        # Check if MIME type is allowed
        return mime in ALLOWED_MIME_TYPES
    except Exception as e:
        print(f"Magic detection failed: {e}")
        # Fallback to extension check
        return validate_file_extension(file.filename)

def validate_upload_file(file: UploadFile) -> tuple[bool, str]:
    """
    Comprehensive file validation
    Returns: (is_valid, error_message)
    """
    # Check if file exists
    if not file:
        return False, "No file provided"
    
    # Check filename
    if not file.filename:
        return False, "Filename is required"
    
    # Check extension
    if not validate_file_extension(file.filename):
        allowed = ", ".join(settings.allowed_extensions_list)
        return False, f"File type not allowed. Allowed types: {allowed}"
    
    # Check file size
    if not validate_file_size(file):
        return False, f"File too large. Maximum size: {settings.MAX_FILE_SIZE_MB}MB"
    
    # Check actual file type (magic bytes)
    if not validate_file_type(file):
        return False, "File content doesn't match extension. Possible file corruption or security risk."
    
    return True, "File is valid"

async def save_upload_file(file: UploadFile, filepath: str) -> int:
    """
    Save uploaded file to specified path
    Returns: file size in bytes
    """
    try:
        with open(filepath, "wb") as f:
            content = await file.read()
            f.write(content)
            return len(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    finally:
        await file.seek(0)  # Reset file pointer