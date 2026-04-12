@router.get("/admin/dashboard")
def admin_dashboard(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403)

    negocios = db.query(Negocio).all()

    return {
        "total_negocios": len(negocios),
        "activos": len([n for n in negocios if n.activo]),
        "turnos_totales": sum(len(n.turnos) for n in negocios),
        "negocios": [
            {
                "id": n.id_negocio,
                "nombre": n.nombre,
                "categoria": n.rubro,
                "activo": n.activo,
                "slug": n.slug,
                "usuario": {
                    "nombre": n.usuario.usuario_us,
                    "email": n.usuario.email_us,
                }
            }
            for n in negocios
        ]
    }