def percentage_change(current, baseline):
    if baseline in (None, 0) or current is None:
        return None
    return (current - baseline) / baseline * 100

def format_metric(value, suffix=""):
    if value is None:
        return "Unavailable"
    return f"{value:,.2f}{suffix}" if isinstance(value, float) else f"{value:,}{suffix}"

