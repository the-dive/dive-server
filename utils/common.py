import os


def to_camelcase(snake_str):
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def get_file_extension(file_path: str):
    return os.path.splitext(file_path)[1].replace(".", "")
