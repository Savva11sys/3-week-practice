# fix_colors.py
import os

def replace_in_file(filepath, old_text, new_text):
    """Заменить текст в файле"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if old_text in content:
            content = content.replace(old_text, new_text)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Исправлено в {filepath}")
            return True
        else:
            return False
    except Exception as e:
        print(f"Ошибка при обработке {filepath}: {e}")
        return False

# Исправляем файлы
files_to_fix = [
    'widgets/charts.py',
    'widgets/__init__.py',
    'forms/main_form.py',
    'forms/request_form.py',
    'forms/login_form.py',
    'forms/statistics_form.py',
    'forms/quality_manager_form.py'
]

# Заменяем 'dark_gray' на 'gray_dark'
for file in files_to_fix:
    if os.path.exists(file):
        replace_in_file(file, "StyleManager.COLORS['dark_gray']", "StyleManager.COLORS['gray_dark']")
        replace_in_file(file, 'dark_gray', 'gray_dark')
    else:
        print(f"Файл не найден: {file}")

print("\nИсправление завершено!")