from fastapi.middleware.cors import CORSMiddleware

def configure_cors(app):
    origins = [
        "http://localhost:5173",  # Frontend React (Vite)
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
