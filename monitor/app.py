import os
from datetime import datetime
from functools import wraps
from pathlib import Path

import psutil
import yaml
from flask import (
    Flask,
    jsonify,
    redirect,
    render_template_string,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash

try:
    from .checklist_monitoramento import get_full_checklist
except ImportError:  # fallback when executed as a script (python monitor/app.py)
    from checklist_monitoramento import get_full_checklist
HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Monitoramento · Hub</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600&display=swap');
        :root {
            --bg-page: #030712;
            --bg-panel: rgba(9, 14, 25, 0.92);
            --bg-soft: rgba(13, 20, 38, 0.8);
            --border: rgba(148, 163, 184, 0.25);
            --accent: #4ade80;
            --accent-strong: #16a34a;
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
        }
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Space Grotesk', 'Segoe UI', sans-serif;
        }
        body {
            min-height: 100vh;
            background: radial-gradient(circle at top, #0b1120 0, #030712 55%, #000 100%);
            color: var(--text-primary);
            padding: 32px;
        }
        .layout {
            display: grid;
            grid-template-columns: 260px minmax(0, 1fr);
            gap: 24px;
            max-width: 1440px;
            margin: 0 auto;
        }
        .sidebar {
            background: var(--bg-panel);
            border-radius: 28px;
            padding: 28px 24px 32px;
            border: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            gap: 28px;
        }
        .brand {
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .brand-dot {
            width: 12px;
            height: 12px;
            border-radius: 999px;
            background: var(--accent);
            box-shadow: 0 0 12px rgba(74, 222, 128, 0.8);
        }
        nav ul {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }
        nav a {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 12px 14px;
            border-radius: 16px;
            color: var(--text-secondary);
            text-decoration: none;
            font-weight: 500;
            border: 1px solid transparent;
        }
        nav a.active {
            background: rgba(74, 222, 128, 0.12);
            color: var(--text-primary);
            border-color: rgba(74, 222, 128, 0.4);
        }
        nav a:hover {
            border-color: rgba(148, 163, 184, 0.4);
        }
        .sidebar-footer {
            margin-top: auto;
            padding: 16px;
            border-radius: 18px;
            background: rgba(148, 163, 184, 0.08);
        }
        .sidebar-footer strong {
            display: block;
            font-size: 1rem;
        }
        .content {
            background: var(--bg-panel);
            border-radius: 32px;
            border: 1px solid var(--border);
            padding: 36px 40px 44px;
            display: flex;
            flex-direction: column;
            gap: 28px;
            box-shadow: 0 40px 120px rgba(2, 6, 23, 0.9);
        }
        .hero {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            align-items: center;
        }
        .hero-text {
            flex: 1 1 360px;
        }
        .hero h1 {
            font-size: clamp(2rem, 4vw, 2.6rem);
            margin-bottom: 8px;
        }
        .hero p {
            color: var(--text-secondary);
            line-height: 1.4;
        }
        .hero-actions {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }
        .hero-actions a {
            padding: 14px 20px;
            border-radius: 18px;
            text-decoration: none;
            font-weight: 600;
            border: 1px solid transparent;
        }
        .primary-btn {
            background: linear-gradient(135deg, var(--accent), var(--accent-strong));
            color: #041007;
        }
        .ghost-btn {
            border-color: var(--border);
            color: var(--text-secondary);
        }
        .section-title {
            text-transform: uppercase;
            letter-spacing: 0.18em;
            font-size: 0.78rem;
            color: var(--text-secondary);
        }
        .highlights-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
        }
        .highlight-card {
            border-radius: 22px;
            padding: 22px;
            border: 1px solid rgba(148,163,184,0.35);
            background: var(--bg-soft);
        }
        .highlight-label {
            text-transform: uppercase;
            letter-spacing: 0.16em;
            font-size: 0.7rem;
            color: var(--accent);
        }
        .highlight-card h3 {
            margin: 10px 0 6px;
            font-size: 1.15rem;
        }
        .highlights-grid p {
            color: var(--text-secondary);
            line-height: 1.45;
        }
        .actions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
        }
        .action-card {
            border-radius: 22px;
            padding: 20px;
            border: 1px solid var(--border);
            background: var(--bg-soft);
            text-decoration: none;
            color: inherit;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }
        .config-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 16px;
        }
        .config-card {
            border-radius: 22px;
            padding: 22px;
            border: 1px solid rgba(148,163,184,0.35);
            background: var(--bg-soft);
        }
        .config-label {
            font-size: 0.75rem;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            color: var(--accent);
        }
        .config-card h3 {
            margin: 8px 0 6px;
            font-size: 1.15rem;
        }
        .config-card p {
            color: var(--text-secondary);
            line-height: 1.4;
        }
        .config-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 12px;
        }
        .config-tags span {
            padding: 4px 10px;
            border-radius: 999px;
            background: rgba(74, 222, 128, 0.12);
            color: var(--accent);
            font-size: 0.75rem;
        }
        .insights {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 16px;
        }
        .panel {
            border-radius: 22px;
            padding: 20px;
            border: 1px solid rgba(148,163,184,0.3);
            background: var(--bg-soft);
        }
        .panel h2 {
            font-size: 0.85rem;
            letter-spacing: 0.2em;
            text-transform: uppercase;
            color: var(--text-secondary);
            margin-bottom: 12px;
        }
        .list-simple {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 10px;
            font-size: 0.92rem;
            color: var(--text-secondary);
        }
        .list-simple li {
            display: flex;
            justify-content: space-between;
            gap: 16px;
        }
        .list-simple li div {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }
        .list-simple small {
            color: rgba(148, 163, 184, 0.7);
            font-size: 0.75rem;
        }
        .badge-light {
            padding: 4px 10px;
            border-radius: 999px;
            border: 1px solid rgba(148,163,184,0.4);
            color: var(--text-primary);
            font-size: 0.75rem;
        }
        .highlight {
            margin-top: 12px;
            padding: 12px 14px;
            border-radius: 14px;
            border: 1px dashed rgba(148,163,184,0.35);
            background: rgba(59, 130, 246, 0.08);
        }
        @media (max-width: 1080px) {
            .layout { grid-template-columns: 1fr; }
            .sidebar { flex-direction: row; flex-wrap: wrap; }
            nav ul { flex-direction: row; flex-wrap: wrap; }
            nav a { flex: 1 1 140px; }
        }
        @media (max-width: 720px) {
            body { padding: 16px; }
            .content { padding: 24px; }
        }
    </style>
</head>
<body>
    <div class="layout">
        <aside class="sidebar">
            <div class="brand">
                <span class="brand-dot"></span>
                Monitor Hub
            </div>
            <nav>
                <ul>
                    {% for link in nav_links %}
                    <li>
                        <a href="{{ link.url }}" class="{% if link.active %}active{% endif %}">
                            <span>{{ link.icon }}</span>
                            <span>{{ link.label }}</span>
                        </a>
                    </li>
                    {% endfor %}
                </ul>
            </nav>
            <div class="sidebar-footer">
                <strong>{{ user_name }}</strong>
                <span>Último login · {{ last_refresh }}</span>
            </div>
        </aside>

        <main class="content">
            <header class="hero">
                <div class="hero-text">
                    <p class="section-title">Centro de configuração</p>
                    <h1>Olá, {{ user_name }} 👋</h1>
                    <p>Este hub apresenta a proposta do sistema, sinaliza integrações disponíveis e orienta operadores sobre próximos passos antes de falar de qualquer equipamento.</p>
                </div>
                <div class="hero-actions">
                    <a class="primary-btn" href="{{ overview_url }}">Abrir infraestrutura</a>
                    <a class="ghost-btn" href="{{ demo_url }}">Ver demo Mikrotik</a>
                </div>
            </header>

            <section>
                <p class="section-title">Como o sistema ajuda</p>
                <div class="highlights-grid">
                    {% for item in system_highlights %}
                    <article class="highlight-card">
                        <span class="highlight-label">{{ item.label }}</span>
                        <h3>{{ item.title }}</h3>
                        <p>{{ item.description }}</p>
                    </article>
                    {% endfor %}
                </div>
            </section>

            <section>
                <p class="section-title">Explorar recursos</p>
                <section class="actions-grid">
                    {% for tile in action_tiles %}
                    <a class="action-card" href="{{ tile.url }}">
                        <div style="font-size:1.5rem;">{{ tile.icon }}</div>
                        <strong>{{ tile.title }}</strong>
                        <span style="color: var(--text-secondary);">{{ tile.description }}</span>
                    </a>
                    {% endfor %}
                </section>
            </section>

            <section>
                <p class="section-title">Playbook do sistema</p>
                <div class="config-grid">
                    {% for step in config_steps %}
                    <article class="config-card">
                        <div class="config-label">{{ step.label }}</div>
                        <h3>{{ step.title }}</h3>
                        <p>{{ step.description }}</p>
                        <div class="config-tags">
                            {% for tag in step.tags %}
                            <span>{{ tag }}</span>
                            {% endfor %}
                        </div>
                    </article>
                    {% endfor %}
                </div>
            </section>

            <section class="insights">
                <article class="panel">
                    <h2>Estado do sistema</h2>
                    <ul class="list-simple">
                        {% for status in status_notes %}
                        <li>
                            <div>
                                <strong>{{ status.topic }}</strong>
                                <small>{{ status.detail }}</small>
                            </div>
                            <span class="badge-light">{{ status.value }}</span>
                        </li>
                        {% endfor %}
                    </ul>
                    <div class="highlight">{{ docs_hint }}</div>
                </article>
                <article class="panel">
                    <h2>Roadmap e referências</h2>
                    <ul class="list-simple">
                        {% for item in roadmap_items %}
                        <li>
                            <span>{{ item.item }}</span>
                            <strong>{{ item.status }}</strong>
                        </li>
                        {% endfor %}
                    </ul>
                    <div class="highlight">Use o menu lateral para navegar entre módulos, integrações e demos.</div>
                </article>
            </section>
        </main>
    </div>
