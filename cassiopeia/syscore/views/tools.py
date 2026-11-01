class sysTools():
    def __init__(self):
        self.ttuple = {"application_code":   "cassiopeia"}
        self.webdata = {"htmlbody":""}
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