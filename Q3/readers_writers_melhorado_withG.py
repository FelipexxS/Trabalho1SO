import threading
import time
import keyboard  # pip install keyboard
import matplotlib.pyplot as plt

# ==============================
# Parâmetros Iniciais
# ==============================
writers_init_threads_length = 6   # Número de threads de escritores inicial
readers_init_threads_length = 50  # Número de threads de leitores inicial

# Contador de leitores (quantos estão lendo agora)
readers = 0
# Contador de escritores (quantos estão escrevendo agora)
active_writers = 0

# Semáforos
mutex = threading.Semaphore(1)       # Protege o contador de leitores
roomIsEmpty = threading.Semaphore(1) # Garante exclusão mútua (ninguém na sala)
turnstile = threading.Semaphore(1)   # Controla a preferência para escritores

# Evento para sinal de parada
stop_execution = threading.Event()

# ==============================
# Variáveis para Coleta de Dados
# ==============================
time_data = []
readers_data = []
writers_data = []
data_lock = threading.Lock()  # Para evitar concorrência na hora de gravar dados

start_time = time.time()       # Momento em que o programa começou

# ==============================
# Funções de Escrita e Leitura
# ==============================
def writer():
    global active_writers
    while not stop_execution.is_set():
        # Escritor requer o "turnstile"
        turnstile.acquire()
        roomIsEmpty.acquire()
        turnstile.release()

        # Início da escrita
        with data_lock:
            active_writers += 1

        print(f'\n{threading.current_thread().name} está escrevendo algo na região crítica.')
        time.sleep(1)  # Simula tempo de escrita

        # Fim da escrita
        with data_lock:
            active_writers -= 1

        roomIsEmpty.release()
        time.sleep(1)  # Simula tempo fora da sala

def reader():
    global readers
    while not stop_execution.is_set():
        # Respeita o turnstile (para não furar fila de escritores)
        turnstile.acquire()
        turnstile.release()

        mutex.acquire()
        readers += 1
        if readers == 1:
            roomIsEmpty.acquire()  # Primeiro leitor bloqueia a sala
        mutex.release()

        print(f'\n{threading.current_thread().name} está lendo algo na região crítica.')
        time.sleep(1)  # Simula tempo de leitura

        mutex.acquire()
        readers -= 1
        if readers == 0:
            roomIsEmpty.release()  # Último leitor libera a sala
        mutex.release()

        time.sleep(1)  # Simula tempo fora da sala

# ==============================
# Thread para criar mais leitores continuamente
# ==============================
def increase_readers_thread_length():
    global readers_threads
    while not stop_execution.is_set():
        time.sleep(0.09)  # Intervalo de criação de novos leitores
        if not stop_execution.is_set():
            new_reader_thread = threading.Thread(target=reader, 
                                                 name=f'Leitor {len(readers_threads) + 1}')
            readers_threads.append(new_reader_thread)
            new_reader_thread.start()

# ==============================
# Thread de Monitoramento (coleta de dados para o gráfico)
# ==============================
def monitor_data():
    while not stop_execution.is_set():
        with data_lock:
            current_time = time.time() - start_time
            time_data.append(current_time)
            # readers é global (número de leitores lendo agora)
            readers_data.append(readers)
            # active_writers é global (0 ou 1, dependendo se alguém está escrevendo)
            writers_data.append(active_writers)

        time.sleep(0.1)  # Intervalo de amostragem dos dados

# ==============================
# Programa Principal
# ==============================
if __name__ == '__main__':
    print('\nPressione qualquer tecla para finalizar o script...')

    # Cria as threads iniciais
    writers_threads = [threading.Thread(target=writer, name=f'Escritor {i+1}') 
                       for i in range(writers_init_threads_length)]
    readers_threads = [threading.Thread(target=reader, name=f'Leitor {i+1}') 
                       for i in range(readers_init_threads_length)]

    # Inicia escritores e leitores
    for t in writers_threads + readers_threads:
        t.start()

    # Thread que adiciona ainda mais leitores durante a execução
    monitor_thread = threading.Thread(target=increase_readers_thread_length, 
                                      name='Monitor')
    monitor_thread.start()

    # Thread que coleta dados para o gráfico
    data_thread = threading.Thread(target=monitor_data, name='DataMonitor')
    data_thread.start()

    # Espera o usuário pressionar qualquer tecla para encerrar
    keyboard.read_key()
    stop_execution.set()  # Sinaliza parada para todas as threads

    print('\nScript finalizado pela entrada. Aguardando threads...')

    # Aguarda todas as threads terminarem
    for t in writers_threads + readers_threads:
        t.join()
    monitor_thread.join()
    data_thread.join()

    # ==============================
    # Plot dos Dados Coletados
    # ==============================
    plt.figure(figsize=(10, 5))
    plt.plot(time_data, readers_data, label='Leitores Ativos')
    plt.plot(time_data, writers_data, label='Escritores Ativos', color='red')

    plt.title('Quantidade de Leitores e Escritores ao longo do tempo')
    plt.xlabel('Tempo (segundos)')
    plt.ylabel('Número de Threads Ativas')
    plt.legend(loc='upper right')
    plt.grid(True)

    # Exibe o gráfico
    plt.show()
