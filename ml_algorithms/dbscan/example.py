import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_moons, make_blobs

# 设置随机种子以确保结果可重现
np.random.seed(42)
plt.rcParams['font.family'] = ['WenQuanYi Zen Hei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 300

def generate_data(n_samples=300, noise=0.1, random_state=42):
    """
    生成用于DBSCAN的示例数据
    n_samples: 样本数量
    noise: 噪声水平
    random_state: 随机种子
    """
    # 生成两个新月形数据集
    moons_data = make_moons(n_samples=n_samples//2, noise=noise, random_state=random_state)
    X1, y1 = moons_data[0], moons_data[1]
    
    # 生成一个圆形簇
    blobs_data = make_blobs(n_samples=n_samples//2, centers=1, cluster_std=0.3,
                           random_state=random_state)
    X2, _ = blobs_data[0], blobs_data[1]
    y2 = np.zeros(n_samples//2)
    X2 = X2 + [2, 2]
    
    # 合并数据集
    X = np.vstack([X1, X2])
    y = np.hstack([y1, y2 + 2])  # 添加偏移以区分标签
    
    # 添加噪声点
    noise_points = np.random.uniform(low=-1, high=4, size=(n_samples//10, 2))
    X = np.vstack([X, noise_points])
    y = np.hstack([y, -1 * np.ones(n_samples//10)])  # 噪声点标记为-1
    
    return X, y

class DBSCAN:
    def __init__(self, eps=0.3, min_samples=5):
        """
        初始化DBSCAN
        eps: 邻域半径
        min_samples: 核心点的最小邻域样本数
        """
        self.eps = eps
        self.min_samples = min_samples
        self.labels_ = None
        
    def _get_neighbors(self, X, point_idx):
        """
        获取给定点的邻域内的所有点的索引
        """
        distances = np.sqrt(np.sum((X - X[point_idx])**2, axis=1))
        return np.where(distances <= self.eps)[0]
    
    def fit(self, X):
        """
        执行DBSCAN聚类
        X: 输入数据，形状为(n_samples, n_features)
        """
        n_samples = X.shape[0]
        self.labels_ = np.full(n_samples, -1)  # 初始化所有点为噪声点
        
        # 当前簇标签
        current_label = 0
        
        # 遍历所有点
        for point_idx in range(n_samples):
            # 跳过已经访问过的点
            if self.labels_[point_idx] != -1:
                continue
                
            # 获取邻域点
            neighbors = self._get_neighbors(X, point_idx)
            
            # 如果不是核心点，标记为噪声点并继续
            if len(neighbors) < self.min_samples:
                continue
                
            # 开始一个新的簇
            self.labels_[point_idx] = current_label
            
            # 存储需要检查的点
            seeds = list(neighbors)
            
            # 扩展簇
            while seeds:
                current_point = seeds.pop(0)
                
                # 如果是噪声点，将其加入当前簇
                if self.labels_[current_point] == -1:
                    self.labels_[current_point] = current_label
                    
                    # 获取当前点的邻域
                    current_neighbors = self._get_neighbors(X, current_point)
                    
                    # 如果是核心点，将其邻域点加入待检查列表
                    if len(current_neighbors) >= self.min_samples:
                        seeds.extend([n for n in current_neighbors if self.labels_[n] == -1])
            
            # 更新簇标签
            current_label += 1
            
        return self

def plot_clusters(X, labels, title):
    """
    可视化聚类结果
    """
    unique_labels = np.unique(labels)
    # 使用颜色映射
    cmap = plt.get_cmap('tab10')
    
    plt.figure(figsize=(10, 6))
    for i, label in enumerate(unique_labels):
        mask = labels == label
        if label == -1:
            # 噪声点
            plt.scatter(X[mask, 0], X[mask, 1], c='black',
                       marker='x', label='噪声', alpha=0.3)
        else:
            plt.scatter(X[mask, 0], X[mask, 1], c=[cmap(i)],
                       label=f'簇 {label}', alpha=0.6)
            
    plt.xlabel('特征1')
    plt.ylabel('特征2')
    plt.title(title)
    plt.legend()
    plt.grid(True)

# 生成数据
X, y_true = generate_data()

# 数据标准化
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 基础DBSCAN效果展示
dbscan = DBSCAN(eps=0.3, min_samples=5)
dbscan.fit(X_scaled)

plt.figure(figsize=(10, 6))
plot_clusters(X_scaled, dbscan.labels_, 'DBSCAN聚类示例')
plt.savefig('images/dbscan_basic.png', dpi=300, bbox_inches='tight')
plt.close()

# 不同eps值的效果比较
eps_list = [0.2, 0.3, 0.5]
plt.figure(figsize=(15, 5))

for i, eps in enumerate(eps_list):
    plt.subplot(1, 3, i+1)
    dbscan = DBSCAN(eps=eps, min_samples=5)
    dbscan.fit(X_scaled)
    plot_clusters(X_scaled, dbscan.labels_, f'DBSCAN (eps={eps})')

plt.tight_layout()
plt.savefig('images/dbscan_eps_comparison.png', dpi=300, bbox_inches='tight')
plt.close()

# 不同min_samples值的效果比较
min_samples_list = [3, 5, 10]
plt.figure(figsize=(15, 5))

for i, min_samples in enumerate(min_samples_list):
    plt.subplot(1, 3, i+1)
    dbscan = DBSCAN(eps=0.3, min_samples=min_samples)
    dbscan.fit(X_scaled)
    plot_clusters(X_scaled, dbscan.labels_, f'DBSCAN (min_samples={min_samples})')

plt.tight_layout()
plt.savefig('images/dbscan_min_samples_comparison.png', dpi=300, bbox_inches='tight')
plt.close()

# 不同数据分布的效果比较
noise_levels = [0.05, 0.1, 0.2]
plt.figure(figsize=(15, 5))

for i, noise in enumerate(noise_levels):
    plt.subplot(1, 3, i+1)
    X_temp, _ = generate_data(noise=noise)
    X_temp_scaled = scaler.fit_transform(X_temp)
    dbscan = DBSCAN(eps=0.3, min_samples=5)
    dbscan.fit(X_temp_scaled)
    plot_clusters(X_temp_scaled, dbscan.labels_, f'DBSCAN (噪声={noise})')

plt.tight_layout()
plt.savefig('images/dbscan_noise_comparison.png', dpi=300, bbox_inches='tight')
plt.close()
