import json
import os
import random
import re
import shutil
import threading
import time
import tkinter as tk
from tkinter import ttk
import winsound
from playwright.sync_api import sync_playwright

URL_JOGO = "https://ntoidle.online/game"
PASTA_SESSAO = "./sessao_nto_stealth"
ARQUIVO_CONFIG = "./config_bot.json"
ARQUIVO_BACKUP = "./config_bot.backup.json"


# =========================================================
# 1. MOTOR DE INTELIGÊNCIA ARTIFICIAL ADAPTATIVA
# =========================================================
class MotorIAAdaptativa:
    def __init__(self):
        self.estrategias = {
            "Precisao_Cooldown": {"delay": 0.32, "rajada": 2, "score": 1.0, "usos": 1},
            "Burst_Sincronizado": {"delay": 0.22, "rajada": 4, "score": 1.2, "usos": 1},
            "Ritmo_Equilibrado": {"delay": 0.42, "rajada": 3, "score": 1.0, "usos": 1},
            "Overdrive_Maximo": {"delay": 0.18, "rajada": 4, "score": 1.1, "usos": 1},
        }
        self.estrategia_atual = "Burst_Sincronizado"
        self.inicio_janela = time.time()
        self.eventos_positivos_janela = 0
        self.acoes_economizadas = 0

    def registrar_recompensa(self, peso=1.0):
        self.eventos_positivos_janela += peso

    def avaliar_e_adaptar(self):
        agora = time.time()
        decorrido = agora - self.inicio_janela
        if decorrido < 30.0:
            return None

        taxa_recompensa = (self.eventos_positivos_janela / decorrido) * 60.0
        dados = self.estrategias[self.estrategia_atual]
        dados["score"] = (dados["score"] * 0.7) + (taxa_recompensa * 0.3)
        dados["usos"] += 1

        if random.random() < 0.20:
            escolha = random.choice(list(self.estrategias.keys()))
        else:
            escolha = max(self.estrategias.items(), key=lambda x: x[1]["score"])[0]

        self.estrategia_atual = escolha
        self.inicio_janela = agora
        self.eventos_positivos_janela = 0
        return self.estrategia_atual, self.estrategias[escolha]


