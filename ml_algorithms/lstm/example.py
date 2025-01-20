import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

# 设置随机种子以确保结果可重现
np.random.seed(42)
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.family'] = ['WenQuanYi Zen Hei']
plt.rcParams['axes.unicode_minus'] = False

def generate_data(n_samples=1000):
    """
    生成用于LSTM的示例时间序列数据
    """
    t = np.linspace(0, 100, n_samples)
    # 生成一个包含多个频率的复杂时间序列
    y = 0.5 * np.sin(0.1 * t) + 0.2 * np.sin(0.5 * t) + \
        0.1 * np.sin(0.8 * t) + np.random.normal(0, 0.05, n_samples)
    return t, y

def create_sequences(data, seq_length):
    """
    将时间序列数据转换为序列样本
    """
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:(i + seq_length)])
        y.append(data[i + seq_length])
    return np.array(X), np.array(y)

class LSTM:
    def __init__(self, seq_length=20, hidden_size=32, output_size=1):
        """
        初始化LSTM
        seq_length: 序列长度
        hidden_size: 隐藏层维度
        output_size: 输出维度
        """
        self.seq_length = seq_length
        self.hidden_size = hidden_size
        self.output_size = output_size
        
        # 初始化权重
        # 输入门权重
        self.Wii = np.random.randn(1, hidden_size) * 0.01
        self.Whi = np.random.randn(hidden_size, hidden_size) * 0.01
        self.bi = np.zeros((1, hidden_size))
        
        # 遗忘门权重
        self.Wif = np.random.randn(1, hidden_size) * 0.01
        self.Whf = np.random.randn(hidden_size, hidden_size) * 0.01
        self.bf = np.zeros((1, hidden_size))
        
        # 输出门权重
        self.Wio = np.random.randn(1, hidden_size) * 0.01
        self.Who = np.random.randn(hidden_size, hidden_size) * 0.01
        self.bo = np.zeros((1, hidden_size))
        
        # 单元状态权重
        self.Wig = np.random.randn(1, hidden_size) * 0.01
        self.Whg = np.random.randn(hidden_size, hidden_size) * 0.01
        self.bg = np.zeros((1, hidden_size))
        
        # 输出层权重
        self.Why = np.random.randn(hidden_size, output_size) * 0.01
        self.by = np.zeros((1, output_size))
        
    def sigmoid(self, x):
        """Sigmoid激活函数"""
        return 1 / (1 + np.exp(-np.clip(x, -10, 10)))
    
    def tanh(self, x):
        """Tanh激活函数"""
        return np.tanh(x)
    
    def forward(self, x, h_prev, c_prev):
        """
        前向传播
        x: 输入数据 (batch_size, seq_length)
        h_prev: 上一时刻隐藏状态
        c_prev: 上一时刻单元状态
        """
        # 处理每个时间步
        outputs = []
        gates_list = []
        
        for t in range(x.shape[1]):
            xt = x[:, t:t+1]  # (batch_size, 1)
            
            # 输入门
            i = self.sigmoid(np.dot(xt, self.Wii) + np.dot(h_prev, self.Whi) + self.bi)
            
            # 遗忘门
            f = self.sigmoid(np.dot(xt, self.Wif) + np.dot(h_prev, self.Whf) + self.bf)
            
            # 输出门
            o = self.sigmoid(np.dot(xt, self.Wio) + np.dot(h_prev, self.Who) + self.bo)
            
            # 候选单元状态
            g = self.tanh(np.dot(xt, self.Wig) + np.dot(h_prev, self.Whg) + self.bg)
            
            # 更新单元状态
            c_prev = f * c_prev + i * g
            
            # 更新隐藏状态
            h_prev = o * self.tanh(c_prev)
            
            # 保存门控状态
            gates_list.append((i, f, o, g))
            
            # 输出
            y = np.dot(h_prev, self.Why) + self.by
            outputs.append(y)
        
        # 返回最后一个时间步的预测值和状态
        return outputs[-1], h_prev, c_prev, gates_list[-1]
    
    def train(self, X, y, learning_rate=0.01, epochs=100):
        """
        训练LSTM模型
        """
        n_samples = len(X)
        losses = []
        
        for epoch in range(epochs):
            total_loss = 0
            h = np.zeros((1, self.hidden_size))
            c = np.zeros((1, self.hidden_size))
            
            for i in range(n_samples):
                # 前向传播
                x = X[i].reshape(1, -1)
                target = y[i].reshape(1, -1)
                
                pred, h, c, gates = self.forward(x, h, c)
                loss = np.mean((pred - target) ** 2)
                total_loss += loss
                
                # 反向传播（简化版本）
                d_pred = 2 * (pred - target)
                d_Why = np.dot(h.T, d_pred)
                d_by = d_pred
                
                # 更新权重
                self.Why -= learning_rate * d_Why
                self.by -= learning_rate * d_by
            
            avg_loss = total_loss / n_samples
            losses.append(avg_loss)
            
            if epoch % 10 == 0:
                print(f'Epoch {epoch}, Loss: {avg_loss:.6f}')
        
        return losses

