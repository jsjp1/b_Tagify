from pydantic import BaseModel


class DefaultSuccessResponse(BaseModel):
  message: str