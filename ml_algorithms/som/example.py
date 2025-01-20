import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import os

# 确保images目录存在
os.makedirs('images', exist_ok=True)

# 设置随机种子以确保结果可重现
np.random.seed(42)
plt.rcParams['font.family'] = ['WenQuanYi Zen Hei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 300

def generate_data(n_samples=1000, n_features=2):
    """
    生成用于SOM的示例数据
    n_samples: 样本数量
    n_features: 特征维度
    """
    # 生成三个高斯分布的数据
    centers = [(0, 0), (2, 2), (-2, -2)]
    X = np.zeros((n_samples, n_features))
    samples_per_center = n_samples // len(centers)
    
    for i, center in enumerate(centers):
        start_idx = i * samples_per_center
        end_idx = (i + 1) * samples_per_center if i < len(centers) - 1 else n_samples
        X[start_idx:end_idx] = np.random.normal(loc=center, scale=0.5, 
                                              size=(end_idx-start_idx, n_features))
    
    return X

def plot_som_grid(som, X, title):
    """
    可视化SOM网格
    som: 训练好的SOM模型
    X: 原始数据
    title: 图表标题
    """
    plt.figure(figsize=(10, 10))
    
    # 绘制权重向量
    for i in range(som.map_size[0]):
        for j in range(som.map_size[1]):
            plt.plot(som.weights[i, j, 0], som.weights[i, j, 1], 'k.', markersize=7)
            if i < som.map_size[0]-1:
                plt.plot([som.weights[i, j, 0], som.weights[i+1, j, 0]],
                        [som.weights[i, j, 1], som.weights[i+1, j, 1]], 'gray', alpha=0.3)
            if j < som.map_size[1]-1:
                plt.plot([som.weights[i, j, 0], som.weights[i, j+1, 0]],
                        [som.weights[i, j, 1], som.weights[i, j+1, 1]], 'gray', alpha=0.3)
    
    # 绘制原始数据点
    plt.scatter(X[:, 0], X[:, 1], c='r', alpha=0.2, label='训练数据')
    plt.title(title)
    plt.xlabel('特征1')
    plt.ylabel('特征2')
    plt.legend()
    plt.grid(True)

class SOM:
    """
    自组织映射(Self-Organizing Map)实现
    """
    def __init__(self, map_size=(10, 10), n_features=2, learning_rate=0.1, sigma=1.0):
        """
        初始化SOM
        map_size: 输出层网格大小
        n_features: 输入特征维度
        learning_rate: 学习率
        sigma: 邻域函数的宽度参数
        """
        self.map_size = map_size
        self.n_features = n_features
        self.initial_learning_rate = learning_rate
        self.initial_sigma = sigma
        
        # 初始化权重
        self.weights = np.random.randn(map_size[0], map_size[1], n_features) * 0.1
        
        # 创建网格坐标
        self.grid_coords = np.array([(i, j) 
                                   for i in range(map_size[0]) 
                                   for j in range(map_size[1])])
    
    def find_bmu(self, x):
        """
        找到最佳匹配单元(BMU)
        x: 输入向量
        返回: BMU的坐标
        """
        distances = np.sum((self.weights - x) ** 2, axis=2)
        bmu_idx = np.unravel_index(np.argmin(distances), self.map_size)
        return bmu_idx
    
    def neighborhood_function(self, bmu_loc, sigma):
        """
        计算邻域函数
        bmu_loc: BMU的位置
        sigma: 当前的sigma值
        返回: 所有神经元的邻域值
        """
        bmu_grid = np.array([bmu_loc[0], bmu_loc[1]])
        grid_dist = np.sum((self.grid_coords - bmu_grid) ** 2, axis=1).reshape(self.map_size)
        return np.exp(-grid_dist / (2 * sigma ** 2))
    
    def train(self, X, n_iterations=1000):
        """
        训练SOM
        X: 训练数据
        n_iterations: 迭代次数
        """
        for i in range(n_iterations):
            # 计算当前的学习率和sigma
            t = i / n_iterations
            lr = self.initial_learning_rate * np.exp(-t)
            sigma = self.initial_sigma * np.exp(-t)
            
            # 随机选择一个样本
            x = X[np.random.randint(len(X))]
            
            # 找到BMU
            bmu_loc = self.find_bmu(x)
            
            # 计算邻域函数
            h = self.neighborhood_function(bmu_loc, sigma)
            
            # 更新权重
            for i in range(self.map_size[0]):
                for j in range(self.map_size[1]):
                    self.weights[i, j] += lr * h[i, j] * (x - self.weights[i, j])
    
    def transform(self, X):
        """
        将数据映射到SOM网格
        X: 输入数据
        返回: 每个样本对应的BMU坐标
        """
        bmu_coords = np.zeros((len(X), 2))
        for i, x in enumerate(X):
            bmu_coords[i] = self.find_bmu(x)
        return bmu_coords

if __name__ == "__main__":
    # 生成数据
    X = generate_data(n_samples=1000)

    # 数据标准化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 基础SOM效果展示
    som = SOM(map_size=(10, 10), n_features=2, learning_rate=0.1, sigma=1.0)
    som.train(X_scaled, n_iterations=1000)

    plt.figure(figsize=(10, 6))
    plot_som_grid(som, X_scaled, 'SOM网格示例')
    plt.savefig('images/som_basic.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 不同网格大小的效果比较
    grid_sizes = [(5, 5), (10, 10), (20, 20)]
    plt.figure(figsize=(15, 5))

    for i, size in enumerate(grid_sizes):
        plt.subplot(1, 3, i+1)
        som = SOM(map_size=size, n_features=2, learning_rate=0.1, sigma=1.0)
        som.train(X_scaled, n_iterations=1000)
        plot_som_grid(som, X_scaled, f'SOM网格 ({size[0]}x{size[1]})')

    plt.tight_layout()
    plt.savefig('images/som_grid_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 学习过程可视化
    plt.figure(figsize=(15, 5))
    iterations = [10, 100, 1000]

    for i, n_iter in enumerate(iterations):
        plt.subplot(1, 3, i+1)
        som = SOM(map_size=(10, 10), n_features=2, learning_rate=0.1, sigma=1.0)
        som.train(X_scaled, n_iterations=n_iter)
        plot_som_grid(som, X_scaled, f'SOM学习过程 ({n_iter}次迭代)')

    plt.tight_layout()
    plt.savefig('images/som_learning_process.png', dpi=300, bbox_inches='tight')
    plt.close()
