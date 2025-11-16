# Sistema de Administrador Unificado - Cambios Realizados

## Resumen
Se ha implementado un sistema de login unificado que permite que usuarios administradores accedan a funcionalidades exclusivas (listar reservas y clientes) desde la misma página de login que los usuarios regulares.

## Cambios Realizados

### 1. **Views (reservas/views.py)**
- ✅ Creada clase `CustomLoginView` que hereda de `LoginView`
- ✅ Redirige a usuarios staff (admin) a `/admin/dashboard/`
- ✅ Redirige a usuarios regulares a `/` (home)
- ✅ Agregada vista `admin_clients()` para listar clientes únicos
- ✅ Agregada vista `admin_dashboard()` para mostrar estadísticas generales
- ✅ Mejorada vista `admin_reservations()` (ya existía)

### 2. **URLs (reservas/urls.py)**
- ✅ Actualizado login para usar `CustomLoginView` en lugar de `LoginView` genérico
- ✅ Agregada ruta `/admin/dashboard/` → `admin_dashboard`
- ✅ Agregada ruta `/admin/clientes/` → `admin_clients`
- ✅ Mantenida ruta `/admin/reservas/` → `admin_reservations`

### 3. **Templates**

#### **admin_base.html** (nuevo)
- Template base para todas las páginas admin
- Navegación con pestañas (Dashboard, Reservas, Clientes)
- Estilos profesionales para el panel administrativo
- Indicadores visuales de sección activa

#### **admin_dashboard.html** (nuevo)
- Página de inicio del panel admin
- Mostrar estadísticas: total de reservas y clientes únicos
- Descripción de funcionalidades disponibles

#### **admin_reservations.html** (mejorado)
- Tabla mejorada con todos los datos de reservas
- Columnas: Fecha, Hora, Cliente, Email, Teléfono, Oferta/Servicio, Notas, Fecha de creación
- Diseño consistente con el resto del panel admin
- Orden: más recientes primero

#### **admin_clients.html** (nuevo)
- Tabla de clientes únicos
- Columnas: Nombre, Email (con enlace mailto), Teléfono (con enlace tel)
- Ideal para enviar comunicaciones a los clientes

#### **base.html** (actualizado)
- Menú de navegación actualizado para mostrar enlaces admin cuando el usuario es staff
- Nuevos enlaces: "🔧 Panel Admin", "📅 Reservas", "👥 Clientes"

### 4. **Comando de Gestión (reservas/management/commands/create_admin.py)**
- ✅ Mejorado con argumentos de línea de comandos
- ✅ Opción de especificar username, email y password
- ✅ Usa variables de entorno como fallback
- ✅ Mensajes de estado mejorados con emojis

## Flujo de Login

### Usuario Regular
1. Accede a `/accounts/login/`
2. Ingresa credenciales
3. Si login exitoso → redirige a `/` (home)
4. No ve opciones administrativas

### Usuario Admin
1. Accede a `/accounts/login/`
2. Ingresa credenciales de admin
3. Si login exitoso → redirige a `/admin/dashboard/`
4. Ve menú completo en navegación:
   - 🔧 Panel Admin (dashboard con estadísticas)
   - 📅 Reservas (listado completo de todas las reservas)
   - 👥 Clientes (listado de contactos de clientes)

## Cómo Crear un Usuario Admin

### Opción 1: Comando con argumentos
```bash
python manage.py create_admin --username admin --email admin@natursur.com --password tu_contraseña
```

### Opción 2: Usar variables de entorno
```bash
ADMIN_USERNAME=admin ADMIN_EMAIL=admin@natursur.com ADMIN_PASSWORD=tu_contraseña python manage.py create_admin
```

### Opción 3: Valores por defecto
```bash
python manage.py create_admin
# Crea usuario "admin" con email "admin@natursur.com" y contraseña "admin123"
```

## URLs Disponibles

| URL | Usuario | Descripción |
|-----|---------|-------------|
| `/accounts/login/` | Todos | Página de login unificada |
| `/` | Todos | Página de inicio |
| `/admin/dashboard/` | Admin | Panel de administración con estadísticas |
| `/admin/reservas/` | Admin | Listado de todas las reservas |
| `/admin/clientes/` | Admin | Listado de clientes |

## Protección de Vistas

Todas las vistas administrativas están protegidas con el decorador `@user_passes_test(lambda u: u.is_staff)`:
- Si un usuario no autenticado intenta acceder → redirige a login
- Si un usuario regular intenta acceder → acceso denegado

## Próximas Mejoras Sugeridas

- [ ] Agregar filtros por fecha en listado de reservas
- [ ] Agregar búsqueda de clientes
- [ ] Exportar reservas a CSV/Excel
- [ ] Dashboard con gráficas de reservas por mes/servicio
- [ ] Sistema de confirmación de reservas por email
- [ ] Editar/eliminar reservas desde el panel admin
