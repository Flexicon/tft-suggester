class Champion:
    def __init__(self, name: str, image: str):
        self.name = name
        self.image = image

    def to_dict(self):
        return {"name": self.name, "image": self.image}
