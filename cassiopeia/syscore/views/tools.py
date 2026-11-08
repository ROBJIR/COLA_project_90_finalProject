class sysTools():
    def __init__(self):
        self.ttuple = {"application_code":   "cassiopeia"}
        self.webdata = {"htmlbody":""}
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

        def escape_key(key):
            return (str(key).replace("\\", "\\\\")
                    .replace(".", "\\.")
                    .replace("[", "\\[").replace("]", "\\]"))

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

    def session_get(request,session_name):
        session_value = request.session.get(session_name)
        return session_value

    def session_set(request,session_name, session_value):
        request.session[session_name] = session_value
        return request.session.get(session_name)

    def session_clear(request,session_name):
        request.session.pop(session_name, None)
        return True