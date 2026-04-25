from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from slowapi.errors import RateLimitExceeded

from app.models import PredictionRequest, PredictionResponse
from app.inference import inference_service
from app.rate_limiter import limiter
from app.security import check_prompt_injection


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        inference_service.load_model()
        yield
    finally:
        pass


app = FastAPI(
    title="AI Production API",
    version="1.0.0",
    description="API для генерации текста с помощью дообученной модели",
    lifespan=lifespan,
)

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "detail": "Превышен лимит запросов. Максимум 10 запросов в минуту на IP.",
        },
    )


@app.get("/")
async def root():
    return {
        "service": "AI Production API",
        "version": "1.0.0",
        "description": "Fine-tuned LLM inference API",
    }


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/generate", response_model=PredictionResponse)
@limiter.limit("10/minute")
async def generate_text(request: Request, body: PredictionRequest):
    # Проверка на prompt injection
    injection_result = check_prompt_injection(body.prompt)
    if injection_result:
        return JSONResponse(
            status_code=400,
            content={
                "error": "prompt_injection_detected",
                "detail": f"Запрос отклонён: обнаружен подозрительный паттерн ({injection_result}).",
            },
        )

    try:
        result = inference_service.generate(body.prompt, body.max_tokens)
        return PredictionResponse(
            prompt=body.prompt,
            generated_text=result["text"],
            model=inference_service.model_path,
            tokens_used=result["tokens_used"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))