/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class MetabaseDashboardView extends Component {
    static template = "mba_metabase_bi.MetabaseDashboardView";

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            loading: true,
            embedUrl: "",
            dashboardName: "",
            currentDashboardId: this.props.action?.params?.dashboard_id || false,
            dashboardsList: [],
        });

        onWillStart(async () => {
            await this.loadDashboardData(this.state.currentDashboardId);
        });
    }

    async loadDashboardData(dashboardId) {
        this.state.loading = true;
        try {
            let targetId = dashboardId;
            if (!targetId) {
                // Si no viene en los params, buscar el primer tablero activo
                const firstDash = await this.orm.searchRead(
                    "metabase.dashboard",
                    [["active", "=", true]],
                    ["id"],
                    { limit: 1, order: "sequence asc" }
                );
                if (firstDash.length > 0) {
                    targetId = firstDash[0].id;
                }
            }

            if (!targetId) {
                this.state.loading = false;
                this.state.embedUrl = "";
                return;
            }

            const data = await this.orm.call(
                "metabase.dashboard",
                "get_dashboard_embed_info",
                [[targetId]]
            );

            this.state.embedUrl = data.embed_url;
            this.state.dashboardName = data.dashboard_name;
            this.state.currentDashboardId = data.current_id;
            this.state.dashboardsList = data.dashboards || [];
            this.state.loading = false;
        } catch (error) {
            this.state.loading = false;
            this.notification.add(
                error.message || "Error al conectar con Metabase. Verifica los Ajustes.",
                { type: "danger" }
            );
        }
    }

    async onChangeDashboard(ev) {
        const newId = parseInt(ev.target.value);
        if (newId) {
            await this.loadDashboardData(newId);
        }
    }

    async onRefresh() {
        // Solicitar token renovado y forzar recarga fresca del dashboard
        if (this.state.currentDashboardId) {
            await this.loadDashboardData(this.state.currentDashboardId);
            const iframe = document.getElementById("metabase_bi_iframe");
            if (iframe && this.state.embedUrl) {
                // Agregar timestamp único para romper caché de iframe/navegador
                const separator = this.state.embedUrl.includes("?") ? "&" : "?";
                iframe.src = `${this.state.embedUrl}${separator}_t=${Date.now()}`;
            }
        }
    }

    onOpenFullscreen() {
        const iframe = document.getElementById("metabase_bi_iframe");
        if (iframe) {
            if (iframe.requestFullscreen) {
                iframe.requestFullscreen();
            } else if (iframe.webkitRequestFullscreen) {
                iframe.webkitRequestFullscreen();
            }
        }
    }
}

registry.category("actions").add("metabase_dashboard_client_action", MetabaseDashboardView);
