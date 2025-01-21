import threading
import time
import keyboard  # pip install keyboard
import matplotlib.pyplot as plt

# ==============================
# Parâmetros Iniciais
# ==============================
writers_init_threads_length = 6   # Número de threads de escritores inicial
readers_init_threads_length = 50  # Número de threads de leitores inicial

# Contadores de leitores e escritores
readers = 0
active_writers = 0  # indica se (e quantos) escritores estão escrevendo agora

# Semáforos de sincronização
mutex = threading.Semaphore(1)       # Protege o contador de leitores
roomIsEmpty = threading.Semaphore(1) # Garante exclusão mútua (sala vazia)
stop_execution = threading.Event()   # Evento para dar o sinal de parada

# ==============================
# Variáveis para Coleta de Dados
# ==============================
time_data = []
readers_data = []
writers_data = []
data_lock = threading.Lock()  # Evita condições de corrida ao acessar as listas
start_time = time.time()       # Marca o início da execução

# ==============================
# Funções de Escrita e Leitura
# ==============================
def writer():
    global active_writers
    while not stop_execution.is_set():
        roomIsEmpty.acquire()  # Bloqueia a sala para poder escrever

        # Indica que este escritor começou a escrever
        with data_lock:
            active_writers += 1

        print(f'\n{threading.current_thread().name} está escrevendo algo na região crítica.')
        time.sleep(1)  # Simula tempo de escrita

        # Ao terminar, decrementa o contador de escritores
        with data_lock:
            active_writers -= 1

        roomIsEmpty.release()   # Libera a sala
        time.sleep(1)          # Simula tempo fora da sala

def reader():
    global readers
    while not stop_execution.is_set():
        mutex.acquire()  # Protege o contador de leitores
        readers += 1
        if readers == 1:
            roomIsEmpty.acquire()  # Se for o primeiro leitor, bloqueia a sala
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
# Função que cria mais leitores
# ==============================
def increase_readers_thread_length():
    global readers_threads
    while not stop_execution.is_set():
        time.sleep(0.09)  # Intervalo de criação de novos leitores
        if not stop_execution.is_set():
            new_reader_thread = threading.Thread(target=reader, name=f'Leitor {len(readers_threads) + 1}')
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
            # readers é o número de leitores ativos agora
            readers_data.append(readers)
            # active_writers (nesse código "piorado", pode ser 0 ou 1, pois cada escritor adquire a sala sozinho)
            writers_data.append(active_writers)

        time.sleep(0.1)  # Intervalo de amostragem dos dados

# ==============================
# Programa Principal
# ==============================
if __name__ == '__main__':
    # Criação das threads iniciais
    writers_threads = [threading.Thread(target=writer, name=f'Escritor {index + 1}') 
                       for index in range(writers_init_threads_length)]
    readers_threads = [threading.Thread(target=reader, name=f'Leitor {index + 1}') 
                       for index in range(readers_init_threads_length)]

    print('\nPressione qualquer tecla para finalizar o script...')

    # Inicia as threads de leitores e escritores
    for trd in (readers_threads + writers_threads):
        trd.start()

    # Thread que cria mais leitores durante a execução
    monitor_thread = threading.Thread(target=increase_readers_thread_length, name='Monitor')
    monitor_thread.start()

    # Thread que coleta dados para o gráfico
    data_thread = threading.Thread(target=monitor_data, name='DataMonitor')
    data_thread.start()

    # Aguarda o usuário pressionar uma tecla para encerrar
    keyboard.read_key()
    stop_execution.set()  # Sinaliza parada

    print('\nScript finalizado pela entrada. Aguardando threads...')

    # Aguarda todas as threads terminarem
    for t in (writers_threads + readers_threads):
        t.join()
    monitor_thread.join()
    data_thread.join()

    # ==============================
    # Plot dos Dados Coletados
    # ==============================
    plt.figure(figsize=(10, 5))
    plt.plot(time_data, readers_data, label='Leitores Ativos')
    plt.plot(time_data, writers_data, label='Escritores Ativos', color='red')

    plt.title('Leitores vs Escritores ao longo do tempo (sem preferência para escritores)')
    plt.xlabel('Tempo (segundos)')
    plt.ylabel('Quantidade de Threads Ativas')
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.show()
