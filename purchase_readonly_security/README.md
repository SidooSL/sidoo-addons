# Purchase Readonly Security

## Propósito

Este módulo crea un permiso específico que permite la modificación de órdenes de compra en Odoo, restringiendo por defecto la capacidad de editar, crear o eliminar pedidos de compra a usuarios que no tengan el permiso específico.

## Casos de Uso

- Control granular de quién puede modificar órdenes de compra
- Separación de roles entre usuarios que solo consultan y usuarios que gestionan pedidos
- Implementación de workflows de aprobación donde solo ciertos usuarios pueden editar

## Funcionalidad

### Nuevo Grupo de Permisos

El módulo implementa un **grupo de seguridad independiente** llamado **"Purchase Orders Edition"** que:

- **Controla operaciones CRUD**: Crear, modificar y eliminar órdenes de compra
- **Es opcional y granular**: No se asigna automáticamente a roles existentes
- **Funciona por exclusión**: Sin el grupo = solo lectura, con el grupo = edición completa

### Comportamiento de la Interfaz

#### Usuarios SIN permisos de edición:
- ✅ **Lectura completa**: Acceso a listados y formularios de pedidos
- ✅ **Navegación**: Búsqueda, filtros y reportes
- ❌ **Botones de acción ocultos**: No ven "Crear", "Editar", "Eliminar"
- ❌ **Header de formulario oculto**: Sin acceso a botones de estado/workflow

#### Usuarios CON permisos de edición:
- ✅ **Funcionalidad completa**: Todas las operaciones estándar de purchase
- ✅ **Botones visibles**: Crear, editar, eliminar, cambios de estado
- ✅ **Workflow completo**: Confirmación, recepción, facturación

#### Administradores del sistema:
- ✅ **Permisos completos**: Sin restricciones, comportamiento estándar de Odoo

## Configuración

### Asignación de Permisos

#### Por Usuario Individual:
1. **Usuarios y Compañías** → **Usuarios**
2. **Seleccionar usuario** → **Editar**
3. **Pestaña "Access Rights"** → Marcar **"Purchase Orders Edition"**
4. **Guardar cambios**

#### Por Grupos Existentes:
1. **Configuración** → **Usuarios y Compañías** → **Grupos**
2. **Buscar grupo objetivo** (ej: "Purchase User")
3. **Pestaña "Implied Groups"** → Añadir **"Purchase Orders Edition"**

### Verificación de Configuración

- **Usuario con permisos**: Ve botones de acción en vista formulario
- **Usuario sin permisos**: Header de formulario completamente oculto
- **Ambos tipos**: Pueden acceder a vistas de lista y consultar datos


## Instalación

### Proceso Automático

El módulo se instala sin configuración manual requerida:

1. **Grupos creados automáticamente**: Durante la instalación
2. **Permisos aplicados**: A usuarios existentes según configuración
3. **Sin interrupciones**: Funcionalidad existente preservada
4. **Listo para usar**: Inmediatamente tras instalación

### Post-Instalación

**Solo se requiere**: Asignar el grupo "Purchase Orders Edition" a usuarios que necesiten capacidades de edición.

**Por defecto**: Todos los usuarios quedan en modo solo lectura hasta asignación explícita de permisos.

## Limitaciones y Consideraciones

### Scope del Módulo

- **Solo órdenes de compra**: No afecta otros módulos de purchase (ej: agreements)
- **Interfaz web únicamente**: APIs y acceso programático siguen reglas estándar Odoo
- **Sin gradación**: Permisos binarios (todo o nada), sin niveles intermedios

### Casos No Cubiertos

- **Permisos por compañía**: Funciona a nivel global, no por empresa
- **Restricciones temporales**: Sin control basado en fechas o períodos
- **Aprobación workflow**: No incluye flujos de aprobación multi-nivel
