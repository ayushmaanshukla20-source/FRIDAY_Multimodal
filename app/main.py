# Backward compatibility wrapper pointing to the full F.R.I.D.A.Y. backend
from backend.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
