class Champion:
    def __init__(self, name: str, image: str):
        self.name = name
        self.image = image

    def dict(self):
        return {"name": self.name, "image": self.image}
