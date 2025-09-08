# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from database.engine import engine, Base
from api.routes.dealership import  router as dealership_router  # ai nevoie de api/routers/dealership.py

from api.routes.vehicle import router as vehicle_router
from api.routes.service_item import router as service_item_router
from api.routes.sale_item import router as sale_item_router


app = FastAPI(title=settings.APP_NAME)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(dealership_router, prefix=settings.API_V1_PREFIX)
app.include_router(vehicle_router,      prefix=settings.API_V1_PREFIX)
app.include_router(service_item_router, prefix=settings.API_V1_PREFIX)
app.include_router(sale_item_router,    prefix=settings.API_V1_PREFIX)

# Healthcheck
@app.get("/health")
def health():
    return {"status": "ok"}

# Creează tabelele la startup în dev (opțional, util pentru test rapid)
@app.on_event("startup")
def on_startup():
    if settings.ENVIRONMENT.lower() == "dev":
        Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
