import dataclasses
import io


@dataclasses.dataclass
class ExtractorResource:
    path: str


@dataclasses.dataclass
class TransformerResource:
    path: str
    content: io.BytesIO


@dataclasses.dataclass
class SaverResource:
    path: str