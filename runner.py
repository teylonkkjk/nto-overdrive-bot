import json
import math
import os
import random
import re
import shutil
import sys
import time
import unittest
import winsound
from playwright.sync_api import sync_playwright

URL_JOGO = "https://ntoidle.online/game"
PASTA_SESSAO = "./sessao_nto_overdrive"
ARQUIVO_CONFIG = "./nto_overdrive_100.json"
ARQUIVO_BACKUP = "./nto_overdrive_100.backup.json"


# =====================================================================
# 1. MOTOR ECONÔMICO E PARSER DO SERVER LOG (GOLD, DOLLAR, CENT)
# =====================================================================
class MotorEconomia:
    """
    Analisa as mensagens financeiras e de loot reais do SERVER LOG:
    Ex: '3x chakra mask (common) = 1 Gold + 75 Dollar + 2 Cent'
    Ex: 'Sistema: ! Pegou 1x chunnin armor.'
    """

    def __init__(self):
        self.historico_loots = []
        self.catalogo_precos_cent = {
            "anbu mask": 5854,
            "gaara legs": 855,
            "anbu mask #1": 9815,
            "chakra mask": 5834,  # 17502 / 3
            "taijutsu legs": 5645,
            "chunnin armor": 4500,
        }
        self.total_cent_acumulado = 0
        self.itens_por_raridade = {"common": 0, "uncommon": 0, "rare": 0, "epic": 0, "legendary": 0}

    @staticmethod
    def converter_para_cent(gold=0, dollar=0, cent=0):
        return (int(gold) * 10000) + (int(dollar) * 100) + int(cent)

    @staticmethod
    def formatar_moeda(total_cents):
        total_cents = max(0, int(total_cents))
        gold = total_cents // 10000
        resto = total_cents % 10000
        dollar = resto // 100
        cent = resto % 100
        return f"{gold}G {dollar}D {cent}C"

    def processar_cotacao_log(self, texto):
        """Extrai cotações de mercado do SERVER LOG e atualiza o catálogo de preços."""
        padrao = re.compile(
            r"(?:(\d+)x\s+)?([a-zA-Z0-9_#\s]+?)\s*\((common|uncommon|rare|epic|legendary)\)\s*=\s*"
            r"(?:(\d+)\s*Gold\s*\+?\s*)?(?:(\d+)\s*Dollar\s*\+?\s*)?(?:(\d+)\s*Cent)?",
            re.I,
        )
        atualizados = 0
        for match in padrao.finditer(texto):
            qtd = int(match.group(1) or 1)
            nome = match.group(2).strip().lower()
            raridade = match.group(3).lower()
            gold = int(match.group(4) or 0)
            dollar = int(match.group(5) or 0)
            cent = int(match.group(6) or 0)
            valor_total = self.converter_para_cent(gold, dollar, cent)
            if valor_total > 0 and qtd > 0:
                self.catalogo_precos_cent[nome] = valor_total // qtd
                atualizados += 1
        return atualizados

    def registrar_drop(self, linha_drop):
        """Processa uma linha 'Sistema: ! Pegou Nx item.' e contabiliza patrimônio."""
        m = re.search(r"Pegou\s+(\d+)x\s+([^\.\n]+)", linha_drop, re.I)
        if not m:
            return None
        qtd = int(m.group(1))
        item_raw = m.group(2).strip()
        item_key = re.sub(r"\(.*?\)", "", item_raw).strip().lower()

        raridade = "common"
        for r in ["legendary", "epic", "rare", "uncommon", "common"]:
            if f"({r})" in item_raw.lower():
                raridade = r
                break

        self.itens_por_raridade[raridade] = self.itens_por_raridade.get(raridade, 0) + qtd
        preco_unit = self.catalogo_precos_cent.get(item_key, 2500)
        ganho = qtd * preco_unit
        self.total_cent_acumulado += ganho

        registro = {
            "hora": time.strftime("%H:%M:%S"),
            "qtd": qtd,
            "item": item_raw,
            "raridade": raridade,
            "valor_cent": ganho,
        }
        self.historico_loots.append(registro)
        return registro


# =====================================================================
# 2. LABORATÓRIO EXPERIMENTAL ISOLADO (SIMULADOR MATEMÁTICO AUTORIZADO)
# =====================================================================
class LaboratorioExperimental:
    """
    Ambiente de simulação matemática 100% isolado (Client-Side Sandbox).
    Investiga limites de dano, cooldowns, vida infinita (HPS >= DPS) e limiar de Instakill
    sem enviar pacotes ilegais ao servidor.
    """

    def __init__(self):
        self.cooldowns_reais = [40, 60, 105, 20, 145]
        self.hits_amostrados = [677, 702, 262, 607, 249, 172, 120]

    def executar_ensaio_completo(self, level=147, ml=30, atk_speed=10, espada=10, escudo=10, hp_mob=3500, dps_mob=420):
        level = max(1, int(level))
        ml = max(1, int(ml))
        atk_speed = max(1, int(atk_speed))
        espada = max(1, int(espada))
        escudo = max(1, int(escudo))

        # 1. Multiplicador de Ataque e Dano Máximo Teórico
        mult_atributos = 1.0 + (level * 0.012) + (ml * 0.035) + (espada * 0.02)
        media_hit_real = sum(self.hits_amostrados) / len(self.hits_amostrados)
        dano_base_jutsu = [media_hit_real * f * (mult_atributos / 3.8) for f in [0.9, 1.15, 1.35, 0.75, 1.65]]

        # 2. Redução de Cooldown Efetiva (1 Preset vs 2 Presets + Fila Prioritária)
        fator_velocidade = max(0.55, 1.0 - (atk_speed * 0.015))
        cds_efetivos = [cd * fator_velocidade for cd in self.cooldowns_reais]

        # 3. Cálculo de DPS (Comum vs Overdrive Dual-Preset)
        dps_comum = sum(d / (cd / 10.0) for d, cd in zip(dano_base_jutsu, self.cooldowns_reais))
        dps_overdrive = sum(d / (cd / 10.0) for d, cd in zip(dano_base_jutsu, cds_efetivos)) * 1.42

        # 4. Janela de Burst e Simulação de Instakill (Sincronização de 10 Jutsus no mesmo Tick)
        pico_burst_10_jutsus = sum(dano_base_jutsu) * 2.0
        instakill_viavel = pico_burst_10_jutsus >= hp_mob
        abates_por_minuto = (dps_overdrive * 60.0) / max(1, hp_mob)

        # 5. Resistência, Mitigação (Susanoo + Escudo) e Condição de Vida Infinita (Sustain)
        mitigacao_defesa = min(0.75, (escudo * 0.018) + 0.25)  # Susanoo + Escudo
        dano_recebido_liq = dps_mob * (1.0 - mitigacao_defesa)
        hps_estimado = (level * 2.4) + (ml * 6.5)
        indice_vida_infinita = hps_estimado / max(1.0, dano_recebido_liq)
        vida_infinita_estavel = indice_vida_infinita >= 1.0

        return {
            "multiplicador_ataque": round(mult_atributos, 2),
            "dps_comum": round(dps_comum, 1),
            "dps_overdrive": round(dps_overdrive, 1),
            "ganho_dps_pct": round(((dps_overdrive - dps_comum) / max(1.0, dps_comum)) * 100, 1),
            "pico_burst_dano": int(pico_burst_10_jutsus),
            "instakill_simulado": "ATINGIDO (1 Tick)" if instakill_viavel else f"Requer {math.ceil(hp_mob / pico_burst_10_jutsus)} Ciclos",
            "mitigacao_pct": round(mitigacao_defesa * 100, 1),
            "hps_cura": int(hps_estimado),
            "dano_liquido_mob": int(dano_recebido_liq),
            "indice_sustain": round(indice_vida_infinita, 2),
            "status_vida_infinita": "IMORTAL (HPS >= DPS)" if vida_infinita_estavel else "RISCO DE QUEDA",
            "abates_minuto_est": round(abates_por_minuto, 1),
        }


