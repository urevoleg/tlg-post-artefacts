**WALLE читает Reddit**


В прошлом [посте]() собрали полный каркас:
- к тому что было добавили формирование тасок из ямла (пока только Mock объекты)

Сегодня реализуем объекты решающие нашу задачу по получению топ реддитов за последний час и сохранению на S3. 
Напомню, структуру экстратора:

```yaml
    tasks:
      extractor:
        RedditExtractor:
          src_s3_conection_id: reddit_s3_connection_id
          src_s3_bucket: raw-public
          src_s3_prefix_template: reddit/{dm_date}
          src_s3_partition_fmt: '%Y-%m-%d'
```

API - здесь, нужный нам метод тут.

Трансформер будет выполнять простую задачу: `json to parquet` (мы же хотим модно-молодежно 🙃)

tags:
- walle
- framework
- automate