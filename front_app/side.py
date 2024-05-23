from string import printable
def is_english(name: str):
    if not isinstance(name,str):
        raise TypeError(f'name must be a string got {type(name)}')
    return all([ch in printable for ch in name])
