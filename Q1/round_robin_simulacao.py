from collections import deque
import random

# Classe pra representar um processo do sistema
class Process:
  def __init__(self, name, burst_time):
    self.name = name
    self.burst_time = burst_time
    self.remaining_time = burst_time
    self.initial_time = None
    self.completion_time = None

# Algoritmo round robin pra simular o comportamento de um escalonador
def round_robin(processes, quantum):
  ready_queue = deque(processes) # Usamos uma fila de dupla extremidade
  current_time = 0 # Variável pra controlar o tempo de execução
  finished_processes = 0
  total_processes_len = len(processes)
  waiting_time_list = []
  return_time_list = []

  # Itera enquanto existir processos na fila de prontos
  while finished_processes < total_processes_len:
    # Em cada iteração o processo é executado por um tempo quantum
    # Se ele tiver um tempo de exec menor, finaliza sua execução
    # Se ele tiver um tempo de exec maior, retornará para a fila de prontos e mais tarde será executado nvamente
    chosen_process = ready_queue.popleft()
      
    if chosen_process.initial_time is None:
      chosen_process.initial_time = current_time
      
    if chosen_process.remaining_time > quantum:
      current_time += quantum
      chosen_process.remaining_time -= quantum
      ready_queue.append(chosen_process)
      print(f"\nTempo {current_time}: Executando {chosen_process.name} por {quantum} unidades de tempo. Tempo restante: {chosen_process.remaining_time}")
    else:
      current_time += chosen_process.remaining_time
      chosen_process.completion_time = current_time
      finished_processes += 1
      print(f"\nTempo {current_time}: Executando {chosen_process.name} por {chosen_process.remaining_time} unidades de tempo. Processo concluiu sua tarefa!")
      
      # Tempo de chegada igual para todos os N processos
      wait_time = chosen_process.initial_time - 0
      return_time = chosen_process.completion_time - 0
      waiting_time_list.append(wait_time)
      return_time_list.append(return_time)
    
    current_time += 1 # Mudança de contexto

  # Agora só precisa contabilizar os tempos médios
  process_flow = finished_processes / current_time
  average_waiting_time = sum(waiting_time_list) / total_processes_len
  average_return_time = sum(return_time_list) / total_processes_len
   
  print(f"\nTempo médio de espera: {average_waiting_time:.2f}")
  print(f"\nTempo médio de retorno: {average_return_time:.2f}")
  print(f"\nVazão: {process_flow:.2f}")

def main(chosen_quantum):
  print(f"\n=-=-=-=-=-=-=-=-= Escalonador Round Robin quantum = {chosen_quantum} =-=-=-=-=-=-=-=-=\n")
  round_robin(processes, chosen_quantum)
  print(f"\n=-=-=-=-=-=-=-=-=-=-=-=-=-= Fim da Execução =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n")

if __name__ == "__main__":
    # Define os intervalos de tempo
    T1 = 0
    T2 = 5
    T3 = 20
    T4 = 25

    num_processes = 10

    # Gera os processos com burst times aleatórios em intervalos diferentes
    processes = []
    for i in range(num_processes):
        if i % 2 == 0:
            burst_time = random.randint(1, 5)  # Intervalo [T1, T2]
        else:
            burst_time = random.randint(10, 20)  # Intervalo [T3, T4]
        processes.append(Process(f"P{i+1}", burst_time))

    # Executa o Round Robin com diferentes quanta
    for quantum in [2, 4, 6]:
        main(quantum)
