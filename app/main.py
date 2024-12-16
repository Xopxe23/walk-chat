import os
import sys

import uvicorn
from fastapi import FastAPI
from app.chats.router import router as chat_router

sys.path.insert(1, os.path.join(sys.path[0], '..'))

app = FastAPI(
    title="WALK Chat"
)

app.include_router(chat_router)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", reload=True,
    )
