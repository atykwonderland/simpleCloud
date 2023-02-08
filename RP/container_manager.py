class Pod:
    def __init__(self, name, id) -> None:
        self.name = name
        self.id = id
        pass
    
class Node:
    def __init__(self, name, id) -> None:
        self.name = name
        self.status = "Idle"
        self.id = id
        pass

class Job:
    def __init__(self, path, status) -> None:
        self.path = path
        self.id = id(self.path)
        self.status = status
        pass