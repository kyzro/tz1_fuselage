import numpy as np
from logger import logger

def export_to_data(sections_data: list, output_filepath: str):
    """
    Экспортирует данные сечений в файл config.data
    
    Args:
        sections_data: данные сечений
        output_filepath: путь для сохранения файла
    """
    logger.info(f"Экспорт в {output_filepath}...")
    
    with open(output_filepath, 'w') as f:
        _write_header(f)
        
        for section in sections_data:
            _write_section_data(f, section)
    
    logger.info(f"Файл успешно сохранен: {output_filepath}")

def _write_header(file):
    """Записывает заголовочные данные"""
    file.write("""<  XLEF  ><  YLEF  ><  XTEF  ><  YTEF  >< XTEF0  ><  NSF   >                     
  0.00000   0.00000  29.82000   1.69800  29.4000  33.00000                    
<   XF   ><   YF   ><   RF   ><  FCONT  > - SECTION -  2                        
  0.23146   0.05404   0.36250   1.00000                                        
<   NT   >                                                                      
  30.\n""")

def _write_section_data(file, section: dict):
    """Записывает данные одного сечения"""
    file.write("<    Y   ><    Z   >\n")
    for point in section['points_2d']:
        y, z = point
        file.write(f"  {y:8.5f}   {z:8.5f}\n")
