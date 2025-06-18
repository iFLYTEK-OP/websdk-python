from dataclasses import dataclass, asdict, field
from typing import (
    Any,
    List,
    Union,
    Dict
)


@dataclass
class PPTSearch:
    style: str = None
    color: str = None
    industry: str = None
    pageNum: int = 1
    pageSize: int = 10
    url: str = None

    def to_dict(self):
        return asdict(self)


@dataclass
class ChapterContents:
    chapterTitle: str = None
    chapterContents: Any = None


@dataclass
class Chapters:
    chapterTitle: str = None
    chapterContents: List[ChapterContents] = field(default_factory=list)


@dataclass
class Outline:
    title: str = None
    subTitle: str = None
    chapters: List[Chapters] = field(default_factory=list)


@dataclass
class PPTCreate:
    query: str = None
    file: object = None
    fileUrl: str = None
    fileName: str = None
    templateId: str = None
    businessId: str = None
    author: str = "讯飞智文"
    isCardNote: bool = False
    search: bool = False
    language: str = "cn"
    isFigure: bool = False
    aiImage: str = None
    outline: Union[Outline, Dict[str, Any]] = None
    outlineSid: str = None

    def to_dict(self):
        return asdict(self)

    def create_check(self):
        if self.query and len(self.query) > 8000:
            raise ValueError("query参数最大8000字符")

        if not self.query and not self.file and not self.fileUrl:
            raise ValueError("query、file、fileUrl参数必填其一")

        if (self.file or self.fileUrl) and not self.fileName:
            raise ValueError("文件名称不能为空")

    def to_form_data_body(self):
        form_data = {}
        if self.query:
            form_data['query'] = self.query
        if self.fileUrl:
            form_data['fileUrl'] = self.fileUrl
        if self.fileName:
            form_data['fileName'] = self.fileName
        if self.templateId:
            form_data['templateId'] = self.templateId
        if self.businessId:
            form_data['businessId'] = self.businessId
        if self.author:
            form_data['author'] = self.author
        if self.isCardNote is not None:
            form_data['isCardNote'] = str(self.isCardNote).lower()
        if self.search is not None:
            form_data['search'] = str(self.search).lower()
        if self.language:
            form_data['language'] = self.language
        if self.isFigure is not None:
            form_data['isFigure'] = str(self.isFigure).lower()
        if self.aiImage:
            form_data['aiImage'] = self.aiImage
        return form_data

    def create_out_line_check(self):
        if not self.query or len(self.query) > 8000:
            raise ValueError("query参数不合法")

    def create_outline_by_doc_check(self):
        if not self.fileName:
            raise ValueError("fileName不能为空")

        if not self.fileUrl and not self.file:
            raise ValueError("file、fileUrl必填其一")

    def create_ppt_by_outline_check(self):
        if not self.query or len(self.query) > 8000:
            raise ValueError("query参数不合法")

        if not self.outline:
            raise ValueError("大纲内容不能为空")
