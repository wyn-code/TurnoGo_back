from app.models.turnos import Turno
from datetime import datetime, timedelta
from sqlalchemy import func
from app.models.turnos import Turno

class StatisticsService:

    def __init__(self, db):
        self.db = db

    def get_dashboard_statistics(self, business_id: int):
        return {
            "summary": self.get_summary(business_id)
    }

    def get_summary(self, business_id: int):

        today = self._get_today_appointments(business_id)
        yesterday = self._get_yesterday_appointments(business_id)

        week = self._get_week_appointments(business_id)
        last_week = self._get_last_week_appointments(business_id)

        month = self._get_month_appointments(business_id)
        last_month = self._get_last_month_appointments(business_id)

        return {
            "today": {
                "appointments": today,
                "variation": self._calculate_variation(today, yesterday)
            },
            "week": {
                "appointments": week,
                "variation": self._calculate_variation(week, last_week)
            },
            "month": {
                "appointments": month,
                "variation": self._calculate_variation(month, last_month)
            },
            "chart": self._get_summary_chart(business_id)
        }

    def _calculate_variation(self, current: int, previous: int) -> float:
        if previous == 0:
            if current == 0:
                return 0.0
            return 100.0

        return round(((current - previous) / previous) * 100, 2)
    
    def _get_today_appointments(self, business_id: int) -> int:
        return (
            self.db.query(func.count(Turno.id_turno))
            .filter(
                Turno.id_negocio == business_id,
                func.date(Turno.fecha_hora_inicio) == func.current_date()
            )
            .scalar()
            or 0
        )

    def _get_yesterday_appointments(self, business_id: int) -> int:
        yesterday = datetime.now().date() - timedelta(days=1)

        return (
            self.db.query(func.count(Turno.id_turno))
            .filter(
                Turno.id_negocio == business_id,
                func.date(Turno.fecha_hora_inicio) == yesterday
            )
            .scalar()
            or 0
        )

    def _get_week_appointments(self, business_id: int) -> int:
        today = datetime.now().date()

        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)

        return (
            self.db.query(func.count(Turno.id_turno))
            .filter(
                Turno.id_negocio == business_id,
                func.date(Turno.fecha_hora_inicio).between(start_week, end_week)
            )
            .scalar()
            or 0
        )

    def _get_last_week_appointments(self, business_id: int) -> int:
        today = datetime.now().date()

        start_this_week = today - timedelta(days=today.weekday())

        start_last_week = start_this_week - timedelta(days=7)
        end_last_week = start_this_week - timedelta(days=1)

        return (
            self.db.query(func.count(Turno.id_turno))
            .filter(
                Turno.id_negocio == business_id,
                func.date(Turno.fecha_hora_inicio).between(
                    start_last_week,
                    end_last_week
                )
            )
            .scalar()
            or 0
        )

    def _get_month_appointments(self, business_id: int) -> int:

        today = datetime.now().date()

        first_day = today.replace(day=1)

        return (
            self.db.query(func.count(Turno.id_turno))
            .filter(
                Turno.id_negocio == business_id,
                func.date(Turno.fecha_hora_inicio).between(
                    first_day,
                    today
                )
            )
            .scalar()
            or 0
        )

    def _get_last_month_appointments(self, business_id: int) -> int:
        today = datetime.now().date()

        first_day_this_month = today.replace(day=1)

        last_day_last_month = first_day_this_month - timedelta(days=1)

        first_day_last_month = last_day_last_month.replace(day=1)

        return (
            self.db.query(func.count(Turno.id_turno))
            .filter(
                Turno.id_negocio == business_id,
                func.date(Turno.fecha_hora_inicio).between(
                    first_day_last_month,
                    last_day_last_month
                )
            )
            .scalar()
            or 0
        )

    def _get_summary_chart(self, business_id: int):

        today = datetime.now().date()

        start_week = today - timedelta(days=today.weekday())
        start_last_week = start_week - timedelta(days=7)

        chart = []

        days = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

        for i in range(7):

            current_day = start_week + timedelta(days=i)
            previous_day = start_last_week + timedelta(days=i)

            current = (
                self.db.query(func.count(Turno.id_turno))
                .filter(
                    Turno.id_negocio == business_id,
                    func.date(Turno.fecha_hora_inicio) == current_day
                )
                .scalar()
                or 0
            )

            previous = (
                self.db.query(func.count(Turno.id_turno))
                .filter(
                    Turno.id_negocio == business_id,
                    func.date(Turno.fecha_hora_inicio) == previous_day
                )
                .scalar()
                or 0
            )

            chart.append({
                "label": days[i],
                "current": current,
                "previous": previous
            })

        return chart



