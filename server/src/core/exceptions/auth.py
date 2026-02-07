class UnauthorizedError(Exception):
    def __init__(self, message: str = "User is not authenticated"):
        self.message = message
        super().__init__(self.message)
