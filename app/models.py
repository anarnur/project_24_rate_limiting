from pydantic import BaseModel, field_validator, Field


class PredictionRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000, description="Текст запроса")
    max_tokens: int = Field(default=256, ge=1, le=2048, description="Максимальное количество токенов")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Температура генерации")

    @field_validator("prompt")
    @classmethod
    def prompt_must_not_be_blank(cls, v: str) -> str:
        if v.strip() == "":
            raise ValueError("Поле prompt не может состоять только из пробелов")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "prompt": "Напиши короткое стихотворение о весне",
                    "max_tokens": 256,
                    "temperature": 0.7,
                }
            ]
        }
    }


class PredictionResponse(BaseModel):
    prompt: str
    generated_text: str
    model: str
    tokens_used: int