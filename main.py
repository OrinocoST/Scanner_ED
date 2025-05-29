import socket
import time
import sys
import platform

if not platform.system() == "Windows":
    import select

IP_LASER = '192.168.10.90'
PUERTO_LASER = 45678

ocupado = False
ultimo_codigo = ""
hora_ultimo_codigo = 0
ventana_antirrep = 2
falhas_consecutivas = 0
FALHAS_LIMITE = 5
PAUSA_APOS_FALHAS = 30
SISTEMA_WINDOWS = platform.system() == "Windows"

def enviar_comando(comando, tentativas=3):
    for intento in range(tentativas):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect((IP_LASER, PUERTO_LASER))
                s.sendall(comando.encode())
                resposta = s.recv(1024).decode('utf-8', errors='replace').strip()
                print(f">> {comando.strip()} → {resposta}")
                return resposta
        except Exception as e:
            print(f"[ERROR] Tentativa {intento + 1}/{tentativas} falhou: {e}")
            time.sleep(1)
    print("[FALHA] Todas as tentativas falharam para o comando:", comando)
    return ""

def obter_estado_laser():
    resposta = enviar_comando("GetMarkStatus;;")
    try:
        return int(resposta.replace(";", "").strip())
    except:
        return -1

def esperar_estado_idle(timeout=5):
    print("[INFO] Aguardando estado Idle (0)...")
    inicio = time.time()
    while time.time() - inicio < timeout:
        if obter_estado_laser() == 0:
            print("[OK] Estado Idle alcançado.")
            return True
        time.sleep(0.2)
    print("[FALHA] Timeout ao aguardar estado Idle.")
    return False

def marcar_documento(nome):
    global ocupado, falhas_consecutivas
    ocupado = True

    doc = nome.strip() + ".bpd"
    print("[INFO] Verificando estado do laser...")

    estado = obter_estado_laser()
    if estado == -1:
        print("[ERRO] Não foi possível obter o estado do laser. Abortando.")
        falhas_consecutivas += 1
        ocupado = False
        return

    if estado == 2:
        print("[AÇÃO] Laser está marcando. Enviando StopMark...")
        enviar_comando("StopMark;;")
        if not esperar_estado_idle():
            print("[ERRO] Timeout após StopMark. Abortando.")
            falhas_consecutivas += 1
            ocupado = False
            return

    print(f"[AÇÃO] Abrindo documento: {doc}")
    if enviar_comando(f"OpenDoc,{doc};;") == "":
        print("[ERRO] Falha ao abrir documento. Abortando.")
        falhas_consecutivas += 1
        ocupado = False
        return

    if not esperar_estado_idle():
        print("[ERRO] Timeout após abrir documento. Abortando.")
        falhas_consecutivas += 1
        ocupado = False
        return

    print("[AÇÃO] Iniciando marcação...")
    if enviar_comando("StartMark;;") == "":
        print("[ERRO] Falha ao iniciar marcação. Abortando.")
        falhas_consecutivas += 1
        ocupado = False
        return

    print("[OK] Marcação concluída.")
    falhas_consecutivas = 0
    time.sleep(1)
    ocupado = False

def ciclo_principal():
    global ocupado, ultimo_codigo, hora_ultimo_codigo, falhas_consecutivas

    print("[SISTEMA] Inicializado. Pronto para escanear. Ctrl+C para sair.")
    try:
        while True:
            if SISTEMA_WINDOWS:
                entrada = input("Código escaneado: ").strip()
            else:
                if ocupado:
                    time.sleep(0.1)
                    continue
                print("Código escaneado: ", end="", flush=True)
                rlist, _, _ = select.select([sys.stdin], [], [], 0.5)
                if not rlist:
                    continue
                entrada = sys.stdin.readline().strip()

            agora = time.time()

            if ocupado:
                print("[IGNORADO] Sistema ocupado. Aguarde o fim da marcação.")
                continue

            if entrada == "":
                continue

            if entrada == ultimo_codigo and (agora - hora_ultimo_codigo) < ventana_antirrep:
                print("[IGNORADO] Código repetido detectado nos últimos 2 segundos.")
                continue

            ultimo_codigo = entrada
            hora_ultimo_codigo = agora

            marcar_documento(entrada)

            if falhas_consecutivas >= FALHAS_LIMITE:
                print(f"[ALERTA] {falhas_consecutivas} falhas seguidas. Aguardando {PAUSA_APOS_FALHAS}s.")
                time.sleep(PAUSA_APOS_FALHAS)
                falhas_consecutivas = 0

    except KeyboardInterrupt:
        print("\n[SISTEMA] Encerrado pelo usuário.")

if __name__ == "__main__":
    ciclo_principal()
