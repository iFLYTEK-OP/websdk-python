from dataclasses import dataclass, asdict


@dataclass
class UploadParam:
    fileName: str
    fileSize: int
    language: str = None
    callbackUrl: str = None
    hotWord: str = None
    candidate: int = None
    roleType: int = None
    roleNum: int = None
    pd: str = None
    audioUrl: str = None
    standardWav: int = None
    languageType: int = None
    trackMode: int = None
    transLanguage: str = None
    transMode: int = None
    eng_seg_max: int = None
    eng_seg_min: int = None
    eng_seg_weight: float = None
    eng_smoothproc: bool = None
    eng_colloqproc: bool = None
    eng_vad_mdn: int = None
    eng_vad_margin: int = None
    eng_rlang: int = None
    audioMode: str = "fileStream"
    duration: int = 60

    def to_dict(self):
        return asdict(self)
