# 🚨 Problema detectado en POS con descuentos generales

**Versiones afectadas:** 14.0, 15.0, 16.0
**Módulos instalados:** `point_of_sale` + `pos_discount` (ambos de core)

## Configuración
- **Descuentos Generales:** Activados
- **Idioma:** Español

## Descripción del problema
Cuando se aplica un descuento general, el valor decimal no se interpreta correctamente.

El motivo es que la función nativa de JavaScript `parseFloat` recibe `"10,5"` (con coma) en lugar de `"10.5"` (con punto).
Como resultado, el descuento se convierte en `10` en lugar de `10.5`, es decir, **se pierden los decimales**.

### Observaciones
- Este bug **no ocurre** si se aplican descuentos por línea.
- Este bug **no ocurre** si el idioma es inglés (por el uso de punto en lugar de coma).

## Estado actual
- El error fue **corregido en Odoo 17.0**.
- Todo indica que también afecta a versiones anteriores a la 14.0.
