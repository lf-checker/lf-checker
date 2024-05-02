import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import sys


# 定义一个简单的Q网络
class QNetwork(nn.Module):
    def __init__(self, state_size, action_size):
        super(QNetwork, self).__init__()
        self.fc1 = nn.Linear(state_size, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, action_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x


# 定义Q-learning智能体
class QAgent:
    def __init__(self, state_size, action_size, learning_rate, gamma):
        self.q_network = QNetwork(state_size, action_size)
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=learning_rate)
        self.gamma = gamma
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )  # 检查是否有可用的 GPU

        # 将模型和优化器移到 GPU 上
        self.q_network.to(self.device)

    def select_action(self, state, epsilon):
        if np.random.rand() < epsilon:
            return np.random.randint(0, self.q_network.fc3.out_features)
        else:
            with torch.no_grad():
                q_values = self.q_network(
                    torch.tensor(state, dtype=torch.float32).to(self.device)
                )  # 将张量移到 GPU 上
                return torch.argmax(q_values).item()

    def train(self, state, action, reward, next_state, done):
        state = torch.tensor(state, dtype=torch.float32).to(self.device)  # 将张量移到 GPU 上
        next_state = torch.tensor(next_state, dtype=torch.float32).to(
            self.device
        )  # 将张量移到 GPU 上
        action = torch.tensor(action).to(self.device)  # 将张量移到 GPU 上
        reward = torch.tensor(reward).to(self.device)  # 将张量移到 GPU 上

        q_values = self.q_network(state)
        next_q_values = self.q_network(next_state)

        q_value = q_values[action]
        next_q_value = reward + (1 - done) * self.gamma * torch.max(next_q_values)

        loss = nn.functional.mse_loss(q_value, next_q_value.detach())
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def save_model(self, file_path):
        torch.save(self.q_network.state_dict(), file_path)

    def load_model(self, file_path):
        self.q_network.load_state_dict(torch.load(file_path))


# 定义一个简单的环境，即一个格子世界
class GridWorld:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.state = [0, 0]

    def reset(self):
        self.state = [0, 0]
        return self.state

    def step(self, action):
        if action == 0:  # 向右移动
            self.state[0] = min(self.state[0] + 1, self.width - 1)
        elif action == 1:  # 向左移动
            self.state[0] = max(self.state[0] - 1, 0)
        elif action == 2:  # 向下移动
            self.state[1] = min(self.state[1] + 1, self.height - 1)
        elif action == 3:  # 向上移动
            self.state[1] = max(self.state[1] - 1, 0)

        reward = 0
        if self.state == [self.width - 1, self.height - 1]:  # 达到目标位置
            reward = 1
            done = True
        else:
            reward = 0
            done = False

        return self.state, reward, done


# 定义训练函数
def train_agent(agent, env, episodes, epsilon_decay, min_epsilon):
    epsilon = 1.0
    for episode in range(episodes):
        state = env.reset()
        done = False
        while not done:
            action = agent.select_action(state, epsilon)
            next_state, reward, done = env.step(action)
            agent.train(state, action, reward, next_state, done)
            state = next_state
        epsilon = max(min_epsilon, epsilon * epsilon_decay)


# 参数设置
state_size = 2
action_size = 4
learning_rate = 0.001
gamma = 0.99
episodes = 700
epsilon_decay = 0.995
min_epsilon = 0.01

if torch.cuda.is_available():
    print("GPU: ", torch.cuda.get_device_name(torch.cuda.current_device()))
else:
    print("No gpu in use.")

# 创建环境和智能体
env = GridWorld(width=4, height=4)
agent = QAgent(state_size, action_size, learning_rate, gamma)
# 训练智能体
train_agent(agent, env, episodes, epsilon_decay, min_epsilon)
# 保存训练的模型
agent.save_model("q_network_model.pth")
# 在训练后测试智能体
state = env.reset()
done = False
while not done:
    action = agent.select_action(state, 0)  # 使用贪婪策略选择动作
    state, _, done = env.step(action)
    print("Agent's current position:", state)

# 当需要加载模型时
# 创建一个新的智能体
agent_to_load = QAgent(state_size, action_size, learning_rate, gamma)
# 加载之前保存的模型
agent_to_load.load_model("q_network_model.pth")
# 使用加载的模型进行测试
state = env.reset()
done = False
while not done:
    action = agent_to_load.select_action(state, 0)  # 使用贪婪策略选择动作
    state, _, done = env.step(action)
    print("Loaded Agent's current position:", state)
