import socket
import time

IP_LASER = '192.168.10.90'
PUERTO_LASER = 45678

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
    doc = nome.strip() + ".bpd"

    print("[INFO] Verificando estado do laser...")
    estado = obter_estado_laser()

    if estado == 2:
        print("[AÇÃO] Laser está marcando. Enviando StopMark...")
        enviar_comando("StopMark;;")
        esperar_estado_idle()

    print(f"[AÇÃO] Abrindo documento: {doc}")
    enviar_comando(f"OpenDoc,{doc};;")
    esperar_estado_idle()

    print("[AÇÃO] Iniciando marcação...")
    enviar_comando("StartMark;;")
    print("[OK] Marcação concluída.")

def ciclo_principal():
    print("[SISTEMA] Aguardando escaneamento. Pressione Ctrl+C para sair.")
    try:
        while True:
            entrada = input("Código escaneado: ").strip()
            if entrada:
                marcar_documento(entrada)
    except KeyboardInterrupt:
        print("\n[SISTEMA] Encerrado pelo usuário.")

if __name__ == "__main__":
    ciclo_principal()
