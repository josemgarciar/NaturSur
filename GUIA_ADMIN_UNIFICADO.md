# 🎉 Sistema de Admin Unificado - Guía de Uso

## ✅ Implementación Completada

Se ha unificado el sistema de login de la aplicación NaturSur para que usuarios administradores y regulares accedan por la misma página de login, siendo redirigidos a diferentes destinos según su rol.

---

## 🔑 Credenciales de Admin (Prueba)

**Usuario:** `admin`
**Email:** `admin@natursur.com`
**Contraseña:** `admin123` (o la que especificaste al crear el usuario)

---

## 📍 URLs Principales

### Para Usuarios Regulares
- **`/`** - Página de inicio con formulario de reserva
- **`/accounts/login/`** - Login unificado
- **`/accounts/signup/`** - Registro de nuevas cuentas

### Para Administradores
- **`/accounts/login/`** - Login unificado (igual que usuarios regulares)
- **`/admin/dashboard/`** - Panel principal con estadísticas
- **`/admin/reservas/`** - Listado completo de reservas
- **`/admin/clientes/`** - Listado de contactos de clientes

---

## 🚀 Flujo de Login

### 1️⃣ Usuario Regular
```
Ingresa credenciales regulares en /accounts/login/
          ↓
    Verifica que no es staff
          ↓
    Redirige a / (home)
```

### 2️⃣ Usuario Administrador
```
Ingresa credenciales admin en /accounts/login/
          ↓
    Verifica que es staff (is_staff=True)
          ↓
    Redirige a /admin/dashboard/
```

---

## 📊 Panel de Administración

### Dashboard (`/admin/dashboard/`)
- **Mostrar:** Total de reservas | Total de clientes únicos
- **Opciones:** Navegación rápida a Reservas y Clientes

### Reservas (`/admin/reservas/`)
- **Tabla con:** Fecha, Hora, Nombre, Email, Teléfono, Oferta/Servicio, Notas, Fecha de creación
- **Ordenado por:** Más recientes primero
- **Ideal para:** Gestionar agenda y confirmar reservas

### Clientes (`/admin/clientes/`)
- **Tabla con:** Nombre, Email (clickeable), Teléfono (clickeable)
- **Datos:** Clientes únicos que han realizado reservas
- **Ideal para:** Enviar comunicaciones o crear base de datos

---

## 🛠️ Crear Nuevo Usuario Admin

### Opción 1: Con argumentos de línea de comandos
```bash
python manage.py create_admin --username nuevo_admin --email admin@natursur.com --password contraseña123
```

### Opción 2: Con variables de entorno
```bash
set ADMIN_USERNAME=nuevo_admin
set ADMIN_EMAIL=admin2@natursur.com
set ADMIN_PASSWORD=contraseña123
python manage.py create_admin
```

### Opción 3: Usar valores por defecto
```bash
python manage.py create_admin
# Crea usuario "admin" con contraseña "admin123"
```

---

## 🔐 Seguridad

✅ **Protección de vistas administrativas:**
- Todas las vistas de admin usan `@user_passes_test(lambda u: u.is_staff)`
- Solo usuarios con `is_staff=True` pueden acceder
- Usuarios no autenticados son redirigidos a login
- Usuarios regulares reciben acceso denegado

✅ **Cambiar contraseña admin:**
```bash
python manage.py changepassword admin
```

✅ **Crear superuser alternativo (Django admin):**
```bash
python manage.py createsuperuser
```

---

## 📝 Menú de Navegación

Cuando un administrador está logueado, el menú muestra:

```
Inicio
Únete al equipo
Estudio corporal
🔧 Panel Admin      ← NUEVO
📅 Reservas         ← NUEVO
👥 Clientes         ← NUEVO
Cerrar sesión
```

Los usuarios regulares **no ven** estas opciones.

---

## 🎯 Archivos Modificados/Creados

### Vistas
- ✅ `reservas/views.py` - Agregadas `CustomLoginView`, `admin_dashboard`, `admin_clients`

### URLs
- ✅ `reservas/urls.py` - Rutas actualizadas para admin

### Templates
- ✅ `reservas/templates/reservas/admin_base.html` - Template base para admin (NUEVO)
- ✅ `reservas/templates/reservas/admin_dashboard.html` - Dashboard (NUEVO)
- ✅ `reservas/templates/reservas/admin_clients.html` - Listado de clientes (NUEVO)
- ✅ `reservas/templates/reservas/admin_reservations.html` - Mejorado
- ✅ `reservas/templates/reservas/base.html` - Navegación actualizada

### Management Commands
- ✅ `reservas/management/commands/create_admin.py` - Mejorado

---

## ⚠️ Notas Importantes

1. **Cambiar contraseña por defecto:** Después de crear el usuario admin, se recomienda cambiar la contraseña `admin123` por una más segura.

2. **Usuarios múltiples:** Puedes crear varios usuarios admin ejecutando el comando varias veces con diferentes usernames.

3. **Permisos:** Todos los usuarios admin tienen acceso a todas las funcionalidades administrativas.

4. **Datos sensibles:** El listado de clientes muestra información de contacto. Asegúrate de que solo el personal autorizado tenga acceso.

---

## 🧪 Probar la Aplicación

1. **Inicio del servidor:**
   ```bash
   python manage.py runserver
   ```

2. **Acceder a:**
   - Login: `http://127.0.0.1:8000/accounts/login/`
   - Home (usuario regular): `http://127.0.0.1:8000/`
   - Dashboard (admin): `http://127.0.0.1:8000/admin/dashboard/`

3. **Pruebas recomendadas:**
   - [ ] Login como admin → debe ir a dashboard
   - [ ] Login como usuario regular → debe ir a home
   - [ ] Ver listado de reservas desde admin
   - [ ] Ver listado de clientes desde admin
   - [ ] Verificar que usuarios regulares no puedan acceder a `/admin/*`

---

## 📞 Soporte

Para cualquier problema o mejora, revisa:
- `CAMBIOS_ADMIN.md` - Detalle técnico de los cambios
- `docs/requisitos_estado.md` - Requisitos del proyecto
- Archivo de configuración: `natursur/settings.py`

---

**Última actualización:** 16 de noviembre de 2025  
**Estado:** ✅ Implementado y Probado
