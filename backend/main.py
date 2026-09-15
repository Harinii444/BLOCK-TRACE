from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="BLOCK-TRACE API",
    description="Backend tracking engine for tracing cryptocurrency transactions across addresses",
    version="1.0.0"
)

# Allow your frontend (Divakar's Streamlit App) to connect securely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "project": "BLOCK-TRACE",
        "message": "FastAPI tracking gateway is running smoothly!"
    }