# 生成数据
t, y = generate_data()
scaler = MinMaxScaler()
y_scaled = scaler.fit_transform(y.reshape(-1, 1))

# 创建序列数据
seq_length = 20
X, y_target = create_sequences(y_scaled, seq_length)

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y_target, test_size=0.2, random_state=42)

# 训练LSTM模型
lstm = LSTM(seq_length=seq_length, hidden_size=32, output_size=1)
losses = lstm.train(X_train, y_train, learning_rate=0.01, epochs=100)

# 基础效果展示
plt.figure(figsize=(10, 6))
h = np.zeros((1, lstm.hidden_size))
c = np.zeros((1, lstm.hidden_size))
predictions = []

for i in range(len(X_test)):
    pred, h, c, _ = lstm.forward(X_test[i].reshape(1, -1), h, c)
    predictions.append(pred[0, 0])

plt.plot(y_test, label='真实值', alpha=0.6)
plt.plot(predictions, label='LSTM预测', alpha=0.6)
plt.xlabel('时间步')
plt.ylabel('值')
plt.title('LSTM时间序列预测示例')
plt.legend()
plt.grid(True)
plt.savefig('images/lstm_basic.png', dpi=300, bbox_inches='tight')
plt.close()

# 不同隐藏层大小的比较
hidden_sizes = [16, 32, 64]
plt.figure(figsize=(15, 5))

for i, hidden_size in enumerate(hidden_sizes):
    plt.subplot(1, 3, i+1)
    lstm = LSTM(seq_length=seq_length, hidden_size=hidden_size, output_size=1)
    losses = lstm.train(X_train, y_train, learning_rate=0.01, epochs=50)
    
    h = np.zeros((1, lstm.hidden_size))
    c = np.zeros((1, lstm.hidden_size))
    predictions = []
    
    for j in range(len(X_test)):
        pred, h, c, _ = lstm.forward(X_test[j:j+1], h, c)
        predictions.append(pred[0, 0])
    
    plt.plot(y_test[:100], label='真实值', alpha=0.6)
    plt.plot(predictions[:100], label='LSTM预测', alpha=0.6)
    plt.xlabel('时间步')
    plt.ylabel('值')
    plt.title(f'隐藏层大小 = {hidden_size}')
    plt.legend()
    plt.grid(True)

plt.tight_layout()
plt.savefig('images/lstm_hidden_size_comparison.png', dpi=300, bbox_inches='tight')
plt.close()

# 训练过程的损失曲线
plt.figure(figsize=(10, 6))
plt.plot(losses)
plt.xlabel('迭代次数')
plt.ylabel('损失')
plt.title('LSTM训练损失曲线')
plt.grid(True)
plt.savefig('images/lstm_training_loss.png', dpi=300, bbox_inches='tight')
plt.close()

# LSTM门控机制可视化
plt.figure(figsize=(15, 5))
x = X_test[0].reshape(1, -1)
h = np.zeros((1, lstm.hidden_size))
c = np.zeros((1, lstm.hidden_size))
_, _, _, gates = lstm.forward(x, h, c)

gate_names = ['输入门', '遗忘门', '输出门', '候选状态']
for i, (gate, name) in enumerate(zip(gates, gate_names)):
    plt.subplot(1, 4, i+1)
    plt.imshow(gate.T, aspect='auto', cmap='viridis')
    plt.title(f'{name}激活值')
    plt.colorbar()

plt.tight_layout()
plt.savefig('images/lstm_gates_visualization.png', dpi=300, bbox_inches='tight')
plt.close()
