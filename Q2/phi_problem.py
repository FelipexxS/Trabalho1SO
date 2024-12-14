import threading
import time
import sys

# Define o número de filósofos e a quantidade inicial de comida disponível, além do tempo de espera de cada filósofo
PHILOS = 5
FOOD = 50
DELAY = 0.005

# Aqui pode ser defino o número de vezes que o scrip irá executar
num_of_executions = 1000

#Cria uma lista de threads lock pra representar os hashis
chopstick = [threading.Lock() for _ in range(PHILOS)]

# Cria uma thread lock pra proteger o acesso ao recurso compartilhado 
food_lock = threading.Lock()

# Essa variável controla o tempo de espera extra de algum filósofo específico
sleep_seconds = 0

food = FOOD

def food_on_table():
    global food
    with food_lock: # Bloqueia pra garantir acesso exclusivo
        if food > 0:
            food -= 1
        return food

def grab_chopstick(phil, c, hand):
    chopstick[c].acquire() # Bloqueia o hashi pra um único filósofo utilizar ele
    print(f"O filósofo {phil}: pegou {hand} o hashi {c}")

def down_chopsticks(c1, c2):
    chopstick[c1].release() # Libera o hashi esquerdo
    chopstick[c2].release() # Libera o hashi direito

def philosopher(num):
    id = num
    left_chopstick = (id + 1) % PHILOS # calcula o índice do hashi esquerdo
    right_chopstick = id # Pega o índice do hashi direito

    print(f"O filósofo {id} terminou de refletir e agora está com fome.")

    while True:
        f = food_on_table() # Checa se ainda tem comida sobrando
        if f <= 0:
            break

       
        # Pega os hashis em uma ordem específica pra evitar starvation
        if id % 2 == 0:
            grab_chopstick(id, right_chopstick, "direito")
            grab_chopstick(id, left_chopstick, "esquerdo")
        else:
            grab_chopstick(id, left_chopstick, "esquerdo")
            grab_chopstick(id, right_chopstick, "direito")

        print(f"O filósofo {id}: está comendo.")
        time.sleep(DELAY * (FOOD - f + 1)) # Simula o tempo de comer

        down_chopsticks(left_chopstick, right_chopstick)

    print(f"O filósofo {id} já está satisfeito.")

def main():
    for i in range(num_of_executions): # Cria e inicia as threads pra cada filósofo, executando n vezes
        philosophers_threads = []
        for i in range(PHILOS):
            t = threading.Thread(target=philosopher, args=(i,))
            philosophers_threads.append(t)
            t.start()

        for t in philosophers_threads:
            t.join()

        print("\n Todos os filósofos terminaram de comer. \n\n")
    
    print(f"\nNúmero de execuções: {num_of_executions}\n")

if __name__ == "__main__":

    if len(sys.argv) == 2:
        sleep_seconds = float(sys.argv[1])
    
    main()
