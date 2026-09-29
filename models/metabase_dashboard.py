# -*- coding: utf-8 -*-
import base64
import hashlib
import hmac
import json
import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MetabaseDashboard(models.Model):
    _name = 'metabase.dashboard'
    _description = 'Tablero de Metabase BI'
    _order = 'sequence, id'

    name = fields.Char(string="Nombre del Tablero", required=True)
    sequence = fields.Integer(string="Secuencia", default=10)
    metabase_dashboard_id = fields.Integer(
        string="ID del Dashboard en Metabase",
        required=True,
        help="ID numérico del Dashboard en Metabase (ej. 3 para Performance, 4 para Inventario, etc.)"
    )
    description = fields.Text(string="Descripción de Negocio")
    active = fields.Boolean(string="Activo", default=True)
    theme = fields.Selection([
        ('transparent', 'Transparente / Claro'),
        ('night', 'Modo Oscuro (Dark)'),
    ], string="Tema Visual", default='transparent')
    bordered = fields.Boolean(string="Mostrar Bordes", default=False)
    titled = fields.Boolean(string="Mostrar Título de Metabase", default=False)

    @api.model
    def _generate_jwt_token(self, dashboard_id, secret_key, exp_minutes=15):
        """Genera un token JWT HMAC-SHA256 usando solo la librería estándar de Python."""
        header = {"alg": "HS256", "typ": "JWT"}
        exp = round(time.time()) + (exp_minutes * 60)
        payload = {
            "resource": {"dashboard": dashboard_id},
            "params": {},
            "exp": exp
        }

        def b64_url(data_bytes):
            return base64.urlsafe_b64encode(data_bytes).decode("utf-8").rstrip("=")

        seg1 = b64_url(json.dumps(header, separators=(",", ":")).encode("utf-8"))
        seg2 = b64_url(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
        msg = f"{seg1}.{seg2}".encode("utf-8")
        signature = hmac.new(secret_key.encode("utf-8"), msg, hashlib.sha256).digest()
        seg3 = b64_url(signature)

        return f"{seg1}.{seg2}.{seg3}"

    def get_dashboard_embed_info(self):
        """Método RPC invocado por el cliente web Owl para obtener la URL firmada lista."""
        self.ensure_one()
        IrConfig = self.env['ir.config_parameter'].sudo()
        metabase_url = IrConfig.get_param('mba_metabase_bi.metabase_url', 'http://localhost:3000').rstrip('/')
        secret_key = IrConfig.get_param('mba_metabase_bi.metabase_secret_key', '').strip()

        if not secret_key:
            raise UserError(_("No se ha configurado la clave secreta de Embedding en Ajustes > Metabase BI."))

        token = self._generate_jwt_token(self.metabase_dashboard_id, secret_key)
        
        url_hash_parts = []
        if not self.bordered:
            url_hash_parts.append("bordered=false")
        if not self.titled:
            url_hash_parts.append("titled=false")
        if self.theme == 'night':
            url_hash_parts.append("theme=night")

        hash_str = ("#" + "&".join(url_hash_parts)) if url_hash_parts else ""
        embed_url = f"{metabase_url}/embed/dashboard/{token}{hash_str}"

        # Obtener lista de todos los tableros activos para el selector superior
        all_dashboards = self.search([('active', '=', True)]).read(['id', 'name', 'metabase_dashboard_id'])

        return {
            'embed_url': embed_url,
            'dashboard_name': self.name,
            'current_id': self.id,
            'dashboards': all_dashboards,
        }

    def action_open_dashboard(self):
        """Acción de ventana para abrir el componente Owl con este tablero cargado."""
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'metabase_dashboard_client_action',
            'name': self.name,
            'params': {
                'dashboard_id': self.id,
            },
        }
