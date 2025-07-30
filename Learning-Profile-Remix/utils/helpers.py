def title_case_name(name):
    """Convert a name to title case, handling None values."""
    if not name:
        return None
    return name.strip().title()
