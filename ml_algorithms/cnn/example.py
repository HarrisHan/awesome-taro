import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.utils import Bunch  # Add Bunch type

# 设置随机种子以确保结果可重现
np.random.seed(42)
plt.rcParams['font.family'] = ['WenQuanYi Zen Hei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 300

def generate_data():
    """
    生成用于CNN的示例数据（使用MNIST子集）
    返回:
        tuple[np.ndarray, np.ndarray]: (X, y) 其中X是形状为(n_samples, 8, 8)的图像数组，
                                      y是对应的标签数组
    """
    # 加载数据集
    digits: Bunch = load_digits()
    # 将数据重塑为图像格式
    X = digits.data.reshape(-1, 8, 8)
    y = digits.target
    return np.array(X), np.array(y)

class CNN:
    def __init__(self, input_shape=(8, 8), n_filters=32, kernel_size=3, n_classes=10, dropout_rate=0.5):
        """
        初始化CNN
        input_shape: 输入图像尺寸
        n_filters: 卷积核数量
        kernel_size: 卷积核大小
        n_classes: 分类类别数
        dropout_rate: Dropout比率
        """
        self.input_shape = input_shape
        self.n_filters = n_filters
        self.kernel_size = kernel_size
        self.n_classes = n_classes
        self.dropout_rate = dropout_rate
        
        # 初始化权重
        self.conv_weights = np.random.randn(
            n_filters, 
            kernel_size, 
            kernel_size
        ) * np.sqrt(2.0 / (kernel_size * kernel_size))
        
        # 全连接层权重
        self.fc_weights = np.random.randn(
            n_filters * (input_shape[0] - kernel_size + 1) * (input_shape[1] - kernel_size + 1),
            n_classes
        ) * 0.01
        
        self.fc_bias = np.zeros(n_classes)
    
    def relu(self, x):
        """ReLU激活函数"""
        return np.maximum(0, x)
    
    def softmax(self, x):
        """Softmax激活函数"""
        exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=1, keepdims=True)
    
    def convolve(self, x):
        """
        执行卷积操作
        x: 输入数据 (batch_size, height, width)
        """
        batch_size = x.shape[0]
        h_out = self.input_shape[0] - self.kernel_size + 1
        w_out = self.input_shape[1] - self.kernel_size + 1
        
        conv_out = np.zeros((batch_size, self.n_filters, h_out, w_out))
        
        for i in range(h_out):
            for j in range(w_out):
                patch = x[:, i:i+self.kernel_size, j:j+self.kernel_size]
                for k in range(self.n_filters):
                    conv_out[:, k, i, j] = np.sum(
                        patch * self.conv_weights[k], 
                        axis=(1,2)
                    )
        
        return conv_out
    
    def forward(self, x, training=True):
        """
        前向传播
        x: 输入数据 (batch_size, height, width)
        training: 是否处于训练模式
        """
        # 卷积层
        self.conv_output = self.convolve(x)
        
        # ReLU激活
        self.relu_output = self.relu(self.conv_output)
        
        # 展平
        batch_size = x.shape[0]
        self.flatten = self.relu_output.reshape(batch_size, -1)
        
        # Dropout (仅在训练时使用)
        if training:
            self.dropout_mask = np.random.binomial(1, 1-self.dropout_rate, size=self.flatten.shape) / (1-self.dropout_rate)
            self.flatten *= self.dropout_mask
        
        # 全连接层
        self.fc_output = np.dot(self.flatten, self.fc_weights) + self.fc_bias
        
        # Softmax
        self.probabilities = self.softmax(self.fc_output)
        
        return self.probabilities
    
    def train(self, X, y, X_val, y_val, learning_rate=0.01, epochs=100, batch_size=32):
        """
        训练CNN模型
        """
        n_samples = len(X)
        train_losses, val_losses = [], []
        train_accuracies, val_accuracies = [], []
        
        for epoch in range(epochs):
            # 训练阶段
            total_loss = 0
            correct_predictions = 0
            
            # 批量训练
            for i in range(0, n_samples, batch_size):
                batch_X = X[i:i+batch_size]
                batch_y = y[i:i+batch_size]
                
                # 前向传播（训练模式）
                probs = self.forward(batch_X, training=True)
                
                # 计算交叉熵损失
                y_one_hot = np.eye(self.n_classes)[batch_y]
                loss = -np.mean(np.sum(y_one_hot * np.log(probs + 1e-8), axis=1))
                total_loss += loss
                
                # 计算准确率
                predictions = np.argmax(probs, axis=1)
                correct_predictions += np.sum(predictions == batch_y)
                
                # 反向传播（简化版本）
                d_fc = probs - y_one_hot
                d_fc_weights = np.dot(self.flatten.T, d_fc)
                d_fc_bias = np.sum(d_fc, axis=0)
                
                # 更新权重（增强L2正则化）
                l2_reg = 0.1  # 增加L2正则化系数
                d_fc_weights += l2_reg * self.fc_weights
                d_conv_weights = l2_reg * self.conv_weights
                
                # 更新全连接层权重
                self.fc_weights -= learning_rate * d_fc_weights
                self.fc_bias -= learning_rate * d_fc_bias
                
                # 更新卷积层权重
                self.conv_weights -= learning_rate * d_conv_weights
            
            # 计算训练指标
            train_loss = total_loss / (n_samples / batch_size)
            train_acc = correct_predictions / n_samples
            train_losses.append(train_loss)
            train_accuracies.append(train_acc)
            
            # 验证阶段
            val_probs = self.forward(X_val, training=False)
            val_y_one_hot = np.eye(self.n_classes)[y_val]
            val_loss = -np.mean(np.sum(val_y_one_hot * np.log(val_probs + 1e-8), axis=1))
            val_predictions = np.argmax(val_probs, axis=1)
            val_acc = np.sum(val_predictions == y_val) / len(y_val)
            val_losses.append(val_loss)
            val_accuracies.append(val_acc)
            
            if epoch % 10 == 0:
                print(f'Epoch {epoch}, Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}, '
                      f'Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}')
        
        return train_losses, train_accuracies, val_losses, val_accuracies
        
        return losses

