import os
import sys

import uvicorn
from fastapi import FastAPI

sys.path.insert(1, os.path.join(sys.path[0], '..'))


app = FastAPI(
    title="WALK Chat"
)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", reload=True,
    )
