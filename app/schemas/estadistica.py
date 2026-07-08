from pydantic import BaseModel


class SummaryCard(BaseModel):
    appointments: int
    variation: float


class SummaryChartItem(BaseModel):
    label: str
    current: int
    previous: int


class SummaryStatistics(BaseModel):
    today: SummaryCard
    week: SummaryCard
    month: SummaryCard
    chart: list[SummaryChartItem]


class DashboardStatistics(BaseModel):
    summary: SummaryStatistics