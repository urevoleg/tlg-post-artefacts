**WALLE - Выстраиваем структуру**

![walle_3.png](img/walle_3.png)

В прошлом [посте]() собрали фундамент:
- сформировали yml
- научились его читать
- научились создавать даг из yml метадаты

Пока в даге только пустые таски (`start\end`), сейчас будем исправлять это. Во [вступительном посте](https://t.me/double_data/143)
очертили архитектуру дага, она повторяет процессы **E(xtract)T(ransform)L(Save)**.
Таски transform, save предлагаю объеднить, тк transformer отдает какие-то данные, а saver их сохраняет, то есть таски обмениваются данные, а делать это через 
XComm неблагодарное дело, поэтому наши даги будут состоять из двух тасок (минимум):
- extractor
- transformer_and_saver


Исходные данные (например, выгрузка API или файл на S3) в единственном числе (в смысле, что данные ASIS могут быть только одни) поэтому 
extractor всегда 1, но может возвращать несколько объектов (например, N путей до файлов)

А вот обработать данные мы уже можем несколькими способами, поэтому transformers может быть несколько, а saver всегда идет в комплекте к transformer.

Для описания тасок выделим секцию в нашем yml:

```yaml
version: 2
models:
  - name: reddit # имя интеграции, оно же dag_id
    description: Топ реддитов за последний час # описание интеграции, оно же dag_description
    dag:
#      dag_id: "" # можно переопределить dag_id != name
      schedule_interval: 0 * * * *
      start_date: '2024-08-01'
#      end_date: '2024-08-31'
      catchup: False
      owner: dwh
      tags:
        - reddit
        - api_integration
    tasks:
      extractor:
        RedditExtractor:
      transformers:
        - RedditTransformer:
      saver:
        S3Saver:
    alerting_chat_id: -987654321
    alerting_secret_name: alerting_bot_token
```

Тут важно проверить, что ошибок в структуре нет и yaml_reader успешно читает такой конфиг (самостоятельно).

Структуру описали, теперь разбираемся что же это за `RedditExtractor`, `RedditTransformer` и `S3Saver`🤔. А этих товарищей нужно реализовать: то есть 
это некие Python-классы, которые реализуют некоторый базовый интерфейс. На текущий момент мы знаем, что extractor что-то передает transformer, этот
в свою очередь передаёт уже данные в saver. Условимся называть то чем обмениваются классы ресурсом (`Resource`). Итого у нас будет 3 ресурса:
- ExtractorResource
- TransformerResource
- SaverResource

Ресурс - это объект Python, будем использовать датаклассы (`dataclasses`), но до них доберемся чуть позже. А сейчас про функции каждого объекта:
- Extractor (выгружает из API и складывает на S3 (это я называю RAW-слоем = данные ASIS) и отдает далее пути до файлов 
или ищет наличие файлов на S3 или FTP и возвращает пути к нужным файлам)
- Transformer (читаем данные по полученным путям, перекодирует согласно нашей логике и отдаёт saver-у набор байтов для сохранения)
- Saver (просто сохраняет байтики на S3 в нужном нам формате\партицировании - это я называю ODS-слой)

Интерфейс у нас будет единообразный, поэтому опишем какие методы должны быть реализованы у каждого класса:
- Extractor - должен иметь метод `get_resources` - возвращает генератор объетов ExtractResource
- Transformer - должен иметь метод `transform`, который принимает ExtractResource, возвращает объект TransformResource
- Saver - имеет 1 метод `save`, который принимает TransformResource и возвращает SaveResource.

Все остальные внутренности каждого класса разрабатываются на усмотрение инженера - творческий процесс однако 😎.

Расчехляем Pycharm и кодируем, ресурсы:

```python
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
```

Для проверки идеи и работоспособности дага создадим Mock классы, для примера MockExtractor:

```python
from models import ExtractorResource


class MockExtractor:
    def __init__(self, integration_meta: dict):
        self.integration_meta = integration_meta

    def get_resources(self):
        for idx in range(5):
            yield ExtractorResource(path=f'mock_s3_file_{idx}.csv')
```

Остальные классы, реализуем самостоятельно или заглядываем в [репу]()

tags:
- walle
- framework
- automate