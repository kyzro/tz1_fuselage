import trimesh
from logger import logger

def load_stl(filepath: str) -> trimesh.Trimesh:
    """
    Загружает STL файл и возвращает объект меша
    """
    try:
        logger.info(f"Загрузка STL файла: {filepath}")
        mesh = trimesh.load_mesh(filepath)
        
        # Проверка успешной загрузки
        if hasattr(mesh, 'vertices') and len(mesh.vertices) > 0:
            logger.info("STL успешно загружен:")
            logger.info(f"Количество треугольников: {len(mesh.faces)}")
            logger.info(f"Количество вершин: {len(mesh.vertices)}")
        else:
            raise Exception("Не удалось загрузить геометрию из файла")
            
        return mesh
        
    except FileNotFoundError:
        logger.error(f"Файл не найден: {filepath}")
        raise FileNotFoundError()
    except Exception as e:
        logger.error(f"Ошибка при загрузке STL: {e}")
        raise Exception()

def calc_xyz_len(mesh: trimesh.Trimesh):
    """
    Вычисляет размеры меша вдоль осей X, Y, Z
    """
    min_xyz, max_xyz = mesh.bounds
    
    x_len = max_xyz[0] - min_xyz[0]
    y_len = max_xyz[1] - min_xyz[1] 
    z_len = max_xyz[2] - min_xyz[2]
    
    dimensions = {
        'length_x': x_len,
        'length_y': y_len, 
        'length_z': z_len,
        'min_bounds': min_xyz,
        'max_bounds': max_xyz,
        'center': mesh.center_mass,
        'volume': mesh.volume,
        'is_watertight': mesh.is_watertight
    }
    
    # Логирование информации
    logger.info(f"Размеры модели (X, Y, Z): {(x_len, y_len, z_len)}")
    logger.info(f"Объем модели: {mesh.volume:.2f}")
    
    if mesh.is_watertight:
        logger.info("Модель замкнутая")
    else:
        logger.error("Модель не замкнутая => может быть неполной")
    
    return dimensions
