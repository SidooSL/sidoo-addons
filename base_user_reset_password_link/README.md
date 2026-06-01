# Reset Password URL Viewer

Módulo para entornos **neutralizados o de prueba** en Odoo 18.

## ¿Qué hace?

En bases de datos neutralizadas el envío de correos está bloqueado, lo que impide
que el flujo estándar de "Enviar instrucciones de restablecimiento" llegue al usuario.

Este módulo añade una **acción de servidor** en el modelo `res.users` que:

1. Genera el token de restablecimiento (el mismo que usaría el email)
2. Construye la URL completa
3. La muestra en un **wizard emergente** con el widget `CopyClipboardChar`
   para copiar la URL al portapapeles con un solo clic

## Instalación

Copiar la carpeta `reset_url_viewer` al directorio de addons de Odoo, actualizar
la lista de aplicaciones e instalar desde Ajustes → Aplicaciones.

## Uso

1. Ir a **Ajustes → Usuarios y compañías → Usuarios**
2. Seleccionar **un único usuario**
3. Menú **Acción** → "Obtener link restablecimiento de contraseña"
4. Copiar la URL con el botón de copia y enviársela al usuario

## Dependencias

- `base`
- `auth_signup`

## Compatibilidad

- Odoo 18.0

## Notas de seguridad

- La acción solo está disponible para el grupo **Administración / Ajustes**
- La URL generada es temporal (expira según la configuración de Odoo)
- El enlace debe compartirse **solo con el usuario correspondiente**
