import datetime
import logging
import traceback

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
METADATA_MODULE_NAME = "_from_importer"


class AITemplateFileMap(models.Model):
    _name = "ai.template.file.map"
    _description = "Template File Map"

    template_id = fields.Many2one(
        "ai.template.file", string="Plantilla", compute="_compute_template_id"
    )
    model_id = fields.Many2one("ir.model", string="Destino")
    action_ids = fields.One2many(
        "ai.template.model.actions",
        "mapper_id",
        string="Acciones post-importación",
    )

    def _compute_template_id(self):
        for record in self:
            record.template_id = self.env["ai.template.file"].search(
                [("mapper_id", "=", record.id)], limit=1
            )

    def process_record(self, record):  # noqa
        if record.external_id and not record.col1:
            return
        if record.header:
            return
        if not record.mapped("file_id.template_id.mapper_id"):
            raise ValidationError(_("No se ha definido un mapeador para la plantilla"))

        has_tomany = False
        try:
            has_tomany = self.has_tomany(record)
            if has_tomany:
                records = self.env["ai.record"].search(
                    [
                        ("batch_id", "=", record.batch_id.id),
                        ("sequence", "<", record.id),
                    ],
                    order="sequence desc",
                )
                main_record = records.filtered(lambda r: r.col1 != "")
                if not main_record:
                    raise ValidationError(
                        _("No se ha encontrado el registro principal")
                    )
                main_record = main_record[0]
                odoo_vals = self.map_direct(record)
                odoo_vals = self.map_relational(record, odoo_vals)
                return odoo_vals
            odoo_vals = self.map_direct(record)
            odoo_vals = self.map_relational(record, odoo_vals)
        except Exception as e:
            error_traceback = traceback.format_exc()
            _logger.error(
                f"Error al procesar el registro {record.id}: {str(e)}\n{error_traceback}"
            )

            self.env["ai.error"].create(
                {
                    "name": str(e),
                    "stacktrace": error_traceback,
                    "record_id": record.id,
                    "batch_id": record.batch_id.id,
                }
            )
            raise e

        try:
            has_to_create = True
            if record.col1:
                external_id_name = record.col1
                external_id_name = self.normalize_external_id(
                    record.mapped("file_id.template_id.mapper_id.model_id.model")[0],
                    external_id_name,
                    record,
                )
                existing_odoo_record = self.env.ref(
                    external_id_name, raise_if_not_found=False
                )
                if existing_odoo_record and not has_tomany:
                    for (
                        action
                    ) in record.file_id.template_id.mapper_id.action_ids.sorted(
                        "sequence"
                    ):
                        try:
                            method = getattr(
                                existing_odoo_record.with_context(
                                    importer_record=record, odoo_vals=odoo_vals
                                ),
                                action.action,
                            )
                            method()
                        except Exception as e:
                            error_traceback = traceback.format_exc()
                            _logger.error(
                                f"Error al procesar el registro {record.id}: {str(e)}\n{error_traceback}"
                            )
                            self.env["ai.error"].create(
                                {
                                    "name": str(e),
                                    "stacktrace": error_traceback,
                                    "record_id": record.id,
                                    "batch_id": record.batch_id.id,
                                }
                            )
                    existing_odoo_record.write(odoo_vals)
                    has_to_create = False

            destination_model = self.get_destination_model(record)
            odoo_id = None
            if not has_tomany and has_to_create:
                odoo_id = self.env[destination_model].create(odoo_vals)
            external_name = record.col1
            module_name = METADATA_MODULE_NAME
            if "." in record.col1:
                external_name = record.col1.split(".")[1] if record.col1 else False
                module_name = (
                    record.col1.split(".")[0].replace(".", "_")
                    if record.col1
                    else METADATA_MODULE_NAME
                )
            else:
                external_name = f"{destination_model.replace('.','_')}_{record.col1}"
            external_id = False
            if external_name and not has_tomany:
                external_id = self.env["ir.model.data"].search(
                    [
                        ("model", "=", destination_model),
                        ("module", "=", module_name),
                        ("name", "=", external_name),
                        (
                            "res_id",
                            "=",
                            odoo_id.id
                            if odoo_id
                            else existing_odoo_record and existing_odoo_record.id,
                        ),
                    ],
                    limit=1,
                )
                if not external_id and not has_tomany:
                    external_id = self.env["ir.model.data"].create(
                        {
                            "module": module_name,
                            "name": external_name,
                            "model": destination_model,
                            "res_id": odoo_id.id
                            if odoo_id
                            else existing_odoo_record and existing_odoo_record.id,
                            "noupdate": True,
                        }
                    )
            if not external_id and not has_tomany:
                external_id = self.env["ir.model.data"].create(
                    {
                        "module": METADATA_MODULE_NAME,
                        "name": f"{destination_model}_{record.id or odoo_id.id}",
                        "model": destination_model,
                        "res_id": odoo_id.id
                        if odoo_id
                        else existing_odoo_record and existing_odoo_record.id,
                        "noupdate": True,
                    }
                )
            if not record.external_id:
                record.external_id = external_id.id
            for action in record.file_id.template_id.mapper_id.action_ids.sorted(
                "sequence"
            ):
                try:
                    method = getattr(
                        odoo_id.with_context(
                            importer_record=record, odoo_vals=odoo_vals
                        ),
                        action.action,
                    )
                    method()
                except Exception as e:
                    error_traceback = traceback.format_exc()
                    _logger.error(
                        f"Error al procesar el registro {record.id}: {str(e)}\n{error_traceback}"
                    )
                    self.env["ai.error"].create(
                        {
                            "name": str(e),
                            "stacktrace": error_traceback,
                            "record_id": record.id,
                            "batch_id": record.batch_id.id,
                        }
                    )
            return odoo_vals
        except Exception as e:
            error_traceback = traceback.format_exc()
            _logger.error(
                f"Error al procesar el registro {record.id}: {str(e)}\n{error_traceback}"
            )

            self.env["ai.error"].create(
                {
                    "name": str(e),
                    "stacktrace": error_traceback,
                    "record_id": record.id,
                    "batch_id": record.batch_id.id,
                }
            )

    @api.model
    def get_destination_model(self, record):
        destination_model = record.mapped(
            "file_id.template_id.mapper_id.model_id.model"
        )
        if not destination_model:
            raise ValidationError(
                _("No se ha definido un modelo destino para la plantilla")
            )
        else:
            destination_model = destination_model[0]
        return destination_model

    @api.model
    def map_relational(self, record, odoo_vals):  # noqa
        mapper = record.mapped("file_id.template_id.mapper_id")
        relational_fields = []
        for i in range(2, 50):
            relational_field = {}
            col_type = getattr(mapper, f"col{i}_type", False)
            if col_type == "relational":
                relational_field["col_name"] = f"col{i}"
                relational_field["direct_name"] = getattr(
                    mapper, f"col{i}_direct_name", False
                )
                relational_field["destination_field"] = getattr(
                    mapper, f"col{i}_related_field_name", False
                )
                relational_field["model"] = getattr(
                    mapper, f"col{i}_related_model_name", False
                )
                relational_field["lambda"] = getattr(mapper, f"col{i}_lambda", False)
                relational_fields.append(relational_field)

        odoo_vals = self.apply_lambdas(odoo_vals, relational_fields, record)
        return odoo_vals

    @api.model
    def handle_field_value(self, field, value, model, record):
        if "lambda" not in field.keys():
            raise ValidationError(
                _(
                    f"El campo 'lambda' no está definido en el mapeador {field['direct_name']}. Plantilla {self.template_id}"
                )
            )
        handlers = {
            "get_id_by_name": lambda: self.get_id_by_name(model, value),
            "get_id_by_name_required": lambda: self.get_id_by_name(
                model, value, raise_if_not_found=True
            ),
            "get_id_by_ref": lambda: None
            if not value
            else self.get_id_by_ref(
                model, self.normalize_external_id(model, value, record)
            ),
            "get_id_by_ref_required": lambda: self._process_ref_required(
                model, field, value, record
            ),
            "get_ids_by_ref": lambda: None
            if not value
            or not any(
                ref.strip()
                and ref not in ["", "0", "0.0"]
                and self.get_id_by_ref(model, ref.strip(), raise_if_not_found=False)
                for ref in value.split(",")
            )
            else [
                (4, self.get_id_by_ref(model, ref.strip(), raise_if_not_found=False))
                for ref in value.split(",")
                if ref not in ["", "0", "0.0"]
                and ref.strip()
                and self.get_id_by_ref(model, ref.strip(), raise_if_not_found=False)
            ],
            "get_id_by_ref_or_default": lambda: self.get_id_by_ref_or_default(
                model, value
            )
            or value,
            "boolean": lambda: getattr(record, field["col_name"], False)
            in ["1", "true", "True", True],
            "float": lambda: self._parse_float(value)
            if value and value != ""
            else None,
            "integer": lambda: self._parse_integer(value)
            if value and value != ""
            else None,
            "date": lambda: self._parse_date(value) if value else None,
            "direct_lowered": lambda: getattr(record, field["col_name"], False).lower()
            if value
            else None,
            # Caso por defecto
            "default": lambda: getattr(record, field["col_name"], False),
        }

        return handlers.get(field["lambda"], handlers["default"])()

    @api.model
    def _process_ref_required(self, model, field, value, record):
        """Lógica específica para get_id_by_ref_required"""
        original_value = value
        value = self.get_id_by_ref(model, getattr(record, field["col_name"], True))
        if not value:
            value = self.get_id_by_name(model, original_value, raise_if_not_found=True)
        if not value:
            raise ValidationError(
                _(
                    f"El campo '{field['direct_name']}' no puede estar vacío. "
                    f"El valor '{original_value}' no se pudo mapear."
                )
            )
        return value

    @api.model
    def _normalize_numeric_value(self, value):
        """Normaliza una cadena numérica removiendo separadores y devolviendo formato estándar"""
        if not value or value in ["", "0", "0.0"]:
            return None

        try:
            # Limpiar espacios
            clean_value = str(value).strip()

            # Si no tiene separadores, devolver tal como está
            if not any(char in clean_value for char in [",", "."]):
                return clean_value

            # Contar puntos y comas para determinar el formato
            dot_count = clean_value.count(".")
            comma_count = clean_value.count(",")

            # Caso: Solo puntos (formato inglés: 1000.50 o separador de miles 1.000)
            if comma_count == 0 and dot_count == 1:
                parts = clean_value.split(".")
                # Si la parte decimal tiene más de 3 dígitos, probablemente es separador de miles
                if len(parts[1]) > 3:
                    return clean_value.replace(".", "")
                return clean_value  # Formato decimal estándar

            # Caso: Solo comas (formato europeo: 1000,50 o separador de miles 1,000)
            if dot_count == 0 and comma_count == 1:
                parts = clean_value.split(",")
                # Si la parte después de la coma tiene más de 3 dígitos, es separador de miles
                if len(parts[1]) > 3:
                    return clean_value.replace(",", "")
                return clean_value.replace(",", ".")  # Convertir coma decimal a punto

            # Caso: Ambos separadores presentes
            if dot_count > 0 and comma_count > 0:
                last_dot = clean_value.rfind(".")
                last_comma = clean_value.rfind(",")

                if last_dot > last_comma:
                    # Formato inglés: 1,000.50 - coma es separador de miles
                    return clean_value.replace(",", "")
                else:
                    # Formato europeo: 1.000,50 - punto es separador de miles
                    return clean_value.replace(".", "").replace(",", ".")

            # Caso: Múltiples puntos (separador de miles europeo: 1.000.000)
            if dot_count > 1:
                return clean_value.replace(".", "")

            # Caso: Múltiples comas (separador de miles inglés: 1,000,000)
            if comma_count > 1:
                return clean_value.replace(",", "")

            return clean_value

        except (ValueError, TypeError):
            return None

    @api.model
    def _parse_integer(self, int_value):
        """Convierte una cadena en entero manejando separadores de miles"""
        normalized = self._normalize_numeric_value(int_value)
        if normalized is None:
            return None

        try:
            return int(float(normalized))  # Usar float para manejar decimales y truncar
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Formato entero no válido: '{int_value}'. "
                f"Formatos soportados: 1000, 1,000, 1.000, 1000.50 (se truncará)"
            ) from e

    @api.model
    def _parse_float(self, float_value):
        """Convierte una cadena en float manejando separadores de miles y decimales"""
        normalized = self._normalize_numeric_value(float_value)
        if normalized is None:
            return 0.0

        try:
            return float(normalized)
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Formato numérico no válido: '{float_value}'. "
                f"Formatos soportados: 1000.50, 1000,50, 1.000,50, 1,000.50"
            ) from e

    @api.model
    def _parse_date(self, date_value):
        """Convierte una cadena en fecha"""
        try:
            if date_value in ["", "0", "0.0"]:
                return False
            for char in ["/", ".", " ", ",", ":"]:
                date_value = date_value.replace(char, "-")
            _no_use = datetime.datetime.strptime(date_value, "%Y-%m-%d")
            return date_value
        except ValueError as e:
            raise ValueError(
                f"Formato de fecha no válido: {date_value}. Debe ser 'YYYY-MM-DD'"
            ) from e

    @api.model
    def tomany_keys(self, record):
        mapper = record.mapped("file_id.template_id.mapper_id")
        result = []
        for i in range(2, 50):
            col_type = getattr(mapper, f"col{i}_type", False)
            if col_type == "direct":
                direct_name = getattr(mapper, f"col{i}_direct_name", False)
                if not direct_name:
                    continue
                if "/" in direct_name:
                    field = direct_name.split("/")[0]
                    if field not in result:
                        result.append(field)
        return result

    @api.model
    def has_tomany(self, record):
        return len(self.tomany_keys(record)) > 0

    def apply_lambdas(self, odoo_vals, fields, record):
        for field in fields:
            if not field.get("lambda"):
                continue
            if odoo_vals:
                odoo_vals.pop(field["direct_name"], None)
            model = field.get("model", "")
            if "tomany_relation" in field.keys():
                model = field["tomany_relation"]

            value = getattr(record, field["col_name"], False)
            result = self.handle_field_value(field, value, model, record)
            if result is not None:
                odoo_vals[field["destination_field"]] = result

            if (
                field["destination_field"] in odoo_vals
                and not odoo_vals[field["destination_field"]]
                and not field.get("lambda")
            ):
                odoo_vals.pop(field["destination_field"], None)

        return odoo_vals

    @api.model
    def map_tomany(self, record):  # noqa
        mapper = record.mapped("file_id.template_id.mapper_id")
        tomany_fields = []
        result = {}
        for i in range(2, 50):
            tomany_field = {}
            col_type = getattr(mapper, f"col{i}_type", False)
            if col_type != "direct":
                continue
            direct_name = getattr(mapper, f"col{i}_direct_name", False)
            if not direct_name or "/" not in direct_name:
                continue
            if len(direct_name.split("/")) != 2:
                raise ValidationError(
                    _("El nombre de campo relacional debe tener uno y solo un '/'")
                )
            tomany_field["col_name"] = f"col{i}"
            tomany_field["direct_name"] = direct_name.split("/")[1]
            tomany_field["destination_field"] = direct_name.split("/")[1]
            tomany_field["field_name"] = direct_name.split("/")[0]
            related_field = self.env["ir.model.fields"].search(
                [
                    ("model", "=", mapper.model_id.model),
                    ("name", "=", direct_name.split("/")[0]),
                ],
                limit=1,
            )
            tomany_field["model"] = related_field.relation
            tomany_field["lambda"] = getattr(mapper, f"col{i}_lambda", False)
            tomany_related_field_model = (
                self.env["ir.model.fields"]
                .search(
                    [
                        ("model", "=", tomany_field["model"]),
                        ("name", "=", tomany_field["direct_name"]),
                    ],
                    limit=1,
                )
                .relation
            )
            if tomany_related_field_model or tomany_field["direct_name"] == "id":
                tomany_field["tomany_relation"] = (
                    tomany_related_field_model
                    if tomany_related_field_model
                    else tomany_field["model"]
                )
                tomany_field["lambda"] = (
                    tomany_field["lambda"]
                    if tomany_field["lambda"]
                    else "get_id_by_ref_or_default"
                )
            tomany_field["to_manyfield"] = direct_name.split("/")[0]
            tomany_fields.append(tomany_field)

        grouped_by_tomany_fields = {}
        for field in tomany_fields:
            if field["field_name"] not in grouped_by_tomany_fields:
                grouped_by_tomany_fields[field["field_name"]] = []
            grouped_by_tomany_fields[field["field_name"]].append(field)
        for tomany_field_name in grouped_by_tomany_fields:
            fields_metadata = grouped_by_tomany_fields[tomany_field_name]
            related_field = {}
            related_field = self.apply_lambdas(result, fields_metadata, record)
        return {
            field["field_name"]: [
                related_field,
            ]
        }

    @api.model
    def get_id_by_name(self, model_name, value, raise_if_not_found=False):
        if value in ["", "0", "0.0"]:
            if raise_if_not_found:
                raise ValidationError(
                    _(
                        f"El campo '{model_name}' no puede estar vacío. "
                        f"El valor '{value}' no se pudo mapear."
                    )
                )
            else:
                return False
        model = self.env[model_name]
        name_field_name = "name"
        if model_name in ["account.account"]:
            name_field_name = "code"
        if model_name in ["res.partner.bank"]:
            name_field_name = "acc_number"
        record = model.search([(name_field_name, "=", value)], limit=1)
        if not record:
            # From normalize_external_id, we can have a value like '****account_217001'
            valueArr = value.split("_")
            if len(valueArr) > 1:
                value = valueArr[-1]
                record = model.search([(name_field_name, "=", value)], limit=1)
        result = record.id if record else None
        if not result and raise_if_not_found:
            raise ValidationError(
                _(f"El registro {value} no existe en el modelo '{model_name}'")
            )
        return result

    @api.model
    def get_id_by_ref(self, model, value, raise_if_not_found=False):
        if not value:
            return
        result = self.env.ref(
            value,
            raise_if_not_found=False,
        )
        if not result and "." not in value:
            external_id_name = self.normalize_external_id(model, value, None)
            result = self.env.ref(
                external_id_name,
                raise_if_not_found=False,
            )
        if not result:
            if model == "account.payment":
                return self.get_id_by_ref("account.move", value, raise_if_not_found)
            return self.get_id_by_name(model, value, raise_if_not_found)
        if raise_if_not_found and not result:
            raise ValidationError(
                _(f"El registro {value} no existe en el modelo '{model}'")
            )
        return result.id if result else None

    @api.model
    def get_id_by_ref_required(self, model, value):
        if not value:
            return
        is_external_id = True
        external_arr = value.split(".")
        if "." not in value:
            is_external_id = False
        elif len(external_arr) != 2 or not external_arr[1]:
            is_external_id = False
        if not is_external_id:
            result = self.get_id_by_name(model, value, False)
            if not result:
                raise ValidationError(
                    _(f"El registro {value} no existe en el modelo '{model}'")
                )
            return result
        return self.env.ref(
            value,
            raise_if_not_found=True,
        ).id

    @api.model
    def get_id_by_ref_or_default(self, model, value):
        if not value:
            return
        result = None
        if "." in value:
            result = self.env.ref(
                value,
                raise_if_not_found=False,
            )
            if result:
                result = result.id
        if not result:
            return self.get_id_by_name(model, value, False)
        return result or value

    @api.model
    def map_direct(self, record):
        values = {
            "id": record.col1,
        }
        mapper = record.mapped("file_id.template_id.mapper_id")
        direct_fields = []
        for i in range(2, 50):
            direct_field = {}
            col_type = getattr(mapper, f"col{i}_type", False)
            lambda_name = getattr(mapper, f"col{i}_lambda", False)
            if col_type == "direct":
                direct_name = getattr(mapper, f"col{i}_direct_name", False)
                if not direct_name or "/" in direct_name:
                    continue
                direct_field["col_name"] = f"col{i}"
                direct_field["direct_name"] = direct_name
                direct_field["destination_field"] = direct_name
                if lambda_name:
                    direct_field["lambda"] = lambda_name
                direct_fields.append(direct_field)

        for field in direct_fields:
            values[field["direct_name"]] = getattr(record, field["col_name"], False)
        only_lambdas = self.apply_lambdas(values, direct_fields, record)
        values.update(only_lambdas)
        return values

    def normalize_external_id(self, model, value, record):
        prefix = ""
        if record and record.file_id.template_id.name == "invoices":
            prefix = "invoice"
        result = value or ""
        if "." not in result:
            result = (
                f"{METADATA_MODULE_NAME}.{prefix}{model.replace('.', '_')}_{result}"
            )
        return result

    def get_ir_model_data(self, odoo_record):
        if not odoo_record:
            return False

        return self.env["ir.model.data"].search(
            [("model", "=", odoo_record._name), ("res_id", "=", odoo_record.id)],
            limit=1,
        )

    col2_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col2 Tipo",
        default="direct",
    )
    col2_direct_name = fields.Char(string="Col2 Columna destino")
    col2_related_field_name = fields.Char(string="Col2 Columna relacional destino")
    col2_related_model_name = fields.Char(string="Col2 Modelo relacional")
    col2_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col3_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col3 Tipo",
        default="direct",
    )
    col3_direct_name = fields.Char(string="Col3 Columna destino")
    col3_related_field_name = fields.Char(string="Col3 Columna relacional destino")
    col3_related_model_name = fields.Char(string="Col3 Modelo relacional")
    col3_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col4_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col4 Tipo",
        default="direct",
    )
    col4_direct_name = fields.Char(string="Col4 Columna destino")
    col4_related_field_name = fields.Char(string="Col4 Columna relacional destino")
    col4_related_model_name = fields.Char(string="Col4 Modelo relacional")
    col4_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col5_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col5 Tipo",
        default="direct",
    )
    col5_direct_name = fields.Char(string="Col5 Columna destino")
    col5_related_field_name = fields.Char(string="Col5 Columna relacional destino")
    col5_related_model_name = fields.Char(string="Col5 Modelo relacional")
    col5_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col6_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col6 Tipo",
        default="direct",
    )
    col6_direct_name = fields.Char(string="Col6 Columna destino")
    col6_related_field_name = fields.Char(string="Col6 Columna relacional destino")
    col6_related_model_name = fields.Char(string="Col6 Modelo relacional")
    col6_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col7_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col7 Tipo",
        default="direct",
    )
    col7_direct_name = fields.Char(string="Col7 Columna destino")
    col7_related_field_name = fields.Char(string="Col7 Columna relacional destino")
    col7_related_model_name = fields.Char(string="Col7 Modelo relacional")
    col7_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col8_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col8 Tipo",
        default="direct",
    )
    col8_direct_name = fields.Char(string="Col8 Columna destino")
    col8_related_field_name = fields.Char(string="Col8 Columna relacional destino")
    col8_related_model_name = fields.Char(string="Col8 Modelo relacional")
    col8_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col9_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col9 Tipo",
        default="direct",
    )
    col9_direct_name = fields.Char(string="Col9 Columna destino")
    col9_related_field_name = fields.Char(string="Col9 Columna relacional destino")
    col9_related_model_name = fields.Char(string="Col9 Modelo relacional")
    col9_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col10_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col10 Tipo",
        default="direct",
    )
    col10_direct_name = fields.Char(string="Col10 Columna destino")
    col10_related_field_name = fields.Char(string="Col10 Columna relacional destino")
    col10_related_model_name = fields.Char(string="Col10 Modelo relacional")
    col10_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col11_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col11 Tipo",
        default="direct",
    )
    col11_direct_name = fields.Char(string="Col11 Columna destino")
    col11_related_field_name = fields.Char(string="Col11 Columna relacional destino")
    col11_related_model_name = fields.Char(string="Col11 Modelo relacional")
    col11_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col12_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col12 Tipo",
        default="direct",
    )
    col12_direct_name = fields.Char(string="Col12 Columna destino")
    col12_related_field_name = fields.Char(string="Col12 Columna relacional destino")
    col12_related_model_name = fields.Char(string="Col12 Modelo relacional")
    col12_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col13_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col13 Tipo",
        default="direct",
    )
    col13_direct_name = fields.Char(string="Col13 Columna destino")
    col13_related_field_name = fields.Char(string="Col13 Columna relacional destino")
    col13_related_model_name = fields.Char(string="Col13 Modelo relacional")
    col13_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col14_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col14 Tipo",
        default="direct",
    )
    col14_direct_name = fields.Char(string="Col14 Columna destino")
    col14_related_field_name = fields.Char(string="Col14 Columna relacional destino")
    col14_related_model_name = fields.Char(string="Col14 Modelo relacional")
    col14_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col15_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col15 Tipo",
        default="direct",
    )
    col15_direct_name = fields.Char(string="Col15 Columna destino")
    col15_related_field_name = fields.Char(string="Col15 Columna relacional destino")
    col15_related_model_name = fields.Char(string="Col15 Modelo relacional")
    col15_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col16_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col16 Tipo",
        default="direct",
    )
    col16_direct_name = fields.Char(string="Col16 Columna destino")
    col16_related_field_name = fields.Char(string="Col16 Columna relacional destino")
    col16_related_model_name = fields.Char(string="Col16 Modelo relacional")
    col16_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col17_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col17 Tipo",
        default="direct",
    )
    col17_direct_name = fields.Char(string="Col17 Columna destino")
    col17_related_field_name = fields.Char(string="Col17 Columna relacional destino")
    col17_related_model_name = fields.Char(string="Col17 Modelo relacional")
    col17_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col18_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col18 Tipo",
        default="direct",
    )
    col18_direct_name = fields.Char(string="Col18 Columna destino")
    col18_related_field_name = fields.Char(string="Col18 Columna relacional destino")
    col18_related_model_name = fields.Char(string="Col18 Modelo relacional")
    col18_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col19_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col19 Tipo",
        default="direct",
    )
    col19_direct_name = fields.Char(string="Col19 Columna destino")
    col19_related_field_name = fields.Char(string="Col19 Columna relacional destino")
    col19_related_model_name = fields.Char(string="Col19 Modelo relacional")
    col19_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col20_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col20 Tipo",
        default="direct",
    )
    col20_direct_name = fields.Char(string="Col20 Columna destino")
    col20_related_field_name = fields.Char(string="Col20 Columna relacional destino")
    col20_related_model_name = fields.Char(string="Col20 Modelo relacional")
    col20_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col21_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col21 Tipo",
        default="direct",
    )
    col21_direct_name = fields.Char(string="Col21 Columna destino")
    col21_related_field_name = fields.Char(string="Col21 Columna relacional destino")
    col21_related_model_name = fields.Char(string="Col21 Modelo relacional")
    col21_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col22_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col22 Tipo",
        default="direct",
    )
    col22_direct_name = fields.Char(string="Col22 Columna destino")
    col22_related_field_name = fields.Char(string="Col22 Columna relacional destino")
    col22_related_model_name = fields.Char(string="Col22 Modelo relacional")
    col22_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col23_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col23 Tipo",
        default="direct",
    )
    col23_direct_name = fields.Char(string="Col23 Columna destino")
    col23_related_field_name = fields.Char(string="Col23 Columna relacional destino")
    col23_related_model_name = fields.Char(string="Col23 Modelo relacional")
    col23_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col24_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col24 Tipo",
        default="direct",
    )
    col24_direct_name = fields.Char(string="Col24 Columna destino")
    col24_related_field_name = fields.Char(string="Col24 Columna relacional destino")
    col24_related_model_name = fields.Char(string="Col24 Modelo relacional")
    col24_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col25_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col25 Tipo",
        default="direct",
    )
    col25_direct_name = fields.Char(string="Col25 Columna destino")
    col25_related_field_name = fields.Char(string="Col25 Columna relacional destino")
    col25_related_model_name = fields.Char(string="Col25 Modelo relacional")
    col25_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col26_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col26 Tipo",
        default="direct",
    )
    col26_direct_name = fields.Char(string="Col26 Columna destino")
    col26_related_field_name = fields.Char(string="Col26 Columna relacional destino")
    col26_related_model_name = fields.Char(string="Col26 Modelo relacional")
    col26_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col27_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col27 Tipo",
        default="direct",
    )
    col27_direct_name = fields.Char(string="Col27 Columna destino")
    col27_related_field_name = fields.Char(string="Col27 Columna relacional destino")
    col27_related_model_name = fields.Char(string="Col27 Modelo relacional")
    col27_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col28_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col28 Tipo",
        default="direct",
    )
    col28_direct_name = fields.Char(string="Col28 Columna destino")
    col28_related_field_name = fields.Char(string="Col28 Columna relacional destino")
    col28_related_model_name = fields.Char(string="Col28 Modelo relacional")
    col28_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col29_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col29 Tipo",
        default="direct",
    )
    col29_direct_name = fields.Char(string="Col29 Columna destino")
    col29_related_field_name = fields.Char(string="Col29 Columna relacional destino")
    col29_related_model_name = fields.Char(string="Col29 Modelo relacional")
    col29_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col30_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col30 Tipo",
        default="direct",
    )
    col30_direct_name = fields.Char(string="Col30 Columna destino")
    col30_related_field_name = fields.Char(string="Col30 Columna relacional destino")
    col30_related_model_name = fields.Char(string="Col30 Modelo relacional")
    col30_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col31_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col31 Tipo",
        default="direct",
    )
    col31_direct_name = fields.Char(string="Col31 Columna destino")
    col31_related_field_name = fields.Char(string="Col31 Columna relacional destino")
    col31_related_model_name = fields.Char(string="Col31 Modelo relacional")
    col31_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col32_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col32 Tipo",
        default="direct",
    )
    col32_direct_name = fields.Char(string="Col32 Columna destino")
    col32_related_field_name = fields.Char(string="Col32 Columna relacional destino")
    col32_related_model_name = fields.Char(string="Col32 Modelo relacional")
    col32_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col33_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col33 Tipo",
        default="direct",
    )
    col33_direct_name = fields.Char(string="Col33 Columna destino")
    col33_related_field_name = fields.Char(string="Col33 Columna relacional destino")
    col33_related_model_name = fields.Char(string="Col33 Modelo relacional")
    col33_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col34_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col34 Tipo",
        default="direct",
    )
    col34_direct_name = fields.Char(string="Col34 Columna destino")
    col34_related_field_name = fields.Char(string="Col34 Columna relacional destino")
    col34_related_model_name = fields.Char(string="Col34 Modelo relacional")
    col34_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col35_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col35 Tipo",
        default="direct",
    )
    col35_direct_name = fields.Char(string="Col35 Columna destino")
    col35_related_field_name = fields.Char(string="Col35 Columna relacional destino")
    col35_related_model_name = fields.Char(string="Col35 Modelo relacional")
    col35_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col36_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col36 Tipo",
        default="direct",
    )
    col36_direct_name = fields.Char(string="Col36 Columna destino")
    col36_related_field_name = fields.Char(string="Col36 Columna relacional destino")
    col36_related_model_name = fields.Char(string="Col36 Modelo relacional")
    col36_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col37_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col37 Tipo",
        default="direct",
    )
    col37_direct_name = fields.Char(string="Col37 Columna destino")
    col37_related_field_name = fields.Char(string="Col37 Columna relacional destino")
    col37_related_model_name = fields.Char(string="Col37 Modelo relacional")
    col37_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col38_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col38 Tipo",
        default="direct",
    )
    col38_direct_name = fields.Char(string="Col38 Columna destino")
    col38_related_field_name = fields.Char(string="Col38 Columna relacional destino")
    col38_related_model_name = fields.Char(string="Col38 Modelo relacional")
    col38_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col39_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col39 Tipo",
        default="direct",
    )
    col39_direct_name = fields.Char(string="Col39 Columna destino")
    col39_related_field_name = fields.Char(string="Col39 Columna relacional destino")
    col39_related_model_name = fields.Char(string="Col39 Modelo relacional")
    col39_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col40_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col40 Tipo",
        default="direct",
    )
    col40_direct_name = fields.Char(string="Col40 Columna destino")
    col40_related_field_name = fields.Char(string="Col40 Columna relacional destino")
    col40_related_model_name = fields.Char(string="Col40 Modelo relacional")
    col40_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col41_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col41 Tipo",
        default="direct",
    )
    col41_direct_name = fields.Char(string="Col41 Columna destino")
    col41_related_field_name = fields.Char(string="Col41 Columna relacional destino")
    col41_related_model_name = fields.Char(string="Col41 Modelo relacional")
    col41_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col42_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col42 Tipo",
        default="direct",
    )
    col42_direct_name = fields.Char(string="Col42 Columna destino")
    col42_related_field_name = fields.Char(string="Col42 Columna relacional destino")
    col42_related_model_name = fields.Char(string="Col42 Modelo relacional")
    col42_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col43_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col43 Tipo",
        default="direct",
    )
    col43_direct_name = fields.Char(string="Col43 Columna destino")
    col43_related_field_name = fields.Char(string="Col43 Columna relacional destino")
    col43_related_model_name = fields.Char(string="Col43 Modelo relacional")
    col43_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col44_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col44 Tipo",
        default="direct",
    )
    col44_direct_name = fields.Char(string="Col44 Columna destino")
    col44_related_field_name = fields.Char(string="Col44 Columna relacional destino")
    col44_related_model_name = fields.Char(string="Col44 Modelo relacional")
    col44_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col45_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col45 Tipo",
        default="direct",
    )
    col45_direct_name = fields.Char(string="Col45 Columna destino")
    col45_related_field_name = fields.Char(string="Col45 Columna relacional destino")
    col45_related_model_name = fields.Char(string="Col45 Modelo relacional")
    col45_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col46_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col46 Tipo",
        default="direct",
    )
    col46_direct_name = fields.Char(string="Col46 Columna destino")
    col46_related_field_name = fields.Char(string="Col46 Columna relacional destino")
    col46_related_model_name = fields.Char(string="Col46 Modelo relacional")
    col46_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col47_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col47 Tipo",
        default="direct",
    )
    col47_direct_name = fields.Char(string="Col47 Columna destino")
    col47_related_field_name = fields.Char(string="Col47 Columna relacional destino")
    col47_related_model_name = fields.Char(string="Col47 Modelo relacional")
    col47_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col48_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col48 Tipo",
        default="direct",
    )
    col48_direct_name = fields.Char(string="Col48 Columna destino")
    col48_related_field_name = fields.Char(string="Col48 Columna relacional destino")
    col48_related_model_name = fields.Char(string="Col48 Modelo relacional")
    col48_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col49_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col49 Tipo",
        default="direct",
    )
    col49_direct_name = fields.Char(string="Col49 Columna destino")
    col49_related_field_name = fields.Char(string="Col49 Columna relacional destino")
    col49_related_model_name = fields.Char(string="Col49 Modelo relacional")
    col49_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )

    col50_type = fields.Selection(
        [("direct", "Directo"), ("relational", "Relacional")],
        string="Col50 Tipo",
        default="direct",
    )
    col50_direct_name = fields.Char(string="Col50 Columna destino")
    col50_related_field_name = fields.Char(string="Col50 Columna relacional destino")
    col50_related_model_name = fields.Char(string="Col50 Modelo relacional")
    col50_lambda = fields.Selection(
        [
            ("get_id_by_name", "ID por nombre"),
            ("get_id_by_name_required", "ID por nombre obligatorio"),
            ("get_id_by_ref", "ID externo"),
            ("get_id_by_ref_required", "ID externo obligatorio"),
            ("get_ids_by_ref", "Lista de ID externos"),
            ("direct_lowered", "A minúsculas"),
            ("boolean", "A booleano"),
            ("float", "Con decimales"),
            ("integer", "Entero"),
            ("date", "Fecha"),
        ],
    )
