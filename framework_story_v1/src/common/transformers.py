import io

from models import ExtractorResource, TransformerResource


class MockTransfromer:
    def __init__(self, integration_meta: dict):
        self.integration_meta = integration_meta

    def transform(self, resource: ExtractorResource) -> TransformerResource:
        return TransformerResource(
                path=resource.path,
                content_type=io.BytesIO()
            )