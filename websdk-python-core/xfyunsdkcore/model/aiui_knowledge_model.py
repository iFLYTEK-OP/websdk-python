from dataclasses import dataclass, asdict, field
from typing import (
    Any,
    List,
    Union,
    Dict
)


@dataclass
class AiUiCreate:
    uid: int = None
    name: str = None
    description: str = None
    sid: str = None
    channel: str = None

    def to_dict(self):
        return asdict(self)

    def create_check(self):
        if not self.uid:
            raise ValueError("uid不能为空")

        if not self.name:
            raise ValueError("知识库名称不能为空")


@dataclass
class AiUiFileInfo:
    fileName: str = None
    filePath: str = None
    fileSize: int = None


@dataclass
class Repo:
    groupId: str = None
    repoName: str = None
    threshold: str = None


@dataclass
class ParseConfig:
    chunkType: str = None
    separator: str = None
    cutLevel: str = None
    lengthRange: str = None
    cutOff: str = None


@dataclass
class AiUiUpload:
    uid: int = None
    sid: str = None
    groupId: str = None
    files: List[object] = field(default_factory=list)
    labels: str = None
    fileList: List[AiUiFileInfo] = field(default_factory=list)
    parseConfig: ParseConfig = None

    def to_dict(self):
        return asdict(self)

    def upload_check(self):
        if self.uid is None:
            raise ValueError("uid不能为空")
        if not self.groupId or not self.groupId.strip():
            raise ValueError("groupId不能为空")
        if not self.files and not self.fileList:
            raise ValueError("files和fileList不能同时为空")


@dataclass
class AiUiDelete:
    uid: int = None
    sid: str = None
    groupId: str = None
    docId: str = None
    repoId: str = None

    def to_dict(self):
        return asdict(self)

    def delete_check(self):
        if self.uid is None:
            raise ValueError("uid不能为空")


@dataclass
class AiUiSearch:
    uid: int = None
    appId: str = None
    sceneName: str = None
    sid: str = None
    channel: str = None

    def to_dict(self):
        return asdict(self)

    def search_check(self):
        if self.uid is None:
            raise ValueError("uid不能为空")

        if self.sceneName is None:
            raise ValueError("sceneName不能为空")

        if self.appId is None:
            raise ValueError("appId不能为空")


@dataclass
class AiUiLink:
    uid: int = None
    appId: str = None
    sceneName: str = None
    sid: str = None
    repos: List[Repo] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)

    def link_check(self):
        if self.uid is None:
            raise ValueError("uid不能为空")

        if self.sceneName is None:
            raise ValueError("sceneName不能为空")

        if self.appId is None:
            raise ValueError("appId不能为空")
