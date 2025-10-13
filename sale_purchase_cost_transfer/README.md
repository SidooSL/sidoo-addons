# Módulo: Sale Purchase Cost Transfer

## Propósito

Permite trasladar automáticamente el coste de compra (`purchase_price`) definido en la línea del pedido de venta (`sale.order.line`) al precio unitario (`price_unit`) de la línea del pedido de compra (`purchase.order.line`) generada a partir de la venta.

## Casos de Uso

- Empresas que gestionan ventas que disparan automáticamente compras (dropshipping, make-to-order, etc.) y requieren que el coste real pactado en la venta se refleje fielmente en la compra.
- Escenarios donde el precio de compra puede variar por cliente, proyecto o acuerdo comercial y debe quedar registrado en la compra asociada.
- Flujos donde se necesita trazabilidad y control de márgenes reales entre ventas y compras.

## Configuración

- No requiere configuración manual tras la instalación.
- El campo `purchase_price` debe estar disponible y rellenado en la línea del pedido de venta.
- El módulo es compatible con los flujos estándar de Odoo para generación automática de compras desde ventas (incluyendo `purchase_stock` y `sale_purchase`).

## Funcionamiento

- Al confirmar un pedido de venta que genera una compra, el sistema transfiere el valor de `purchase_price` de la línea de venta al campo `price_unit` de la línea de compra correspondiente.
- Compatible tanto con productos de inventario como con servicios.
- No modifica la lógica central de Odoo, solo extiende los métodos de preparación de líneas de compra para incluir el coste pactado en la venta.

## Dependencias

- sale
- purchase
- sale_purchase
- purchase_stock

## Datos de ejemplo

No incluye datos de demostración. Para probar el módulo:
1. Crear un pedido de venta con líneas que tengan el campo `purchase_price` rellenado.
2. Confirmar el pedido de venta y verificar que el pedido de compra generado refleja ese coste en el campo `price_unit` de sus líneas.

```# Módulo: Sale Purchase Cost Transfer

## Propósito

Permite trasladar automáticamente el coste de compra (`purchase_price`) definido en la línea del pedido de venta (`sale.order.line`) al precio unitario (`price_unit`) de la línea del pedido de compra (`purchase.order.line`) generada a partir de la venta.

## Casos de Uso

- Empresas que gestionan ventas que disparan automáticamente compras (dropshipping, make-to-order, etc.) y requieren que el coste real pactado en la venta se refleje fielmente en la compra.
- Escenarios donde el precio de compra puede variar por cliente, proyecto o acuerdo comercial y debe quedar registrado en la compra asociada.
- Flujos donde se necesita trazabilidad y control de márgenes reales entre ventas y compras.

## Configuración

- No requiere configuración manual tras la instalación.
- El campo `purchase_price` debe estar disponible y rellenado en la línea del pedido de venta.
- El módulo es compatible con los flujos estándar de Odoo para generación automática de compras desde ventas (incluyendo `purchase_stock` y `sale_purchase`).

## Funcionamiento

- Al confirmar un pedido de venta que genera una compra, el sistema transfiere el valor de `purchase_price` de la línea de venta al campo `price_unit` de la línea de compra correspondiente.
- Compatible tanto con productos de inventario como con servicios.
- No modifica la lógica central de Odoo, solo extiende los métodos de preparación de líneas de compra para incluir el coste pactado en la venta.

## Dependencias

- sale
- purchase
- sale_purchase
- purchase_stock

## Datos de ejemplo

No incluye datos de demostración. Para probar el módulo:
1. Crear un pedido de venta con líneas que tengan el campo `purchase_price` rellenado.
2. Confirmar el pedido de venta y verificar que el pedido de compra generado refleja ese coste en el campo `price_unit` de sus líneas.
