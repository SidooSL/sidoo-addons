# Project Attachments

## Propósito

Este módulo añade un smartbutton en la vista formulario de proyectos que permite acceder rápidamente a todos los archivos adjuntos relacionados con el proyecto y sus tareas.

## Funcionalidad

- **Smartbutton "Attachments"**: Muestra el número total de archivos adjuntos del proyecto y sus tareas
- **Acceso directo**: Al hacer clic, abre la vista kanban de `ir.attachment` filtrada por los archivos del proyecto y sus tareas
- **Conteo automático**: El botón muestra el número actualizado de archivos adjuntos

## Casos de Uso

- Visualizar todos los documentos relacionados con un proyecto en un solo lugar
- Gestionar archivos adjuntos tanto del proyecto como de sus tareas
- Acceso rápido a documentación del proyecto sin navegar por cada tarea individualmente

## Características Técnicas

### Modelo Extendido: `project.project`

- **Campo computed**: `attachment_count` - Cuenta total de archivos adjuntos
- **Método de acción**: `action_view_attachments()` - Abre la vista filtrada de archivos

### Filtrado de Archivos

El módulo busca archivos adjuntos donde:
- `res_model = 'project.project'` AND `res_id = project_id`, O
- `res_model = 'project.task'` AND `res_id IN task_ids_del_proyecto`

### Vista Kanban

Los archivos se muestran en vista kanban por defecto, con opciones para cambiar a vista de árbol o formulario.

## Instalación

```bash
/opt/odoo/src/odoo/odoo-bin -i project_attachments --stop-after-init --config=/opt/odoo/conf/odoo.conf
```

## Dependencias

- `project`: Módulo base de proyectos de Odoo
- `base`: Funcionalidades básicas de Odoo

## Permisos

Los usuarios con roles de proyecto (Project User/Project Manager) tienen acceso completo a la funcionalidad de archivos adjuntos.