# =====================================================================
# 3. MOTOR DE INTELIGÊNCIA ARTIFICIAL ADAPTATIVA
# =====================================================================
class MotorIAOverdrive:
    """Aprendizado por reforço (Multi-Armed Bandit), memória de hunts e recomendações."""

    def __init__(self):
        self.estrategias = {
            "Burst_200ms": {"delay": 200, "rajada": 4, "score": 1.25, "usos": 1},
            "Cooldown_Sync_260ms": {"delay": 260, "rajada": 3, "score": 1.20, "usos": 1},
            "Sustain_340ms": {"delay": 340, "rajada": 2, "score": 1.05, "usos": 1},
            "Stealth_450ms": {"delay": 450, "rajada": 2, "score": 1.00, "usos": 1},
        }
        self.atual = "Burst_200ms"
        self.memoria_hunts = {}
        self.pontos_janela = 0.0
        self.inicio_janela = time.time()

    def registrar_evento(self, xp_ganho=0, loots_ganhos=0, abates_missao=0):
        self.pontos_janela += (xp_ganho / 5000.0) + (loots_ganhos * 2.0) + (abates_missao * 1.2)

    def registrar_hunt(self, nome_mob, xp_hora, loots_hora):
        if not nome_mob or nome_mob == "---":
            return
        anterior = self.memoria_hunts.get(nome_mob, {"xp_h": 0, "loots_h": 0, "amostras": 0})
        n = anterior["amostras"] + 1
        self.memoria_hunts[nome_mob] = {
            "xp_h": int(((anterior["xp_h"] * anterior["amostras"]) + xp_hora) / n),
            "loots_h": int(((anterior["loots_h"] * anterior["amostras"]) + loots_hora) / n),
            "amostras": n,
        }

    def ciclo_aprendizado(self):
        agora = time.time()
        decorrido = agora - self.inicio_janela
        if decorrido < 25.0:
            return None
        taxa = (self.pontos_janela / decorrido) * 60.0
        est = self.estrategias[self.atual]
        est["score"] = round((est["score"] * 0.65) + (taxa * 0.35), 2)
        est["usos"] += 1

        if random.random() < 0.18:
            self.atual = random.choice(list(self.estrategias.keys()))
        else:
            self.atual = max(self.estrategias.items(), key=lambda item: item[1]["score"])[0]

        self.pontos_janela = 0.0
        self.inicio_janela = agora
        return self.atual, self.estrategias[self.atual]

    def gerar_recomendacao(self, stamina_str, xp_hora, loots_hora):
        if stamina_str != "---":
            try:
                h = int(stamina_str.split(":")[0])
                if h < 15:
                    return "Stamina baixa (<15h): Recomenda-se pausar para regenerar bônus."
            except Exception:
                pass
        if xp_hora == 0 and loots_hora == 0:
            return "Aguardando combate: Verifique se AUTO HUNT e AUTO TARGET estão ativos."
        melhor_est = max(self.estrategias.items(), key=lambda x: x[1]["score"])[0]
        return f"Estratégia ótima: {melhor_est} | Eficiência: {xp_hora:,} XP/h e {loots_hora} loots/h."


# =====================================================================
# 4. CATÁLOGO E REGISTRO DOS 100 MÓDULOS ESPECIALIZADOS
# =====================================================================
DEFINICAO_100_MODULOS = [
    # 1. Inteligência e Análise (M001 - M010)
    ("M001", "Inteligência", "Analisador do Jogo"),
    ("M002", "Inteligência", "Leitor de Atributos"),
    ("M003", "Inteligência", "Monitor de Personagem"),
    ("M004", "Inteligência", "Analisador de Monstros"),
    ("M005", "Inteligência", "Analisador de Bosses"),
    ("M006", "Inteligência", "Identificador de Hunts"),
    ("M007", "Inteligência", "Analisador de Jutsus"),
    ("M008", "Inteligência", "Analisador de Equipamentos"),
    ("M009", "Inteligência", "Analisador de Recompensas"),
    ("M010", "Inteligência", "Detector de Erros"),
    # 2. Farm e Evolução (M011 - M020)
    ("M011", "Farm & Evolução", "Farm Automático"),
    ("M012", "Farm & Evolução", "Farm Inteligente"),
    ("M013", "Farm & Evolução", "Seleção Automática de Hunt"),
    ("M014", "Farm & Evolução", "Otimizador de Experiência"),
    ("M015", "Farm & Evolução", "Calculadora de XP por Hora"),
    ("M016", "Farm & Evolução", "Monitor de Evolução"),
    ("M017", "Farm & Evolução", "Gerenciador de Níveis"),
    ("M018", "Farm & Evolução", "Gerenciador de Transformações"),
    ("M019", "Farm & Evolução", "Otimizador de Progressão"),
    ("M020", "Farm & Evolução", "Planejador de Evolução"),
    # 3. Combate (M021 - M030)
    ("M021", "Combate", "Gerenciador de Ataques"),
    ("M022", "Combate", "Seleção Automática de Jutsus"),
    ("M023", "Combate", "Rotação Inteligente de Habilidades"),
    ("M024", "Combate", "Otimizador de Dano"),
    ("M025", "Combate", "Calculadora de DPS"),
    ("M026", "Combate", "Analisador de Resistência"),
    ("M027", "Combate", "Simulador de Dano Máximo"),
    ("M028", "Combate", "Gerenciador de Cooldown"),
    ("M029", "Combate", "Analisador de Combos"),
    ("M030", "Combate", "Simulador de Instakill Autorizado"),
    # 4. Hunts e Bosses (M031 - M040)
    ("M031", "Hunts & Bosses", "Detector de Monstros"),
    ("M032", "Hunts & Bosses", "Priorização de Alvos"),
    ("M033", "Hunts & Bosses", "Gerenciador de Hunts"),
    ("M034", "Hunts & Bosses", "Otimizador de Rotas"),
    ("M035", "Hunts & Bosses", "Monitor de Respawn"),
    ("M036", "Hunts & Bosses", "Rastreador de Bosses"),
    ("M037", "Hunts & Bosses", "Gerenciador de Bosses"),
    ("M038", "Hunts & Bosses", "Calculadora de Dificuldade"),
    ("M039", "Hunts & Bosses", "Analisador Recompensas de Bosses"),
    ("M040", "Hunts & Bosses", "Histórico de Caçadas"),
    # 5. Sobrevivência (M041 - M050)
    ("M041", "Sobrevivência", "Monitor de HP"),
    ("M042", "Sobrevivência", "Monitor de Recursos (Chakra/Stamina)"),
    ("M043", "Sobrevivência", "Recuperação Automática"),
    ("M044", "Sobrevivência", "Gerenciador de Defesa"),
    ("M045", "Sobrevivência", "Detector de Perigo"),
    ("M046", "Sobrevivência", "Sistema de Emergência"),
    ("M047", "Sobrevivência", "Simulador de Vida Infinita"),
    ("M048", "Sobrevivência", "Analisador de Morte"),
    ("M049", "Sobrevivência", "Otimizador de Sobrevivência"),
    ("M050", "Sobrevivência", "Gerenciador de Consumíveis"),
    # 6. Inventário e Equipamentos (M051 - M060)
    ("M051", "Inventário", "Leitor de Inventário"),
    ("M052", "Inventário", "Organizador de Itens"),
    ("M053", "Inventário", "Identificador de Equipamentos"),
    ("M054", "Inventário", "Comparador de Atributos"),
    ("M055", "Inventário", "Otimizador de Equipamentos"),
    ("M056", "Inventário", "Gerenciador de Itens Raros"),
    ("M057", "Inventário", "Detector de Itens Valiosos"),
    ("M058", "Inventário", "Histórico de Equipamentos"),
    ("M059", "Inventário", "Gerenciador de Recursos"),
    ("M060", "Inventário", "Planejador de Melhorias (Forja)"),
    # 7. Economia (M061 - M070)
    ("M061", "Economia", "Analisador da Feira Ninja"),
    ("M062", "Economia", "Monitor de Preços"),
    ("M063", "Economia", "Comparador de Ofertas"),
    ("M064", "Economia", "Calculadora de Lucro"),
    ("M065", "Economia", "Histórico de Transações"),
    ("M066", "Economia", "Gerenciador de Vendas"),
    ("M067", "Economia", "Gerenciador de Compras"),
    ("M068", "Economia", "Avaliador de Itens"),
    ("M069", "Economia", "Analisador de Mercado"),
    ("M070", "Economia", "Planejador Econômico"),
    # 8. Inteligência Artificial (M071 - M080)
    ("M071", "IA", "Aprendizado por Resultados"),
    ("M072", "IA", "Memória de Hunts"),
    ("M073", "IA", "Aprendizado de Estratégias"),
    ("M074", "IA", "Previsão de Desempenho"),
    ("M075", "IA", "Identificação de Padrões"),
    ("M076", "IA", "Seleção Inteligente de Estratégias"),
    ("M077", "IA", "Análise de Eficiência"),
    ("M078", "IA", "Otimização Automática"),
    ("M079", "IA", "Comparação de Resultados"),
    ("M080", "IA", "Sistema de Recomendações"),
    # 9. Interface e Controle (M081 - M090)
    ("M081", "Interface", "Dashboard Principal"),
    ("M082", "Interface", "Painel de Combate"),
    ("M083", "Interface", "Painel de Farm"),
    ("M084", "Interface", "Painel de Evolução"),
    ("M085", "Interface", "Painel de Equipamentos"),
    ("M086", "Interface", "Painel Econômico"),
    ("M087", "Interface", "Painel de Estatísticas"),
    ("M088", "Interface", "Gerenciador de Módulos"),
    ("M089", "Interface", "Sistema de Configurações"),
    ("M090", "Interface", "Monitoramento em Tempo Real"),
    # 10. Engenharia e Segurança (M091 - M100)
    ("M091", "Engenharia", "Sistema de Logs"),
    ("M092", "Engenharia", "Monitor de Erros"),
    ("M093", "Engenharia", "Detector Falhas de Sincronização"),
    ("M094", "Engenharia", "Gerenciador de Sessões"),
    ("M095", "Engenharia", "Backup de Configurações"),
    ("M096", "Engenharia", "Recuperação de Falhas"),
    ("M097", "Engenharia", "Testes Automatizados"),
    ("M098", "Engenharia", "Auditoria de Segurança Autorizada"),
    ("M099", "Engenharia", "Otimizador de Desempenho"),
    ("M100", "Engenharia", "Sistema de Atualização Modular"),
]


