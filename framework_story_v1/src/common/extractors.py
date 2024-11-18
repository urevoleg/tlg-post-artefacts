from .models import ExtractorResource


class MockExtractor:
    def __init__(self, intergation_metadata: dict):
        self.intergation_metadata = intergation_metadata

    def get_resources(self):
        for idx in range(5):
            yield ExtractorResource(path=f'mock_s3_file_{idx}.csv')