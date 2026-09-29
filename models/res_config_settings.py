# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    metabase_url = fields.Char(
        string="URL de Metabase",
        config_parameter="mba_metabase_bi.metabase_url",
        default="http://localhost:3000",
        help="URL base del servidor de Metabase accesible por el navegador de los usuarios.",
    )
    metabase_secret_key = fields.Char(
        string="Embedding Secret Key",
        config_parameter="mba_metabase_bi.metabase_secret_key",
        help="Clave secreta generada en Ajustes > Embedding de Metabase para firmar tokens JWT.",
    )
