import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# 设置随机种子以确保结果可重现
np.random.seed(42)
plt.rcParams['font.family'] = ['WenQuanYi Zen Hei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 300

def generate_random_features(X, n_features=1000, gamma=1.0):
    """
    生成随机厨房池特征
    X: 输入数据
    n_features: 随机特征的数量
    gamma: RBF核参数
    """
    n_samples, n_dims = X.shape
    
    # 生成随机投影矩阵
    W = np.random.normal(0, np.sqrt(2 * gamma), (n_dims, n_features))
    b = np.random.uniform(0, 2 * np.pi, n_features)
    
    # 计算随机特征
    Z = np.sqrt(2.0 / n_features) * np.cos(X @ W + b)
    
    return Z

def generate_data(n_samples=300):
    """
    生成非线性可分的数据
    """
    X = np.random.randn(n_samples, 2)
    r = X[:, 0]**2 + X[:, 1]**2
    y = (r < 2).astype(int)
    return X, y

class RandomKitchenSink:
    def __init__(self, n_features=1000, gamma=1.0):
        """
        初始化随机厨房池模型
        n_features: 随机特征的数量
        gamma: RBF核参数
        """
        self.n_features = n_features
        self.gamma = gamma
        self.W = None
        self.b = None
        self.linear_model = None
        
    def fit(self, X, y):
        """
        训练模型
        """
        n_samples, n_dims = X.shape
        
        # 生成随机投影
        self.W = np.random.normal(0, np.sqrt(2 * self.gamma), (n_dims, self.n_features))
        self.b = np.random.uniform(0, 2 * np.pi, self.n_features)
        
        # 计算随机特征
        Z = np.sqrt(2.0 / self.n_features) * np.cos(X @ self.W + self.b)
        
        # 使用线性回归
        self.linear_model = np.linalg.lstsq(Z, y, rcond=None)[0]
        
    def predict(self, X):
        """
        预测新数据
        """
        Z = np.sqrt(2.0 / self.n_features) * np.cos(X @ self.W + self.b)
        y_pred = Z @ self.linear_model
        return (y_pred > 0.5).astype(int)

def plot_decision_boundary(X, y, model, title):
    """
    绘制决策边界
    """
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.02),
                        np.arange(y_min, y_max, 0.02))
    
    X_grid = np.c_[xx.ravel(), yy.ravel()]
    Z = model.predict(X_grid)
    Z = Z.reshape(xx.shape)
    
    plt.contourf(xx, yy, Z, alpha=0.4)
    plt.scatter(X[:, 0], X[:, 1], c=y, alpha=0.8)
    plt.xlabel('特征1')
    plt.ylabel('特征2')
    plt.title(title)
    plt.grid(True)

# 生成数据
X, y = generate_data(n_samples=300)

# 数据标准化
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# 基础效果展示
rks = RandomKitchenSink(n_features=100, gamma=1.0)
rks.fit(X_train, y_train)

plt.figure(figsize=(10, 6))
plot_decision_boundary(X_scaled, y, rks, '随机厨房池分类示例')
plt.savefig('images/rks_basic.png', dpi=300, bbox_inches='tight')
plt.close()

# 不同特征数量的效果比较
n_features_list = [50, 100, 200]
plt.figure(figsize=(15, 5))

for i, n_features in enumerate(n_features_list):
    plt.subplot(1, 3, i+1)
    rks = RandomKitchenSink(n_features=n_features)
    rks.fit(X_train, y_train)
    plot_decision_boundary(X_scaled, y, rks, f'随机厨房池 (特征数={n_features})')

plt.tight_layout()
plt.savefig('images/rks_features_comparison.png', dpi=300, bbox_inches='tight')
plt.close()

# 不同gamma值的效果比较
gamma_list = [0.1, 1.0, 10.0]
plt.figure(figsize=(15, 5))

for i, gamma in enumerate(gamma_list):
    plt.subplot(1, 3, i+1)
    rks = RandomKitchenSink(n_features=100, gamma=gamma)
    rks.fit(X_train, y_train)
    plot_decision_boundary(X_scaled, y, rks, f'随机厨房池 (gamma={gamma})')

plt.tight_layout()
plt.savefig('images/rks_gamma_comparison.png', dpi=300, bbox_inches='tight')
plt.close()
