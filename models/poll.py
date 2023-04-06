from enum import Enum, auto
from typing import Any, TypeAlias

from pydantic import validator

from models import BaseModel


class QuestionType(Enum):
    selector = auto()
    slider = auto()
    top_list = auto()
    text = auto()


class BaseQuestion(BaseModel):
    question_type: QuestionType
    label: str
    description: str | None = None
    image: str | None = None


class Option(BaseModel):
    label: str
    image: str | None


class BaseOptionQuestion(BaseQuestion):
    options: list[Option] = []

    @validator("options")
    def options_validator(
        cls,
        value: list[Option],
        values: dict[str, Any],
        **kwargs: Any,
    ) -> list[Option]:
        assert len(value) >= 1, "len(options) >= 1"
        return value


class SelectorQuestion(BaseOptionQuestion):
    question_type = QuestionType.selector
    max_checked: int | None

    @validator("max_checked")
    def object_validator(
        cls,
        value: int | None,
        values: dict[str, Any],
        **kwargs: Any,
    ) -> int | None:
        assert (
            value is None or "options" not in values or value <= len(values["options"])
        ), "max_checked <= len(options)"
        return value


class SliderQuestion(BaseOptionQuestion):
    question_type = QuestionType.slider
    min_value: int = 1
    max_value: int = 5
    step: int = 1

    @validator("max_value")
    def max_value_validator(
        cls,
        value: int,
        values: dict[str, Any],
        **kwargs: Any,
    ) -> int:
        assert (
            "min_value" not in values or value > values["min_value"]
        ), "max_value > min_value"
        return value

    @validator("step")
    def step_validator(
        cls,
        value: int,
        values: dict[str, Any],
        **kwargs: Any,
    ) -> int:
        assert (
            "min_value" not in values
            or "max_value" not in values
            or (
                values["min_value"] <= value <= values["max_value"]
                and value % (values["max_value"] - values["min_value"]) == 0
            )
        ), "min_value <= step <= max_value and value % (max_value - min_value) == 0"
        return value


class TopListQuestion(BaseOptionQuestion):
    question_type = QuestionType.top_list
    ranks: int | None = None

    @validator("ranks")
    def ranks_validator(
        cls,
        value: int | None,
        values: dict[str, Any],
        **kwargs: Any,
    ) -> int | None:
        assert (
            value is None or "options" not in values or value <= values["options"]
        ), "ranks <= len(options)"
        return value


class TextQuestion(BaseQuestion):
    question_type = QuestionType.text
    min_length: int | None = None
    max_length: int | None = None

    @validator("max_length")
    def max_length_validator(
        cls,
        value: int | None,
        values: dict[str, Any],
        **kwargs: Any,
    ) -> int | None:
        assert (
            value is None
            or "min_length" not in values
            or values["min_length"] is None
            or value > values["min_length"]
        ), "max_length > min_length"
        return value


Question: TypeAlias = SelectorQuestion | SliderQuestion | TopListQuestion | TextQuestion


class PlotType(Enum):
    bar = auto()
    pie = auto()
    doughnut = auto()
    radar = auto()
    area = auto()
    word_cloud = auto()


class BasePlot(BaseModel):
    plot_type: PlotType
    name: str
    questions: list[Question] = []
    hide_results: bool = False

    @validator("questions")
    def questions_validator(
        cls,
        value: list[Question],
        values: dict[str, Any],
        **kwargs: Any,
    ) -> list[Question]:
        assert len(value) >= 1, "len(questions) >= 1"

        question_type = value[0].question_type
        for question in value[1:]:
            assert (
                question.question_type == question_type
            ), "All questions must be of the same type"

        return value


class BaseNumberPlot(BasePlot):
    @validator("questions")
    def questions_validator(
        cls,
        value: list[Question],
        values: dict[str, Any],
        **kwargs: Any,
    ) -> list[Question]:
        assert all(
            question.question_type
            in (
                QuestionType.selector,
                QuestionType.slider,
                QuestionType.top_list,
            )
            for question in value
        ), "Question must only have these types: selector, slider and top_list"

        return value


class BarPlot(BaseNumberPlot):
    plot_type = PlotType.bar


class PiePlot(BaseNumberPlot):
    plot_type = PlotType.pie


class DoughnutPlot(BaseNumberPlot):
    plot_type = PlotType.doughnut


class RadarPlot(BaseNumberPlot):
    plot_type = PlotType.radar


class AreaPlot(BaseNumberPlot):
    plot_type = PlotType.area


class WordCloudPlot(BasePlot):
    plot_type = PlotType.word_cloud


Plot: TypeAlias = (
    BarPlot | PiePlot | DoughnutPlot | RadarPlot | AreaPlot | WordCloudPlot
)


class PollSchema(BaseModel):
    name: str
    plots: list[Plot] = []


class Poll(BaseModel):
    id: int
    name: str
    poll: PollSchema
