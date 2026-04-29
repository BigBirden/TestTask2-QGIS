# Тестовое задание №2: QGIS

Выполнил: Краснослободцев Артём Александрович;
Группа: ИВТб22о-2.

## QGIS Processor

Модуль для обработки векторных геоданных в QGIS. Доступны следующие функции:
- Загрузка векторных слоёв из GeoJSON;
- Фильтрация объектов по выражениям;
- Создание буферных зон вокруг объектов с заданным радиусом;
- Трансформация координат из WGS84 в ГСК-2011.

## Структура проекта

TestTask2-QGIS/  
├── tests/  
│ └── test_processor.py  
├── processor.py  
├── test_data.geojson  
└── README.md  

## Требования

- **[Python](https://www.python.org/downloads/)** 3.8+
- **[QGIS](https://qgis.org/download/)** 3.28+ (установлен локально)
- **pytest** 7.0+

## Установка и настройка

### 1. Клонирование репозитория

```bash
git clone https://github.com/BigBirden/TestTask2-QGIS.git
cd [Ваш путь]/TestTask2-QGIS
```

### 2. Установка зависимостей

Запустите **OSGeo4W Shell** (устанавливается вместе с QGIS) и выполните:

```bash
pip install pytest
```

### 3. Запуск тестов

Из **OSGeo4W Shell** в папке проекта выполните команду:

```bash
python -m pytest tests/ -v
```

## Пример использования

```python
from processor import Processor

processor = Processor()

# Загрузка слоя
layer = processor.load_layer("test_data.geojson")

# Фильтрация: города с населением > 1000
filtered = processor.filter_features(layer, "population > 1000")

# Создание буферных зон (1000 метров)
buffer_layer = processor.create_buffer_layer(filtered, 1000)

# Трансформация координат WGS84 -> ГСК-2011
transformed = processor.wgs84_to_gsk2011(layer)

# Полный пайплайн: загрузка -> фильтрация -> буфер
result = processor.full_pipeline("test_data.geojson")
```

## Дополнительно
### Используемые системы координат

| EPSG | Система | Единицы | Применение |
|------|---------|---------|------------|
| 4326 | WGS84 | градусы | Международная |
| 7683 | ГСК-2011 (географическая) | градусы | Россия |

### Разработанные unit-тесты

| Тест | Описание |
|------|----------|
| `test_load_layer_success` | Загрузка слоя: тип, количество объектов, CRS |
| `test_filter_features_population` | Фильтрация по population > 1000 |
| `test_create_buffer_layer` | Создание буфера: тип геометрии, количество объектов |
| `test_full_pipeline` | Полный пайплайн с проверкой добавления слоя в проект |
| `test_transform_coordinates` | Трансформация WGS84 -> ГСК-2011 |

### Примечание

Тесты необходимо запускать исключительно из **OSGeo4W Shell**, так как требуется доступ к модулям QGIS (PyQGIS). Обычная командная строка Windows не содержит путей к библиотекам QGIS.
