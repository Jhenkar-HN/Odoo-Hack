from fastapi import APIRouter
from app.models import DashboardStatsResponse
from app import crud

router = APIRouter(prefix="/api/stats", tags=["Dashboard Analytics"])


@router.get("/dashboard", response_model=DashboardStatsResponse)
def get_dashboard_metrics():
    """Retrieve summarized analytics KPIs for dashboard cards, attendance charts, and departments."""
    return crud.get_dashboard_stats()
