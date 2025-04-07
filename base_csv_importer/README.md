Base CSV Importer
=================

Este módulo proporciona una solución base para la importación de archivos CSV en Odoo. Es una herramienta low-code diseñada para ser extendida y utilizada en módulos específicos. Puedes revisar `account_importer`, para casos de uso concretos.

Características principales
---------------------------
- Proporciona una base genérica para la importación de datos desde archivos CSV.
- Utiliza tablas intermedias planas que será procesada por jobs para no saturar el sistema
- Facilita la personalización y extensión para necesidades específicas. Aporta plantilla para algunos datos maestros.
- Manejo de errores y validaciones básicas durante la importación.

Uso
-----
1. Ve a la app "Importador Sidoo"
2. Añada un nuevo registro en la sección de "Importaciones" y suba un fichero zip
3. Presiona "Importar". Esto transformará los csv del zip en tablas intermedias
4. Presiona sobre el nuevo botón "Encolar ficheros"
5. Esperar a que el sistema termine la importación. El proceso se ejecuta en segundo plano y no bloquea el sistema
6. Una vez terminado, el registro cambia de estado a "Finalizado" o "Finalizado con errores". Existe un cron que actualiza el estado. También puedes pulsar sobre "Comprobar estado" para actualizarlo manualmente
7. Si el estado es "Finalizado con errores", puedes revisar la pestaña de "Errores" o pulsar sobre "Registros" para editar y reintentar registro por registro. Si falló un conjunto amplio de registros y no se pudo procesar, tienes la pestaña Lotes donde se vincula el job que falló. Puedes reencolar el job para reintentarlo

Dependencias
------------
Este módulo depende de queue_job
