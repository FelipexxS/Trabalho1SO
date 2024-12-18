from collections import deque
import random
import copy
import statistics
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

# Configuração de estilo para os gráficos
sns.set(style="whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)

# Classe para representar um processo do sistema
class Process:
    def __init__(self, name, burst_time):
        self.name = name
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.initial_time = None
        self.completion_time = None
        self.last_executed_time = 0
        self.waiting_time = 0

    def reset(self):
        self.remaining_time = self.burst_time
        self.initial_time = None
        self.completion_time = None
        self.last_executed_time = 0
        self.waiting_time = 0

# Algoritmo Round Robin para simular o comportamento de um escalonador
def round_robin(processes, quantum):
    ready_queue = deque(processes)
    current_time = 0
    finished_processes = 0
    total_processes_len = len(processes)
    waiting_time_list = []
    return_time_list = []
    execution_sequence = []

    # Como os processos chegam todos ao tempo 0, arrival_time = 0 para simplificar
    while finished_processes < total_processes_len:
        if not ready_queue:
            current_time +=1
            continue

        chosen_process = ready_queue.popleft()

        # Caso o processo esteja sendo executado pela primeira vez
        if chosen_process.initial_time is None:
            chosen_process.initial_time = current_time

        # Tempo de execução: min(quantum, tempo_restante_do_processo)
        exec_time = min(quantum, chosen_process.remaining_time)
        chosen_process.remaining_time -= exec_time

        # Armazena no histórico de execução (para o diagrama de Gantt)
        execution_sequence.append((current_time, chosen_process.name, exec_time))

        current_time += exec_time

        if chosen_process.remaining_time > 0:
            # Processo não finalizado, retorna para a fila
            ready_queue.append(chosen_process)
            print(f"Tempo {current_time}: Executando {chosen_process.name} por {exec_time} unidades de tempo. Tempo restante: {chosen_process.remaining_time}")
        else:
            # Processo finalizado
            chosen_process.completion_time = current_time
            finished_processes += 1
            print(f"Tempo {current_time}: Executando {chosen_process.name} por {exec_time} unidades de tempo. Processo concluiu sua tarefa!")

            # Como todos chegaram no tempo 0, o tempo de espera será (tempo inicial - chegada)
            # E o tempo de retorno será (tempo de conclusão - chegada)
            # Chegada = 0
            wait_time = chosen_process.initial_time
            return_time = chosen_process.completion_time
            waiting_time_list.append(wait_time)
            return_time_list.append(return_time)

        # Tempo para troca de contexto (se ainda houver processos a executar)
        if ready_queue:
            current_time += 1
            print(f"Tempo {current_time}: Troca de contexto.")

    # Cálculo das métricas
    average_waiting_time = sum(waiting_time_list) / total_processes_len
    average_return_time = sum(return_time_list) / total_processes_len
    waiting_time_std = statistics.stdev(waiting_time_list) if len(waiting_time_list) > 1 else 0
    return_time_std = statistics.stdev(return_time_list) if len(return_time_list) > 1 else 0
    process_flow = finished_processes / current_time if current_time > 0 else 0

    metrics = {
        'quantum': quantum,
        'average_waiting_time': average_waiting_time,
        'waiting_time_std': waiting_time_std,
        'average_return_time': average_return_time,
        'return_time_std': return_time_std,
        'throughput': process_flow,
        'execution_sequence': execution_sequence
    }

    print(f"\nTempo médio de espera: {average_waiting_time:.2f}")
    print(f"Tempo médio de retorno: {average_return_time:.2f}")
    print(f"Vazão: {process_flow:.2f}")

    return metrics

# Função para simular Round Robin para diferentes quanta
def simulate_round_robin(processes, quanta):
    all_metrics = []
    for quantum in quanta:
        # Cria uma cópia profunda dos processos para cada simulação
        processes_copy = copy.deepcopy(processes)
        print(f"\n=-=-=-=-=-=-=-=-= Escalonador Round Robin quantum = {quantum} =-=-=-=-=-=-=-=-=\n")
        metrics = round_robin(processes_copy, quantum)
        all_metrics.append(metrics)
        print(f"\n=-=-=-=-=-=-=-=-=-=-=-=-=-= Fim da Execução para quantum = {quantum} =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n")
    return all_metrics

# Função para plotar as métricas
def plot_metrics(all_metrics):
    quanta = [metric['quantum'] for metric in all_metrics]
    avg_waiting = [metric['average_waiting_time'] for metric in all_metrics]
    std_waiting = [metric['waiting_time_std'] for metric in all_metrics]
    avg_return = [metric['average_return_time'] for metric in all_metrics]
    std_return = [metric['return_time_std'] for metric in all_metrics]
    throughput = [metric['throughput'] for metric in all_metrics]

    plt.figure(figsize=(14, 6))

    # Plot do Tempo Médio de Espera
    plt.subplot(1, 3, 1)
    sns.barplot(x=quanta, y=avg_waiting, palette="Blues_d")
    plt.errorbar(x=range(len(quanta)), y=avg_waiting, yerr=std_waiting, fmt='none', color='black', capsize=5)
    plt.xlabel('Quantum')
    plt.ylabel('Tempo Médio de Espera')
    plt.title('Tempo Médio de Espera vs Quantum')

    # Plot do Tempo Médio de Retorno
    plt.subplot(1, 3, 2)
    sns.barplot(x=quanta, y=avg_return, palette="Greens_d")
    plt.errorbar(x=range(len(quanta)), y=avg_return, yerr=std_return, fmt='none', color='black', capsize=5)
    plt.xlabel('Quantum')
    plt.ylabel('Tempo Médio de Retorno')
    plt.title('Tempo Médio de Retorno vs Quantum')

    # Plot da Vazão
    plt.subplot(1, 3, 3)
    sns.barplot(x=quanta, y=throughput, palette="Oranges_d")
    plt.xlabel('Quantum')
    plt.ylabel('Vazão (Processos/Unidade de Tempo)')
    plt.title('Vazão vs Quantum')

    plt.tight_layout()
    plt.show()

# Função para plotar o diagrama de Gantt da sequência de execução
def plot_gantt_chart(metrics, title_suffix=""):
    execution_sequence = metrics['execution_sequence']
    quantum = metrics['quantum']

    fig, ax = plt.subplots(figsize=(14, 6))

    colors = {}
    color_palette = sns.color_palette("hsv", len(execution_sequence))
    color_idx = 0

    for start_time, proc_name, duration in execution_sequence:
        if proc_name not in colors:
            colors[proc_name] = color_palette[color_idx]
            color_idx += 1
        ax.barh(proc_name, duration, left=start_time, height=0.4, color=colors[proc_name], edgecolor='black')

    ax.set_xlabel('Tempo')
    ax.set_ylabel('Processos')
    ax.set_title(f'Diagrama de Gantt - Quantum = {quantum} {title_suffix}')
    ax.grid(True)

    # Criação da legenda
    patches = [mpatches.Patch(color=colors[proc], label=proc) for proc in colors]
    ax.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    plt.show()

def main():
    # Define intervalos e número de processos
    T1 = 0
    T2 = 5
    T3 = 20
    T4 = 25
    num_processes = 10

    # Gera os processos com burst times aleatórios em intervalos diferentes
    processes = []
    for i in range(num_processes):
        if i % 2 == 0:
            burst_time = random.randint(T1, T2)  # Intervalo [T1, T2]
        else:
            burst_time = random.randint(T3, T4) # Intervalo [T3, T4]
        processes.append(Process(f"P{i+1}", burst_time))

    # Quanta a serem testados
    quanta = [2, 4, 6]

    # Simula Round Robin para os diferentes quanta
    all_metrics = simulate_round_robin(processes, quanta)

    # Plota as métricas comparando os diferentes quanta
    plot_metrics(all_metrics)

    # Plota o diagrama de Gantt para cada conjunto de métricas
    for metrics in all_metrics:
        plot_gantt_chart(metrics)

if __name__ == "__main__":
    main()
