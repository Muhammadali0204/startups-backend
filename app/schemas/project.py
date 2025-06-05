from uuid import UUID
from typing import List, Literal, Optional, Union
from pydantic import BaseModel, Field, field_validator


class HeaderBlock(BaseModel):
    type: Literal["header"]
    data: dict

    @field_validator("data")
    @classmethod
    def validate_header(cls, v):
        if "text" not in v or "level" not in v:
            raise ValueError("Invalid header data")
        if not (1 <= v["level"] <= 6):
            raise ValueError("Header level out of range")
        return v


class ParagraphBlock(BaseModel):
    type: Literal["paragraph"]
    data: dict


class ListBlock(BaseModel):
    type: Literal["list"]
    data: dict


class CodeBlock(BaseModel):
    type: Literal["code"]
    data: dict


class InlineCodeBlock(BaseModel):
    type: Literal["inlineCode"]
    data: dict


class TableBlock(BaseModel):
    type: Literal["table"]
    data: dict


class EmbedBlock(BaseModel):
    type: Literal["embed"]
    data: dict

    @field_validator("data")
    @classmethod
    def validate_embed(cls, v):
        if "service" not in v or v["service"] not in ["youtube", "coub"]:
            raise ValueError("Unsupported embed service")
        return v


class ImageBlock(BaseModel):
    type: Literal["image"]
    data: dict

    @field_validator("data")
    @classmethod
    def validate_image(cls, v):
        file_data = v.get("file", {})
        url = file_data.get("url")

        if not url:
            raise ValueError("Image must contain URL")
        if isinstance(url, list):
            if len(url) == 0 or not (
                url[0].startswith("http://") or url[0].startswith("https://")
            ):
                raise ValueError("Image URL must be valid")
        return v


BlockType = Union[
    HeaderBlock,
    ParagraphBlock,
    ListBlock,
    CodeBlock,
    InlineCodeBlock,
    EmbedBlock,
    ImageBlock,
    TableBlock,
]


class CreateProjectData(BaseModel):
    blocks: List[BlockType]
    requiredFunds: int = Field(...)

    @field_validator("requiredFunds")
    def check_amount(cls, v):
        if v <= 0:
            raise ValueError("Enter valid amount")

        return v


class ShortProjectOut(BaseModel):
    id: UUID
    title: str
    subtitle: str
    image_url: Optional[str]

    class Config:
        from_attributes = True
