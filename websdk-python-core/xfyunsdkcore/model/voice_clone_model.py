from typing import (
    Any,
    Optional,
    Dict
)
from dataclasses import dataclass


@dataclass
class AudioInfo:
    """Type definition for audio information"""
    audio: Optional[bytes] = None
    encoding: Optional[str] = None
    sample_rate: Optional[int] = None
    ced: Optional[str] = None
    type: Optional[str] = None


@dataclass
class PybufInfo:
    """Type definition for pybuf information"""
    text: Optional[str] = None
    type: Optional[str] = None


@dataclass
class ResponseData:
    """Type definition for response data"""
    audio: Optional[AudioInfo] = None
    pybuf: Optional[PybufInfo] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResponseData':
        """Create ResponseData instance from dictionary"""
        audio_data = data.get('audio', {})
        pybuf_data = data.get('pybuf', {})

        return cls(
            audio=AudioInfo(**audio_data) if audio_data else None,
            pybuf=PybufInfo(**pybuf_data) if pybuf_data else None
        )
