import io

from .models import ExtractorResource, TransformerResource


class MockTransformer:
    def __init__(self, intergation_metadata: dict):
        self.intergation_metadata = intergation_metadata

    def transform(self, resource: ExtractorResource) -> TransformerResource:
        return TransformerResource(
                path=resource.path,
                content=io.BytesIO()
            )