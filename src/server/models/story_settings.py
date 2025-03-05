from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CustomFieldSettings(BaseModel):
    custom_field_name: Optional[str] = None
    custom_field_content: Optional[str] = None


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
    custom_fields: Optional[List[CustomFieldSettings]] = None


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
    custom_fields: Optional[List[CustomFieldSettings]] = None


class PlotSettings(BaseModel):
    content: Optional[str] = None


class IdeanoteSettings(BaseModel):
    idea_title: Optional[str] = None
    idea_content: Optional[str] = None


def create_empty_character_list() -> List[CharacterSettings]:
    return []


def create_empty_custom_field_list() -> List[CustomFieldSettings]:
    return []


class StorySettings(BaseModel):
    """소설 설정 모델"""

    synopsis: Optional[SynopsisSettings] = Field(default_factory=SynopsisSettings)
    worldview: Optional[WorldviewSettings] = Field(default_factory=WorldviewSettings)
    character: Optional[List[CharacterSettings]] = Field(
        default_factory=create_empty_character_list
    )
    plot: Optional[PlotSettings] = Field(default_factory=PlotSettings)
    ideanote: Optional[IdeanoteSettings] = Field(default_factory=IdeanoteSettings)


def settings_to_xml(
    settings: Dict[str, Any],
) -> str:
    """설정 딕셔너리를 XML 문자열로 변환"""
    xml_parts: List[str] = []

    for section_name, section_data in settings.items():
        if not section_data:
            continue

        if section_name == "character":
            if isinstance(section_data, list):
                for idx, item in enumerate(section_data, 1):
                    xml_parts.append(f"  <{section_name}_{idx}>")
                    for field, value in item.items():
                        if (
                            field == "custom_fields"
                            and value
                            and isinstance(value, list)
                        ):
                            for cf_idx, cf_item in enumerate(value, 1):
                                xml_parts.append(f"    <custom_field_{cf_idx}>")
                                if isinstance(cf_item, dict):
                                    for cf_field, cf_value in cf_item.items():
                                        if cf_value:
                                            xml_parts.append(
                                                f"      <{cf_field}>"
                                                f"{cf_value}"
                                                f"</{cf_field}>"
                                            )
                                xml_parts.append(f"    </custom_field_{cf_idx}>")
                        elif value:
                            xml_parts.append(f"    <{field}>{value}</{field}>")
                    xml_parts.append(f"  </{section_name}_{idx}>")
        else:
            if isinstance(section_data, dict):
                xml_parts.append(f"  <{section_name}>")
                for field, value in section_data.items():
                    if field == "custom_fields" and value and isinstance(value, list):
                        for cf_idx, cf_item in enumerate(value, 1):
                            xml_parts.append(f"    <custom_field_{cf_idx}>")
                            if isinstance(cf_item, dict):
                                for cf_field, cf_value in cf_item.items():
                                    if cf_value:
                                        xml_parts.append(
                                            f"      <{cf_field}>"
                                            f"{cf_value}"
                                            f"</{cf_field}>"
                                        )
                            xml_parts.append(f"    </custom_field_{cf_idx}>")
                    elif value:
                        xml_parts.append(f"    <{field}>{value}</{field}>")
                xml_parts.append(f"  </{section_name}>")

    return "\n".join(xml_parts)
