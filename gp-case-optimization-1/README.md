# Превратности GPORCA

![main.png](img/main.png)

## Принес парочку интересных кейсов поведения оптимизатора Greenplum - GPORCA.

1️⃣ **Плевать я хотел на тип данных**

Дано:
1. Таблица партицированная по полю с типом timestamp

```sql
    PARTITION BY RANGE (date)
    (
        START ('2025-01-01'::timestamp) INCLUSIVE
        END ('2026-01-01'::timestamp) EXCLUSIVE
        EVERY (INTERVAL '1 day')
    )
```

При таком отборе дат, оптимизатор отказывается делать Partition Selector:

```sql
...
where date >= date_trunc('month', date)
-- date_trunc('month', date) не меняет тип, он остается timestamp
```

Но вот так, отлично работает 🤷‍♂️:

```sql
...
where date >= date_trunc('month', date)::date
```


2️⃣ **Упс, это вьюха**

Дано:
1. Вьюха, объединяет через `union all` несколько таблиц
2. Каждая таблица партицирована по одному и тому же полю, допустим `date`

Partition Selector не работает:

```sql
...
where date >= '2025-01-01'::date
and data < '2025-02-01'::date
```

Но вот так, отлично взлетает:

```sql
...
where date between '2025-01-01'::date and '2025-02-01'::date
```

Где логика?

tags:
- work
- case
- greenplum