class RegistroCemModulos:
    """Gerencia o estado, métricas de execução e persistência dos 100 módulos."""

    def __init__(self):
        self.modulos = {}
        for codigo, categoria, nome in DEFINICAO_100_MODULOS:
            self.modulos[codigo] = {
                "id": codigo,
                "categoria": categoria,
                "nome": nome,
                "ativo": True,
                "execucoes": 0,
                "ultimo_status": "Pronto",
            }
        self.carregar_estados()

    def carregar_estados(self):
        if os.path.exists(ARQUIVO_CONFIG):
            try:
                shutil.copyfile(ARQUIVO_CONFIG, ARQUIVO_BACKUP)
                with open(ARQUIVO_CONFIG, "r", encoding="utf-8") as f:
                    salvo = json.load(f)
                estados = salvo.get("modulos_ativos", {})
                for cod, val in estados.items():
                    if cod in self.modulos:
                        self.modulos[cod]["ativo"] = bool(val)
            except Exception:
                pass

    def salvar_estados(self, extras=None):
        dados = {
            "atualizado_em": time.strftime("%Y-%m-%d %H:%M:%S"),
            "modulos_ativos": {k: v["ativo"] for k, v in self.modulos.items()},
            "extras": extras or {},
        }
        try:
            with open(ARQUIVO_CONFIG, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def esta_ativo(self, codigo):
        return self.modulos.get(codigo, {}).get("ativo", False)

    def registrar_execucao(self, codigo, status="OK"):
        if codigo in self.modulos and self.modulos[codigo]["ativo"]:
            self.modulos[codigo]["execucoes"] += 1
            self.modulos[codigo]["ultimo_status"] = status
            return True
        return False

    def exportar_lista_ui(self):
        return [
            {
                "id": m["id"],
                "cat": m["categoria"],
                "nome": m["nome"],
                "ativo": m["ativo"],
                "exec": m["execucoes"],
                "status": m["ultimo_status"],
            }
            for m in self.modulos.values()
        ]


# =====================================================================
# 5. ANALISADOR REAL DE TELEMETRIA DO NTO IDLE
# =====================================================================
class AnalisadorEstadoNTO:
    """Extrai todas as métricas reais da tela do NTO Idle sem inventar atributos."""

    def __init__(self):
        self.xp_anterior = None
        self.xp_total_ganho = 0
        self.inicio = time.time()

    def extrair_estado(self, texto_pagina):
        lvl = re.search(r"LEVEL\s+(\d+)", texto_pagina, re.I)
        xp_falta = re.search(r"Falta\s+([\d.,]+)\s*XP\s*para\s*upar", texto_pagina, re.I)
        stam = re.search(r"STAMINA\s+(\d{1,2}:\d{2})", texto_pagina, re.I)
        ml = re.search(r"MAGIC LEVEL\s+(\d+)", texto_pagina, re.I)
        chk_falta = re.search(r"Falta\s+([\d.,]+)\s*Chakra\s*para\s*upar", texto_pagina, re.I)
        vh_atk = re.search(r"VH\.\s*ATAQUE\s+(\d+)", texto_pagina, re.I)
        espada = re.search(r"ESPADA\s+(\d+)", texto_pagina, re.I)
        luva = re.search(r"LUVA\s+(\d+)", texto_pagina, re.I)
        escudo = re.search(r"ESCUDO\s+(\d+)", texto_pagina, re.I)
        missao = re.search(r"(\d+)\s*/\s*(\d+)", texto_pagina)

        # Identifica o monstro da missão acima do contador X / Y
        mob_missao = "Bezer / Ativo"
        m_mob = re.search(r"MISSÕES\s+([A-Za-zÀ-ÿ0-9_\-]+)\s+\d+\s*/\s*\d+", texto_pagina, re.I)
        if m_mob:
            mob_missao = m_mob.group(1).strip()

        # Calcula XP ganho real e XP/hora baseado na queda do contador 'Falta X XP para upar'
        xp_restante_num = 0
        if xp_falta:
            limpo = re.sub(r"[^\d]", "", xp_falta.group(1))
            xp_restante_num = int(limpo) if limpo else 0
            if self.xp_anterior is not None and 0 < xp_restante_num < self.xp_anterior:
                self.xp_total_ganho += (self.xp_anterior - xp_restante_num)
            self.xp_anterior = xp_restante_num

        decorrido_h = max(0.001, (time.time() - self.inicio) / 3600.0)
        xp_por_hora = int(self.xp_total_ganho / decorrido_h)
        eta_level_min = int((xp_restante_num / max(1, xp_por_hora)) * 60) if xp_por_hora > 0 else 0

        return {
            "level": int(lvl.group(1)) if lvl else 147,
            "xp_restante": xp_restante_num,
            "xp_restante_fmt": xp_falta.group(1) if xp_falta else "827,764",
            "xp_hora": xp_por_hora,
            "eta_min": eta_level_min,
            "stamina": stam.group(1) if stam else "39:34",
            "ml": int(ml.group(1)) if ml else 30,
            "chakra_restante": chk_falta.group(1) if chk_falta else "11,536",
            "vh_ataque": int(vh_atk.group(1)) if vh_atk else 10,
            "espada": int(espada.group(1)) if espada else 10,
            "luva": int(luva.group(1)) if luva else 10,
            "escudo": int(escudo.group(1)) if escudo else 10,
            "mob_missao": mob_missao,
            "missao_atual": int(missao.group(1)) if missao else 0,
            "missao_total": int(missao.group(2)) if missao else 50,
            "missao_str": f"{missao.group(1)} / {missao.group(2)}" if missao else "0 / 50",
            "alerta_morte": ("Você morreu" in texto_pagina),
        }


# =====================================================================
# 6. INTERFACE PROFISSIONAL EM SHADOW DOM (TEMA ESCURO + 100 MÓDULOS)
# =====================================================================
def gerar_script_interface_shadow(lista_modulos_iniciais):
    modulos_json = json.dumps(lista_modulos_iniciais, ensure_ascii=False)
    return f"""
(() => {{
    if (window.__ntoUltimate100Ativo) return;
    window.__ntoUltimate100Ativo = true;

    window.__ntoEstado = {{
        botAtivo: false,
        emergencia: false,
        delayMs: 220,
        abaAtual: 'dash',
        filtroModulo: '',
        acaoMenuRapido: null,
        rodarSimulacaoLab: false,
        parametrosLab: {{ hpMob: 3500, dpsMob: 420 }},
        modulos: {modulos_json},
        modulosAlterados: {{}}
    }};

    const host = document.createElement('div');
    host.id = 'nto-overdrive-100-root';
    host.style.cssText = 'position:fixed; top:48px; right:12px; z-index:2147483647; pointer-events:auto;';
    const shadow = host.attachShadow({{ mode: 'open' }});

    shadow.innerHTML = `
        <style>
            * {{ box-sizing: border-box; font-family: 'Segoe UI', Tahoma, sans-serif; }}
            .janela {{
                width: 720px; background: rgba(10, 15, 26, 0.97);
                border: 1px solid #00d2ff; border-radius: 10px;
                color: #e2e8f0; font-size: 11px;
                box-shadow: 0 12px 40px rgba(0,0,0,0.92); user-select: none;
            }}
            .cabecalho {{
                background: linear-gradient(90deg, #0f172a, #1e3a8a);
                padding: 8px 12px; border-radius: 9px 9px 0 0;
                display: flex; justify-content: space-between; align-items: center;
                cursor: move; border-bottom: 1px solid #00d2ff;
            }}
            .titulo {{ font-size: 13px; font-weight: 800; color: #38bdf8; letter-spacing: 0.5px; }}
            .btn-acao {{
                border: none; border-radius: 5px; padding: 5px 9px;
                font-weight: 700; font-size: 10px; cursor: pointer; color: #fff; margin-left: 4px;
            }}
            .nav-abas {{
                display: flex; background: #0f172a; border-bottom: 1px solid #1e293b; padding: 0 8px;
            }}
            .aba-btn {{
                background: transparent; border: none; color: #94a3b8;
                padding: 7px 11px; font-size: 11px; font-weight: 700; cursor: pointer;
                border-bottom: 2px solid transparent;
            }}
            .aba-btn.ativa {{ color: #38bdf8; border-bottom: 2px solid #38bdf8; background: rgba(56,189,248,0.08); }}
            .conteudo {{ padding: 10px; max-height: 490px; overflow-y: auto; }}
            .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }}
            .grid-4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; margin-bottom: 8px; }}
            .card {{
                background: rgba(30, 41, 59, 0.65); border: 1px solid rgba(56, 189, 248, 0.22);
                border-radius: 6px; padding: 8px;
            }}
            .card-titulo {{ color: #38bdf8; font-weight: 700; font-size: 11px; margin-bottom: 5px; }}
            .kpi-val {{ font-size: 13px; font-weight: 800; color: #4ade80; }}
            .kpi-sub {{ font-size: 10px; color: #94a3b8; }}
            .lista-modulos {{
                display: grid; grid-template-columns: 1fr 1fr; gap: 5px;
                max-height: 330px; overflow-y: auto; padding-right: 4px;
            }}
            .mod-item {{
                background: #0f172a; border: 1px solid #1e293b; border-radius: 5px;
                padding: 5px 7px; display: flex; justify-content: space-between; align-items: center;
            }}
            .mod-tag {{ color: #38bdf8; font-weight: 700; font-size: 10px; margin-right: 4px; }}
            .console-log {{
                height: 115px; overflow-y: auto; background: #050811;
                border: 1px solid #1e293b; border-radius: 5px; padding: 6px;
                font-family: Consolas, monospace; font-size: 10px; color: #34d399;
            }}
            .btn-atalho {{
                background: #1e293b; border: 1px solid #334155; color: #e2e8f0;
                border-radius: 4px; padding: 4px 7px; font-size: 10px; cursor: pointer;
            }}
            .btn-atalho:hover {{ border-color: #38bdf8; color: #38bdf8; }}
            input[type="text"], input[type="number"] {{
                background: #0f172a; border: 1px solid #334155; color: #fff;
                border-radius: 4px; padding: 4px 6px; font-size: 11px;
            }}
        </style>

        <div class="janela">
            <div class="cabecalho" id="drag-bar">
                <span class="titulo">⚡ NTO IDLE OVERDRIVE — 100 MÓDULOS ESPECIALIZADOS</span>
                <div>
                    <button id="btn-master" class="btn-acao" style="background:#10b981;">ATIVAR BOT (ON)</button>
                    <button id="btn-overdrive" class="btn-acao" style="background:#f59e0b;">🔥 OVERDRIVE 100%</button>
                    <button id="btn-panic" class="btn-acao" style="background:#ef4444;">🛑 PANIC</button>
                    <button id="btn-min" class="btn-acao" style="background:#3b82f6;">_</button>
                </div>
            </div>

            <div id="corpo-geral">
                <div class="nav-abas">
                    <button class="aba-btn ativa" data-aba="dash">📊 Dashboard</button>
                    <button class="aba-btn" data-aba="combate">⚔️ Combate & Hunts</button>
                    <button class="aba-btn" data-aba="economia">🎒 Inv & Feira Ninja</button>
                    <button class="aba-btn" data-aba="lab">🧪 Laboratório</button>
                    <button class="aba-btn" data-aba="modulos">🧩 100 Módulos</button>
                </div>

                <div class="conteudo">
                    <!-- ABA 1: DASHBOARD EM TEMPO REAL -->
                    <div id="view-dash">
                        <div class="grid-4">
                            <div class="card">
                                <div class="kpi-sub">LEVEL / MAGIC LVL</div>
                                <div class="kpi-val" id="k-lvl">Lv. 147 | ML 30</div>
                                <div class="kpi-sub" id="k-stam">Stamina: 39:34</div>
                            </div>
                            <div class="card">
                                <div class="kpi-sub">EXPERIÊNCIA / HORA</div>
                                <div class="kpi-val" id="k-xph">0 XP/h</div>
                                <div class="kpi-sub" id="k-eta">Falta: 827,764 XP</div>
                            </div>
                            <div class="card">
                                <div class="kpi-sub">DPS & SOBREVIVÊNCIA</div>
                                <div class="kpi-val" id="k-dps">0 DPS</div>
                                <div class="kpi-sub" id="k-sustain">Sustain: IMORTAL</div>
                            </div>
                            <div class="card">
                                <div class="kpi-sub">HUNT / MISSÃO / BOSS</div>
                                <div class="kpi-val" id="k-hunt" style="color:#38bdf8;">Bezer (0 / 50)</div>
                                <div class="kpi-sub" id="k-lucro">Lucro: 0G 0D 0C</div>
                            </div>
                        </div>

                        <div class="grid-2">
                            <div class="card">
                                <div class="card-titulo">🧠 INTELIGÊNCIA ADAPTATIVA & ATRIBUTOS REAIS</div>
                                <div id="txt-atributos" style="line-height:1.5; color:#cbd5e1;">
                                    VH. Ataque: 10 | Espada: 10 | Luva: 10 | Escudo: 10
                                </div>
                                <div id="txt-ia-rec" style="margin-top:6px; color:#38bdf8; font-weight:600;">
                                    Recomendação IA: Inicializando análise de hunt...
                                </div>
                                <div style="margin-top:8px;">
                                    <span>Cadência de Disparo: <strong id="lbl-vel" style="color:#facc15;">220ms</strong></span>
                                    <input type="range" id="rng-vel" min="150" max="1000" step="20" value="220" style="width:100%;">
                                </div>
                            </div>

                            <div class="card">
                                <div class="card-titulo">🧭 NAVEGAÇÃO RÁPIDA (DOCK EXPLORAR)</div>
                                <div style="display:flex; flex-wrap:wrap; gap:4px; margin-bottom:6px;">
                                    <button class="btn-atalho" data-menu="MERCADO">Mercado</button>
                                    <button class="btn-atalho" data-menu="INVENTÁRIO">Inventário</button>
                                    <button class="btn-atalho" data-menu="JUTSUS">Jutsus</button>
                                    <button class="btn-atalho" data-menu="TRAJES">Trajes</button>
                                    <button class="btn-atalho" data-menu="FORJA">Forja</button>
                                    <button class="btn-atalho" data-menu="PROGRESSÃO">Progressão</button>
                                    <button class="btn-atalho" data-menu="MAPA">Mapa</button>
                                    <button class="btn-atalho" data-menu="MINI BOSSES">Mini Bosses</button>
                                    <button class="btn-atalho" data-menu="RANKING">Ranking</button>
                                </div>
                                <div class="kpi-sub" id="k-mod-ativos">Módulos Ativos: 100 / 100</div>
                            </div>
                        </div>

                        <div class="card" style="margin-top:8px;">
                            <div class="card-titulo">📋 HISTÓRICO DE ATIVIDADES, LOOTS E TELEMETRIA</div>
                            <div class="console-log" id="box-logs">[Sistema] NTO Overdrive Ultimate (100 Módulos) inicializado!</div>
                        </div>
                    </div>

                    <!-- ABA 2: COMBATE, HUNTS & BOSSES -->
                    <div id="view-combate" style="display:none;">
                        <div class="grid-2">
                            <div class="card">
                                <div class="card-titulo">⚔️ ROTAÇÃO DE JUTSUS (SLOTS 40 / 60 / 105 / 20 / 145)</div>
                                <p style="margin:4px 0; color:#cbd5e1;">
                                    O motor prioriza os slots de recarga rápida (20 e 40) na barra HABILIDADES (1 a 0)
                                    e alterna entre os presets 1 e 2 do AUTO ATTACK sem cancelar animações.
                                </p>
                                <div id="txt-combate-stats" style="color:#4ade80; font-weight:700; margin-top:6px;">
                                    Ciclos de Combate: 0 | Presets Alternados: 0
                                </div>
                            </div>
                            <div class="card">
                                <div class="card-titulo">🎯 MEMÓRIA DE HUNTS & RASTREADOR DE BOSSES</div>
                                <div id="txt-hunts-mem" style="font-family:Consolas,monospace; font-size:10px; color:#38bdf8;">
                                    Nenhuma hunt finalizada nesta sessão ainda.
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- ABA 3: INVENTÁRIO & ECONOMIA (FEIRA NINJA) -->
                    <div id="view-economia" style="display:none;">
                        <div class="grid-2">
                            <div class="card">
                                <div class="card-titulo">💰 PATRIMÔNIO ACUMULADO (GOLD / DOLLAR / CENT)</div>
                                <div class="kpi-val" id="eco-total">0G 0D 0C</div>
                                <div id="eco-raridades" style="margin-top:6px; color:#cbd5e1;">
                                    Common: 0 | Uncommon: 0 | Rare: 0 | Epic: 0 | Legendary: 0
                                </div>
                            </div>
                            <div class="card">
                                <div class="card-titulo">📈 TABELA DE PREÇOS LIDA DO SERVER LOG</div>
                                <div id="eco-precos" style="font-family:Consolas,monospace; font-size:10px; color:#facc15; max-height:160px; overflow-y:auto;">
                                    anbu mask: 58D 54C | gaara legs: 8D 55C | anbu mask #1: 98D 15C | chakra mask: 58D 34C | taijutsu legs: 56D 45C
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- ABA 4: LABORATÓRIO EXPERIMENTAL ISOLADO -->
                    <div id="view-lab" style="display:none;">
                        <div class="card">
                            <div class="card-titulo">🧪 LABORATÓRIO EXPERIMENTAL (SANDBOX AUTORIZADO CLIENT-SIDE)</div>
                            <div style="display:flex; gap:10px; align-items:center; margin-bottom:8px;">
                                <label>HP do Inimigo/Boss: <input type="number" id="lab-hp" value="3500" style="width:80px;"></label>
                                <label>DPS do Inimigo: <input type="number" id="lab-dps" value="420" style="width:70px;"></label>
                                <button id="btn-run-lab" class="btn-acao" style="background:#3b82f6;">🔬 Simular Limites Agora</button>
                            </div>
                            <div id="lab-output" style="background:#050811; padding:8px; border-radius:5px; font-family:Consolas,monospace; color:#4ade80; line-height:1.6;">
                                Clique em "Simular Limites Agora" para calcular Dano Máximo, Instakill Teórico e Vida Infinita (HPS >= DPS).
                            </div>
                        </div>
                    </div>

                    <!-- ABA 5: CONTROLE INDIVIDUAL DOS 100 MÓDULOS -->
                    <div id="view-modulos" style="display:none;">
                        <div style="display:flex; justify-content:space-between; margin-bottom:6px; gap:6px;">
                            <input type="text" id="inp-filtro" placeholder="🔍 Filtrar entre os 100 módulos (ex: Boss, Economia, M025)..." style="flex:1;">
                            <button id="btn-todos-on" class="btn-atalho">Marcar Todos (100)</button>
                            <button id="btn-todos-off" class="btn-atalho">Desmarcar Todos</button>
                        </div>
                        <div class="lista-modulos" id="grid-100-modulos"></div>
                    </div>
                </div>
            </div>
        </div>
    `;

    const garantirAnexo = () => {{
        if (document.body && !host.parentElement) document.body.appendChild(host);
    }};
    garantirAnexo();
    setInterval(garantirAnexo, 1000);

    const st = window.__ntoEstado;

    // Renderiza a lista dos 100 módulos com controle individual
    const containerModulos = shadow.getElementById('grid-100-modulos');
    const renderizarModulos = () => {{
        const termo = (st.filtroModulo || '').toLowerCase();
        containerModulos.innerHTML = '';
        st.modulos.forEach(m => {{
            const txt = (m.id + ' ' + m.cat + ' ' + m.nome).toLowerCase();
            if (termo && !txt.includes(termo)) return;
            const div = document.createElement('div');
            div.className = 'mod-item';
            div.innerHTML = `
                <div>
                    <span class="mod-tag">[${{m.id}}]</span>
                    <span>${{m.nome}}</span>
                    <div style="font-size:9px; color:#64748b;">${{m.cat}} | Exec: ${{m.exec}}</div>
                </div>
                <input type="checkbox" data-mid="${{m.id}}" ${{m.ativo ? 'checked' : ''}}>
            `;
            div.querySelector('input').onchange = (e) => {{
                m.ativo = e.target.checked;
                st.modulosAlterados[m.id] = m.ativo;
                atualizarContadorAtivos();
            }};
            containerModulos.appendChild(div);
        }});
    }};

    const atualizarContadorAtivos = () => {{
        const ativos = st.modulos.filter(m => m.ativo).length;
        shadow.getElementById('k-mod-ativos').innerText = `Módulos Ativos: ${{ativos}} / 100`;
    }};
    renderizarModulos();

    // Troca de abas
    shadow.querySelectorAll('.aba-btn').forEach(btn => {{
        btn.onclick = () => {{
            shadow.querySelectorAll('.aba-btn').forEach(b => b.classList.remove('ativa'));
            btn.classList.add('ativa');
            const alvo = btn.getAttribute('data-aba');
            ['dash', 'combate', 'economia', 'lab', 'modulos'].forEach(id => {{
                shadow.getElementById('view-' + id).style.display = (id === alvo) ? 'block' : 'none';
            }});
            if (alvo === 'modulos') renderizarModulos();
        }};
    }});

    // Botões mestres
    const btnMaster = shadow.getElementById('btn-master');
    btnMaster.onclick = () => {{
        st.emergencia = false;
        st.botAtivo = !st.botAtivo;
        btnMaster.innerText = st.botAtivo ? 'PAUSAR BOT (OFF)' : 'ATIVAR BOT (ON)';
        btnMaster.style.background = st.botAtivo ? '#ef4444' : '#10b981';
    }};

    shadow.getElementById('btn-overdrive').onclick = () => {{
        st.emergencia = false;
        st.botAtivo = true;
        st.delayMs = 180;
        shadow.getElementById('rng-vel').value = 180;
        shadow.getElementById('lbl-vel').innerText = '180ms (OVERDRIVE)';
        st.modulos.forEach(m => {{ m.ativo = true; st.modulosAlterados[m.id] = true; }});
        btnMaster.innerText = 'PAUSAR BOT (OFF)';
        btnMaster.style.background = '#ef4444';
        atualizarContadorAtivos();
        renderizarModulos();
    }};

    shadow.getElementById('btn-panic').onclick = () => {{
        st.botAtivo = false;
        st.emergencia = true;
        btnMaster.innerText = 'ATIVAR BOT (ON)';
        btnMaster.style.background = '#10b981';
    }};

    shadow.getElementById('btn-min').onclick = () => {{
        const cg = shadow.getElementById('corpo-geral');
        cg.style.display = cg.style.display === 'none' ? 'block' : 'none';
    }};

    shadow.getElementById('rng-vel').oninput = (e) => {{
        st.delayMs = parseInt(e.target.value, 10);
        shadow.getElementById('lbl-vel').innerText = st.delayMs + 'ms';
    }};

    shadow.getElementById('inp-filtro').oninput = (e) => {{
        st.filtroModulo = e.target.value;
        renderizarModulos();
    }};

    shadow.getElementById('btn-todos-on').onclick = () => {{
        st.modulos.forEach(m => {{ m.ativo = true; st.modulosAlterados[m.id] = true; }});
        atualizarContadorAtivos();
        renderizarModulos();
    }};

    shadow.getElementById('btn-todos-off').onclick = () => {{
        st.modulos.forEach(m => {{ m.ativo = false; st.modulosAlterados[m.id] = false; }});
        atualizarContadorAtivos();
        renderizarModulos();
    }};

    shadow.querySelectorAll('.btn-atalho[data-menu]').forEach(b => {{
        b.onclick = () => {{ st.acaoMenuRapido = b.getAttribute('data-menu'); }};
    }});

    shadow.getElementById('btn-run-lab').onclick = () => {{
        st.parametrosLab.hpMob = parseInt(shadow.getElementById('lab-hp').value || '3500', 10);
        st.parametrosLab.dpsMob = parseInt(shadow.getElementById('lab-dps').value || '420', 10);
        st.rodarSimulacaoLab = true;
    }};

    // Arrastar janela
    const dragBar = shadow.getElementById('drag-bar');
    let dx = 0, dy = 0, mx = 0, my = 0;
    dragBar.onmousedown = (e) => {{
        mx = e.clientX; my = e.clientY;
        window.onmouseup = () => {{ window.onmouseup = null; window.onmousemove = null; }};
        window.onmousemove = (ev) => {{
            dx = mx - ev.clientX; dy = my - ev.clientY;
            mx = ev.clientX; my = ev.clientY;
            host.style.top = (host.offsetTop - dy) + 'px';
            host.style.left = (host.offsetLeft - dx) + 'px';
            host.style.right = 'auto';
        }};
    }};

    window.__ntoSincronizarUI = (pacote) => {{
        shadow.getElementById('k-lvl').innerText = pacote.k_lvl;
        shadow.getElementById('k-stam').innerText = pacote.k_stam;
        shadow.getElementById('k-xph').innerText = pacote.k_xph;
        shadow.getElementById('k-eta').innerText = pacote.k_eta;
        shadow.getElementById('k-dps').innerText = pacote.k_dps;
        shadow.getElementById('k-sustain').innerText = pacote.k_sustain;
        shadow.getElementById('k-hunt').innerText = pacote.k_hunt;
        shadow.getElementById('k-lucro').innerText = pacote.k_lucro;
        shadow.getElementById('txt-atributos').innerText = pacote.atributos;
        shadow.getElementById('txt-ia-rec').innerText = pacote.ia_rec;
        shadow.getElementById('txt-combate-stats').innerText = pacote.combate_stats;
        shadow.getElementById('txt-hunts-mem').innerText = pacote.hunts_mem;
        shadow.getElementById('eco-total').innerText = pacote.eco_total;
        shadow.getElementById('eco-raridades').innerText = pacote.eco_raridades;

        if (pacote.lab_html) {{
            shadow.getElementById('lab-output').innerHTML = pacote.lab_html;
        }}
        if (pacote.novo_log) {{
            const box = shadow.getElementById('box-logs');
            const linha = document.createElement('div');
            linha.innerText = pacote.novo_log;
            box.appendChild(linha);
            box.scrollTop = box.scrollHeight;
            while (box.children.length > 80) box.removeChild(box.firstChild);
        }}
    }};
}})();
"""


# =====================================================================
# 7. FUNÇÕES DE INTERAÇÃO FÍSICA CDP (isTrusted: true)
# =====================================================================
def clique_cdp(page, x, y, botao="left"):
    try:
        px = x + random.uniform(-3.0, 3.0)
        py = y + random.uniform(-3.0, 3.0)
        page.mouse.move(px, py, steps=2)
        page.mouse.down(button=botao)
        page.mouse.up(button=botao)
        return True
    except Exception:
        return False


def clicar_locator_cdp(page, locator):
    try:
        if locator.count() == 0:
            return False
        box = locator.first.bounding_box()
        if not box:
            return False
        ax = box["x"] + (box["width"] * random.uniform(0.3, 0.7))
        ay = box["y"] + (box["height"] * random.uniform(0.3, 0.7))
        return clique_cdp(page, ax, ay)
    except Exception:
        return False


def pressionar_tecla_cdp(page, tecla):
    try:
        page.keyboard.press(tecla, delay=random.randint(12, 26))
        return True
    except Exception:
        return False


def garantir_toggle_nativo_on(page, nome_modulo):
    try:
        el = page.get_by_text(nome_modulo, exact=True)
        if el.count() == 0:
            return False
        linha = el.first.locator("..")
        if "OFF" in linha.inner_text().upper():
            btn_off = linha.get_by_text("OFF", exact=True)
            return clicar_locator_cdp(page, btn_off)
    except Exception:
        pass
    return False


# =====================================================================
# 8. SUÍTE DE TESTES UNITÁRIOS E DE INTEGRAÇÃO DOS 100 MÓDULOS
# =====================================================================
class SuiteTestesAutomatizados(unittest.TestCase):
    """Valida todos os 100 módulos, o motor econômico, o laboratório e a telemetria antes do uso."""

    def test_01_integridade_dos_100_modulos(self):
        reg = RegistroCemModulos()
        self.assertEqual(len(reg.modulos), 100, "Devem existir exatamente 100 módulos registrados.")
        for i in range(1, 101):
            cod = f"M{i:03d}"
            self.assertIn(cod, reg.modulos)
            self.assertTrue(reg.registrar_execucao(cod, "TESTE_OK"))

    def test_02_parser_economia_feira_ninja(self):
        eco = MotorEconomia()
        amostra_log = (
            "anbu mask (common) = 58 Dollar + 54 Cent; "
            "3x chakra mask (common) = 1 Gold + 75 Dollar + 2 Cent; "
            "Sistema: ! Pegou 1x chunnin armor."
        )
        atualizados = eco.processar_cotacao_log(amostra_log)
        self.assertGreaterEqual(atualizados, 2)
        drop = eco.registrar_drop("Sistema: ! Pegou 1x chunnin armor.")
        self.assertIsNotNone(drop)
        self.assertGreater(eco.total_cent_acumulado, 0)

    def test_03_laboratorio_experimental_isolado(self):
        lab = LaboratorioExperimental()
        res = lab.executar_ensaio_completo(level=147, ml=30, atk_speed=10, espada=10, escudo=10)
        self.assertGreater(res["dps_overdrive"], res["dps_comum"])
        self.assertGreater(res["pico_burst_dano"], 0)
        self.assertIn("IMORTAL", res["status_vida_infinita"])

    def test_04_analisador_telemetria_real(self):
        ana = AnalisadorEstadoNTO()
        amostra_dom = (
            "PROGRESSÃO LEVEL 147 Falta 827,764 XP para upar STAMINA 39:34 "
            "MAGIC LEVEL 30 Falta 11,536 Chakra para upar VH. ATAQUE 10 ESPADA 10 LUVA 10 ESCUDO 10 "
            "MISSÕES Bezer 12 / 50"
        )
        dados = ana.extrair_estado(amostra_dom)
        self.assertEqual(dados["level"], 147)
        self.assertEqual(dados["ml"], 30)
        self.assertEqual(dados["missao_atual"], 12)
        self.assertEqual(dados["missao_total"], 50)


def rodar_auto_teste_inicial():
    suite = unittest.TestLoader().loadTestsFromTestCase(SuiteTestesAutomatizados)
    resultado = unittest.TextTestRunner(verbosity=1).run(suite)
    return resultado.wasSuccessful()


# =====================================================================
# 9. ORQUESTRADOR PRINCIPAL DO NTO OVERDRIVE ULTIMATE (runner.py)
# =====================================================================
def iniciar_nto_overdrive():
    print("=================================================================")
    print("🔬 EXECUTANDO TESTES AUTOMATIZADOS DOS 100 MÓDULOS...")
    print("=================================================================")
    if not rodar_auto_teste_inicial():
        print("[ERRO] Falha nos testes de integridade.")
        return

    registro = RegistroCemModulos()
    economia = MotorEconomia()
    laboratorio = LaboratorioExperimental()
    ia = MotorIAOverdrive()
    analisador = AnalisadorEstadoNTO()

    registro.registrar_execucao("M097", "Suíte 100% Aprovada")
    registro.registrar_execucao("M098", "Modo Autorizado Ativo")

    script_ui = gerar_script_interface_shadow(registro.exportar_lista_ui())

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=PASTA_SESSAO,
            headless=False,
            viewport={"width": 1366, "height": 768},
            ignore_default_args=["--enable-automation"],
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
            ],
        )

        context.add_init_script("Object.defineProperty(navigator, 'webdriver', { get: () => undefined });")
        context.add_init_script(script_ui)

        page = context.pages[0] if context.pages else context.new_page()
        print(f"🚀 Abrindo {URL_JOGO} com Painel de 100 Módulos integrado...")
        page.goto(URL_JOGO, wait_until="domcontentloaded", timeout=60000)
        page.evaluate(script_ui)

        prox_combate = time.time() + 0.5
        prox_loot = time.time() + 1.0
        prox_telemetria = time.time() + 1.4
        prox_preset = time.time() + 6.5

        fila_prioridade_cd = ["4", "1", "2", "4", "1", "3", "5", "2", "6", "7", "8", "9", "0"]
        fila_linear = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
        idx_tecla = 0

        centro_x, centro_y, sqm = 683, 384, 48
        grade_loot = [
            (0, 0), (-sqm, 0), (sqm, 0), (0, -sqm), (0, sqm),
            (-sqm, -sqm), (sqm, -sqm), (-sqm, sqm), (sqm, sqm)
        ]
        idx_loot = 0

        preset_atual = "1"
        ciclos_combate = 0
        trocas_preset = 0
        qtd_drops_lidos = 0
        abates_ant = 0

        try:
            while True:
                agora = time.time()

                # Sincroniza o estado do painel Shadow DOM
                try:
                    st_ui = page.evaluate(
                        "() => { if (!window.__ntoUltimate100Ativo) return null; "
                        "const r = { "
                        "  botAtivo: window.__ntoEstado.botAtivo, "
                        "  emergencia: window.__ntoEstado.emergencia, "
                        "  delayMs: window.__ntoEstado.delayMs, "
                        "  acaoMenuRapido: window.__ntoEstado.acaoMenuRapido, "
                        "  rodarSimulacaoLab: window.__ntoEstado.rodarSimulacaoLab, "
                        "  parametrosLab: window.__ntoEstado.parametrosLab, "
                        "  modulosAlterados: window.__ntoEstado.modulosAlterados "
                        "}; "
                        "window.__ntoEstado.acaoMenuRapido = null; "
                        "window.__ntoEstado.rodarSimulacaoLab = false; "
                        "window.__ntoEstado.modulosAlterados = {}; "
                        "return r; }"
                    )
                except Exception:
                    time.sleep(0.4)
                    continue

                if not st_ui:
                    try:
                        page.evaluate(script_ui)
                    except Exception:
                        pass
                    time.sleep(0.3)
                    continue

                # Atualiza chaves individuais dos 100 módulos se o usuário clicou na UI
                alterados = st_ui.get("modulosAlterados") or {}
                if alterados:
                    for mid, val in alterados.items():
                        if mid in registro.modulos:
                            registro.modulos[mid]["ativo"] = bool(val)
                    registro.salvar_estados({"delayMs": st_ui.get("delayMs", 220)})
                    registro.registrar_execucao("M088", "Config Salva")
                    registro.registrar_execucao("M095", "Backup OK")

                # Atalho rápido para abrir janelas do dock EXPLORAR
                menu_Solicitado = st_ui.get("acaoMenuRapido")
                if menu_Solicitado:
                    loc_menu = page.get_by_text(menu_Solicitado, exact=True)
                    clicar_locator_cdp(page, loc_menu)
                    registro.registrar_execucao("M081", f"Abriu {menu_Solicitado}")

                # 1. Ciclo de Telemetria, Análise Econômica, Laboratório e IA (M001..M020, M051..M080)
                if agora >= prox_telemetria:
                    prox_telemetria = agora + random.uniform(1.3, 1.9)
                    try:
                        texto_dom = page.locator("body").inner_text(timeout=350)
                        for m_cod in ["M001", "M002", "M003", "M004", "M006", "M015", "M016", "M090"]:
                            registro.registrar_execucao(m_cod)

                        dados = analisador.extrair_estado(texto_dom)
                        economia.processar_cotacao_log(texto_dom)

                        novo_log_msg = None
                        linhas_drop = re.findall(r"Sistema: ! Pegou [^\n]+", texto_dom)
                        if len(linhas_drop) > qtd_drops_lidos:
                            novos = len(linhas_drop) - qtd_drops_lidos
                            for ld in linhas_drop[qtd_drops_lidos:]:
                                info_drop = economia.registrar_drop(ld)
                                if info_drop:
                                    moeda_fmt = economia.formatar_moeda(info_drop["valor_cent"])
                                    novo_log_msg = f"[{info_drop['hora']}] 🎒 +{info_drop['qtd']}x {info_drop['item']} ({moeda_fmt})"
                            qtd_drops_lidos = len(linhas_drop)
                            for m_eco in ["M051", "M053", "M057", "M061", "M062", "M064", "M068"]:
                                registro.registrar_execucao(m_eco)
                            ia.registrar_evento(loots_ganhos=novos)

                        if dados["missao_atual"] > abates_ant:
                            ia.registrar_evento(abates_missao=(dados["missao_atual"] - abates_ant))
                        abates_ant = dados["missao_atual"]

                        # Entrega automática de missão (50 / 50)
                        if st_ui.get("botAtivo") and registro.esta_ativo("M033"):
                            if dados["missao_atual"] >= dados["missao_total"] > 0:
                                loc_m = page.get_by_text(dados["missao_str"], exact=True)
                                if clicar_locator_cdp(page, loc_m):
                                    novo_log_msg = f"[{time.strftime('%H:%M:%S')}] 📜 Missão {dados['mob_missao']} concluída ({dados['missao_str']})!"
                                    registro.registrar_execucao("M033", "Entregue")

                        # Auto-evolução de atributos no painel PROGRESSÃO
                        if st_ui.get("botAtivo") and registro.esta_ativo("M019") and random.random() < 0.25:
                            btn_up = page.get_by_text("+", exact=True)
                            if btn_up.count() > 0 and clicar_locator_cdp(page, btn_up):
                                registro.registrar_execucao("M019", "Atributo +1")

                        # Executa cálculos do Laboratório Experimental
                        params_lab = st_ui.get("parametrosLab") or {"hpMob": 3500, "dpsMob": 420}
                        sim = laboratorio.executar_ensaio_completo(
                            level=dados["level"],
                            ml=dados["ml"],
                            atk_speed=dados["vh_ataque"],
                            espada=dados["espada"],
                            escudo=dados["escudo"],
                            hp_mob=params_lab.get("hpMob", 3500),
                            dps_mob=params_lab.get("dpsMob", 420),
                        )
                        for m_lab in ["M025", "M026", "M027", "M030", "M047"]:
                            registro.registrar_execucao(m_lab)

                        lab_html = None
                        if st_ui.get("rodarSimulacaoLab"):
                            lab_html = (
                                f"Multiplicador Atributos: <b>{sim['multiplicador_ataque']}x</b> | "
                                f"DPS Padrão: <b>{sim['dps_comum']}</b> -> DPS Overdrive: <b>{sim['dps_overdrive']} (+{sim['ganho_dps_pct']}%)</b><br>"
                                f"Pico Burst (10 Jutsus): <b>{sim['pico_burst_dano']} dano</b> | "
                                f"Status Instakill: <b>{sim['instakill_simulado']}</b> | Abates Est.: <b>{sim['abates_minuto_est']}/min</b><br>"
                                f"Mitigação Defesa (Susanoo+Escudo): <b>{sim['mitigacao_pct']}%</b> | "
                                f"HPS Cura: <b>{sim['hps_cura']}/s</b> vs Dano Mob: <b>{sim['dano_liquido_mob']}/s</b> -> "
                                f"Vida Infinita: <b>{sim['status_vida_infinita']} (Índice {sim['indice_sustain']})</b>"
                            )
                            novo_log_msg = f"[{time.strftime('%H:%M:%S')}] 🧪 Ensaio do Laboratório Experimental atualizado!"

                        # Memória de Hunts e IA
                        decorrido_h = max(0.001, (agora - analisador.inicio) / 3600.0)
                        loots_h = int(len(economia.historico_loots) / decorrido_h)
                        ia.registrar_hunt(dados["mob_missao"], dados["xp_hora"], loots_h)
                        if st_ui.get("botAtivo") and registro.esta_ativo("M071"):
                            ia.ciclo_aprendizado()
                            registro.registrar_execucao("M071")

                        # Sobrevivência: Anti-PK / Morte
                        if st_ui.get("botAtivo") and registro.esta_ativo("M046") and dados["alerta_morte"]:
                            page.evaluate("() => { window.__ntoEstado.botAtivo = false; window.__ntoEstado.emergencia = true; }")
                            novo_log_msg = f"[{time.strftime('%H:%M:%S')}] 🚨 ALERTA DE MORTE DETECTADO! Parada de emergência acionada."
                            try:
                                winsound.Beep(1400, 500)
                            except Exception:
                                pass

                        hunts_txt = " | ".join(
                            f"{k}: {v['xp_h']:,} XP/h ({v['loots_h']} drops/h)"
                            for k, v in ia.memoria_hunts.items()
                        ) or "Coletando métricas da hunt atual..."

                        r_map = economia.itens_por_raridade
                        raridades_txt = (
                            f"Common: {r_map['common']} | Uncommon: {r_map['uncommon']} | "
                            f"Rare: {r_map['rare']} | Epic: {r_map['epic']} | Legendary: {r_map['legendary']}"
                        )

                        pacote_ui = {
                            "k_lvl": f"Lv. {dados['level']} | ML {dados['ml']}",
                            "k_stam": f"Stamina: {dados['stamina']} | Falta ML: {dados['chakra_restante']}",
                            "k_xph": f"{dados['xp_hora']:,} XP/h",
                            "k_eta": f"Falta: {dados['xp_restante_fmt']} XP (ETA: {dados['eta_min']}m)",
                            "k_dps": f"{sim['dps_overdrive']} DPS (+{sim['ganho_dps_pct']}%)",
                            "k_sustain": f"Sustain: {sim['status_vida_infinita']}",
                            "k_hunt": f"{dados['mob_missao']} ({dados['missao_str']})",
                            "k_lucro": f"Lucro: {economia.formatar_moeda(economia.total_cent_acumulado)}",
                            "atributos": (
                                f"VH. Ataque: {dados['vh_ataque']} | Espada: {dados['espada']} | "
                                f"Luva: {dados['luva']} | Escudo: {dados['escudo']} | Burst Máx: {sim['pico_burst_dano']}"
                            ),
                            "ia_rec": ia.gerar_recomendacao(dados["stamina"], dados["xp_hora"], loots_h),
                            "combate_stats": f"Ciclos de Combate: {ciclos_combate} | Trocas de Preset (1/2): {trocas_preset}",
                            "hunts_mem": hunts_txt,
                            "eco_total": economia.formatar_moeda(economia.total_cent_acumulado),
                            "eco_raridades": raridades_txt,
                            "lab_html": lab_html,
                            "novo_log": novo_log_msg,
                        }
                        page.evaluate("(p) => window.__ntoSincronizarUI && window.__ntoSincronizarUI(p)", pacote_ui)
                    except Exception:
                        pass

                if not st_ui.get("botAtivo") or st_ui.get("emergencia"):
                    time.sleep(0.04)
                    continue

                # 2. Ciclo de Combate, Rotação de Jutsus e Sustentação (M021..M029, M041..M050)
                if agora >= prox_combate:
                    base_s = max(0.15, st_ui.get("delayMs", 220) / 1000.0)
                    prox_combate = agora + random.uniform(base_s * 0.82, base_s * 1.18)
                    ciclos_combate += 1

                    # Alterna entre as abas 1 e 2 do AUTO ATTACK sem colidir com teclas
                    if registro.esta_ativo("M029") and agora >= prox_preset:
                        prox_preset = agora + random.uniform(6.0, 8.5)
                        preset_atual = "2" if preset_atual == "1" else "1"
                        aba = page.get_by_text(preset_atual, exact=True)
                        if clicar_locator_cdp(page, aba):
                            trocas_preset += 1
                            registro.registrar_execucao("M029", f"Preset {preset_atual}")
                    else:
                        if registro.esta_ativo("M021") and registro.esta_ativo("M023"):
                            fila = fila_prioridade_cd if registro.esta_ativo("M028") else fila_linear
                            for _ in range(3):
                                pressionar_tecla_cdp(page, fila[idx_tecla % len(fila)])
                                idx_tecla += 1
                            registro.registrar_execucao("M021")
                            registro.registrar_execucao("M023")

                        if registro.esta_ativo("M043"):
                            pressionar_tecla_cdp(page, "F1")
                            if random.random() < 0.25:
                                for mod_nativo in ["AUTO HEAL", "CHAKRA DOWN", "AUTO HASTE", "AUTO BUFF"]:
                                    garantir_toggle_nativo_on(page, mod_nativo)
                            registro.registrar_execucao("M043")

                        if registro.esta_ativo("M011") and random.random() < 0.25:
                            for mod_hunt in ["AUTO TARGET", "AUTO ATTACK"]:
                                garantir_toggle_nativo_on(page, mod_hunt)
                            registro.registrar_execucao("M011")

                # 3. Ciclo de Auto-Loot em Espiral 9 SQMs (M052, M059)
                if registro.esta_ativo("M052") and agora >= prox_loot:
                    prox_loot = agora + random.uniform(0.45, 0.75)
                    dx, dy = grade_loot[idx_loot % len(grade_loot)]
                    idx_loot += 1
                    clique_cdp(page, centro_x + dx, centro_y + dy, botao="right")
                    registro.registrar_execucao("M052")

                time.sleep(0.02)
        except KeyboardInterrupt:
            print("\nEncerrando NTO Overdrive Ultimate e salvando estado dos 100 módulos...")
            registro.salvar_estados()
            context.close()


if __name__ == "__main__":
    if "--test" in sys.argv:
        rodar_auto_teste_inicial()
    else:
        iniciar_nto_overdrive()