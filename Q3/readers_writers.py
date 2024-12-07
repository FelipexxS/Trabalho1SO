import threading
import time
import keyboard # pip install keyboard

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
    
if __name__ == '__main__':
  writers_threads = [threading.Thread(target=writer, name=f'Escritor {index + 1}') for index in range(2)]
  readers_threads = [threading.Thread(target=reader, name=f'Leitor {index + 1}') for index in range(16)] # Valores muito altos podem causar starvation dos escritores
  
  print('\nPressione qualquer tecla para finalizar o script...')
  for trd in (readers_threads + writers_threads):
    trd.start()
  
  keyboard.read_key() # Se o usuário pressionar uma tecla, ela é imediatamente lida
  stop_execution.set() # Dispara o sinal de parada do script

  print('\nScript finalizado pela entrada.')