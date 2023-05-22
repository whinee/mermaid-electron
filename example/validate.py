# ruff: noqa: N815
from typing import Any, Optional

import pydantic
from pydantic import BaseModel, StrictBool, StrictFloat, StrictInt


# Models
class ErConfig(BaseModel):
    diagramPadding: Optional[StrictInt]
    layoutDirection: Optional[str]
    minEntityWidth: Optional[StrictInt]
    minEntityHeight: Optional[StrictInt]
    entityPadding: Optional[StrictInt]
    stroke: Optional[str]
    fill: Optional[str]
    fontSize: Optional[StrictInt]
    useMaxWidth: Optional[StrictBool]

    class Config:
        extra = pydantic.Extra.forbid


class FlowchartConfig(BaseModel):
    diagramPadding: Optional[StrictInt]
    htmlLabels: Optional[StrictBool]
    curve: Optional[str]

    class Config:
        extra = pydantic.Extra.forbid


class SequenceConfig(BaseModel):
    diagramMarginX: Optional[StrictInt]
    diagramMarginY: Optional[StrictInt]
    actorMargin: Optional[StrictInt]
    width: Optional[StrictInt]
    height: Optional[StrictInt]
    boxMargin: Optional[StrictInt]
    boxTextMargin: Optional[StrictInt]
    noteMargin: Optional[StrictInt]
    messageMargin: Optional[StrictInt]
    messageAlign: Optional[str]
    mirrorActors: Optional[StrictBool]
    bottomMarginAdj: Optional[StrictInt]
    useMaxWidth: Optional[StrictBool]
    rightAngles: Optional[StrictBool]
    showSequenceNumbers: Optional[StrictBool]

    class Config:
        extra = pydantic.Extra.forbid


class GanttConfig(BaseModel):
    titleTopMargin: Optional[StrictInt]
    barHeight: Optional[StrictInt]
    barGap: Optional[StrictInt]
    topPadding: Optional[StrictInt]
    leftPadding: Optional[StrictInt]
    gridLineStartPadding: Optional[StrictInt]
    fontSize: Optional[StrictInt]
    fontFamily: Optional[str]
    numberSectionStyles: Optional[StrictInt]
    axisFormat: Optional[str]
    topAxis: Optional[StrictBool]
    displayMode: Optional[str]

    class Config:
        extra = pydantic.Extra.forbid


class MermaidConfig(BaseModel):
    theme: Optional[str]
    logLevel: Optional[str]
    securityLevel: Optional[str]
    arrowMarkerAbsolute: Optional[StrictBool]

    er: Optional[ErConfig]
    flowchart: Optional[FlowchartConfig]
    sequence: Optional[SequenceConfig]
    gantt: Optional[GanttConfig]

    class Config:
        extra = pydantic.Extra.forbid


class MermaidDiagram(BaseModel):
    code: str
    config: Optional[MermaidConfig]

    class Config:
        extra = pydantic.Extra.forbid


class AppConfig(BaseModel):
    margin: Optional[StrictInt | StrictFloat] = 20
    max_width: Optional[StrictInt] = -1
    width: Optional[StrictInt] = -1
    zoom: Optional[StrictInt | StrictFloat] = 1

    class Config:
        extra = pydantic.Extra.forbid


class MermaidData(BaseModel):
    mmd: list[MermaidDiagram]
    config: Optional[AppConfig] = AppConfig()  # type: ignore[call-arg]
    mmd_config: Optional[MermaidConfig] = MermaidConfig()  # type: ignore[call-arg]

    class Config:
        extra = pydantic.Extra.forbid


def validate_mermaid_config(config: dict[str, Any]) -> dict[str, Any]:
    try:
        return MermaidData.parse_obj(config).dict(
            exclude_unset=False,
            exclude_none=True,
        )
    except pydantic.error_wrappers.ValidationError as e:
        raise Exception(e) from None
