from .models import TransformerResource, SaverResource


class MockSaver:
    def __init__(self, intergation_metadata: dict):
        self.intergation_metadata = intergation_metadata

    def save(self, resource: TransformerResource) -> SaverResource:
        return SaverResource(
                path=f'{resource.path}.parquet'
            )