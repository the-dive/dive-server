def to_camelcase(snake_str):
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])
