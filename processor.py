import os
# Баг 1: не импортирован QgsFeature
from qgis.core import (
    QgsVectorLayer, QgsProject, QgsFeatureRequest, QgsGeometry,
    QgsFields, QgsField, QgsWkbTypes, QgsCoordinateReferenceSystem,
    QgsCoordinateTransform, QgsFeature
)
from qgis.PyQt.QtCore import QVariant


class Processor:
    def __init__(self):
        self.project = QgsProject.instance()

    def load_layer(self, file_path):
        """Загружает векторный слой из GeoJSON"""

        layer = QgsVectorLayer(file_path, "cities", "ogr")
        if not layer.isValid():
            raise ValueError("Не удалось загрузить слой")

        # Баг 2: дублирование добавления слоя
        self.project.addMapLayer(layer)
        return layer

    def filter_features(self, layer, expression):
        """Фильтрует объекты по выражению"""

        request = QgsFeatureRequest()
        request.setFilterExpression(expression)
        features = [f for f in layer.getFeatures(request)]
        return features

    def wgs84_to_gsk2011(self, layer):
        """Переводит координаты объектов из WGS84 в ГСК-2011 (по градусам)"""
        
        # Задание исходной и целевой систем координат
        source_crs = QgsCoordinateReferenceSystem("EPSG:4326")
        target_crs = QgsCoordinateReferenceSystem("EPSG:7683") 
        
        # Объект трансформации координат
        transform = QgsCoordinateTransform(source_crs, target_crs, self.project)
        
        # Создаем выходной слой в целевой СК, сохраняя геометрию исходного слоя,
        # также копируем структуру полей
        transformed_layer = QgsVectorLayer("Polygon?crs=EPSG:7683", "transformed_cities", "memory")
        transformed_layer.dataProvider().addAttributes(layer.fields())
        transformed_layer.updateFields()
        
        # Трансформируем все объекты на слое
        features = []
        for feature in layer.getFeatures():
            # Создаем объект и копируем данные
            new_feature = QgsFeature()
            new_feature.setFields(layer.fields())
            new_feature.setAttributes(feature.attributes())
            
            # Пересчитываем координаты геометрии и добавляем результат в список
            geom = feature.geometry()
            geom.transform(transform)
            new_feature.setGeometry(geom)
            features.append(new_feature)
        
        # Добавляем все трансформированные объекты в слой
        transformed_layer.dataProvider().addFeatures(features)
        return transformed_layer
        
    def create_buffer_layer(self, input_layer, distance):
        """Создает буферный слой"""

        fields = QgsFields()
        fields.append(QgsField("population", QVariant.Int))

        # Баг 3: пустой crs и LineString вместо Polygon
        buffer_layer = QgsVectorLayer(
            "Polygon?crs=EPSG:4326", "buffered_cities", "memory"
        )
        buffer_layer.dataProvider().addAttributes(fields)
        buffer_layer.updateFields()

        features = []
        # Баг 4: передан список объектов, а не слой
        if isinstance(input_layer, list):
            source_features = input_layer
        else:
            source_features = input_layer.getFeatures()
        
        for feature in source_features:
            # Баг 5: используем другой конструктор
            new_feature = QgsFeature(fields)
            # Баг 6 (возможно): population умножается на 2
            new_feature['population'] = feature['population']
            geom = feature.geometry().buffer(distance, 25)
            new_feature.setGeometry(geom)
            features.append(new_feature)

        buffer_layer.dataProvider().addFeatures(features)
        self.project.addMapLayer(buffer_layer)
        return buffer_layer

    def full_pipeline(self, file_path):
        """Полный пайплайн обработки"""

        layer = self.load_layer(file_path)
        # Баг 7: по условию population > 1000, а не >=
        filtered = self.filter_features(layer, "population > 1000")
        buffer_layer = self.create_buffer_layer(filtered, 1000)
        return buffer_layer


if __name__ == "__main__":
    processor = Processor()
    layer = processor.load_layer("test_data.geojson")
    # Баг 8 (повтор бага 7): по условию population > 1000, а не >=
    filtered = processor.filter_features(layer, "population > 1000")
    print(f"Отфильтровано объектов: {len(filtered)}")
    buffer_layer = processor.create_buffer_layer(layer, 1000)
