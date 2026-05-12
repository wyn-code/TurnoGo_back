# from apscheduler.schedulers.background import BackgroundScheduler
# from datetime import datetime, timedelta
# from app.core.dependencies import get_db
# from app.services.whatsapp_service import enviar_whatsapp
# from app.models.turnos import Turno

# scheduler = BackgroundScheduler()

# def verificar_y_enviar_recordatorios():
#     # Obtenemos una sesión de DB manual ya que estamos fuera del ciclo de FastAPI
#     db = next(get_db())
#     try:
#         # Definimos el rango: turnos que ocurren mañana en esta misma hora
#         mañana = datetime.now() + timedelta(days=1)
#         rango_inicio = mañana.replace(minute=0, second=0, microsecond=0)
#         rango_fin = rango_inicio + timedelta(hours=1)

#         # Buscamos turnos en ese rango que no hayan sido notificados aún
#         turnos_proximos = db.query(Turno).filter(
#             Turno.fecha_hora >= rango_inicio,
#             Turno.fecha_hora < rango_fin,
#             Turno.recordatorio_enviado == False
#         ).all()

#         for turno in turnos_proximos:
#             exito = enviar_whatsapp(
#                 telefono=turno.cliente_telefono,
#                 nombre_cliente=turno.cliente_nombre,
#                 fecha=turno.fecha_hora.strftime("%d/%m/%Y"),
#                 hora=turno.fecha_hora.strftime("%H:%M")
#             )
            
#             if exito:
#                 turno.recordatorio_enviado = True
        
#         db.commit()
#     finally:
#         db.close()

# def start_scheduler():
#     # Se ejecuta cada hora
#     scheduler.add_job(verificar_y_enviar_recordatorios, 'interval', hours=1)
#     scheduler.start()