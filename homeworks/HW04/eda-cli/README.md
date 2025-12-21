# S03 – eda_cli: мини-EDA для CSV

Небольшое CLI-приложение для базового анализа CSV-файлов.
Используется в рамках Семинара 03 курса «Инженерия ИИ».

## Требования

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) установлен в систему

## Инициализация проекта

В корне проекта (S03):

```bash
uv sync
```

Эта команда:

- создаст виртуальное окружение `.venv`;
- установит зависимости из `pyproject.toml`;
- установит сам проект `eda-cli` в окружение.

## Запуск CLI

### Краткий обзор

```bash
uv run eda-cli overview data/example.csv
```

Параметры:

- `--sep` – разделитель (по умолчанию `,`);
- `--encoding` – кодировка (по умолчанию `utf-8`).
- `--out-dir` – каталог для отчета (по умолчанию `reports`).
- `--max-hist-columns` - максимум числовых колонок для гистограмм. (по умолчанию `6`)
- `--top-k-categories` - Сколько top-значений выводить для категориальных признаков. (по умолчанию `10`)
- `--title` - заголовок отчета в Markdown. (по умолчанию `EDA-report`)
- `--min-missing-share` - Порог доли пропусков, выше которого колонка считается проблемной. (по умолчанию: `0.2`)
- `--help` - посмотреть все опции

### Примеры использования новых опций

```bash
uv run eda-cli report data/example.csv --out-dir reports_example --title Eda --min-missing-share 0.03
```

### Полный EDA-отчёт

```bash
uv run eda-cli report data/example.csv --out-dir reports
```

В результате в каталоге `reports/` появятся:

- `report.md` – основной отчёт в Markdown;
- `summary.csv` – таблица по колонкам;
- `missing.csv` – пропуски по колонкам;
- `correlation.csv` – корреляционная матрица (если есть числовые признаки);
- `top_categories/*.csv` – top-k категорий по строковым признакам;
- `hist_*.png` – гистограммы числовых колонок;
- `missing_matrix.png` – визуализация пропусков;
- `correlation_heatmap.png` – тепловая карта корреляций.

## Тесты

Добавлены тесты для проверки новых эвристик и тест для проверки min_share в `missing_table`, чтобы убедиться, что фильтрация по доле пропусков работает корректно после изменений.

```bash
uv run pytest -q
```

## HTTP API (HW04)

Поверх EDA-ядра реализован HTTP-сервис на FastAPI.

Запуск сервера

```bash
uv run uvicorn eda_cli.api:app --reload --port 8000
```

Документация OpenAPI доступна по адресу:

```txt
http://127.0.0.1:8000/docs
```

## Реализованные эндпоинты

### GET /health

Проверка состояния сервиса.
**Ответ:**

```json
{
  "status": "ok",
  "service": "dataset-quality",
  "version": "0.2.0"
}
```

### POST /quality

Эвристическая оценка качества по агрегированным признакам датасета.

Принимает JSON со статистиками (n_rows, n_cols, max_missing_share, и т.д.)
и возвращает оценку качества.

### POST /quality-from-csv

Эндпоинт, который принимает CSV-файл, запускает EDA-ядро (summarize_dataset + missing_table + compute_quality_flags) и возвращает оценку качества данных.

Именно это по сути связывает S03 (CLI EDA) и S04 (HTTP-сервис).

**Ответ:**

```json
{
  "ok_for_model": true,
  "quality_score": 0.7444444444444445,
  "message": "CSV выглядит достаточно качественным для обучения модели (по текущим эвристикам).",
  "latency_ms": 5.605199956335127,
  "flags": {
    "too_few_rows": true,
    "too_many_columns": false,
    "too_many_missing": false,
    "has_constant_columns": false,
    "has_high_cardinality_columns": false
  },
  "dataset_shape": {
    "n_rows": 36,
    "n_cols": 14
  }
}
```

### POST /quality-flags-from-csv

> Эндпоинт, который принимает CSV-файл и возвращает полный набор флагов качества данных, включая все эвристики, реализованные в HW03.

**Ответ:**

```json
{
  "flags": {
    "too_few_rows": true,
    "too_many_columns": false,
    "max_missing_share": 0.05555555555555555,
    "too_many_missing": false,
    "has_constant_columns": false,
    "has_high_cardinality_columns": false,
    "quality_score": 0.7444444444444445
  }
}
```
