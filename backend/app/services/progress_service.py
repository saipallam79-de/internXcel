def calculate_progress(completed_modules: int, total_modules: int) -> int:
    if total_modules <= 0:
        return 0
    return round((completed_modules / total_modules) * 100)
