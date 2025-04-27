UPDATE ir_model_data
SET model = 'product.product',
    res_id = (
        SELECT pp.id
        FROM product_product pp
        WHERE pp.product_tmpl_id = ir_model_data.res_id
        LIMIT 1
    )
WHERE model = 'product.template'
  AND EXISTS (
      SELECT 1
      FROM product_product pp
      WHERE pp.product_tmpl_id = ir_model_data.res_id
  );
