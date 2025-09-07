import numpy as np


class Perceptron:
    def __init__(self, input_size, hidden_size, output_size):
        # Веса между входом и скрытым слоем
        self.weights1 = np.random.randn(input_size, hidden_size) * 0.1
        self.bias1 = np.zeros(hidden_size)

        # Веса между скрытым и выходным слоем
        self.weights2 = np.random.randn(hidden_size, output_size) * 0.1
        self.bias2 = np.zeros(output_size)

    def relu(self, x):
        """Функция активации - делает сеть 'нелинейной'"""
        return np.maximum(0, x)

    def softmax(self, x):
        """Преобразует выходы в вероятности"""
        exp_x = np.exp(x - np.max(x))
        return exp_x / exp_x.sum()

    def predict(self, inputs):
        """Проход информации через сеть"""
        # Скрытый слой
        hidden = self.relu(np.dot(inputs, self.weights1) + self.bias1)

        # Выходной слой
        output = np.dot(hidden, self.weights2) + self.bias2

        return self.softmax(output)


class GeneticTrainer:
    def __init__(self, population_size=10, input_size=5, output_size=3):
        # Создаем популяцию нейросетей
        self.population = [Perceptron(input_size, 8, output_size) for _ in range(population_size)]
        self.scores = [0] * population_size  # Результаты каждой сети

    def mutate(self, network, mutation_rate=0.1):
        """Случайно изменяем веса сети (мутация)"""
        # Мутируем первые веса
        mask = np.random.random(network.weights1.shape) < mutation_rate
        network.weights1 += mask * np.random.randn(*network.weights1.shape) * 0.1

        # Мутируем вторые веса
        mask = np.random.random(network.weights2.shape) < mutation_rate
        network.weights2 += mask * np.random.randn(*network.weights2.shape) * 0.1

        return network

    def crossover(self, parent1, parent2):
        """Смешиваем две сети (скрещивание)"""
        child = Perceptron(
            parent1.weights1.shape[0], parent1.weights1.shape[1], parent1.weights2.shape[1]
        )

        # Скрещиваем веса (берем половину от каждого родителя)
        crossover_point = parent1.weights1.size // 2
        child.weights1 = np.where(
            np.arange(parent1.weights1.size).reshape(parent1.weights1.shape) < crossover_point,
            parent1.weights1,
            parent2.weights1,
        )

        return child

    def evolve(self):
        """Создаем новое поколение сетей"""
        # Сортируем сети по результатам
        sorted_indices = np.argsort(self.scores)[::-1]  # От лучших к худшим

        new_population = []

        # Берем лучшие сети без изменений
        for i in range(len(self.population) // 2):
            new_population.append(self.population[sorted_indices[i]])

        # Создаем новые сети скрещиванием и мутацией
        for i in range(len(self.population) // 2):
            parent1 = self.population[
                sorted_indices[np.random.randint(0, len(self.population) // 2)]
            ]
            parent2 = self.population[
                sorted_indices[np.random.randint(0, len(self.population) // 2)]
            ]

            child = self.crossover(parent1, parent2)
            child = self.mutate(child)
            new_population.append(child)

        self.population = new_population
        self.scores = [0] * len(self.population)


class EnemyAI:
    def __init__(self, perceptron):
        self.brain = perceptron
        self.last_action = 0

    def get_game_state(self, enemy, player, platforms):
        """Преобразуем игровую ситуацию в числа"""
        # Нормализованные данные (все от 0 до 1)
        return np.array(
            [
                # Расстояние до игрока по X (нормализованное)
                (player.rect.centerx - enemy.rect.centerx) / 1000.0,
                # Расстояние до игрока по Y
                (player.rect.centery - enemy.rect.centery) / 1000.0,
                # Стоит ли на земле (0 или 1)
                1.0 if enemy.is_grounded else 0.0,
                # Скорость по X (нормализованная)
                enemy.velocity.x / 500.0,
                # Скорость по Y
                enemy.velocity.y / 500.0,
            ]
        )

    def decide_action(self, enemy, player, platforms):
        """Принимаем решение на основе нейросети"""
        # Получаем состояние игры
        game_state = self.get_game_state(enemy, player, platforms)

        # Получаем вероятности действий от нейросети
        action_probs = self.brain.predict(game_state)

        # 10% случайности для исследования
        if np.random.random() < 0.1:
            action = np.random.randint(0, len(action_probs) - 1)
        else:
            action = np.argmax(action_probs)

        self.last_action = action
        return action


class RewardSystem:
    def __init__(self):
        self.last_distance = float('inf')

    def calculate_reward(self, enemy, player):
        """Вычисляем награду для обучения"""
        current_distance = self.calculate_distance(enemy, player)

        # Награда за приближение к игроку
        distance_reward = (self.last_distance - current_distance) * 10
        self.last_distance = current_distance

        # Штраф за бездействие
        penalty = -0.1

        # Большая награда за атаку игрока
        attack_reward = 0
        if self.check_attack_success(enemy, player):
            attack_reward = 50

        return distance_reward + penalty + attack_reward

    def calculate_distance(self, enemy, player):
        """Расстояние между врагом и игроком"""
        return np.sqrt(
            (enemy.rect.centerx - player.rect.centerx) ** 2
            + (enemy.rect.centery - player.rect.centery) ** 2
        )

    def check_attack_success(self, enemy, player):
        """Проверяем успешную атаку"""
        # Здесь проверяем попадание копья и т.д.
        return False
