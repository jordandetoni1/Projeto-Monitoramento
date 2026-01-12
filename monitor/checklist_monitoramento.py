RECURSOS = [
    "interfaces ópticas e elétricas",
    "CPU",
    "Memória",
    "Disco",
    "Informações de energia (fontes e GBICs)",
    "Uptime",
    "Tráfego de rede",
    "NetFlow",
    "Neighbors interfaces",
    "ARP",
    "Usuários PPPoE",
    "BGP",
    "OSPF",
    "VLANs",
]

EQUIPAMENTOS = [
    "Nobreak",
    "Retificadoras",
    "OLTs (ZTE, Huawei, Nokia, Fiberhome, Parks)",
    "MikroTik (switches, RBs, CCRs)",
    "Huawei (NE8000, S6730, NE20, NE40)",
    "Cisco",
    "UniFi",
    "Antenas Wi-Fi",
    "AP routers",
    "Desktops",
    "Linux/Windows servers",
    "Câmeras",
]


def get_recursos():
    return RECURSOS


def get_equipamentos():
    return EQUIPAMENTOS


def get_full_checklist():
    return {
        "recursos": RECURSOS,
        "equipamentos": EQUIPAMENTOS,
    }
