from flask import Flask, jsonify, request, render_template_string
from checklist_monitoramento import get_full_checklist
import psutil
import yaml
import os

app = Flask(__name__)


def _status_from_percent(value, ok, warn):
    if value < ok:
        return "ok"
    if value < warn:
        return "warning"
    return "critical"


@app.route('/')
def index():
    items = get_full_checklist()
    recursos = items.get("recursos", [])
    equipamentos = items.get("equipamentos", [])

    cpu_percent = psutil.cpu_percent(interval=0.2)
    mem = psutil.virtual_memory()
    mem_percent = mem.percent

    max_disk_percent = 0.0
    for p in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(p.mountpoint)
            if usage.percent > max_disk_percent:
                max_disk_percent = usage.percent
        except PermissionError:
            continue

    cpu_status = _status_from_percent(cpu_percent, ok=60, warn=80)
    memory_status = _status_from_percent(mem_percent, ok=70, warn=85)
    disk_status = _status_from_percent(max_disk_percent, ok=70, warn=90)

    template = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Monitoramento de Equipamentos</title>
        <style>
            :root {
                --bg-main: #050816;
                --bg-card: #0f172a;
                --accent: #22c55e;
                --accent-soft: rgba(34, 197, 94, 0.15);
                --text-primary: #e5e7eb;
                --text-secondary: #9ca3af;
                --border-subtle: rgba(148, 163, 184, 0.3);
            }
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
                font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            }
            body {
                min-height: 100vh;
                background: radial-gradient(circle at top, #1f2937 0, #020617 55%, #000 100%);
                color: var(--text-primary);
                display: flex;
                align-items: stretch;
                justify-content: center;
            }
            .shell {
                max-width: 1200px;
                width: 100%;
                padding: 32px 24px 40px;
            }
            .header {
                display: flex;
                justify-content: space-between;
                gap: 16px;
                align-items: center;
                margin-bottom: 28px;
            }
            .title-wrap h1 {
                font-size: 1.75rem;
                font-weight: 600;
                letter-spacing: 0.03em;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .badge {
                font-size: 0.7rem;
                text-transform: uppercase;
                letter-spacing: 0.16em;
                padding: 2px 8px;
                border-radius: 999px;
                border: 1px solid rgba(148, 163, 184, 0.6);
                color: var(--text-secondary);
            }
            .subtitle {
                font-size: 0.9rem;
                color: var(--text-secondary);
                margin-top: 6px;
            }
            .status-pill {
                padding: 8px 14px;
                border-radius: 999px;
                display: inline-flex;
                align-items: center;
                gap: 8px;
                background: radial-gradient(circle at top left, var(--accent-soft), #020617 55%);
                border: 1px solid rgba(34, 197, 94, 0.35);
                font-size: 0.8rem;
                color: var(--accent);
            }
            .status-dot {
                width: 8px;
                height: 8px;
                border-radius: 999px;
                background: var(--accent);
                box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.25);
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
                gap: 18px;
                margin-bottom: 20px;
            }
            .card {
                background: radial-gradient(circle at top left, rgba(15, 23, 42, 0.9), rgba(15, 23, 42, 0.6));
                border-radius: 16px;
                border: 1px solid var(--border-subtle);
                padding: 18px 18px 16px;
                backdrop-filter: blur(12px);
                box-shadow: 0 18px 60px rgba(15, 23, 42, 0.9);
            }
            .card-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }
            .card-title {
                font-size: 0.9rem;
                font-weight: 600;
                letter-spacing: 0.12em;
                text-transform: uppercase;
                color: var(--text-secondary);
            }
            .pill-count {
                font-size: 0.75rem;
                padding: 2px 8px;
                border-radius: 999px;
                background: rgba(15, 23, 42, 0.9);
                border: 1px solid rgba(148, 163, 184, 0.5);
                color: var(--text-secondary);
            }
            ul {
                list-style: none;
                display: grid;
                grid-template-columns: repeat(1, minmax(0, 1fr));
                gap: 4px;
                font-size: 0.9rem;
            }
            @media (min-width: 720px) {
                ul {
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                }
            }
            li {
                display: flex;
                align-items: center;
                gap: 6px;
                padding: 4px 6px;
                border-radius: 999px;
                color: var(--text-secondary);
            }
            li::before {
                content: '';
                width: 4px;
                height: 4px;
                border-radius: 999px;
                background: rgba(148, 163, 184, 0.8);
            }
            .footer {
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 0.75rem;
                color: var(--text-secondary);
                border-top: 1px solid rgba(31, 41, 55, 0.9);
                padding-top: 10px;
                margin-top: 10px;
            }
            .footer span strong {
                color: var(--accent);
                font-weight: 500;
            }
        </style>
    </head>
    <body>
        <main class="shell">
            <header class="header">
                <div class="title-wrap">
                    <div class="badge">Monitoramento</div>
                    <h1>Visão geral de infraestrutura</h1>
                    <p class="subtitle">Checklist inicial de recursos e equipamentos que serão monitorados (Zabbix + Grafana + serviços Python).</p>
                </div>
                <div class="status-pill">
                    <span class="status-dot"></span>
                    Stack inicial pronta para desenvolvimento
                </div>
            </header>

            <section class="grid">
                <article class="card">
                    <header class="card-header">
                        <h2 class="card-title">Recursos</h2>
                        <span class="pill-count">{{ recursos|length }} itens</span>
                    </header>

                    <div style="display:flex; gap:8px; margin-bottom:10px; flex-wrap:wrap;">
                        <span style="font-size:0.75rem; color:var(--text-secondary); flex-basis:100%;">Status local</span>

                        <div class="status-pill" style="border-color:transparent; background:rgba(15,23,42,0.9);">
                            <span class="status-dot" style="background: {% if cpu_status == 'ok' %}#22c55e{% elif cpu_status == 'warning' %}#eab308{% else %}#ef4444{% endif %}; box-shadow:0 0 0 4px rgba(148,163,184,0.25);"></span>
                            CPU: {{ '%.1f'|format(cpu_percent) }}% ({{ cpu_status }})
                        </div>

                        <div class="status-pill" style="border-color:transparent; background:rgba(15,23,42,0.9);">
                            <span class="status-dot" style="background: {% if memory_status == 'ok' %}#22c55e{% elif memory_status == 'warning' %}#eab308{% else %}#ef4444{% endif %}; box-shadow:0 0 0 4px rgba(148,163,184,0.25);"></span>
                            Memória: {{ '%.1f'|format(mem_percent) }}% ({{ memory_status }})
                        </div>

                        <div class="status-pill" style="border-color:transparent; background:rgba(15,23,42,0.9);">
                            <span class="status-dot" style="background: {% if disk_status == 'ok' %}#22c55e{% elif disk_status == 'warning' %}#eab308{% else %}#ef4444{% endif %}; box-shadow:0 0 0 4px rgba(148,163,184,0.25);"></span>
                            Disco: {{ '%.1f'|format(disk_percent) }}% ({{ disk_status }})
                        </div>
                    </div>

                    <ul>
                        {% for item in recursos %}
                        <li>{{ item }}</li>
                        {% endfor %}
                    </ul>
                </article>

                <article class="card">
                    <header class="card-header">
                        <h2 class="card-title">Equipamentos</h2>
                        <span class="pill-count">{{ equipamentos|length }} itens</span>
                    </header>
                    <ul>
                        {% for item in equipamentos %}
                        <li>{{ item }}</li>
                        {% endfor %}
                    </ul>
                </article>
            </section>

            <footer class="footer">
                <span>Backend Python: <strong>/metrics</strong> · <strong>/health</strong> · integrações com Zabbix / Grafana.</span>
                <span>Pronto para evoluir para dashboards em tempo real.</span>
            </footer>
        </main>
    </body>
    </html>
    """

    return render_template_string(
        template,
        recursos=recursos,
        equipamentos=equipamentos,
        cpu_percent=cpu_percent,
        mem_percent=mem_percent,
        disk_percent=max_disk_percent,
        cpu_status=cpu_status,
        memory_status=memory_status,
        disk_status=disk_status,
    )


@app.route('/metrics')
def metrics():
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory()

    max_disk_percent = 0.0
    disks = []
    for p in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(p.mountpoint)
            disks.append({
                "device": p.device,
                "mountpoint": p.mountpoint,
                "fstype": p.fstype,
                "percent": usage.percent,
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
            })
            if usage.percent > max_disk_percent:
                max_disk_percent = usage.percent
        except PermissionError:
            continue

    status = {
        "cpu": _status_from_percent(cpu, ok=60, warn=80),
        "memory": _status_from_percent(mem.percent, ok=70, warn=85),
        "disk": _status_from_percent(max_disk_percent, ok=70, warn=90),
    }

    data = {
        "cpu_percent": cpu,
        "memory_percent": mem.percent,
        "disk_percent": max_disk_percent,
        "status": status,
        "raw": {
            "memory": mem._asdict(),
            "disks": disks,
        },
    }
    return jsonify(data)


@app.route('/checklist')
def checklist():
    return jsonify(get_full_checklist())


@app.route('/health')
def health():
    return jsonify({"status": "ok"})


@app.route('/config', methods=['GET'])
def get_config():
    cfg_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if not os.path.exists(cfg_path):
        return jsonify({"error": ".env not found"}), 404
    with open(cfg_path) as f:
        content = f.read()
    return jsonify({"env": content})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
