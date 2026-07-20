from pydantic import BaseModel


class MetricWithDelta(BaseModel):
    value: float
    delta: str | None = None
    trend: str | None = None  # "up" | "down"


class DailyComparisonItem(BaseModel):
    dia: str
    actual: int
    anterior: int


class ServiceStatItem(BaseModel):
    nombre: str
    solicitados: int
    ingresos: float
    tiempo: int


class ClientVisitItem(BaseModel):
    nombre: str
    visitas: int
    cancelaciones: int


class ClientCancellationItem(BaseModel):
    nombre: str
    cancelaciones: int


class HourlyDemandItem(BaseModel):
    hora: str
    turnos: int


class AttendanceSlice(BaseModel):
    name: str
    value: int


class EmployeeStatItem(BaseModel):
    nombre: str
    turnos: int
    ingresos: float
    ocupacion: int


class MonthlyIncomeItem(BaseModel):
    mes: str
    ingresos: float


class Kpis(BaseModel):
    ingresoTotal: MetricWithDelta
    clientesActivos: MetricWithDelta
    servicioMasVendido: str
    diaMasFacturado: str
    horaMayorDemanda: str
    ocupacionAgenda: MetricWithDelta


class Resumen(BaseModel):
    turnosHoy: MetricWithDelta
    turnosSemana: MetricWithDelta
    turnosMes: MetricWithDelta
    turnosPorDia: list[DailyComparisonItem]


class Clientes(BaseModel):
    nuevos: MetricWithDelta
    recurrentes: MetricWithDelta
    inactivos: MetricWithDelta
    topVisitas: list[ClientVisitItem]
    topCancelaciones: list[ClientCancellationItem]


class Servicios(BaseModel):
    items: list[ServiceStatItem]
    menosSolicitado: str | None


class Ingresos(BaseModel):
    facturacionDiaria: MetricWithDelta
    facturacionSemanal: MetricWithDelta
    facturacionMensual: MetricWithDelta
    ticketPromedio: MetricWithDelta
    evolucionMensual: list[MonthlyIncomeItem]


class Agenda(BaseModel):
    horariosDemanda: list[HourlyDemandItem]
    horarioPico: str
    diaMasTurnos: str
    menorOcupacion: str
    ocupacionPorcentaje: int


class Asistencia(BaseModel):
    completados: int
    cancelados: int
    reprogramados: int
    noShow: int
    distribucion: list[AttendanceSlice]
    tasaAsistencia: int
    totalTurnos: int


class DashboardStatisticsResponse(BaseModel):
    kpis: Kpis
    resumen: Resumen
    clientes: Clientes
    servicios: Servicios
    ingresos: Ingresos
    agenda: Agenda
    asistencia: Asistencia
    empleados: list[EmployeeStatItem]
