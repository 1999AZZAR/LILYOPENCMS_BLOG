from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ImageProcessRequest(_message.Message):
    __slots__ = ("image_data", "target_format", "target_width", "target_height", "quality")
    IMAGE_DATA_FIELD_NUMBER: _ClassVar[int]
    TARGET_FORMAT_FIELD_NUMBER: _ClassVar[int]
    TARGET_WIDTH_FIELD_NUMBER: _ClassVar[int]
    TARGET_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    QUALITY_FIELD_NUMBER: _ClassVar[int]
    image_data: bytes
    target_format: str
    target_width: int
    target_height: int
    quality: int
    def __init__(self, image_data: _Optional[bytes] = ..., target_format: _Optional[str] = ..., target_width: _Optional[int] = ..., target_height: _Optional[int] = ..., quality: _Optional[int] = ...) -> None: ...

class ImageProcessResponse(_message.Message):
    __slots__ = ("success", "processed_image", "error_message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    PROCESSED_IMAGE_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    processed_image: bytes
    error_message: str
    def __init__(self, success: bool = ..., processed_image: _Optional[bytes] = ..., error_message: _Optional[str] = ...) -> None: ...
