# Estado de requisitos — Listado de requisitos v2

Fecha: 13/11/2025
Origen: `docs/Listado_de_requisitos_v2.txt` (extraído desde el .docx)

Resumen: he analizado los requisitos del documento y los comparé con el código actual del proyecto (app `reservas`). Abajo se indica el estado por requisito, evidencia y acciones recomendadas.

## Mapa rápido
- Cumplidos: RF-1, RF-2, RF-4 (básico), RF-5, RF-6, RF-11, RF-16
- Parciales / Implementación limitada: RF-4 (sin verificación de disponibilidad), RF-13 (depende de despliegue), RF-17 (YouTube OK, Instagram no)
- No cumplidos: RF-3, RF-7, RF-8, RF-9, RF-10, RF-12, RF-14, RF-15

---

## Detalle por requisito

RF-1 | Funcional — Mostrar tipos de servicios para reservar
- Estado: Cumplido
- Evidencia: `reservas.models.Reservation.SERVICE_CHOICES`, `reservas/templates/reservas/home.html` muestra los servicios y el formulario (`ReservationForm`) incluye `service`.
- Comentario: Implementación completa.

RF-2 | Funcional — Mostrar información relacionada con cada servicio
- Estado: Cumplido
- Evidencia: `home.html` secciones `features` con descripciones de cada servicio.

RF-3 | Funcional — Mostrar horarios disponibles para el servicio seleccionado
- Estado: No cumplido
- Evidencia: El formulario (`ReservationForm`) usa campos `date` y `time` libres; no hay lógica de disponibilidad ni modelo de franjas horarios.
- Recomendación: Implementar un sistema de disponibilidad (modelo `Timeslot` o comprobación por servicio/fecha/hora), o un simple bloqueo que evite doble reserva en la misma franja.

RF-4 | Funcional — Permitir reservar el servicio en el horario
- Estado: Parcial / Básico implementado
- Evidencia: `reservas/views.reservar` guarda instancias de `Reservation` si el formulario es válido.
- Limitaciones: No se comprueba disponibilidad ni se envía confirmación por email automáticamente.
- Recomendación: Añadir verificación de disponibilidad (relacionado con RF-3) y envío de correo de confirmación.

RF-5 | Funcional — Mostrar información del negocio (ubicación, teléfono...)
- Estado: Cumplido
- Evidencia: `natursur/context_processors.social()` y `home.html` sección de contacto; enlaces a teléfono y WhatsApp.

RF-6 | Funcional — Permitir acceder a la plataforma de venta de productos
- Estado: Cumplido
- Evidencia: `natursur/settings.EXTERNAL_SHOP_URL` y vista `reservas/tienda` (actualmente devuelve la plantilla de tienda). Nota: existe un cambio anterior para redirigir; confirmar implementación actual.

RF-7 | Funcional — Registrar compras recurrentes de clientes
- Estado: No cumplido
- Evidencia: No existe modelo ni lógica para registrar compras o recurring purchases.
- Recomendación: Crear modelo `Purchase` (usuario/email, producto, fecha, recurring flag) e interfaces para registrar/consultar.

RF-8 | Funcional — Mostrar recomendaciones basadas en compras de cada usuario
- Estado: No cumplido
- Evidencia: No hay histórico de compras ni lógica de recomendaciones.
- Recomendación: Requiere almacenamiento de compras (RF-7) y un componente de recomendaciones (reglas simples o ML).

RF-9 | Funcional — Indicadores en fechas clave (cumpleaños)
- Estado: No cumplido
- Evidencia: No existen perfiles de usuario o fechas de cumpleaños almacenadas.
- Recomendación: Añadir entidad `Customer`/`Profile` con campo `birthdate` y lógica para mostrar badges en UI.

RF-10 | Funcional — Notificar por correo o teléfono ofertas/ descuentos
- Estado: No cumplido
- Evidencia: No hay sistema de notificaciones; Django está listo para enviar emails si se configura `EMAIL_BACKEND`, pero no hay código.
- Recomendación: Implementar envío de emails para comunicaciones (usar `send_mail` o tareas background con Celery) y, si se desea SMS/WhatsApp, integrar proveedor (Twilio o usar el enlace directo a wa.me para mensajes).

