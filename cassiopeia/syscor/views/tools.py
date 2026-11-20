# Provides data conversion and session helpers.
# Poskytuje pomocné funkce pro převod dat a práci s relací.
class sysTools():
    # Initializes the helper without instance data.
    # Inicializuje pomocnou třídu bez vlastních dat instance.
    def __init__(self):
        self.ttuple = {"application_code":   "cassiopeia"}
        self.webdata = {"htmlbody":""}
    # Flattens nested dictionary data into rows.
    # Převádí vnořená data slovníku na ploché řádky.
    @staticmethod
    def dictionary_to_data(source):
        """Flatten a dictionary into path/value pairs for a key/value table.

        Nested keys use dots and list/tuple positions use brackets. Escape
        dots, brackets and backslashes in keys to keep paths unambiguous.
        Empty containers and scalar values are preserved unchanged.
        """
        if not isinstance(source, dict):
            raise TypeError("source must be a dictionary")

        data = {}

        # Escapes characters with a special meaning in a key path.
        # Ošetřuje znaky se zvláštním významem v cestě ke klíči.
        def escape_key(key):
            return (str(key).replace("\\", "\\\\")
                    .replace(".", "\\.")
                    .replace("[", "\\[").replace("]", "\\]"))

        # Visits nested values and collects their paths.
        # Prochází vnořené hodnoty a shromažďuje jejich cesty.
        def walk(value, path):
            if isinstance(value, dict) and value:
                for key, item in value.items():
                    child_path = f"{path}.{escape_key(key)}" if path else escape_key(key)
                    walk(item, child_path)
            elif isinstance(value, (list, tuple)) and value:
                for index, item in enumerate(value):
                    walk(item, f"{path}[{index}]")
            else:
                data[path] = value

        for key, value in source.items():
            walk(value, escape_key(key))
        return data

    # Prints nested values with indentation.
    # Vypisuje vnořené hodnoty s odsazením.
    def showTuple(self, data, level:int=0):
        inde = "  " * level
        rows = []
        if isinstance(data, dict):
            for key, value in data.items():
                rows.append(f"{inde}{key}:")
                rows.append(self.showTuple(value, level + 1))
        elif isinstance(data, (list, tuple)):
            for index, value in enumerate(data):
                rows.append(f"{inde}[{index}]:")
                rows.append(self.showTuple(value, level + 1))
        else:
            rows.append(f"{inde}{data}")
        return "\n".join(rows)

    # Reads a named value from the session.
    # Načítá hodnotu pod zadaným názvem z relace.
    @staticmethod
    def session_get(request, session_name):
        return request.session.get(session_name)

    # Stores a named value in the session.
    # Ukládá hodnotu pod zadaným názvem do relace.
    @staticmethod
    def session_set(request, session_name, session_value):
        request.session[session_name] = session_value
        return request.session.get(session_name)

    # Removes a named value from the session.
    # Odstraňuje hodnotu pod zadaným názvem z relace.
    @staticmethod
    def session_clear(request, session_name):
        request.session.pop(session_name, None)
        return True