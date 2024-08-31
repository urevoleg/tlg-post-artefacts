from models import ExtractorResource


class MockExtractor:
    def __init__(self, integration_meta: dict):
        self.integration_meta = integration_meta

    def get_resources(self):
        for idx in range(5):
            yield ExtractorResource(path=f'mock_s3_file_{idx}.csv')