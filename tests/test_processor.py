# tests/test_processor.py
import sys
import os
from pathlib import Path

# Добавляем пути QGIS
qgis_path = r"C:\PROGRA~1\QGIS34~1.9"
sys.path.insert(0, os.path.join(qgis_path, 'apps', 'qgis-ltr', 'python'))
sys.path.insert(0, os.path.join(qgis_path, 'apps', 'qgis-ltr', 'python', 'plugins'))
sys.path.insert(0, os.path.join(qgis_path, 'apps', 'Python312', 'lib', 'site-packages'))

sys.path.insert(0, str(Path(__file__).parent.parent))

from qgis.core import QgsVectorLayer, QgsProject, QgsWkbTypes, QgsApplication
from processor import Processor

# Инициализация QGIS
app = QgsApplication([], False)
app.initQgis()
project = QgsProject.instance()


class TestProcessor:
    
    def setup_method(self):
        """Очистка проекта между тестами"""
        project.clear()
    
    @property
    def processor(self):
        return Processor()
    
    @property
    def test_data_path(self):
        return str(Path(__file__).parent.parent / "test_data.geojson")
    
    def test_load_layer_success(self):
        """Тест 1: Загрузка слоя"""
        layer = self.processor.load_layer(self.test_data_path)
        assert isinstance(layer, QgsVectorLayer)
        assert layer.featureCount() == 7
        assert layer.crs().authid() == 'EPSG:4326'
    
    def test_filter_features_population(self):
        """Тест 2: Фильтрация объектов"""
        layer = self.processor.load_layer(self.test_data_path)
        filtered = self.processor.filter_features(layer, "population > 1000")
        assert len(filtered) == 3
        assert filtered[0]['population'] == 2500
    
    def test_create_buffer_layer(self):
        """Тест 3: Создание буфера"""
        layer = self.processor.load_layer(self.test_data_path)
        filtered = self.processor.filter_features(layer, "population > 1000")
        buffer_layer = self.processor.create_buffer_layer(filtered, 1000)
        assert buffer_layer is not None
        assert buffer_layer.geometryType() == QgsWkbTypes.PolygonGeometry
        assert buffer_layer.featureCount() == 3
    
    def test_full_pipeline(self):
        """Тест 4: Полный пайплайн"""
        result = self.processor.full_pipeline(self.test_data_path)
        layers = QgsProject.instance().mapLayersByName("buffered_cities")
        assert len(layers) > 0
    
    def test_transform_coordinates(self):
        """Тест 5: Трансформация координат из WGS84 в ГСК-2011"""
        layer = self.processor.load_layer(self.test_data_path)
        transformed = self.processor.wgs84_to_gsk2011(layer)
        assert transformed is not None
        assert transformed.featureCount() == 7
        assert transformed.crs().authid() == 'EPSG:7683'