</body>
</html>
"""


OVERVIEW_TEMPLATE = """
<!DOCTYPE html>
<html lang=\"pt-br\">
<head>
    <meta charset=\"UTF-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
    <title>Monitoramento · Infraestrutura</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600&display=swap');
        :root {
            --bg-page: #030712;
            --bg-panel: rgba(9, 14, 25, 0.92);
            --bg-soft: rgba(13, 20, 38, 0.8);
            --border: rgba(148, 163, 184, 0.25);
            --accent: #4ade80;
            --accent-strong: #16a34a;
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
        }
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Space Grotesk', 'Segoe UI', sans-serif;
        }
        body {
            min-height: 100vh;
            background: radial-gradient(circle at top, #0b1120 0, #030712 55%, #000 100%);
            color: var(--text-primary);
            padding: 32px;
        }
        .layout {
            display: grid;
            grid-template-columns: 260px minmax(0, 1fr);
            gap: 24px;
            max-width: 1440px;
            margin: 0 auto;
        }
        .sidebar {
            background: var(--bg-panel);
            border-radius: 28px;
            padding: 28px 24px 32px;
            border: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            gap: 28px;
        }
        .brand {
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .brand-dot {
            width: 12px;
            height: 12px;
            border-radius: 999px;
            background: var(--accent);
            box-shadow: 0 0 12px rgba(74, 222, 128, 0.8);
        }
        nav ul {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }
        nav a {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 12px 14px;
            border-radius: 16px;
            color: var(--text-secondary);
            text-decoration: none;
            font-weight: 500;
            border: 1px solid transparent;
        }
        nav a.active {
            background: rgba(74, 222, 128, 0.12);
            color: var(--text-primary);
            border-color: rgba(74, 222, 128, 0.4);
        }
        nav a:hover {
            border-color: rgba(148, 163, 184, 0.4);
        }
        .sidebar-footer {
            margin-top: auto;
            padding: 16px;
            border-radius: 18px;
            background: rgba(148, 163, 184, 0.08);
        }
        .sidebar-footer strong {
            display: block;
            font-size: 1rem;
        }
        .content {
            background: var(--bg-panel);
            border-radius: 32px;
            border: 1px solid var(--border);
            padding: 36px 40px 44px;
            display: flex;
            flex-direction: column;
            gap: 28px;
            box-shadow: 0 40px 120px rgba(2, 6, 23, 0.9);
        }
        .hero {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            align-items: center;
        }
        .hero-text {
            flex: 1 1 360px;
        }
        .hero h1 {
            font-size: clamp(2rem, 4vw, 2.6rem);
            margin-bottom: 8px;
        }
        .hero p {
            color: var(--text-secondary);
            line-height: 1.4;
        }
        .hero-actions {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }
        .hero-actions a {
            padding: 14px 20px;
            border-radius: 18px;
            text-decoration: none;
            font-weight: 600;
            border: 1px solid transparent;
        }
        .ghost-btn {
            border-color: var(--border);
            color: var(--text-secondary);
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
        }
        .stat-card {
            padding: 18px 20px;
            border-radius: 20px;
            background: var(--bg-soft);
            border: 1px solid rgba(148, 163, 184, 0.25);
        }
        .stat-label {
            text-transform: uppercase;
            letter-spacing: 0.16em;
            font-size: 0.78rem;
            color: var(--text-secondary);
        }
        .stat-value {
            font-size: 2rem;
            font-weight: 600;
            margin: 10px 0 4px;
        }
        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 0.78rem;
            border: 1px solid var(--border);
        }
        .status-pill.ok { color: #4ade80; border-color: rgba(74,222,128,0.4); }
        .status-pill.warning { color: #facc15; border-color: rgba(250,204,21,0.4); }
        .status-pill.critical { color: #fb7185; border-color: rgba(251,113,133,0.4); }
        .section-title {
            text-transform: uppercase;
            letter-spacing: 0.18em;
            font-size: 0.78rem;
            color: var(--text-secondary);
        }
        .detail-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 18px;
        }
        .detail-card {
            border-radius: 22px;
            padding: 20px;
            border: 1px solid var(--border);
            background: var(--bg-soft);
        }
        .detail-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .detail-title {
            font-size: 0.85rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--text-secondary);
        }
        .pill-count {
            font-size: 0.75rem;
            padding: 2px 8px;
            border-radius: 999px;
            border: 1px solid rgba(148,163,184,0.35);
            color: var(--text-secondary);
        }
        .detail-list {
            list-style: none;
            display: grid;
            grid-template-columns: repeat(1, minmax(0, 1fr));
            gap: 6px;
            color: var(--text-secondary);
            font-size: 0.92rem;
        }
        @media (min-width: 720px) {
            .detail-list { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        }
        .detail-list li {
            display: flex;
            gap: 6px;
            align-items: center;
        }
        .detail-list li::before {
            content: '•';
            color: rgba(148, 163, 184, 0.6);
        }
        .footer-info {
            margin-top: 10px;
            font-size: 0.85rem;
            color: var(--text-secondary);
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 8px;
        }
        @media (max-width: 1080px) {
            .layout { grid-template-columns: 1fr; }
            .sidebar { flex-direction: row; flex-wrap: wrap; }
            nav ul { flex-direction: row; flex-wrap: wrap; }
            nav a { flex: 1 1 140px; }
        }
        @media (max-width: 720px) {
            body { padding: 16px; }
            .content { padding: 24px; }
        }
    </style>
</head>
<body>
    <div class=\"layout\">
        <aside class=\"sidebar\">
            <div class=\"brand\">
                <span class=\"brand-dot\"></span>
                Monitor Hub
            </div>
            <nav>
                <ul>
                    {% for link in nav_links %}
                    <li>
                        <a href=\"{{ link.url }}\" class=\"{% if link.active %}active{% endif %}\">
                            <span>{{ link.icon }}</span>
                            <span>{{ link.label }}</span>
                        </a>
                    </li>
                    {% endfor %}
                </ul>
            </nav>
            <div class=\"sidebar-footer\">
                <strong>{{ user_name }}</strong>
                <span>Último login · {{ last_refresh }}</span>
            </div>
        </aside>

        <main class=\"content\">
            <header class=\"hero\">
                <div class=\"hero-text\">
                    <p class=\"section-title\">Visão de infraestrutura</p>
                    <h1>Checklist e recursos monitorados</h1>
                    <p>Confirme os pontos de observabilidade ativos antes de incorporar novos ativos ou integrações. Esta visão lista recursos previstos e equipamentos em acompanhamento.</p>
                </div>
                <div class=\"hero-actions\">
                    <a class=\"ghost-btn\" href=\"{{ url_for('index') }}\">Voltar ao hub</a>
                </div>
            </header>

            <section class=\"stats-grid\">
                <article class=\"stat-card\">
                    <div class=\"stat-label\">CPU</div>
                    <div class=\"stat-value\">{{ '%.1f'|format(stats.cpu_percent) }}%</div>
                    <div class=\"status-pill {{ stats.cpu_status }}\">Estado {{ stats.cpu_status }}</div>
                </article>
                <article class=\"stat-card\">
                    <div class=\"stat-label\">Memória</div>
                    <div class=\"stat-value\">{{ '%.1f'|format(stats.mem_percent) }}%</div>
                    <div class=\"status-pill {{ stats.memory_status }}\">Estado {{ stats.memory_status }}</div>
                </article>
                <article class=\"stat-card\">
                    <div class=\"stat-label\">Disco</div>
                    <div class=\"stat-value\">{{ '%.1f'|format(stats.disk_percent) }}%</div>
                    <div class=\"status-pill {{ stats.disk_status }}\">Estado {{ stats.disk_status }}</div>
                </article>
            </section>

            <div>
                <p class=\"section-title\">Checklist monitorado</p>
                <section class=\"detail-grid\">
                    <article class=\"detail-card\">
                        <div class=\"detail-header\">
                            <span class=\"detail-title\">Recursos</span>
                            <span class=\"pill-count\">{{ recursos|length }} itens</span>
                        </div>
                        <ul class=\"detail-list\">
                            {% for item in recursos %}
                            <li>{{ item }}</li>
                            {% endfor %}
                        </ul>
                    </article>
                    <article class=\"detail-card\">
                        <div class=\"detail-header\">
                            <span class=\"detail-title\">Equipamentos</span>
                            <span class=\"pill-count\">{{ equipamentos|length }} itens</span>
                        </div>
                        <ul class=\"detail-list\">
                            {% for item in equipamentos %}
                            <li>{{ item }}</li>
                            {% endfor %}
                        </ul>
                    </article>
                </section>
            </div>

            <div class=\"footer-info\">
                <span>Endpoints disponíveis: <strong>/metrics</strong> · <strong>/health</strong> · integrações externas.</span>
                <span>Revise estes itens antes de publicar novos dashboards.</span>
            </div>
        </main>
    </div>
</body>
</html>
"""


SERVERS_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Monitoramento · Servidores</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600&display=swap');
        :root {
            --bg-page: #030712;
            --bg-panel: rgba(9, 14, 25, 0.92);
            --bg-soft: rgba(13, 20, 38, 0.8);
            --border: rgba(148, 163, 184, 0.25);
            --accent: #4ade80;
            --accent-strong: #16a34a;
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
        }
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Space Grotesk', 'Segoe UI', sans-serif;
        }
        body {
            min-height: 100vh;
            background: radial-gradient(circle at top, #0b1120 0, #030712 55%, #000 100%);
            color: var(--text-primary);
            padding: 32px;
        }
        .layout {
            display: grid;
            grid-template-columns: 260px minmax(0, 1fr);
            gap: 24px;
            max-width: 1440px;
            margin: 0 auto;
        }
        .sidebar {
            background: var(--bg-panel);
            border-radius: 28px;
            padding: 28px 24px 32px;
            border: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            gap: 28px;
        }
        nav ul {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }
        nav a {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 12px 14px;
            border-radius: 16px;
            color: var(--text-secondary);
            text-decoration: none;
            font-weight: 500;
            border: 1px solid transparent;
        }
        nav a.active {
            background: rgba(74, 222, 128, 0.12);
            color: var(--text-primary);
            border-color: rgba(74, 222, 128, 0.4);
        }
        nav a:hover {
            border-color: rgba(148, 163, 184, 0.4);
        }
        .brand {
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .brand-dot {
            width: 12px;
            height: 12px;
            border-radius: 999px;
            background: var(--accent);
            box-shadow: 0 0 12px rgba(74, 222, 128, 0.8);
        }
        .sidebar-footer {
            margin-top: auto;
            padding: 16px;
            border-radius: 18px;
            background: rgba(148, 163, 184, 0.08);
        }
        .content {
            background: var(--bg-panel);
            border-radius: 32px;
            border: 1px solid var(--border);
            padding: 36px 40px 44px;
            display: flex;
            flex-direction: column;
            gap: 28px;
            box-shadow: 0 40px 120px rgba(2, 6, 23, 0.9);
        }
        .hero {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            align-items: center;
        }
        .hero-text {
            flex: 1 1 360px;
        }
        .hero h1 {
            font-size: clamp(2rem, 4vw, 2.6rem);
            margin-bottom: 8px;
        }
        .tagline {
            color: var(--text-secondary);
            line-height: 1.5;
        }
        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 18px;
        }
        .field {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }
        label {
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.16em;
            color: var(--text-secondary);
        }
        input,
        select,
        textarea {
            padding: 12px 14px;
            border-radius: 16px;
            border: 1px solid var(--border);
            background: rgba(3, 7, 18, 0.4);
            color: var(--text-primary);
            font-size: 0.95rem;
        }
        textarea { min-height: 120px; resize: none; }
        .cta-row {
            margin-top: 8px;
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }
        button {
            padding: 14px 20px;
            border-radius: 18px;
            border: none;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            background: linear-gradient(135deg, var(--accent), var(--accent-strong));
            color: #041007;
            cursor: pointer;
        }
        .panel {
            border-radius: 24px;
            padding: 24px;
            border: 1px solid rgba(148,163,184,0.35);
            background: var(--bg-soft);
        }
        .panel h2 {
            font-size: 0.9rem;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            color: var(--text-secondary);
        }
        .panel + .panel { margin-top: 18px; }
        .profiles {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 12px;
        }
        .profile-card {
            border-radius: 20px;
            padding: 18px;
            border: 1px solid rgba(148,163,184,0.3);
            background: rgba(10,16,32,0.9);
        }
        .profile-card strong { display: block; margin-bottom: 6px; }
        .pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 999px;
            border: 1px solid rgba(148,163,184,0.4);
            font-size: 0.75rem;
            color: var(--text-secondary);
        }
        .message {
            padding: 14px 16px;
            border-radius: 16px;
            border: 1px solid rgba(74,222,128,0.4);
            background: rgba(74, 222, 128, 0.12);
            color: var(--text-primary);
        }
        @media (max-width: 1080px) {
            .layout { grid-template-columns: 1fr; }
            .sidebar { flex-direction: row; flex-wrap: wrap; }
            nav ul { flex-direction: row; flex-wrap: wrap; }
            nav a { flex: 1 1 140px; }
        }
        @media (max-width: 720px) {
            body { padding: 16px; }
            .content { padding: 24px; }
        }
    </style>
</head>
<body>
    <div class="layout">
        <aside class="sidebar">
            <div class="brand">
                <span class="brand-dot"></span>
                Monitor Hub
            </div>
            <nav>
                <ul>
                    {% for link in nav_links %}
                    <li>
                        <a href="{{ link.url }}" class="{% if link.active %}active{% endif %}">
                            <span>{{ link.icon }}</span>
                            <span>{{ link.label }}</span>
                        </a>
                    </li>
                    {% endfor %}
                </ul>
            </nav>
            <div class="sidebar-footer">
                <strong>{{ user_name }}</strong>
                <span>Último login · {{ last_refresh }}</span>
            </div>
        </aside>

        <main class="content">
            <header class="hero">
                <div class="hero-text">
                    <p class="section-title">Servidores</p>
                    <h1>SERVIDORES SNMP</h1>
                    <p class="tagline">Cadastre hosts, defina grupos, templates e credenciais SNMP v2/v3 usando a mesma lógica aplicada aos demais módulos da plataforma.</p>
                </div>
                <div class="panel" style="min-width:240px;">
                    <h2>Fluxo rápido</h2>
                    <ul style="margin-top:12px;color:var(--text-secondary);display:flex;flex-direction:column;gap:8px;list-style:none;">
                        <li>1 · Informe host, IP e grupo lógico.</li>
                        <li>2 · Ajuste credenciais SNMP (community ou usuário v3).</li>
                        <li>3 · Vincule um template e salve.</li>
                    </ul>
                    <div class="pill" style="margin-top:12px;">SNMP + Templates</div>
                </div>
            </header>

            {% if message %}
            <div class="message">{{ message }}</div>
            {% endif %}

            <form method="post" class="panel">
                <div class="form-grid">
                    <div class="field">
                        <label for="host_name">Nome do host</label>
                        <input id="host_name" name="host_name" value="{{ form_state.host_name }}" placeholder="core-border-01" required />
                    </div>
                    <div class="field">
                        <label for="ip_address">Endereço / Interface</label>
                        <input id="ip_address" name="ip_address" value="{{ form_state.ip_address }}" placeholder="192.168.88.1" required />
                    </div>
                    <div class="field">
                        <label for="host_group">Grupo</label>
                        <select id="host_group" name="host_group" required>
                            <option value="">Selecione</option>
                            {% for group in host_groups %}
                            <option value="{{ group.name }}" {% if form_state.host_group == group.name %}selected{% endif %}>{{ group.name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="field">
                        <label for="template">Template</label>
                        <select id="template" name="template" required>
                            <option value="">Selecione</option>
                            {% for tpl in templates %}
                            <option value="{{ tpl }}" {% if form_state.template == tpl %}selected{% endif %}>{{ tpl }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="field">
                        <label for="snmp_version">SNMP</label>
                        <select id="snmp_version" name="snmp_version" required>
                            {% for version in snmp_versions %}
                            <option value="{{ version }}" {% if form_state.snmp_version == version %}selected{% endif %}>{{ version|upper }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="field">
                        <label for="community">Community / Usuário</label>
                        <input id="community" name="community" value="{{ form_state.community }}" placeholder="public" required />
                    </div>
                    <div class="field">
                        <label for="polling">Intervalo (s)</label>
                        <input id="polling" name="polling" type="number" min="30" value="{{ form_state.polling }}" />
                    </div>
                    <div class="field">
                        <label for="tags">Tags</label>
                        <input id="tags" name="tags" value="{{ form_state.tags }}" placeholder="backbone, mikrotik" />
                    </div>
                    <div class="field" style="grid-column:1/-1;">
                        <label for="notes">Notas / macros</label>
                        <textarea id="notes" name="notes" placeholder="Ex.: {$SNMP_COMMUNITY}=public">{{ form_state.notes }}</textarea>
                    </div>
                </div>
                <div class="cta-row">
                    <button type="submit">Salvar host</button>
                    <div class="pill">Coleta SNMP habilitada</div>
                </div>
            </form>

            <section class="panel">
                <h2>Perfis sugeridos</h2>
                <div class="profiles" style="margin-top:16px;">
                    {% for profile in server_profiles %}
                    <article class="profile-card">
                        <strong>{{ profile.name }}</strong>
                        <p style="color:var(--text-secondary); line-height:1.4;">{{ profile.description }}</p>
                        <div class="pill" style="margin-top:10px;">{{ profile.template }}</div>
                    </article>
                    {% endfor %}
                </div>
            </section>
        </main>
    </div>
</body>
</html>
"""


CHECKLIST_TEMPLATE = """
<!DOCTYPE html>
<html lang=\"pt-br\">
<head>
    <meta charset=\"UTF-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
    <title>Monitoramento · Checklist</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600&display=swap');
        :root {
            --bg-page: #030712;
            --bg-panel: rgba(9, 14, 25, 0.92);
            --bg-soft: rgba(13, 20, 38, 0.8);
            --border: rgba(148, 163, 184, 0.25);
            --accent: #4ade80;
            --accent-strong: #16a34a;
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
        }
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Space Grotesk', 'Segoe UI', sans-serif;
        }
        body {
            min-height: 100vh;
            background: radial-gradient(circle at top, #0b1120 0, #030712 55%, #000 100%);
            color: var(--text-primary);
            padding: 32px;
        }
        .layout {
            display: grid;
            grid-template-columns: 260px minmax(0, 1fr);
            gap: 24px;
            max-width: 1440px;
            margin: 0 auto;
        }
        .sidebar {
            background: var(--bg-panel);
            border-radius: 28px;
            padding: 28px 24px 32px;
            border: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            gap: 28px;
        }
        nav ul {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }
        nav a {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 12px 14px;
            border-radius: 16px;
            color: var(--text-secondary);
            text-decoration: none;
            font-weight: 500;
            border: 1px solid transparent;
        }
        nav a.active {
            background: rgba(74, 222, 128, 0.12);
            color: var(--text-primary);
            border-color: rgba(74, 222, 128, 0.4);
        }
        nav a:hover {
            border-color: rgba(148, 163, 184, 0.4);
        }
        .brand {
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .brand-dot {
            width: 12px;
            height: 12px;
            border-radius: 999px;
            background: var(--accent);
            box-shadow: 0 0 12px rgba(74, 222, 128, 0.8);
        }
        .sidebar-footer {
            margin-top: auto;
            padding: 16px;
            border-radius: 18px;
            background: rgba(148, 163, 184, 0.08);
        }
        .content {
            background: var(--bg-panel);
            border-radius: 32px;
            border: 1px solid var(--border);
            padding: 36px 40px 44px;
            display: flex;
            flex-direction: column;
            gap: 28px;
            box-shadow: 0 40px 120px rgba(2, 6, 23, 0.9);
        }
        .hero {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            align-items: center;
        }
        .hero-text { flex: 1 1 360px; }
        .hero h1 { font-size: clamp(2rem, 4vw, 2.6rem); margin-bottom: 8px; }
        .tagline { color: var(--text-secondary); line-height: 1.5; }
        .hero-actions { display: flex; gap: 12px; flex-wrap: wrap; }
        .primary-btn {
            padding: 14px 20px;
            border-radius: 18px;
            text-decoration: none;
            font-weight: 600;
            border: 1px solid transparent;
            background: linear-gradient(135deg, var(--accent), var(--accent-strong));
            color: #041007;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
        }
        .summary-card {
            border-radius: 24px;
            padding: 20px;
            border: 1px solid rgba(148, 163, 184, 0.35);
            background: var(--bg-soft);
        }
        .summary-card span { color: var(--text-secondary); font-size: 0.8rem; }
        .summary-card strong { display: block; font-size: 1.8rem; margin: 6px 0; }
        .summary-card small { color: rgba(148, 163, 184, 0.7); font-size: 0.75rem; }
        .section-title {
            text-transform: uppercase;
            letter-spacing: 0.18em;
            font-size: 0.78rem;
            color: var(--text-secondary);
        }
        .host-grid {
            margin-top: 16px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 16px;
        }
        .host-card {
            border-radius: 22px;
            padding: 18px;
            border: 1px solid rgba(148,163,184,0.3);
            background: rgba(11,17,32,0.9);
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        .host-card h3 { font-size: 1rem; }
        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 0.75rem;
            border: 1px solid rgba(148,163,184,0.4);
        }
        .status-pill.ok { color: #4ade80; border-color: rgba(74,222,128,0.4); }
        .status-pill.pending { color: #facc15; border-color: rgba(250,204,21,0.4); }
        .meta {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            color: var(--text-secondary);
            font-size: 0.85rem;
        }
        .tags {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }
        .tags span {
            padding: 2px 8px;
            border-radius: 999px;
            background: rgba(148, 163, 184, 0.15);
            font-size: 0.72rem;
        }
        .empty-state {
            margin-top: 18px;
            padding: 24px;
            border: 1px dashed rgba(148,163,184,0.4);
            border-radius: 20px;
            color: var(--text-secondary);
            text-align: center;
        }
        .panels {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
        }
        .panel {
            border-radius: 22px;
            padding: 20px;
            border: 1px solid rgba(148,163,184,0.3);
            background: var(--bg-soft);
        }
        .panel h2 {
            font-size: 0.85rem;
            letter-spacing: 0.2em;
            text-transform: uppercase;
            color: var(--text-secondary);
            margin-bottom: 12px;
        }
        .list-simple {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 8px;
            color: var(--text-secondary);
            font-size: 0.9rem;
        }
        @media (max-width: 1080px) {
            .layout { grid-template-columns: 1fr; }
            .sidebar { flex-direction: row; flex-wrap: wrap; }
            nav ul { flex-direction: row; flex-wrap: wrap; }
            nav a { flex: 1 1 140px; }
        }
        @media (max-width: 720px) {
            body { padding: 16px; }
            .content { padding: 24px; }
        }
    </style>
</head>
<body>
    <div class=\"layout\">
        <aside class=\"sidebar\">
            <div class=\"brand\">
                <span class=\"brand-dot\"></span>
                Monitor Hub
            </div>
            <nav>
                <ul>
                    {% for link in nav_links %}
                    <li>
                        <a href=\"{{ link.url }}\" class=\"{% if link.active %}active{% endif %}\">
                            <span>{{ link.icon }}</span>
                            <span>{{ link.label }}</span>
                        </a>
                    </li>
                    {% endfor %}
                </ul>
            </nav>
            <div class=\"sidebar-footer\">
                <strong>{{ user_name }}</strong>
                <span>Último login · {{ last_refresh }}</span>
            </div>
        </aside>

        <main class=\"content\">
            <header class=\"hero\">
                <div class=\"hero-text\">
                    <p class=\"section-title\">Checklist operacional</p>
                    <h1>Visão geral dos hosts</h1>
                    <p class=\"tagline\">Verifique rapidamente se cada host adicionado possui credenciais SNMP ativas e tags corretas antes de liberar para os times.</p>
                </div>
                <div class=\"hero-actions\">
                    <a class=\"primary-btn\" href=\"{{ servers_url }}\">Cadastrar novo host</a>
                </div>
            </header>

            <section class=\"summary-grid\">
                {% for card in summary_stats %}
                <article class=\"summary-card\">
                    <span>{{ card.label }}</span>
                    <strong>{{ card.value }}</strong>
                    <small>{{ card.detail }}</small>
                </article>
                {% endfor %}
            </section>

            <section>
                <p class=\"section-title\">Hosts monitorados</p>
                {% if hosts %}
                <div class=\"host-grid\">
                    {% for host in hosts %}
                    <article class=\"host-card\">
                        <div style=\"display:flex;justify-content:space-between;align-items:center;gap:8px;\">
                            <h3>{{ host.host_name }}</h3>
                            <span class=\"status-pill {% if host.snmp_active %}ok{% else %}pending{% endif %}\">{% if host.snmp_active %}SNMP ativo{% else %}Configurar{% endif %}</span>
                        </div>
                        <div class=\"meta\">
                            <span>{{ host.ip_address }}</span>
                            <span>{{ host.host_group or 'Sem grupo' }}</span>
                        </div>
                        <div class=\"meta\">
                            <span>{{ host.template }}</span>
                            <span>{{ host.snmp_version|upper }}</span>
                        </div>
                        {% if host.tags %}
                        <div class=\"tags\">
                            {% for tag in host.tags %}
                            <span>{{ tag }}</span>
                            {% endfor %}
                        </div>
                        {% endif %}
                        <small style=\"color:var(--text-secondary);\">{{ host.created_at }}</small>
                    </article>
                    {% endfor %}
                </div>
                {% else %}
                <div class=\"empty-state\">Nenhum host cadastrado ainda. Use o botão acima para iniciar a checklist.</div>
                {% endif %}
            </section>

            <section class=\"panels\">
                <article class=\"panel\">
                    <h2>Recursos monitorados</h2>
                    <ul class=\"list-simple\">
                        {% for item in recursos %}
                        <li>{{ item }}</li>
                        {% endfor %}
                    </ul>
                </article>
                <article class=\"panel\">
                    <h2>Equipamentos previstos</h2>
                    <ul class=\"list-simple\">
                        {% for item in equipamentos %}
                        <li>{{ item }}</li>
                        {% endfor %}
                    </ul>
                </article>
            </section>
        </main>
    </div>
</body>
</html>
"""


LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Monitoramento · Login</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600&display=swap');
        :root {
            --bg: #020617;
            --panel: rgba(15, 23, 42, 0.9);
            --border: rgba(148, 163, 184, 0.35);
            --accent: #4ade80;
            --text: #f8fafc;
            --muted: #94a3b8;
        }
        * {
            box-sizing: border-box;
            font-family: 'Space Grotesk', 'Segoe UI', sans-serif;
        }
        body {
            min-height: 100vh;
            margin: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            background: radial-gradient(circle at top, #0f172a 0, var(--bg) 60%, #000 100%);
            color: var(--text);
            padding: 32px 16px;
        }
        .card {
            width: min(420px, 100%);
            background: var(--panel);
            border-radius: 28px;
            border: 1px solid var(--border);
            padding: 32px;
            display: flex;
            flex-direction: column;
            gap: 18px;
            box-shadow: 0 30px 80px rgba(2, 6, 23, 0.9);
        }
        h1 {
            font-size: 1.5rem;
            margin: 0;
        }
        p {
            margin: 0;
            color: var(--muted);
            line-height: 1.5;
        }
        label {
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: var(--muted);
        }
        input {
            width: 100%;
            padding: 12px 14px;
            border-radius: 16px;
            border: 1px solid var(--border);
            background: rgba(2, 6, 23, 0.4);
            color: var(--text);
            font-size: 1rem;
        }
        .field {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }
        button {
            margin-top: 8px;
            width: 100%;
            padding: 14px;
            border-radius: 18px;
            border: none;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            background: linear-gradient(135deg, #22c55e, #16a34a);
            color: #03120a;
            cursor: pointer;
        }
        .alert {
            padding: 12px 14px;
            border-radius: 14px;
            border: 1px solid rgba(248, 113, 113, 0.4);
            background: rgba(248, 113, 113, 0.1);
            color: #fecaca;
            font-size: 0.9rem;
        }
        small {
            color: var(--muted);
        }
    </style>
</head>
<body>
    <div class="card">
        <div>
            <div style="display:flex;align-items:center;gap:8px;letter-spacing:0.2em;text-transform:uppercase;color:var(--muted);font-size:0.75rem;">
                <span style="width:10px;height:10px;border-radius:999px;background:var(--accent);"></span>
                Monitor Hub
            </div>
            <h1>Acesse o painel</h1>
            <p>Utilize as credenciais definidas em <strong>users.yml</strong> ou exportadas por variáveis de ambiente para liberar o hub de monitoramento.</p>
        </div>

        {% if error %}
        <div class="alert">{{ error }}</div>
        {% endif %}

        <form method="post">
            {% if next_url %}
            <input type="hidden" name="next" value="{{ next_url }}" />
            {% endif %}
            <div class="field">
                <label for="username">Usuário</label>
                <input id="username" name="username" type="text" placeholder="admin" required autofocus />
            </div>
            <div class="field">
                <label for="password">Senha</label>
                <input id="password" name="password" type="password" placeholder="••••••" required />
            </div>
            <button type="submit">Entrar</button>
        </form>

        <small>Precisa de ajuda? Consulte docs/SETUP.md para o passo a passo.</small>
    </div>
</body>
</html>
"""


app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET', 'monitor-secret')

BASE_DIR = Path(__file__).resolve().parent
USERS_FILE = BASE_DIR / 'users.yml'


def _load_user_store():
    if not USERS_FILE.exists():
        return []
    with open(USERS_FILE, 'r', encoding='utf-8') as stream:
        data = yaml.safe_load(stream) or {}
    return data.get('users', [])


def _get_env_credentials():
    env_user = os.getenv('MONITOR_ADMIN_USER') or os.getenv('MONITOR_USER')
    env_password = os.getenv('MONITOR_ADMIN_PASSWORD') or os.getenv('MONITOR_PASSWORD')
    if env_user and env_password:
        return [{"username": env_user, "password": env_password}]
    return []


def _credential_pool():
    records = {}
    for record in _load_user_store():
        username = str(record.get('username', '')).strip()
        if not username:
            continue
        records[username] = str(record.get('password', ''))
    for item in _get_env_credentials():
        username = str(item.get('username', '')).strip()
        if not username:
            continue
        records[username] = str(item.get('password', ''))
    return [{"username": user, "password": pwd} for user, pwd in records.items()]


def _verify_password(stored_password: str, provided_password: str) -> bool:
    if not stored_password:
        return False
    if stored_password.startswith(('pbkdf2:', 'scrypt:', 'sha256$')):
        try:
            return check_password_hash(stored_password, provided_password)
        except ValueError:
            return False
    return stored_password == provided_password


def _authenticate(username: str, password: str) -> bool:
    username = username.strip()
    for record in _credential_pool():
        if record['username'] == username and _verify_password(record.get('password', ''), password):
            return True
    return False


def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not session.get('auth_user'):
            next_target = request.path if request.method == 'GET' else url_for('index')
            return redirect(url_for('login', next=next_target))
        return view_func(*args, **kwargs)

    return wrapped_view


def _status_from_percent(value: float, ok: float, warn: float) -> str:
    if value < ok:
        return 'ok'
    if value < warn:
        return 'warning'
    return 'critical'


def _collect_local_status():
    cpu_percent = psutil.cpu_percent(interval=0.3)
    mem = psutil.virtual_memory()
    disk_percent = 0.0
    disk_path = os.getenv('MONITOR_DISK_PATH') or os.path.abspath(os.sep)
    try:
        disk_percent = psutil.disk_usage(disk_path).percent
    except PermissionError:
        for part in psutil.disk_partitions():
            try:
                disk_percent = max(disk_percent, psutil.disk_usage(part.mountpoint).percent)
            except PermissionError:
                continue

    return {
        "cpu_percent": cpu_percent,
        "mem_percent": mem.percent,
        "disk_percent": disk_percent,
        "cpu_status": _status_from_percent(cpu_percent, ok=60, warn=80),
        "memory_status": _status_from_percent(mem.percent, ok=70, warn=85),
        "disk_status": _status_from_percent(disk_percent, ok=70, warn=90),
    }


NAV_ITEMS = [
    {"key": "dashboard", "endpoint": "index", "label": "Dashboard", "icon": "🏠"},
    {"key": "overview", "endpoint": "overview", "label": "Infraestrutura", "icon": "🛰️"},
    {"key": "servers", "endpoint": "servers", "label": "Servidores", "icon": "🖥️"},
    {"key": "metrics", "endpoint": "metrics", "label": "API /metrics", "icon": "🧪"},
    {"key": "checklist", "endpoint": "checklist", "label": "Checklist", "icon": "✅"},
    {"key": "demo", "endpoint": "demo_mikrotik_view", "label": "Demo Mikrotik", "icon": "⚡"},
    {"key": "logout", "endpoint": "logout", "label": "Sair", "icon": "🚪"},
]


HOST_REGISTRY = []


def _build_nav_links(active_key: str):
    links = []
    for item in NAV_ITEMS:
        links.append({
            "label": item['label'],
            "icon": item['icon'],
            "url": url_for(item['endpoint']),
            "active": item['key'] == active_key,
        })
    return links


def _split_tags(raw_tags):
    if not raw_tags:
        return []
    return [tag.strip() for tag in raw_tags.split(',') if tag.strip()]


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('auth_user'):
        return redirect(url_for('index'))

    error = None
    requested_next = request.values.get('next', '')

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if _authenticate(username, password):
            session['auth_user'] = username
            session['last_login'] = datetime.now().strftime('%d/%m/%Y %H:%M')
            target = requested_next if requested_next.startswith('/') else url_for('index')
            return redirect(target)

        error = 'Credenciais inválidas. Verifique usuário e senha.'

    return render_template_string(
        LOGIN_TEMPLATE,
        error=error,
        next_url=requested_next,
    )


@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    action_tiles = [
        {
            "title": "Infraestrutura",
            "description": "Entenda integrações, recursos monitorados e pendências de rollout.",
            "icon": "🛰️",
            "url": url_for('overview'),
        },
        {
            "title": "Servidores",
            "description": "Cadastre hosts SNMP (Mikrotik, switches, DC) com templates e grupos.",
            "icon": "🖥️",
            "url": url_for('servers'),
        },
        {
            "title": "Checklist",
            "description": "Acompanhe o plano de monitoração e valide o escopo antes de publicar.",
            "icon": "🗂️",
            "url": url_for('checklist'),
        },
        {
            "title": "Demo Mikrotik",
            "description": "Mostre para stakeholders como serão os dashboards de rede.",
            "icon": "⚡",
            "url": url_for('demo_mikrotik_view'),
        },
        {
            "title": "API /metrics",
            "description": "Documentação viva dos endpoints REST que suportam integrações.",
            "icon": "🧩",
            "url": url_for('metrics'),
        },
    ]

    config_steps = [
        {
            "label": "Passo 01",
            "title": "Credenciais e times",
            "description": "Configure usuários, políticas e secret keys antes de liberar acesso compartilhado.",
            "tags": ["Admin", "Segurança"],
        },
        {
            "label": "Passo 02",
            "title": "Integrações core",
            "description": "Associe Zabbix, Grafana e outros coletores verificando o endpoint /metrics.",
            "tags": ["Zabbix", "Grafana"],
        },
        {
            "label": "Passo 03",
            "title": "Validação e demos",
            "description": "Utilize a demo Mikrotik e o checklist para aprovar onboarding com stakeholders.",
            "tags": ["QA", "Stakeholders"],
        },
    ]

    system_highlights = [
        {
            "label": "Onboarding",
            "title": "Usuários ilimitados",
            "description": "Perfis independentes para cada time (NOC, operações, sucesso) com controle centralizado em users.yml ou variáveis de ambiente.",
        },
        {
            "label": "Integrações",
            "title": "Stack pronta",
            "description": "Docker-compose com Zabbix, Grafana e monitor Python para acelerar prova de conceito em minutos.",
        },
        {
            "label": "APIs",
            "title": "Endpoints documentados",
            "description": "Acesse /metrics, /health e futuros webhooks para embutir alertas ou sincronizar com sistemas externos.",
        },
    ]

    status_notes = [
        {
            "topic": "Autenticação",
            "value": "Ativa",
            "detail": "Login obrigatório antes de qualquer módulo, com suporte a hash do Werkzeug.",
        },
        {
            "topic": "Configuração",
            "value": "Arquivo + env",
            "detail": "Variáveis em .env e arquivo users.yml centralizam credenciais e parâmetros.",
        },
        {
            "topic": "Integrações",
            "value": "Zabbix / Grafana",
            "detail": "Containers e endpoints já preparados para apontar dados reais.",
        },
    ]

    roadmap_items = [
        {"item": "Central de alertas e notificações", "status": "Em design"},
        {"item": "Dashboards multi-tenant", "status": "Backlog"},
        {"item": "Provisionamento automático de sites", "status": "Pesquisa"},
    ]

    nav_links = _build_nav_links('dashboard')
    docs_hint = "Consulte docs/SETUP.md e docs/ARCHITECTURE.md para entender a stack completa."

    return render_template_string(
        HOME_TEMPLATE,
        user_name=session.get('auth_user', 'Operador'),
        action_tiles=action_tiles,
        config_steps=config_steps,
        system_highlights=system_highlights,
        status_notes=status_notes,
        roadmap_items=roadmap_items,
        docs_hint=docs_hint,
        nav_links=nav_links,
        overview_url=url_for('overview'),
        demo_url=url_for('demo_mikrotik_view'),
        last_refresh=datetime.now().strftime('%d/%m/%Y %H:%M'),
    )


@app.route('/servers', methods=['GET', 'POST'])
@login_required
def servers():
    nav_links = _build_nav_links('servers')
    snmp_versions = ['v2c', 'v3']
    templates = [
        'Template MikroTik SNMP',
        'Template Generic SNMP Interfaces',
        'Template Core Router KPIs',
    ]
    host_groups = [
        {"name": "Backbone", "description": "Core e agregadores"},
        {"name": "Edge", "description": "Bordas e CPEs"},
        {"name": "Datacenter", "description": "Servidores críticos"},
    ]

    default_form = {
        "host_name": "",
        "ip_address": "",
        "host_group": "",
        "template": "",
        "snmp_version": "v2c",
        "community": "public",
        "polling": "60",
        "tags": "",
        "notes": "",
    }
    form_state = {key: request.form.get(key, default) for key, default in default_form.items()}
    message = None

    if request.method == 'POST':
        host_label = form_state.get('host_name') or 'Host sem nome'
        ip_label = form_state.get('ip_address', 'interface não informada')
        host_record = {
            "host_name": host_label,
            "ip_address": ip_label,
            "host_group": form_state.get('host_group', ''),
            "template": form_state.get('template', ''),
            "snmp_version": form_state.get('snmp_version', 'v2c'),
            "community": form_state.get('community', ''),
            "polling": form_state.get('polling', '60'),
            "tags": _split_tags(form_state.get('tags', '')),
            "notes": form_state.get('notes', ''),
            "snmp_active": bool(form_state.get('community')),
            "created_at": datetime.now().strftime('%d/%m/%Y %H:%M'),
        }
        HOST_REGISTRY.insert(0, host_record)
        if len(HOST_REGISTRY) > 60:
            del HOST_REGISTRY[60:]

        message = f"{host_label} configurado para coleta SNMP em {ip_label}."
        form_state = default_form.copy()

    server_profiles = [
        {
            "name": "CCR / Mikrotik",
            "description": "Mapeia CPU, memória, interfaces óticas/eléctricas, BGP e PPPoE usando SNMP v2c.",
            "template": "Template MikroTik SNMP",
        },
        {
            "name": "Switch L2/L3",
            "description": "Descoberta automática de portas, status, MAC e NetFlow.",
            "template": "Template Generic SNMP Interfaces",
        },
        {
            "name": "Infra DC",
            "description": "Monitora uso de CPU, disco, sensores ambientais e energia.",
            "template": "Template Core Router KPIs",
        },
    ]

    return render_template_string(
        SERVERS_TEMPLATE,
        user_name=session.get('auth_user', 'Operador'),
        nav_links=nav_links,
        last_refresh=datetime.now().strftime('%d/%m/%Y %H:%M'),
        message=message,
        form_state=form_state,
        snmp_versions=snmp_versions,
        templates=templates,
        host_groups=host_groups,
        server_profiles=server_profiles,
    )


@app.route('/overview')
@login_required
def overview():
    items = get_full_checklist()
    recursos = items.get("recursos", [])
    equipamentos = items.get("equipamentos", [])
    stats = _collect_local_status()
    nav_links = _build_nav_links('overview')

    return render_template_string(
        OVERVIEW_TEMPLATE,
        user_name=session.get('auth_user', 'Operador'),
        nav_links=nav_links,
        stats=stats,
        recursos=recursos,
        equipamentos=equipamentos,
        last_refresh=datetime.now().strftime('%d/%m/%Y %H:%M'),
    )


@app.route('/metrics')
@login_required
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
@login_required
def checklist():
    items = get_full_checklist()
    hosts = HOST_REGISTRY.copy()
    recursos = items.get('recursos', [])
    equipamentos = items.get('equipamentos', [])
    total_hosts = len(hosts)
    snmp_active = sum(1 for host in hosts if host.get('snmp_active'))
    inactive = total_hosts - snmp_active
    group_names = sorted({host.get('host_group') for host in hosts if host.get('host_group')})
    group_detail = ', '.join(group_names[:3]) if group_names else 'Defina grupos nos cadastros'
    if len(group_names) > 3:
        group_detail += f" +{len(group_names) - 3}"

    summary_stats = [
        {
            "label": "Hosts cadastrados",
            "value": total_hosts,
            "detail": "Prontos para checklist" if total_hosts else "Aguardando cadastros",
        },
        {
            "label": "SNMP ativos",
            "value": snmp_active,
            "detail": f"{inactive} pendente" if total_hosts else "Configure credenciais",
        },
        {
            "label": "Grupos lógicos",
            "value": len(group_names),
            "detail": group_detail,
        },
    ]

    return render_template_string(
        CHECKLIST_TEMPLATE,
        user_name=session.get('auth_user', 'Operador'),
        nav_links=_build_nav_links('checklist'),
        last_refresh=datetime.now().strftime('%d/%m/%Y %H:%M'),
        summary_stats=summary_stats,
        hosts=hosts,
        recursos=recursos,
        equipamentos=equipamentos,
        servers_url=url_for('servers'),
    )


@app.route('/api/checklist')
@login_required
def checklist_api():
    payload = get_full_checklist()
    payload['hosts'] = HOST_REGISTRY
    return jsonify(payload)


@app.route('/health')
def health():
    return jsonify({"status": "ok"})


@app.route('/config', methods=['GET'])
@login_required
def get_config():
    cfg_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if not os.path.exists(cfg_path):
        return jsonify({"error": ".env not found"}), 404
    with open(cfg_path) as f:
        content = f.read()
    return jsonify({"env": content})


@app.route('/demo/mikrotik')
@login_required
def demo_mikrotik():
    demo = {
        "device": {
            "vendor": "MikroTik",
            "model": "CCR1036-8G-2S+",
            "hostname": "core-border-01",
            "os_version": "RouterOS 7.14",
            "serial": "ABCDE12345",
            "uptime": "12d 03:41:22",
        },
        "interfaces": {
            "opticas": [
                {
                    "name": "sfp-sfpplus1",
                    "description": "Uplink DC-A",
                    "rx_dbm": -18.2,
                    "tx_dbm": -1.5,
                    "speed": "10G",
                    "status": "up",
                },
                {
                    "name": "sfp-sfpplus2",
                    "description": "Uplink DC-B",
                    "rx_dbm": -19.0,
                    "tx_dbm": -1.8,
                    "speed": "10G",
                    "status": "up",
                },
            ],
            "eletricas": [
                {
                    "name": "ether1",
                    "description": "Cliente corporativo A",
                    "speed": "1G",
                    "status": "up",
                },
                {
                    "name": "ether2",
                    "description": "Cliente corporativo B",
                    "speed": "1G",
                    "status": "down",
                },
            ],
        },
        "cpu": {
            "cores": 36,
            "usage_percent": 42.3,
        },
        "memoria": {
            "total_mb": 8192,
            "used_mb": 5120,
            "free_mb": 3072,
            "usage_percent": 62.5,
        },
        "disco": {
            "total_gb": 16,
            "used_gb": 9.5,
            "free_gb": 6.5,
            "usage_percent": 59.4,
        },
        "energia": {
            "inputs": [
                {"name": "PSU1", "status": "ok", "voltage": 48.1},
                {"name": "PSU2", "status": "ok", "voltage": 47.9},
            ],
            "gbics": [
                {"port": "sfp-sfpplus1", "vendor": "FS", "serial": "FS123456", "temp_c": 38.2},
                {"port": "sfp-sfpplus2", "vendor": "Huawei", "serial": "HW987654", "temp_c": 39.0},
            ],
        },
        "trafego": {
            "total_in_mbps": 920.4,
            "total_out_mbps": 873.2,
            "interfaces_top": [
                {"name": "sfp-sfpplus1", "in_mbps": 450.2, "out_mbps": 430.1},
                {"name": "sfp-sfpplus2", "in_mbps": 320.0, "out_mbps": 310.0},
                {"name": "ether1", "in_mbps": 90.0, "out_mbps": 80.0},
            ],
        },
        "netflow": {
            "export_enabled": True,
            "collector_ip": "10.10.10.10",
            "collector_port": 2055,
            "flows_per_second": 13250,
        },
        "neighbors": {
            "lldp": [
                {"local_interface": "sfp-sfpplus1", "neighbor": "core-dc-a", "port": "Ethernet1/1"},
                {"local_interface": "sfp-sfpplus2", "neighbor": "core-dc-b", "port": "Ethernet1/1"},
            ],
        },
        "arp": [
            {"ip": "10.0.0.10", "mac": "00:11:22:33:44:55", "interface": "bridge-pppoe"},
            {"ip": "10.0.0.11", "mac": "00:11:22:33:44:66", "interface": "bridge-pppoe"},
        ],
        "pppoe_users": [
            {"user": "cli001", "ip": "10.0.0.10", "uptime": "01:22:10", "download_gb": 12.4, "upload_gb": 1.2},
            {"user": "cli002", "ip": "10.0.0.11", "uptime": "00:45:03", "download_gb": 4.3, "upload_gb": 0.5},
        ],
        "bgp": {
            "asn_local": 65001,
            "peers_up": 3,
            "peers_down": 1,
            "peers": [
                {"peer": "ISP-A", "asn": 64510, "state": "established", "prefixes_received": 650000},
                {"peer": "ISP-B", "asn": 64520, "state": "established", "prefixes_received": 650000},
                {"peer": "TRANSIT-C", "asn": 64530, "state": "idle", "prefixes_received": 0},
                {"peer": "IX-BRASIL", "asn": 26162, "state": "established", "prefixes_received": 120000},
            ],
        },
        "ospf": {
            "areas": [
                {"id": "0.0.0.0", "name": "backbone", "neighbors": 5},
                {"id": "0.0.0.1", "name": "clientes", "neighbors": 12},
            ],
            "interfaces": [
                {"name": "loopback1", "state": "loopback"},
                {"name": "vlan100", "state": "point-to-point"},
            ],
        },
        "vlans": [
            {"id": 10, "name": "CORPORATIVO", "interfaces": ["bridge-core"]},
            {"id": 20, "name": "PPPoE-ACESSO", "interfaces": ["bridge-pppoe"]},
            {"id": 100, "name": "MGMT", "interfaces": ["bridge-mgmt"]},
        ],
    }
    return jsonify(demo)


@app.route('/demo/mikrotik/view')
@login_required
def demo_mikrotik_view():
    # Reutiliza os dados de demo para montar um dashboard simples
    demo = demo_mikrotik().get_json()
    stats = _collect_local_status()

    template = """
    <!DOCTYPE html>
    <html lang=\"pt-br\">
    <head>
        <meta charset=\"UTF-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
        <title>Demo Mikrotik · Monitoramento</title>
        <style>
            :root {
                --bg-main: #020617;
                --bg-card: #020617;
                --bg-soft: #020617;
                --accent: #22c55e;
                --accent-soft: rgba(34, 197, 94, 0.08);
                --text-primary: #e5e7eb;
                --text-secondary: #9ca3af;
                --border-subtle: rgba(148, 163, 184, 0.25);
            }
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
                font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            }
            body {
                min-height: 100vh;
                background: radial-gradient(circle at top, #020617 0, #020617 40%, #000 100%);
                color: var(--text-primary);
                display: flex;
                align-items: stretch;
                justify-content: center;
            }
            .shell {
                max-width: 1280px;
                width: 100%;
                padding: 24px 20px 32px;
            }
            .topbar {
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 16px;
                margin-bottom: 20px;
            }
            .topbar-left {
                display: flex;
                flex-direction: column;
                gap: 4px;
            }
            .label {
                font-size: 0.7rem;
                text-transform: uppercase;
                letter-spacing: 0.16em;
                color: var(--text-secondary);
            }
            h1 {
                font-size: 1.4rem;
                font-weight: 600;
            }
            .breadcrumb {
                font-size: 0.8rem;
                color: var(--text-secondary);
            }
            .btn-back {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 8px 12px;
                border-radius: 999px;
                font-size: 0.8rem;
                color: var(--text-secondary);
                border: 1px solid var(--border-subtle);
                background: rgba(15, 23, 42, 0.7);
                text-decoration: none;
            }
            .btn-back:hover {
                border-color: rgba(148, 163, 184, 0.8);
            }
            .grid {
                display: grid;
                grid-template-columns: minmax(0, 2fr) minmax(0, 3fr);
                gap: 16px;
            }
            @media (max-width: 960px) {
                .grid {
                    grid-template-columns: minmax(0, 1fr);
                }
            }
            .card {
                background: var(--bg-card);
                border-radius: 16px;
                border: 1px solid var(--border-subtle);
                padding: 16px 16px 14px;
                box-shadow: 0 14px 40px rgba(15, 23, 42, 0.9);
            }
            .card-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }
            .card-title {
                font-size: 0.85rem;
                font-weight: 600;
                letter-spacing: 0.12em;
                text-transform: uppercase;
                color: var(--text-secondary);
            }
            .pill {
                font-size: 0.7rem;
                padding: 2px 8px;
                border-radius: 999px;
                border: 1px solid rgba(148, 163, 184, 0.4);
                color: var(--text-secondary);
            }
            .kv-list {
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 8px 12px;
                font-size: 0.85rem;
            }
            .kv-label {
                color: var(--text-secondary);
                font-size: 0.78rem;
            }
            .kv-value {
                font-weight: 500;
            }
            .metric-row {
                display: grid;
                grid-template-columns: 70px minmax(0, 1fr) 52px;
                gap: 8px;
                align-items: center;
                font-size: 0.8rem;
            }
            .metric-bar {
                height: 6px;
                border-radius: 999px;
                background: #020617;
                overflow: hidden;
            }
            .metric-bar-fill {
                height: 100%;
                border-radius: inherit;
                transition: width 0.4s ease;
            }
            .metric-bar-fill.ok { background: #22c55e; }
            .metric-bar-fill.warning { background: #eab308; }
            .metric-bar-fill.critical { background: #ef4444; }
            .metric-badge {
                font-size: 0.7rem;
                text-align: right;
                color: var(--text-secondary);
            }
            .table-like {
                width: 100%;
                border-collapse: collapse;
                font-size: 0.78rem;
                margin-top: 4px;
            }
            .table-like thead {
                color: var(--text-secondary);
            }
            .table-like th,
            .table-like td {
                padding: 4px 6px;
                border-bottom: 1px solid rgba(15, 23, 42, 0.9);
            }
            .table-like tbody tr:hover {
                background: rgba(15, 23, 42, 0.9);
            }
            .pill-status {
                display: inline-flex;
                align-items: center;
                gap: 4px;
                padding: 2px 6px;
                border-radius: 999px;
                font-size: 0.7rem;
            }
            .pill-status.ok {
                background: rgba(34, 197, 94, 0.15);
                color: #4ade80;
            }
            .pill-status.down {
                background: rgba(248, 113, 113, 0.12);
                color: #fb7185;
            }
        </style>
    </head>
    <body>
        <main class=\"shell\">
            <header class=\"topbar\">
                <div class=\"topbar-left\">
                    <span class=\"label\">Demo · Mikrotik</span>
                    <h1>{{ demo.device.hostname }} · {{ demo.device.model }}</h1>
                    <div class=\"breadcrumb\">Monitoramento / Demo / Mikrotik</div>
                </div>
                <a href=\"/\" class=\"btn-back\">⟵ Voltar para visão geral</a>
            </header>

            <section class=\"grid\">
                <article class=\"panel\">
                    <h2>Checklist operacional</h2>
                    <ul class=\"list-simple\">
                        <li>
                            <span>Estado geral do host</span>
                            <strong>{{ stats.cpu_status|capitalize }}</strong>
                        </li>
                        <li>
                            <span>Memória em uso</span>
                            <strong>{{ '%.1f'|format(stats.mem_percent) }}%</strong>
                        </li>
                        <li>
                            <span>Capacidade em disco</span>
                            <strong>{{ '%.1f'|format(stats.disk_percent) }}%</strong>
                        </li>
                    </ul>
                    <div class=\"highlight\">Revise estes indicadores rápidos antes de ajustar novas integrações ou liberar funcionalidades.</div>
                </article>
                        <div>
                            <div class=\"kv-label\">Versão</div>
                            <div class=\"kv-value\">{{ demo.device.os_version }}</div>
                        </div>
                        <div>
                            <div class=\"kv-label\">Serial</div>
                            <div class=\"kv-value\">{{ demo.device.serial }}</div>
                        </div>
                        <div>
                            <div class=\"kv-label\">Uptime</div>
                            <div class=\"kv-value\">{{ demo.device.uptime }}</div>
                        </div>
                    </div>

                    <div style=\"margin-top:14px; display:flex; flex-direction:column; gap:6px;\">
                        <div class=\"kv-label\" style=\"margin-bottom:2px;\">Recursos principais</div>

                        <div class=\"metric-row\">
                            <div class=\"kv-label\">CPU</div>
                            <div class=\"metric-bar\">
                                <div class=\"metric-bar-fill {{ cpu_class }}\" style=\"width: {{ demo.cpu.usage_percent }}%;\"></div>
                            </div>
                            <div class=\"metric-badge\">{{ '%.1f'|format(demo.cpu.usage_percent) }}%</div>
                        </div>

                        <div class=\"metric-row\">
                            <div class=\"kv-label\">Memória</div>
                            <div class=\"metric-bar\">
                                <div class=\"metric-bar-fill {{ mem_class }}\" style=\"width: {{ demo.memoria.usage_percent }}%;\"></div>
                            </div>
                            <div class=\"metric-badge\">{{ '%.1f'|format(demo.memoria.usage_percent) }}%</div>
                        </div>

                        <div class=\"metric-row\">
                            <div class=\"kv-label\">Disco</div>
                            <div class=\"metric-bar\">
                                <div class=\"metric-bar-fill {{ disk_class }}\" style=\"width: {{ demo.disco.usage_percent }}%;\"></div>
                            </div>
                            <div class=\"metric-badge\">{{ '%.1f'|format(demo.disco.usage_percent) }}%</div>
                        </div>
                    </div>
                </article>

                <article class=\"card\">
                    <header class=\"card-header\">
                        <h2 class=\"card-title\">Tráfego e sessões</h2>
                        <span class=\"pill\">Interfaces ativas</span>
                    </header>
                    <div class=\"kv-list\" style=\"margin-bottom:8px;\">
                        <div>
                            <div class=\"kv-label\">Tráfego total in</div>
                            <div class=\"kv-value\">{{ '%.1f'|format(demo.trafego.total_in_mbps) }} Mbps</div>
                        </div>
                        <div>
                            <div class=\"kv-label\">Tráfego total out</div>
                            <div class=\"kv-value\">{{ '%.1f'|format(demo.trafego.total_out_mbps) }} Mbps</div>
                        </div>
                        <div>
                            <div class=\"kv-label\">Usuários PPPoE</div>
                            <div class=\"kv-value\">{{ demo.pppoe_users|length }}</div>
                        </div>
                        <div>
                            <div class=\"kv-label\">Peers BGP up</div>
                            <div class=\"kv-value\">{{ demo.bgp.peers_up }} / {{ demo.bgp.peers|length }}</div>
                        </div>
                    </div>

                    <table class=\"table-like\">
                        <thead>
                            <tr>
                                <th>Interface</th>
                                <th>In</th>
                                <th>Out</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for iface in demo.trafego.interfaces_top %}
                            <tr>
                                <td>{{ iface.name }}</td>
                                <td>{{ '%.1f'|format(iface.in_mbps) }} Mbps</td>
                                <td>{{ '%.1f'|format(iface.out_mbps) }} Mbps</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </article>
            </section>

            <section class=\"grid\" style=\"margin-top:16px;\">
                <article class=\"card\">
                    <header class=\"card-header\">
                        <h2 class=\"card-title\">Interfaces ópticas</h2>
                        <span class=\"pill\">{{ demo.interfaces.opticas|length }} portas</span>
                    </header>
                    <table class=\"table-like\">
                        <thead>
                            <tr>
                                <th>Porta</th>
                                <th>Descrição</th>
                                <th>RX (dBm)</th>
                                <th>TX (dBm)</th>
                                <th>Vel.</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for it in demo.interfaces.opticas %}
                            <tr>
                                <td>{{ it.name }}</td>
                                <td>{{ it.description }}</td>
                                <td>{{ '%.1f'|format(it.rx_dbm) }}</td>
                                <td>{{ '%.1f'|format(it.tx_dbm) }}</td>
                                <td>{{ it.speed }}</td>
                                <td>
                                    <span class=\"pill-status {{ 'ok' if it.status == 'up' else 'down' }}\">{{ it.status }}</span>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </article>

                <article class=\"card\">
                    <header class=\"card-header\">
                        <h2 class=\"card-title\">Interfaces elétricas</h2>
                        <span class=\"pill\">{{ demo.interfaces.eletricas|length }} portas</span>
                    </header>
                    <table class=\"table-like\">
                        <thead>
                            <tr>
                                <th>Porta</th>
                                <th>Descrição</th>
                                <th>Vel.</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for it in demo.interfaces.eletricas %}
                            <tr>
                                <td>{{ it.name }}</td>
                                <td>{{ it.description }}</td>
                                <td>{{ it.speed }}</td>
                                <td>
                                    <span class=\"pill-status {{ 'ok' if it.status == 'up' else 'down' }}\">{{ it.status }}</span>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </article>
            </section>
        </main>
    </body>
    </html>
    """

    def status_class(percent, ok, warn):
        if percent < ok:
            return "ok"
        if percent < warn:
            return "warning"
        return "critical"

    cpu_class = status_class(demo["cpu"]["usage_percent"], 60, 80)
    mem_class = status_class(demo["memoria"]["usage_percent"], 70, 85)
    disk_class = status_class(demo["disco"]["usage_percent"], 70, 90)

    return render_template_string(
        template,
        demo=demo,
        cpu_class=cpu_class,
        mem_class=mem_class,
        disk_class=disk_class,
        stats=stats,
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
