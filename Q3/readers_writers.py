import threading
import time
import keyboard # pip install keyboard

writers_init_threads_length = 2 # Número de threads de escritores inicial
readers_init_threads_length = 5 # Número de threads de leitores inicial
readers = 0 # Contador para ter controle do número de leitores
mutex = threading.Semaphore(1) # Semáforo para proteger o contador de leitores
roomIsEmpty = threading.Semaphore(1) # Semáforo para verificar se a sala (região crítica) está vazia ou não
stop_execution = threading.Event() # Evento para dar o sinal de parada

def writer():
  while not stop_execution.is_set(): # Continua executando enquanto o sinal não estiver setado
    roomIsEmpty.acquire() # Bloqueia a sala para poder escrever
    
    print(f'\n{threading.current_thread().name} está escrevendo algo na região critíca.')
    time.sleep(1)
    
    roomIsEmpty.release() # Libera a sala
    
    time.sleep(1) # Simula que está fazendo algo fora da sala

def reader():
  global readers
  while not stop_execution.is_set(): # Continua executando enquanto o sinal não estiver setado
    mutex.acquire() # Impede que outra thread modifique o contador
    readers += 1
    if readers == 1:
      roomIsEmpty.acquire() # Se tiver algum leitor, bloqueia a entrada na sala
    mutex.release() # Libera que outra thread modifique o contador
    
    print(f'\n{threading.current_thread().name} está lendo algo na região critíca.')
    time.sleep(1)
    
    mutex.acquire()
    readers -= 1
    if readers == 0:
      roomIsEmpty.release() # Último leitor libera a sala para o escritor
    mutex.release()
    
    time.sleep(1) # Simula que está fazendo algo fora da sala

def increase_readers_thread_length(): # Cria mais leitores no tempo de execução
  global readers_init_threads_length
  global readers_threads
  
  while not stop_execution.is_set():
    time.sleep(2) # Diminuir esse tempo de espera, pode causar starvation nos escritores
    if not stop_execution.is_set():
      new_reader_thread = threading.Thread(target=reader, name=f'Leitor {len(readers_threads) + 1}')
      readers_threads.append(new_reader_thread)
      new_reader_thread.start()
      
      
    
if __name__ == '__main__':
  writers_threads = [threading.Thread(target=writer, name=f'Escritor {index + 1}') for index in range(writers_init_threads_length)]
  readers_threads = [threading.Thread(target=reader, name=f'Leitor {index + 1}') for index in range(readers_init_threads_length)] # Valores muito altos podem causar starvation dos escritores
  
  print('\nPressione qualquer tecla para finalizar o script...')
  
  for trd in (readers_threads + writers_threads):
    trd.start()

  # Thread monitora para adicionar mais leitores na execução do script
  monitor_thread = threading.Thread(target=increase_readers_thread_length, name=f'Monitor')
  monitor_thread.start()
  
  keyboard.read_key() # Se o usuário pressionar uma tecla, ela é imediatamente lida
  stop_execution.set() # Dispara o sinal de parada do script

  print('\nScript finalizado pela entrada.')