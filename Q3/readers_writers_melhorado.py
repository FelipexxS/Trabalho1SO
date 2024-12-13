import threading
import time
import keyboard  # pip install keyboard

writers_init_threads_length = 6   # Número de threads de escritores inicial
readers_init_threads_length = 50   # Número de threads de leitores inicial

# Contador de leitores
readers = 0

# Semáforos:
mutex = threading.Semaphore(1)       # Protege o contador de leitores
roomIsEmpty = threading.Semaphore(1) # Garante exclusão mútua (ninguém na sala)
turnstile = threading.Semaphore(1)   # Controla a entrada, garantindo que se um escritor quer entrar, leitores não entrem até que escritores entrem primeiro

stop_execution = threading.Event()   # Evento para sinal de parada

def writer():
    while not stop_execution.is_set():
        # Escritor requer o "turnstile" para sinalizar sua intenção de escrever antes de aguardar a sala vazia
        turnstile.acquire()          # Bloqueia a entrada de novos leitores enquanto aguarda
        roomIsEmpty.acquire()        # Garante exclusão mútua completa para escrever
        turnstile.release()          # Libera para que outros, inclusive leitores, possam tentar entrar após este escritor

        print(f'\n{threading.current_thread().name} está escrevendo algo na região crítica.')
        time.sleep(1)

        roomIsEmpty.release()        # Libera a sala após a escrita
        time.sleep(1)                # Simula tempo fora da sala

def reader():
    global readers
    while not stop_execution.is_set():
        # Leitores também passam pelo turnstile, para garantir que não "pulem a fila" de escritores que estejam esperando
        turnstile.acquire()
        turnstile.release()

        mutex.acquire()
        readers += 1
        if readers == 1:
            roomIsEmpty.acquire()   # Primeiro leitor bloqueia a sala
        mutex.release()

        print(f'\n{threading.current_thread().name} está lendo algo na região crítica.')
        time.sleep(1)

        mutex.acquire()
        readers -= 1
        if readers == 0:
            roomIsEmpty.release()   # Último leitor libera a sala
        mutex.release()

        time.sleep(1)

def increase_readers_thread_length():
    global readers_threads
    while not stop_execution.is_set():
        time.sleep(0.09)  # Como antes, pode alterar o intervalo de criação de novos leitores
        if not stop_execution.is_set():
            new_reader_thread = threading.Thread(target=reader, name=f'Leitor {len(readers_threads) + 1}')
            readers_threads.append(new_reader_thread)
            new_reader_thread.start()

if __name__ == '__main__':
    writers_threads = [threading.Thread(target=writer, name=f'Escritor {index + 1}') for index in range(writers_init_threads_length)]
    readers_threads = [threading.Thread(target=reader, name=f'Leitor {index + 1}') for index in range(readers_init_threads_length)]

    print('\nPressione qualquer tecla para finalizar o script...')

    for trd in (readers_threads + writers_threads):
        trd.start()

    # Thread monitora para adicionar mais leitores na execução
    monitor_thread = threading.Thread(target=increase_readers_thread_length, name='Monitor')
    monitor_thread.start()

    keyboard.read_key()   # Aguarda o usuário pressionar uma tecla
    stop_execution.set()  # Sinaliza parada

    print('\nScript finalizado pela entrada.')
