class Champion:
    def __init__(self, name: str, image: str, cost: int):
        self.name = name
        self.image = image
        self.cost = cost

    def dict(self):
        return {"name": self.name, "image": self.image, "cost": self.cost}
