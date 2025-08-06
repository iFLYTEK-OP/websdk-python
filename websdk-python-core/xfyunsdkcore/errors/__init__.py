from ..log.logger import logger


class BusinessException(Exception):
    """Base class for Client errors"""


class VoiceCloneError(Exception):
    """Custom exception for Voice Clone related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"VoiceCloneError: {message} (Error Code: {error_code})")
        logger.error(f"VoiceCloneError occurred: {message} (Error Code: {error_code})")


class AIPPTError(Exception):
    """Custom exception for Voice Clone related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"AIPPTError: {message} (Error Code: {error_code})")
        logger.error(f"AIPPTError occurred: {message} (Error Code: {error_code})")


class RtasrError(Exception):
    """Custom exception for Rtasr related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"RtasrError: {message} (Error Code: {error_code})")
        logger.error(f"RtasrError occurred: {message} (Error Code: {error_code})")


class IatError(Exception):
    """Custom exception for Iat related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"IatError: {message} (Error Code: {error_code})")
        logger.error(f"IatError occurred: {message} (Error Code: {error_code})")


class IseError(Exception):
    """Custom exception for Ise related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"IseError: {message} (Error Code: {error_code})")
        logger.error(f"IseError occurred: {message} (Error Code: {error_code})")


class IgrError(Exception):
    """Custom exception for Igr related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"IgrError: {message} (Error Code: {error_code})")
        logger.error(f"IgrError occurred: {message} (Error Code: {error_code})")


class TtsError(Exception):
    """Custom exception for TTS related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"TtsError: {message} (Error Code: {error_code})")
        logger.error(f"TtsError occurred: {message} (Error Code: {error_code})")


class LFasrError(Exception):
    """Custom exception for LFasr related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"LFasrError: {message} (Error Code: {error_code})")
        logger.error(f"LFasrError occurred: {message} (Error Code: {error_code})")


class OralError(Exception):
    """Custom exception for Oral related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"OralError: {message} (Error Code: {error_code})")
        logger.error(f"OralError occurred: {message} (Error Code: {error_code})")


class QbhError(Exception):
    """Custom exception for Qbh related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"QbhError: {message} (Error Code: {error_code})")
        logger.error(f"QbhError occurred: {message} (Error Code: {error_code})")


class SparkIatError(Exception):
    """Custom exception for Spark Iat related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"SparkIat: {message} (Error Code: {error_code})")
        logger.error(f"SparkIat occurred: {message} (Error Code: {error_code})")


class ResumeGenError(Exception):
    """Custom exception for Qbh related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"QbhError: {message} (Error Code: {error_code})")
        logger.error(f"QbhError occurred: {message} (Error Code: {error_code})")


class BankCardError(Exception):
    """Custom exception for bank card related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"BankCardError: {message} (Error Code: {error_code})")
        logger.error(f"BankCardError occurred: {message} (Error Code: {error_code})")


class BusinessCardError(Exception):
    """Custom exception for Business Card related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"BusinessCardError: {message} (Error Code: {error_code})")
        logger.error(f"BusinessCardError occurred: {message} (Error Code: {error_code})")


class FingerOCRError(Exception):
    """Custom exception for Finger OCR related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"FingerOCRError: {message} (Error Code: {error_code})")
        logger.error(f"FingerOCRError occurred: {message} (Error Code: {error_code})")


class WordOCRError(Exception):
    """Custom exception for General Words related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"WordOCRError: {message} (Error Code: {error_code})")
        logger.error(f"WordOCRError occurred: {message} (Error Code: {error_code})")


class ImageWordOCRError(Exception):
    """Custom exception for Image Word related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"ImageWordOCRError: {message} (Error Code: {error_code})")
        logger.error(f"ImageWordOCRError occurred: {message} (Error Code: {error_code})")


class RecOCRError(Exception):
    """Custom exception for rec ocr related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"RecOCRError: {message} (Error Code: {error_code})")
        logger.error(f"RecOCRError occurred: {message} (Error Code: {error_code})")


class IntsigOCRError(Exception):
    """Custom exception for Intsig OCR related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"IntsigOCRError: {message} (Error Code: {error_code})")
        logger.error(f"IntsigOCRError occurred: {message} (Error Code: {error_code})")


class ItrOCRError(Exception):
    """Custom exception for Itr OCR related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"ItrOCRError: {message} (Error Code: {error_code})")
        logger.error(f"ItrOCRError occurred: {message} (Error Code: {error_code})")


