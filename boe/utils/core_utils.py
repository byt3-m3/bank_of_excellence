def extract_type(data_class):
    type_string = str(type(data_class))
    type_string = type_string[6:]
    type_string = type_string.replace("'", "")
    type_string = type_string.replace(">", "").strip()

    type_string = type_string[type_string.rfind(".") + 1:]

    return type_string
