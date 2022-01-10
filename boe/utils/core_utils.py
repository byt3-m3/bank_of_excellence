def extract_name_from_object(obj):
    type_string = str(type(obj))
    type_string = type_string[6:]
    type_string = type_string.replace("'", "")
    type_string = type_string.replace(">", "").strip()

    type_string = type_string[type_string.rfind(".") + 1:]

    return type_string