RF-11 | Funcional — Mantener enlaces a servicios externos previos
- Estado: Cumplido
- Evidencia: Enlaces a redes y tienda en plantillas y context processor.

RF-12 | Seguridad — Datos almacenados deben estar cifrados
- Estado: No cumplido
- Evidencia: Base de datos SQLite normal (sin cifrado) y no hay cifrado a nivel de campo.
- Recomendación: Evaluar necesidad real: cifrado en reposo en producción (disco cifrado, RDS con cifrado) y cifrado a nivel de campo para datos sensibles (use django-cryptography o field-encryption). Añadir políticas y pruebas.

RF-13 | Seguridad — Transacciones con protocolos seguros (HTTPS)
- Estado: Parcial
- Evidencia: El código usa URLs HTTPS para externos; asegurar HTTPS es responsabilidad de despliegue (serve behind HTTPS). En desarrollo está `DEBUG=True`.
- Recomendación: En despliegue, habilitar HTTPS, HSTS y `SECURE_SSL_REDIRECT=True` en `settings.py` para producción.

RF-14 | Funcional — Almacenar tiempo de uso/regularidad de compras
- Estado: No cumplido
- Evidencia: No hay métricas o histórico sobre tiempo de uso.
- Recomendación: Añadir timestamps y agregaciones en `Purchase`/`Reservation` para calcular métricas de uso.

RF-15 | Funcional — Sistema de experiencia / fidelización
- Estado: No cumplido
- Evidencia: No existe módulo de puntos o niveles.
- Recomendación: Diseñar modelo de fidelización (puntos por compra/reserva) y reglas para ventajas. Inicialmente puede quedar como requisito a planificar.

RF-16 | Funcional — Adaptarse a diferentes dispositivos (responsive)
- Estado: Cumplido
- Evidencia: `static/reservas/css/style.css` incluye estilos responsivos y `prefers-color-scheme`; plantillas usan layout adaptable.

RF-17 | Funcional — Mostrar contenido publicado en redes sociales
- Estado: Parcial
- Evidencia: `reservas/views._fetch_youtube_videos` implementado usando feed RSS → YouTube muestra vídeos. Instagram fetch es placeholder y `home.html` contiene iframe/embed de Instagram y Facebook plugin.
- Recomendación: Para Instagram usar Graph API oficial o un proceso que actualice cachés; mejorar manejo de fallos y mostrar mensajes claros al usuario si no están disponibles.

---

## Siguientes pasos propuestos (rápidos)
1. Priorizar la implementación de RF-3 (comprobación de disponibilidad) y RF-7 (registro de compras) — ambos habilitan RF-4 completo y RF-8.
2. Crear modelos y migraciones iniciales para `Purchase` y, si procede, `Profile` con `birthdate`.
3. Preparar envío de correos (configurar `EMAIL_BACKEND` en `settings.py` y plantilla de email para confirmación de reserva).
4. Evaluar cifrado (RF-12): si es requisito legal, planificar cifrado a nivel de campo y revisión de despliegue.
5. Mejorar `reservas/views._fetch_instagram_posts` o integrar Instagram Graph API.

---

## Archivos revisados (evidencia rápida)
- `reservas/models.py`, `reservas/forms.py`, `reservas/views.py`
- `reservas/templates/reservas/home.html`, `tienda.html`, `base.html`
- `natursur/settings.py` (EXTERNAL_SHOP_URL)

---

Si quieres, puedo:
- Implementar un sistema básico de disponibilidad (bloqueo simple por servicio/fecha/hora) y pruebas unitarias.
- Añadir el modelo `Purchase` y una vista sencilla para registrar compras recurrentes (API o formulario).
- Crear las tareas/PRs necesarias y aplicar migraciones.

Dime cuál de estas acciones prefieres que haga ahora y la priorizo.
