from pydantic import BaseModel, ConfigDict


class ExceptionDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    source: str
    type: str
    message: str
