import trimesh
import numpy as np
from scipy.interpolate import splprep, splev
from typing import List, Dict
from logger import logger

def slice_fuselage(mesh: trimesh.Trimesh, sections_count: int,
                   points_per_section: int) -> List[Dict]:
    """
    Нарезает фюзеляж на сечения и возвращает данные сечений
    
    Args:
        mesh: объект меша
        num_sections: количество сечений
        
    Returns:
        List[Dict]: список данных сечений
    """
    logger.info(f"Нарезка на {sections_count} сечений...")
    
    min_bounds, max_bounds = mesh.bounds
    # delta - смещение, чтобы граничные сечения точно пересекли модель
    delta = (max_bounds[0] - min_bounds[0]) * 0.01
    section_positions = np.linspace(min_bounds[0] + delta, 
                                    max_bounds[0] - delta, sections_count)
    sections = []
    
    for i, x_pos in enumerate(section_positions):
        logger.info(f"Обработка сечения {i+1}/{sections_count}")
        
        plane_normal = [1, 0, 0]
        plane_origin = [x_pos, 0, 0]
        
        section = mesh.section(plane_normal, plane_origin)
        
        if section is None:
            logger.warning(f"Сечение {i+1}: не найдено пересечение")
            continue
        
        points_2d = section.vertices[:, 1:3]  # YZ
        
        if len(points_2d) < 10:
            logger.warning(f"Сечение {i+1}: слишком мало точек ({len(points_2d)})")
            continue
        
        # Сортируем точки по углу для правильной аппроксимации
        points_2d = sort_points_by_angle(points_2d)
        points_2d = approximate_points(points_2d, points_per_section)
        
        sections.append({
            'section_id': i + 1,
            'x_position': x_pos,
            'points_2d': points_2d,
            'num_points': len(points_2d)
        })
    
    logger.info(f"Успешно обработано {len(sections)} сечений")       
    
    return sections

def sort_points_by_angle(points: np.ndarray) -> np.ndarray:
    """
    Сортирует точки по углу относительно центра
    """
    center = np.mean(points, axis=0)
    vectors = points - center
    angles = np.arctan2(vectors[:, 1], vectors[:, 0])
    sorted_indices = np.argsort(angles)
    return points[sorted_indices]

def approximate_points(points: np.ndarray, num_output_points: int = 30) -> np.ndarray:
    """
    Аппроксимирует точки сечения и возвращает новые точки
    
    Args:
        points: исходные точки сечения
        num_output_points: количество точек на выходе
        
    Returns:
        np.ndarray: аппроксимированные точки
    """
    # Параметризация кривой
    t = np.linspace(0, 1, len(points))
    
    try:
        tck, u = splprep([points[:, 0], points[:, 1]], s=0, per=1)
        t_new = np.linspace(0, 1, num_output_points)
        y_new, z_new = splev(t_new, tck)
        
        return np.column_stack([y_new, z_new])
    
    except Exception as e:
        logger.warning(f"Ошибка аппроксимации: {e}. Используется линейная интерполяция.")
        # Резервный вариант: линейная интерполяция
        t_new = np.linspace(0, 1, num_output_points)
        y_new = np.interp(t_new, np.linspace(0, 1, len(points)), points[:, 0])
        z_new = np.interp(t_new, np.linspace(0, 1, len(points)), points[:, 1])
        
        return np.column_stack([y_new, z_new])

def visualize_sections(sections: List[Dict]):
    """
    Последовательно отображает сечения в matplotlib
    Ожидает закрытия каждого окна перед показом следующего
    """
    import matplotlib.pyplot as plt
    logger.info("Визуализация сечений...")
    
    # Устанавливаем интерактивный режим
    plt.ion()
    
    try:
        for i, section in enumerate(sections):
            logger.info(f"Отображение сечения {i+1}/{len(sections)}")
            
            # Создаем новую фигуру
            fig, ax = plt.subplots(figsize=(7, 7))
            
            # Получаем точки сечения
            points_2d = section['points_2d']
            
            # Отображаем аппроксимированные точки и кривую
            ax.scatter(points_2d[:, 0], points_2d[:, 1], 
                      c='blue', label='Точки сечения', s=40, alpha=0.7)
            ax.plot(points_2d[:, 0], points_2d[:, 1], 'b-', alpha=0.8, linewidth=2)
            
            # Замыкаем контур (соединяем последнюю точку с первой)
            ax.plot([points_2d[-1, 0], points_2d[0, 0]], 
                   [points_2d[-1, 1], points_2d[0, 1]], 'b-', alpha=0.8, linewidth=2)
            
            # Настройки графика
            ax.set_xlabel('Y координата')
            ax.set_ylabel('Z координата')
            ax.set_title(f'Сечение {section["section_id"]} - X = {section["x_position"]:.2f}')
            ax.legend()
            ax.grid(True, alpha=0.3)
            ax.axis('equal')
            ax.set_aspect('equal', adjustable='box')
            
            plt.tight_layout()
            
            # Показываем и ждем закрытия окна
            logger.info("Закройте окно для перехода к следующему сечению...")
            plt.show(block=True)
            
            # Явно закрываем фигуру
            plt.close(fig)
            
    except Exception as e:
        logger.error(f"Ошибка при визуализации: {e}")
    
    finally:
        # Возвращаем в нормальный режим
        plt.ioff()
    
    logger.info("Визуализация завершена")
