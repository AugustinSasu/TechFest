# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from contextlib import asynccontextmanager

from core.config import settings
from database.engine import engine, Base

from api.routes.dealership import router as dealership_router
from api.routes.customers import router as customers_router
from api.routes.vehicle import router as vehicle_router
from api.routes.service_item import router as service_item_router
from api.routes.sale_order import router as sale_order_router
from api.routes.employee import router as employees_router
from api.routes.car_sale_item import router as car_sale_router
from api.routes.review import router as review_router  # <-- NEW
from api.routes.employee_stats import router as employee_stats_router  # <-- NEW


def generate_unique_id(route: APIRoute) -> str:
    """Face operationId unic indiferent de numele funcției."""
    method = sorted(route.methods)[0].lower()
    tag = (route.tags[0] if route.tags else "default").replace(" ", "_")
    path = (
        route.path_format
        .replace("/", "_")
        .replace("{", "")
        .replace("}", "")
        .strip("_")
    )
    return f"{tag}_{path}_{method}"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    if settings.ENVIRONMENT.lower() == "dev":
        Base.metadata.create_all(bind=engine)
    yield
    # shutdown

app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
    generate_unique_id_function=generate_unique_id,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers — asigură-te că fiecare este inclus O SINGURĂ DATĂ!
app.include_router(dealership_router,   prefix=settings.API_V1_PREFIX)
app.include_router(vehicle_router,      prefix=settings.API_V1_PREFIX)
app.include_router(service_item_router, prefix=settings.API_V1_PREFIX)
app.include_router(sale_order_router,   prefix=settings.API_V1_PREFIX)
app.include_router(customers_router,    prefix=settings.API_V1_PREFIX)
app.include_router(employees_router,    prefix=settings.API_V1_PREFIX)
app.include_router(car_sale_router,     prefix=settings.API_V1_PREFIX)
app.include_router(review_router,       prefix=settings.API_V1_PREFIX)  # <-- NEW
app.include_router(employee_stats_router, prefix=settings.API_V1_PREFIX)  # <-- NEW

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
