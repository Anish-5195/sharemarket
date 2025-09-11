from fastapi import FastAPI
from auth.auth import router as auth_router
from db.session import Base, engine

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Multi-User Auth API")

# Include routers
app.include_router(auth_router)