# =========================================================
# 2. DASHBOARD DE TELA ÚNICA (THREAD PRINCIPAL GARANTIDA)
# =========================================================
class PainelUnicoOverdriveHUD:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NTO Game Overdrive — Dashboard Completo")
        self.root.geometry("760x580+250+120")
        self.root.configure(bg="#0d1321")

        # Força a janela a aparecer na frente de tudo imediatamente
        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.focus_force()

        self.ativo = False
        self.emergencia_acionada = False
        self.encerrado = False
        self.inicio_sessao = time.time()
        self.ia = MotorIAAdaptativa()

        cfg = self._carregar_config_com_backup()

        self.var_perfil = tk.StringVar(value=cfg.get("perfil", "Overdrive IA"))
        self.var_ia_ativa = tk.BooleanVar(value=cfg.get("ia_ativa", True))
        self.var_burst = tk.BooleanVar(value=cfg.get("burst", True))
        self.var_priorizar_cd = tk.BooleanVar(value=cfg.get("priorizar_cd", True))
        self.var_sustain = tk.BooleanVar(value=cfg.get("sustain", True))
        self.var_hunt = tk.BooleanVar(value=cfg.get("hunt", True))
        self.var_presets = tk.BooleanVar(value=cfg.get("presets", True))
        self.var_auto_loot = tk.BooleanVar(value=cfg.get("auto_loot", True))
        self.var_missoes = tk.BooleanVar(value=cfg.get("missoes", True))
        self.var_up_stats = tk.BooleanVar(value=cfg.get("up_stats", True))
        self.var_reconnect = tk.BooleanVar(value=cfg.get("reconnect", True))
        self.var_anti_pk = tk.BooleanVar(value=cfg.get("anti_pk", True))
        self.var_proteger_stamina = tk.BooleanVar(value=cfg.get("proteger_stamina", True))
        self.var_delay_medio = tk.DoubleVar(value=cfg.get("delay_medio", 0.24))

        self._construir_dashboard_unico()
        self.root.protocol("WM_DELETE_WINDOW", self._ao_fechar)

    def _carregar_config_com_backup(self):
        if os.path.exists(ARQUIVO_CONFIG):
            try:
                shutil.copyfile(ARQUIVO_CONFIG, ARQUIVO_BACKUP)
                with open(ARQUIVO_CONFIG, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def salvar_config(self, _=None):
        dados = {
            "perfil": self.var_perfil.get(),
            "ia_ativa": self.var_ia_ativa.get(),
            "burst": self.var_burst.get(),
            "priorizar_cd": self.var_priorizar_cd.get(),
            "sustain": self.var_sustain.get(),
            "hunt": self.var_hunt.get(),
            "presets": self.var_presets.get(),
            "auto_loot": self.var_auto_loot.get(),
            "missoes": self.var_missoes.get(),
            "up_stats": self.var_up_stats.get(),
            "reconnect": self.var_reconnect.get(),
            "anti_pk": self.var_anti_pk.get(),
            "proteger_stamina": self.var_proteger_stamina.get(),
            "delay_medio": round(self.var_delay_medio.get(), 2),
        }
        try:
            with open(ARQUIVO_CONFIG, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=2)
        except Exception as e:
            self.log_erro(f"Erro ao salvar config: {e}")

    def _criar_secao(self, pai, titulo):
        frame = tk.LabelFrame(
            pai, text=titulo, bg="#111a2e", fg="#00d2ff",
            font=("Segoe UI", 8, "bold"), bd=1, relief="solid", padx=8, pady=5
        )
        frame.pack(fill="x", pady=4)
        return frame

    def _criar_chk(self, pai, texto, variavel):
        tk.Checkbutton(
            pai, text=texto, variable=variavel, command=self.salvar_config,
            bg="#111a2e", fg="#e0e6ed", selectcolor="#162447",
            activebackground="#111a2e", activeforeground="#00d2ff", font=("Segoe UI", 8)
        ).pack(anchor="w", pady=1)

    def _construir_dashboard_unico(self):
        topo = tk.Frame(self.root, bg="#162447", padx=10, pady=6)
        topo.pack(fill="x")

        tk.Label(
            topo, text="🚀 NTO OVERDRIVE — PAINEL COMPLETO", bg="#162447", fg="#00d2ff",
            font=("Segoe UI", 10, "bold")
        ).pack(side="left")

        tk.Button(
            topo, text="🛑 EMERGÊNCIA (PANIC)", bg="#ff1e42", fg="white",
            font=("Segoe UI", 8, "bold"), relief="flat", padx=8, command=self.acionar_emergencia
        ).pack(side="right", padx=(6, 0))

        tk.Button(
            topo, text="⚡ ATIVAR TUDO MAX", bg="#e67e22", fg="white",
            font=("Segoe UI", 8, "bold"), relief="flat", padx=8, command=self.ativar_tudo
        ).pack(side="right", padx=4)

        self.btn_toggle = tk.Button(
            topo, text="ATIVAR BOT (ON)", bg="#0f9d58", fg="white",
            font=("Segoe UI", 8, "bold"), relief="flat", padx=10, command=self.alternar_bot
        )
        self.btn_toggle.pack(side="right", padx=4)

        combo_perfil = ttk.Combobox(
            topo, textvariable=self.var_perfil, state="readonly", width=14,
            values=["Overdrive IA", "Burst Boss", "Farm Seguro", "Stealth Lento"]
        )
        combo_perfil.pack(side="right", padx=6)
        combo_perfil.bind("<<ComboboxSelected>>", self.aplicar_perfil)

        tk.Label(
            topo, text="Perfil:", bg="#162447", fg="#e0e6ed", font=("Segoe UI", 8, "bold")
        ).pack(side="right")

        corpo = tk.Frame(self.root, bg="#0d1321", padx=8, pady=6)
        corpo.pack(fill="both", expand=True)

        col_esq = tk.Frame(corpo, bg="#0d1321", width=370)
        col_esq.pack(side="left", fill="both", expand=True, padx=(0, 6))

        col_dir = tk.Frame(corpo, bg="#0d1321", width=370)
        col_dir.pack(side="right", fill="both", expand=True, padx=(6, 0))

        # Coluna Esquerda
        sec_vel = self._criar_secao(col_esq, "⚡ CONTROLE DE VELOCIDADE E CADÊNCIA")
        self.lbl_speed = tk.Label(
            sec_vel, text="Ritmo de Disparo: ~240ms (OVERDRIVE)",
            bg="#111a2e", fg="#ffcc00", font=("Segoe UI", 8, "bold")
        )
        self.lbl_speed.pack(anchor="w")

        slider = ttk.Scale(
            sec_vel, from_=0.16, to=1.5, variable=self.var_delay_medio,
            command=self._atualizar_label_velocidade
        )
        slider.pack(fill="x", pady=3)
        self._atualizar_label_velocidade()

        sec_combate = self._criar_secao(col_esq, "⚔️ MÓDULOS DE COMBATE & BURST DPS")
        self._criar_chk(sec_combate, "💥 Burst DPS Inteligente (Disparo nos 10 Jutsus)", self.var_burst)
        self._criar_chk(sec_combate, "🎯 Priorizar Cooldowns Rápidos (20s/40s > 145s)", self.var_priorizar_cd)
        self._criar_chk(sec_combate, "❤️ Sustain Total (Auto Heal, Chakra, Haste, Susanoo)", self.var_sustain)
        self._criar_chk(sec_combate, "🔄 Combar Abas 1 e 2 do Auto-Attack (Sem Colisão)", self.var_presets)
        self._criar_chk(sec_combate, "🔒 Travar Auto-Target & Auto-Attack Sempre ON", self.var_hunt)

        sec_farm = self._criar_secao(col_esq, "🎒 MÓDULOS DE FARM, LOOT & EVOLUÇÃO")
        self._criar_chk(sec_farm, "🎒 Auto-Loot em Espiral (Coletar 9 SQMs ao redor)", self.var_auto_loot)
        self._criar_chk(sec_farm, "📜 Auto-Coletar e Renovar Missões (50 / 50)", self.var_missoes)
        self._criar_chk(sec_farm, "📈 Auto-Evoluir Atributos (Painel Progressão '+')", self.var_up_stats)

        sec_seg = self._criar_secao(col_esq, "🛡️ SEGURANÇA, SOBREVIVÊNCIA & IA")
        self._criar_chk(sec_seg, "🧠 IA Adaptativa Ativa (Auto-Ajuste por Loot/XP)", self.var_ia_ativa)
        self._criar_chk(sec_seg, "🔄 Auto-Reconectar se o Jogo Cair / Deslogar", self.var_reconnect)
        self._criar_chk(sec_seg, "🚨 Alarme Sonoro + Pausa em Morte / PK", self.var_anti_pk)
        self._criar_chk(sec_seg, "⏳ Pausar Bot se Stamina Baixar de 14:00", self.var_proteger_stamina)

        # Coluna Direita
        sec_tele = self._criar_secao(col_dir, "📡 TELEMETRIA EM TEMPO REAL")
        self.lbl_info1 = tk.Label(
            sec_tele, text="Level: --- | ML: --- | Stamina: ---",
            bg="#111a2e", fg="#4cd137", font=("Segoe UI", 8, "bold")
        )
        self.lbl_info1.pack(anchor="w")

        self.lbl_info2 = tk.Label(
            sec_tele, text="Missão: 0 / 0 | Loots: 0 (0/h)",
            bg="#111a2e", fg="#74b9ff", font=("Segoe UI", 8, "bold")
        )
        self.lbl_info2.pack(anchor="w")

        self.lbl_info3 = tk.Label(
            sec_tele, text="Falta XP: --- | Ciclo: 0ms | Tempo: 00:00:00",
            bg="#111a2e", fg="#ffeaa7", font=("Segoe UI", 8)
        )
        self.lbl_info3.pack(anchor="w")

        self.lbl_ia_status = tk.Label(
            sec_tele, text="IA: Burst_Sincronizado | Ações Otimizadas: 0",
            bg="#111a2e", fg="#00d2ff", font=("Segoe UI", 8, "italic")
        )
        self.lbl_ia_status.pack(anchor="w")

        sec_sim = self._criar_secao(col_dir, "📊 SIMULADOR DE BURST DPS & COOLDOWNS")
        self.lbl_simulacao = tk.Label(
            sec_sim, text="Clique abaixo para calcular o ganho real de DPS.",
            bg="#090f1c", fg="#55efc4", font=("Consolas", 8), justify="left", padx=6, pady=4
        )
        self.lbl_simulacao.pack(fill="x", pady=2)

        tk.Button(
            sec_sim, text="⚙️ Calcular Simulação de Dano Agora", bg="#3282b8", fg="white",
            font=("Segoe UI", 8, "bold"), relief="flat", command=self.executar_simulacao_dano
        ).pack(fill="x", pady=2)

        sec_logs = self._criar_secao(col_dir, "📋 REGISTRO DE ATIVIDADES E LOOTS")
        self.txt_log = tk.Text(
            sec_logs, height=8, bg="#070b14", fg="#55efc4",
            font=("Consolas", 8), state="disabled", relief="flat"
        )
        self.txt_log.pack(fill="both", expand=True)

        sec_erros = self._criar_secao(col_dir, "🛠️ MONITOR DE ERROS / DIAGNÓSTICO")
        self.txt_erros = tk.Text(
            sec_erros, height=4, bg="#1a0b0b", fg="#ff6b6b",
            font=("Consolas", 8), state="disabled", relief="flat"
        )
        self.txt_erros.pack(fill="both", expand=True)

    def _atualizar_label_velocidade(self, _=None):
        ms = int(self.var_delay_medio.get() * 1000)
        tag = "OVERDRIVE" if ms <= 240 else "Agressivo" if ms <= 450 else "Humanizado"
        self.lbl_speed.config(text=f"Ritmo de Disparo: ~{ms}ms ({tag})")
        self.salvar_config()

    def aplicar_perfil(self, _=None):
        p = self.var_perfil.get()
        if p == "Overdrive IA":
            self.var_ia_ativa.set(True)
            self.var_delay_medio.set(0.22)
            self.var_burst.set(True)
            self.var_auto_loot.set(True)
        elif p == "Burst Boss":
            self.var_ia_ativa.set(False)
            self.var_delay_medio.set(0.18)
            self.var_burst.set(True)
            self.var_priorizar_cd.set(True)
            self.var_auto_loot.set(False)
        elif p == "Farm Seguro":
            self.var_ia_ativa.set(True)
            self.var_delay_medio.set(0.45)
            self.var_anti_pk.set(True)
            self.var_proteger_stamina.set(True)
        elif p == "Stealth Lento":
            self.var_ia_ativa.set(False)
            self.var_delay_medio.set(0.85)
        self._atualizar_label_velocidade()
        self.log(f"Perfil '{p}' aplicado.")

    def executar_simulacao_dano(self):
        cd_jutsus = [20, 40, 60, 105, 145]
        dano_base = [520, 677, 702, 950, 1250]
        dps_padrao = sum(d / (c * 1.15) for d, c in zip(dano_base, cd_jutsus)) * 10
        dps_overdrive = sum(d / (c * 0.85) for d, c in zip(dano_base, cd_jutsus)) * 10 * 1.35
        ganho = ((dps_overdrive - dps_padrao) / dps_padrao) * 100
        texto = (
            f"DPS Padrão: {int(dps_padrao)}/s | Overdrive: {int(dps_overdrive)}/s\n"
            f"Ganho: +{ganho:.1f}% | Pico Burst (2 Abas): ~{sum(dano_base)*2} dano"
        )
        self.lbl_simulacao.config(text=texto)
        self.log("Simulação de Burst DPS atualizada.")

    def acionar_emergencia(self):
        self.ativo = False
        self.emergencia_acionada = True
        self.btn_toggle.config(text="ATIVAR BOT (ON)", bg="#0f9d58")
        self.log("🛑 EMERGÊNCIA ACIONADA! Todas as ações foram travadas.")

    def alternar_bot(self):
        self.emergencia_acionada = False
        self.ativo = not self.ativo
        if self.ativo:
            self.btn_toggle.config(text="PAUSAR BOT (OFF)", bg="#d93025")
            self.log("Motor Overdrive ATIVADO!")
        else:
            self.btn_toggle.config(text="ATIVAR BOT (ON)", bg="#0f9d58")
            self.log("Motor pausado.")

    def ativar_tudo(self):
        self.emergencia_acionada = False
        for var in [
            self.var_ia_ativa, self.var_burst, self.var_priorizar_cd,
            self.var_sustain, self.var_hunt, self.var_presets,
            self.var_auto_loot, self.var_missoes, self.var_up_stats,
            self.var_reconnect, self.var_anti_pk, self.var_proteger_stamina
        ]:
            var.set(True)
        self.var_delay_medio.set(0.20)
        self._atualizar_label_velocidade()
        if not self.ativo:
            self.alternar_bot()
        self.log("TODAS AS FUNÇÕES ATIVADAS NO MÁXIMO!")

    # Métodos thread-safe usando root.after para atualizar a UI a partir da thread do Playwright
    def log(self, msg):
        hora = time.strftime("%H:%M:%S")
        linha = f"[{hora}] {msg}\n"
        print(f"[OVERDRIVE] {linha.strip()}")
        def _inserir():
            if not self.encerrado:
                self.txt_log.config(state="normal")
                self.txt_log.insert("end", linha)
                self.txt_log.see("end")
                self.txt_log.config(state="disabled")
        self.root.after(0, _inserir)

    def log_erro(self, msg):
        hora = time.strftime("%H:%M:%S")
        linha = f"[{hora}] {msg}\n"
        def _inserir():
            if not self.encerrado:
                self.txt_erros.config(state="normal")
                self.txt_erros.insert("end", linha)
                self.txt_erros.see("end")
                self.txt_erros.config(state="disabled")
        self.root.after(0, _inserir)

    def atualizar_labels_telemetria(self, t1, t2, t3, t_ia):
        def _atualizar():
            if not self.encerrado:
                self.lbl_info1.config(text=t1)
                self.lbl_info2.config(text=t2)
                self.lbl_info3.config(text=t3)
                self.lbl_ia_status.config(text=t_ia)
        self.root.after(0, _atualizar)

    def _ao_fechar(self):
        self.salvar_config()
        self.encerrado = True
        self.root.destroy()


# =========================================================
# 3. INTERAÇÃO FÍSICA NÃO-BLOQUEANTE (CDP - isTrusted: true)
# =========================================================
def clique_fisico_coordenada(page, x, y, botao="left"):
    try:
        px = x + random.uniform(-3.5, 3.5)
        py = y + random.uniform(-3.5, 3.5)
        page.mouse.move(px, py, steps=2)
        page.mouse.down(button=botao)
        page.mouse.up(button=botao)
        return True
    except Exception:
        return False


def clique_elemento_real(page, locator):
    try:
        if locator.count() == 0:
            return False
        box = locator.first.bounding_box()
        if not box:
            return False
        alvo_x = box["x"] + (box["width"] * random.uniform(0.3, 0.7))
        alvo_y = box["y"] + (box["height"] * random.uniform(0.3, 0.7))
        return clique_fisico_coordenada(page, alvo_x, alvo_y)
    except Exception:
        return False


def tecla_rapida_real(page, tecla):
    try:
        page.keyboard.press(tecla, delay=random.randint(12, 28))
    except Exception:
        pass


def garantir_chave_ligada(page, hud, nome_modulo):
    try:
        el_texto = page.get_by_text(nome_modulo, exact=True)
        if el_texto.count() == 0:
            return
        linha = el_texto.first.locator("..")
        if "OFF" in linha.inner_text().upper():
            btn_off = linha.get_by_text("OFF", exact=True)
            if clique_elemento_real(page, btn_off):
                hud.log(f"Reativado: {nome_modulo}")
    except Exception as e:
        hud.log_erro(f"Toggle {nome_modulo}: {e}")


def formatar_tempo(segundos):
    h = int(segundos // 3600)
    m = int((segundos % 3600) // 60)
    s = int(segundos % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


# =========================================================
# 4. THREAD DO PLAYWRIGHT (RODA EM SEGUNDO PLANO SEM TRAVAR A UI)
# =========================================================
def worker_playwright(hud: PainelUnicoOverdriveHUD):
    hud.log("Abrindo navegador em thread dedicada...")
    try:
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

            context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            """)

            page = context.pages[0] if context.pages else context.new_page()
            # Usa domcontentloaded para não travar esperando recursos infinitos do jogo
            page.goto(URL_JOGO, wait_until="domcontentloaded", timeout=60000)
            hud.log("Jogo carregado! Painel conectado em tempo real.")

            prox_combate = time.time() + 0.5
            prox_loot = time.time() + 1.0
            prox_telemetria = time.time() + 1.5
            prox_preset = time.time() + 6.5

            fila_prioridade_cd = ["4", "1", "2", "4", "1", "3", "5", "2", "6", "7", "8", "9", "0"]
            fila_linear = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
            idx_tecla = 0

            centro_x, centro_y, sqm = 683, 384, 48
            grade_loot = [
                (0, 0), (-sqm, 0), (sqm, 0), (0, -sqm), (0, sqm),
                (-sqm, -sqm), (sqm, -sqm), (-sqm, sqm), (sqm, sqm)
            ]
            idx_loot_sqm = 0

            preset_atual = "1"
            qtd_loots_anterior = 0
            loots_total = 0
            progresso_missao_ant = 0
            rajada_atual = 3

            while not hud.encerrado:
                inicio_ciclo = time.time()
                agora = time.time()

                if hud.emergencia_acionada:
                    time.sleep(0.05)
                    continue

                # 1. Watchdog de Auto-Reconexão
                if hud.var_reconnect.get() and random.random() < 0.05:
                    try:
                        if "login" in page.url.lower() or page.locator("text=Login").count() > 0:
                            hud.log("⚠️ Queda detectada! Reconectando...")
                            page.goto(URL_JOGO, wait_until="domcontentloaded")
                            time.sleep(4.0)
                            continue
                    except Exception as e:
                        hud.log_erro(f"Reconnect: {e}")

                # 2. Telemetria, Loots, Missões e IA
                if agora >= prox_telemetria:
                    prox_telemetria = agora + random.uniform(1.4, 2.0)
                    try:
                        texto_body = page.locator("body").inner_text(timeout=350)
                        lvl = re.search(r"LEVEL\s+(\d+)", texto_body, re.I)
                        ml = re.search(r"MAGIC LEVEL\s+(\d+)", texto_body, re.I)
                        stam = re.search(r"STAMINA\s+(\d{1,2}:\d{2})", texto_body, re.I)
                        xp_falta = re.search(r"Falta\s+([\d.,]+\s*XP)", texto_body, re.I)
                        missao = re.search(r"(\d+)\s*/\s*(\d+)", texto_body)

                        str_lvl = lvl.group(1) if lvl else "---"
                        str_ml = ml.group(1) if ml else "---"
                        str_stam = stam.group(1) if stam else "---"
                        str_xp = xp_falta.group(1) if xp_falta else "---"
                        str_missao = f"{missao.group(1)} / {missao.group(2)}" if missao else "0 / 0"

                        loots = re.findall(r"Sistema: ! Pegou [^\n]+", texto_body)
                        if len(loots) > qtd_loots_anterior:
                            novos = len(loots) - qtd_loots_anterior
                            qtd_loots_anterior = len(loots)
                            loots_total += novos
                            hud.ia.registrar_recompensa(peso=novos * 1.5)
                            hud.log(f"🎒 +{novos} Loot: {loots[-1].replace('Sistema: ! ', '')}")

                        if missao:
                            atual_m, total_m = int(missao.group(1)), int(missao.group(2))
                            if atual_m > progresso_missao_ant:
                                hud.ia.registrar_recompensa(peso=(atual_m - progresso_missao_ant) * 0.8)
                            progresso_missao_ant = atual_m

                            if hud.ativo and hud.var_missoes.get() and atual_m >= total_m > 0:
                                loc_missao = page.get_by_text(missao.group(0), exact=True)
                                if clique_elemento_real(page, loc_missao):
                                    hud.log(f"📜 Missão concluída ({str_missao})!")

                        if hud.ativo and hud.var_ia_ativa.get():
                            resultado_ia = hud.ia.avaliar_e_adaptar()
                            if resultado_ia:
                                nome_est, params = resultado_ia
                                hud.var_delay_medio.set(params["delay"])
                                rajada_atual = params["rajada"]
                                hud.root.after(0, hud._atualizar_label_velocidade)
                                hud.log(f"🧠 IA ajustou para [{nome_est}] (Score: {params['score']:.2f})")

                        decorrido = max(1.0, agora - hud.inicio_sessao)
                        loots_hora = int((loots_total / decorrido) * 3600)
                        latencia_ms = int((time.time() - inicio_ciclo) * 1000)

                        hud.atualizar_labels_telemetria(
                            f"Level: {str_lvl} | ML: {str_ml} | Stamina: {str_stam}",
                            f"Missão: {str_missao} | Loots: {loots_total} ({loots_hora}/h)",
                            f"Falta: {str_xp} | Ciclo: {latencia_ms}ms | {formatar_tempo(decorrido)}",
                            f"IA: {hud.ia.estrategia_atual} | Ações Otimizadas: {hud.ia.acoes_economizadas}",
                        )

                        if hud.ativo and hud.var_anti_pk.get() and "Você morreu" in texto_body:
                            hud.root.after(0, hud.acionar_emergencia)
                            try:
                                winsound.Beep(1400, 600)
                            except Exception:
                                pass

                        if hud.ativo and hud.var_proteger_stamina.get() and stam:
                            if int(str_stam.split(":")[0]) < 14:
                                hud.log(f"⏳ Stamina crítica ({str_stam})! Pausando.")
                                hud.root.after(0, hud.alternar_bot)

                        if hud.ativo and hud.var_up_stats.get() and random.random() < 0.25:
                            btn_mais = page.get_by_text("+", exact=True)
                            if btn_mais.count() > 0:
                                clique_elemento_real(page, btn_mais)
                    except Exception as e:
                        hud.log_erro(f"Telemetria: {e}")

                # 3. Combate
                if hud.ativo and agora >= prox_combate:
                    base = hud.var_delay_medio.get()
                    prox_combate = agora + random.uniform(base * 0.8, base * 1.2)

                    if hud.var_presets.get() and agora >= prox_preset:
                        prox_preset = agora + random.uniform(6.0, 8.5)
                        preset_atual = "2" if preset_atual == "1" else "1"
                        try:
                            aba = page.get_by_text(preset_atual, exact=True)
                            clique_elemento_real(page, aba)
                            hud.ia.acoes_economizadas += 1
                        except Exception as e:
                            hud.log_erro(f"Preset: {e}")
                    else:
                        if hud.var_burst.get():
                            fila = fila_prioridade_cd if hud.var_priorizar_cd.get() else fila_linear
                            for _ in range(rajada_atual):
                                tecla_rapida_real(page, fila[idx_tecla % len(fila)])
                                idx_tecla += 1

                        if hud.var_sustain.get():
                            tecla_rapida_real(page, "F1")
                            if random.random() < 0.25:
                                for mod in ["AUTO HEAL", "CHAKRA DOWN", "AUTO HASTE", "AUTO BUFF"]:
                                    garantir_chave_ligada(page, hud, mod)

                        if hud.var_hunt.get() and random.random() < 0.25:
                            for mod in ["AUTO TARGET", "AUTO ATTACK"]:
                                garantir_chave_ligada(page, hud, mod)

                # 4. Auto-Loot em Espiral
                if hud.ativo and hud.var_auto_loot.get() and agora >= prox_loot:
                    prox_loot = agora + random.uniform(0.45, 0.75)
                    dx, dy = grade_loot[idx_loot_sqm % len(grade_loot)]
                    idx_loot_sqm += 1
                    clique_fisico_coordenada(page, centro_x + dx, centro_y + dy, botao="right")

                time.sleep(0.02)

            context.close()
    except Exception as erro_fatal:
        hud.log_erro(f"Falha no Playwright: {erro_fatal}")


if __name__ == "__main__":
    # 1. Cria a janela gráfica na Thread Principal (aparece imediatamente)
    painel = PainelUnicoOverdriveHUD()
    painel.log("Painel carregado! Iniciando navegador em segundo plano...")

    # 2. Inicia o Playwright em uma Thread separada para nunca travar a janela
    thread_bot = threading.Thread(target=worker_playwright, args=(painel,), daemon=True)
    thread_bot.start()

    # 3. Mantém o loop nativo do Windows para a janela ficar sempre visível e responsiva
    painel.root.mainloop()