# 生成数据
X, y = generate_data()
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 划分验证集
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.2, random_state=42)

# 训练CNN模型
cnn = CNN(input_shape=(8, 8), n_filters=16, kernel_size=3, n_classes=10, dropout_rate=0.5)
# 使用较小的学习率和强正则化
train_losses, train_accuracies, val_losses, val_accuracies = cnn.train(
    X_train, y_train, X_val, y_val, learning_rate=0.001, epochs=100
)

# 训练过程可视化
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(train_losses, 'b-', label='训练损失')
plt.plot(val_losses, 'r--', label='验证损失')
plt.xlabel('迭代次数')
plt.ylabel('损失值')
plt.title('CNN训练与验证损失曲线')
plt.grid(True)
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(train_accuracies, 'b-', label='训练准确率')
plt.plot(val_accuracies, 'r--', label='验证准确率')
plt.xlabel('迭代次数')
plt.ylabel('准确率')
plt.title('CNN训练与验证准确率曲线')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.savefig('images/cnn_training_metrics.png', dpi=300, bbox_inches='tight')
plt.close()

# 卷积核可视化改进
plt.figure(figsize=(15, 5))
for i in range(min(3, cnn.n_filters)):
    plt.subplot(1, 3, i+1)
    im = plt.imshow(cnn.conv_weights[i], cmap='viridis')
    plt.title(f'卷积核 #{i+1}\n(权重分布)')
    plt.colorbar(im, label='权重值')
plt.tight_layout()
plt.savefig('images/cnn_filters.png', dpi=300, bbox_inches='tight')
plt.close()

# 特征图可视化改进
sample_image = X_test[0]
conv_output = cnn.convolve(sample_image.reshape(1, 8, 8))[0]
plt.figure(figsize=(15, 5))

# 原始图像
plt.subplot(1, 4, 1)
plt.imshow(sample_image, cmap='gray')
plt.title('输入图像')
plt.colorbar(label='像素值')

# 三个特征图
for i in range(min(3, cnn.n_filters)):
    plt.subplot(1, 4, i+2)
    im = plt.imshow(conv_output[i], cmap='viridis')
    plt.title(f'特征图 #{i+1}\n(激活值分布)')
    plt.colorbar(im, label='激活值')

plt.tight_layout()
plt.savefig('images/cnn_feature_maps.png', dpi=300, bbox_inches='tight')
plt.close()

# 可视化卷积核
plt.figure(figsize=(15, 5))
for i in range(min(3, cnn.n_filters)):
    plt.subplot(1, 3, i+1)
    plt.imshow(cnn.conv_weights[i], cmap='viridis')
    plt.title(f'卷积核 #{i+1}')
    plt.colorbar()
plt.tight_layout()
plt.savefig('images/cnn_filters.png', dpi=300, bbox_inches='tight')
plt.close()

# 可视化特征图
sample_image = X_test[0]
conv_output = cnn.convolve(sample_image.reshape(1, 8, 8))[0]
plt.figure(figsize=(15, 5))
for i in range(min(3, cnn.n_filters)):
    plt.subplot(1, 3, i+1)
    plt.imshow(conv_output[i], cmap='viridis')
    plt.title(f'特征图 #{i+1}')
    plt.colorbar()
plt.tight_layout()
plt.savefig('images/cnn_feature_maps.png', dpi=300, bbox_inches='tight')
plt.close()
