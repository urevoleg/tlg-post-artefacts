from models import TransformerResource, SaverResource


class MockSaver:
    def __init__(self, integration_meta: dict):
        self.integration_meta = integration_meta

    def save(self, resource: TransformerResource) -> SaverResource:
        return SaverResource(
                path=f'{resource.path}.parquet'
            )