class JDOCRError(Exception):
    """Custom exception for JD OCR related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"JDOCRError: {message} (Error Code: {error_code})")
        logger.error(f"JDOCRError occurred: {message} (Error Code: {error_code})")


class PDRecError(Exception):
    """Custom exception for PD Rec related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"PDRecError: {message} (Error Code: {error_code})")
        logger.error(f"PDRecError occurred: {message} (Error Code: {error_code})")


class InvoiceOCRError(Exception):
    """Custom exception for Invoice OCR related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"InvoiceOCRError: {message} (Error Code: {error_code})")
        logger.error(f"InvoiceOCRError occurred: {message} (Error Code: {error_code})")


class ModerationError(Exception):
    """Custom exception for Moderation related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"ModerationError: {message} (Error Code: {error_code})")
        logger.error(f"ModerationError occurred: {message} (Error Code: {error_code})")


class TextCheckError(Exception):
    """Custom exception for TextCheck related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"TextCheckError: {message} (Error Code: {error_code})")
        logger.error(f"TextCheckError occurred: {message} (Error Code: {error_code})")


class TextProofError(Exception):
    """Custom exception for TextProof related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"TextProofError: {message} (Error Code: {error_code})")
        logger.error(f"TextProofError occurred: {message} (Error Code: {error_code})")


class TextRewriteError(Exception):
    """Custom exception for TextRewrite related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"TextRewriteError: {message} (Error Code: {error_code})")
        logger.error(f"TextRewriteError occurred: {message} (Error Code: {error_code})")


class TranslateError(Exception):
    """Custom exception for Translate related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"TranslateError: {message} (Error Code: {error_code})")
        logger.error(f"TranslateError occurred: {message} (Error Code: {error_code})")


class SimInterpError(Exception):
    """Custom exception for SimInterp related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"SimInterpError: {message} (Error Code: {error_code})")
        logger.error(f"SimInterpError occurred: {message} (Error Code: {error_code})")


class AntiSpoofError(Exception):
    """Custom exception for AntiSpoof related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"AntiSpoofError: {message} (Error Code: {error_code})")
        logger.error(f"AntiSpoofError occurred: {message} (Error Code: {error_code})")


class FaceCompareError(Exception):
    """Custom exception for Face Compare related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"FaceCompareError: {message} (Error Code: {error_code})")
        logger.error(f"FaceCompareError occurred: {message} (Error Code: {error_code})")


class FaceDetectError(Exception):
    """Custom exception for Face Detect related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"FaceDetectError: {message} (Error Code: {error_code})")
        logger.error(f"FaceDetectError occurred: {message} (Error Code: {error_code})")


class FaceStatusError(Exception):
    """Custom exception for Face Status related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"FaceStatusError: {message} (Error Code: {error_code})")
        logger.error(f"FaceStatusError occurred: {message} (Error Code: {error_code})")


class FaceVerificationError(Exception):
    """Custom exception for Face Verification related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"FaceVerificationError: {message} (Error Code: {error_code})")
        logger.error(f"FaceVerificationError occurred: {message} (Error Code: {error_code})")


class SilentDetectionError(Exception):
    """Custom exception for Silent Detection related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"SilentDetectionError: {message} (Error Code: {error_code})")
        logger.error(f"SilentDetectionError occurred: {message} (Error Code: {error_code})")


class TupApiError(Exception):
    """Custom exception for Tup Api related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"TupApiError: {message} (Error Code: {error_code})")
        logger.error(f"TupApiError occurred: {message} (Error Code: {error_code})")


class WatermarkVerificationError(Exception):
    """Custom exception for Watermark Verification related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"WatermarkVerificationError: {message} (Error Code: {error_code})")
        logger.error(f"WatermarkVerificationError occurred: {message} (Error Code: {error_code})")


class AgentClientError(Exception):
    """Custom exception for Spark Agent related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"AgentClientError: {message} (Error Code: {error_code})")
        logger.error(f"AgentClientError occurred: {message} (Error Code: {error_code})")


class OralChatClientError(Exception):
    """Custom exception for Oral Chat related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"OralChatClientError: {message} (Error Code: {error_code})")
        logger.error(f"OralChatClientError occurred: {message} (Error Code: {error_code})")


class LlmOcrError(Exception):
    """Custom exception for LLM OCR client related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"LlmOcrError: {message} (Error Code: {error_code})")
        logger.error(f"LlmOcrError occurred: {message} (Error Code: {error_code})")


class SignatureError(Exception):
    """Custom exception for Voice Clone related errors"""

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code
        super().__init__(f"SignatureError: {message} (Error Code: {error_code})")
        logger.error(f"SignatureError occurred: {message} (Error Code: {error_code})")
