from odoo import fields, models


class AIRecord(models.Model):
    _name = "ai.record"
    _description = "AI Record"

    bundle_id = fields.Many2one(
        "ai.file.bundle", string="Histórico", related="file_id.bundle_id", store=True
    )
    file_id = fields.Many2one(
        "ai.file", string="Fichero", index=True, ondelete="cascade"
    )
    template_id = fields.Many2one(
        "ai.template.file",
        string="Plantilla",
        related="file_id.template_id",
        store=True,
    )
    mapper_id = fields.Many2one(
        "ai.template.file.map",
        string="Mapeo",
        related="file_id.template_id.mapper_id",
        store=True,
    )
    queued = fields.Boolean(string="En cola", default=False)
    header = fields.Boolean(string="Es cabecera", default=False)
    batch_id = fields.Many2one("ai.record.batch", string="Lote", ondelete="cascade")
    external_id = fields.Many2one("ir.model.data", string="ID Externo")
    error_ids = fields.One2many("ai.error", "record_id", string="Errores")

    _sql_constraints = [
        (
            "file_queued_header_idx",
            "CREATE INDEX file_queued_header_idx ON ai_record (file_id, queued, header, sequence)",
            "Your index, your performance",
        )
    ]

    def process_record(self):
        result_id = False
        if len(self) > 1:
            has_tomany = self[0].template_id.mapper_id.has_tomany(self[0])
            if has_tomany:
                self.env["ai.record.batch"].process_batch(self)
                return
        odoo_vals = {}
        mapper = self.file_id.template_id.mapper_id
        has_tomany = mapper.has_tomany(self)
        for record in self:
            record.error_ids.unlink()
            odoo_vals = mapper.process_record(record)
            if not odoo_vals:
                # process_record ya registró el error
                return
            if has_tomany:
                to_many_values = mapper.map_tomany(record)
                to_many_keys = to_many_values.keys()
                for key in to_many_keys:
                    if key in odoo_vals:
                        odoo_vals[key].append(to_many_values[key][0])
                    else:
                        odoo_vals.update(to_many_values)
        if has_tomany:
            external_id_name = self.env["ai.template.file.map"].normalize_external_id(
                record.file_id.template_id.mapper_id.model_id.model, record.col1, record
            )
            external_id = (
                self.env.ref(external_id_name, raise_if_not_found=False)
                if external_id_name
                else False
            )
            if external_id:
                result_id = record.batch_id.write_odoo_record(record, odoo_vals)
            else:
                result_id = record.batch_id.create_odoo_record(
                    record, odoo_vals, external_id_name
                )
        odoo_id = result_id or record.external_id
        external_id = False
        if odoo_id and not record.external_id:
            external_id = self.env["ai.template.file.map"].get_ir_model_data(odoo_id)
        external_id_name = self.env["ai.template.file.map"].normalize_external_id(
            record.file_id.template_id.mapper_id.model_id.model, record.col1, record
        )
        if external_id_name:
            odoo_id = self.env.ref(external_id_name, raise_if_not_found=False)
            external_id = self.env["ai.template.file.map"].get_ir_model_data(odoo_id)
        if not odoo_id:
            raise ValueError(
                "No se ha podido encontrar el registro creado. Contacte con el administrador."
            )
        if external_id and not record.external_id:
            record.external_id = external_id
        return result_id or record.external_id

    sequence = fields.Integer(string="Secuencia")
    col1 = fields.Char(string="Col1")
    col2 = fields.Char(string="Col2")
    col3 = fields.Char(string="Col3")
    col4 = fields.Char(string="Col4")
    col5 = fields.Char(string="Col5")
    col6 = fields.Char(string="Col6")
    col7 = fields.Char(string="Col7")
    col8 = fields.Char(string="Col8")
    col9 = fields.Char(string="Col9")
    col10 = fields.Char(string="Col10")
    col11 = fields.Char(string="Col11")
    col12 = fields.Char(string="Col12")
    col13 = fields.Char(string="Col13")
    col14 = fields.Char(string="Col14")
    col15 = fields.Char(string="Col15")
    col16 = fields.Char(string="Col16")
    col17 = fields.Char(string="Col17")
    col18 = fields.Char(string="Col18")
    col19 = fields.Char(string="Col19")
    col20 = fields.Char(string="Col20")
    col21 = fields.Char(string="Col21")
    col22 = fields.Char(string="Col22")
    col23 = fields.Char(string="Col23")
    col24 = fields.Char(string="Col24")
    col25 = fields.Char(string="Col25")
    col26 = fields.Char(string="Col26")
    col27 = fields.Char(string="Col27")
    col28 = fields.Char(string="Col28")
    col29 = fields.Char(string="Col29")
    col30 = fields.Char(string="Col30")
    col31 = fields.Char(string="Col31")
    col32 = fields.Char(string="Col32")
    col33 = fields.Char(string="Col33")
    col34 = fields.Char(string="Col34")
    col35 = fields.Char(string="Col35")
    col36 = fields.Char(string="Col36")
    col37 = fields.Char(string="Col37")
    col38 = fields.Char(string="Col38")
    col39 = fields.Char(string="Col39")
    col40 = fields.Char(string="Col40")
    col41 = fields.Char(string="Col41")
    col42 = fields.Char(string="Col42")
    col43 = fields.Char(string="Col43")
    col44 = fields.Char(string="Col44")
    col45 = fields.Char(string="Col45")
    col46 = fields.Char(string="Col46")
    col47 = fields.Char(string="Col47")
    col48 = fields.Char(string="Col48")
    col49 = fields.Char(string="Col49")
    col50 = fields.Char(string="Col50")
