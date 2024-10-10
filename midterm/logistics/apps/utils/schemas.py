from ninja import Schema


class NotFoundSchema(Schema):
    message: str


class NoContentSchema(Schema):
    pass
