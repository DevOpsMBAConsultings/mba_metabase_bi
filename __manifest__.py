# -*- coding: utf-8 -*-
{
    'name': 'MBA - Centro de Inteligencia de Negocios Metabase BI',
    'version': '19.0.1.0.0',
    'summary': 'Visualización ejecutiva de Dashboards Metabase interactivos mediante Signed JWT en Odoo',
    'category': 'Productivity/Analytics',
    'author': 'MBA Consultings, Brooks González',
    'website': 'https://mbaconsultings.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/metabase_dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'mba_metabase_bi/static/src/js/metabase_dashboard_view.js',
            'mba_metabase_bi/static/src/xml/metabase_dashboard_view.xml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
