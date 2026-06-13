from fastapi import FastAPI, HTTPException
from app.models.request import SignalRequest
from app.models.response import SignalResponse
from app.services.signal_engine import generate_signal

app = FastAPI(
    title       = "MarketPulse AI Signal Engine",
    description = "Probabilistic market signal generator. Not financial advice.",
    version     = "1.0.0"
)


@app.post("/generate-signal", response_model=SignalResponse)
def generate(request: SignalRequest) -> SignalResponse:
    try:
        return generate_signal(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {
        "status":  "ok",
        "service": "MarketPulse AI Signal Engine",
        "version": "1.0.0"
    }