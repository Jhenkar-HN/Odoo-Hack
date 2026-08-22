from fastapi import APIRouter
from backend.app.routes.auth import router as auth_router
from backend.app.routes.users import router as users_router
from backend.app.routes.employees import router as employees_router
from backend.app.routes.profiles import router as profiles_router
from backend.app.routes.salaries import router as salaries_router
from backend.app.routes.attendance import router as attendance_router
from backend.app.routes.time_off import router as time_off_router
from backend.app.routes.settings import router as settings_router
from backend.app.routes.stats import router as stats_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(employees_router)
api_router.include_router(profiles_router)
api_router.include_router(salaries_router)
api_router.include_router(attendance_router)
api_router.include_router(time_off_router)
api_router.include_router(settings_router)
api_router.include_router(stats_router)
