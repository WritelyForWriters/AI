from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field


class SynopsisSettings(BaseModel):
    genre: Optional[str] = None
    length: Optional[str] = None
    purpose: Optional[str] = None
    logline: Optional[str] = None
    example: Optional[str] = None


class WorldviewSettings(BaseModel):
    geography: Optional[str] = None
    history: Optional[str] = None
    politics: Optional[str] = None
    society: Optional[str] = None
    religion: Optional[str] = None
    economy: Optional[str] = None
    technology: Optional[str] = None
    lifestyle: Optional[str] = None
    language: Optional[str] = None
    culture: Optional[str] = None
    species: Optional[str] = None
    occupation: Optional[str] = None
    conflict: Optional[str] = None
    custom_field: Optional[str] = None


class CharacterSettings(BaseModel):
    intro: Optional[str] = None
    character_name: Optional[str] = None
    age: Optional[str] = None
    gender: Optional[str] = None
    character_occupation: Optional[str] = None
    appearance: Optional[str] = None
    personality: Optional[str] = None
    characteristic: Optional[str] = None
    relationship: Optional[str] = None


class PlotSettings(BaseModel):
    exposition: Optional[str] = None
    complication: Optional[str] = None
    climax: Optional[str] = None
    resolution: Optional[str] = None


class IdeanoteSettings(BaseModel):
    idea_title: Optional[str] = None
    idea_content: Optional[str] = None


class CustomFieldSettings(BaseModel):
    section_code: Optional[str] = None
    custom_field_name: Optional[str] = None
    custom_field_content: Optional[str] = None


class StorySettings(BaseModel):
    """소설 설정 모델"""

    synopsis: Optional[SynopsisSettings] = Field(default_factory=SynopsisSettings)
    worldview: Optional[WorldviewSettings] = Field(default_factory=WorldviewSettings)
    character: Optional[List[CharacterSettings]] = Field(default_factory=list)
    plot: Optional[PlotSettings] = Field(default_factory=PlotSettings)
    ideanote: Optional[IdeanoteSettings] = Field(default_factory=IdeanoteSettings)
    custom_field: Optional[List[CustomFieldSettings]] = Field(default_factory=list)


def settings_to_xml(
    settings: Dict[str, Union[Dict[str, str], List[Dict[str, str]]]],
) -> str:
    """설정 딕셔너리를 XML 문자열로 변환"""
    xml_parts: List[str] = []

    for section_name, section_data in settings.items():
        if not section_data:
            continue

        if section_name in ["character", "custom_field"]:
            # 리스트 형태의 섹션 처리
            if isinstance(section_data, list):
                for idx, item in enumerate(section_data, 1):
                    xml_parts.append(f"  <{section_name}_{idx}>")
                    for field, value in item.items():
                        if value:
                            xml_parts.append(f"    <{field}>{value}</{field}>")
                    xml_parts.append(f"  </{section_name}_{idx}>")
        else:
            # 일반 딕셔너리 섹션 처리
            if isinstance(section_data, dict):
                xml_parts.append(f"  <{section_name}>")
                for field, value in section_data.items():
                    if value:
                        xml_parts.append(f"    <{field}>{value}</{field}>")
                xml_parts.append(f"  </{section_name}>")

    return "\n".join(xml_parts)
