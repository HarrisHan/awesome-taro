import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.datasets import make_blobs, make_moons, make_circles

# 设置随机种子以确保结果可重现
np.random.seed(42)
plt.rcParams['font.family'] = ['WenQuanYi Zen Hei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 300

def generate_data(dataset_type='blobs', n_samples=300):
    """
    生成用于t-SNE的示例数据
    dataset_type: 数据集类型 ('blobs', 'moons', 'circles')
    n_samples: 样本数量
    """
    if dataset_type == 'blobs':
        data = make_blobs(n_samples=n_samples, centers=5, cluster_std=0.5,
                         random_state=42)
        X, y = data[0], data[1]
    elif dataset_type == 'moons':
        data = make_moons(n_samples=n_samples, noise=0.1, random_state=42)
        X, y = data[0], data[1]
    else:  # circles
        data = make_circles(n_samples=n_samples, noise=0.05, factor=0.3,
                          random_state=42)
        X, y = data[0], data[1]
    return X, y

class TSNE:
    def __init__(self, n_components=2, perplexity=30.0, learning_rate=500.0,
                 n_iter=500, random_state=None, visualization_mode=False):
        """
        初始化t-SNE
        n_components: 降维后的维度
        perplexity: 困惑度，影响局部邻域大小
        learning_rate: 学习率
        n_iter: 最大迭代次数
        random_state: 随机种子
        visualization_mode: 是否为可视化模式（减少迭代次数）
        """
        self.n_components = n_components
        self.perplexity = perplexity
        self.learning_rate = learning_rate
        self.n_iter = n_iter
        self.random_state = random_state
        self.visualization_mode = visualization_mode
        
    def _compute_pairwise_distances(self, X):
        """计算成对欧氏距离的平方"""
        sum_X = np.sum(np.square(X), axis=1)
        D = np.add(np.add(-2 * np.dot(X, X.T), sum_X).T, sum_X)
        return np.maximum(D, 0)  # 确保距离非负
    
    def _compute_joint_probabilities(self, D):
        """计算高维空间的联合概率分布"""
        n_samples = D.shape[0]
        P = np.zeros((n_samples, n_samples))
        beta = np.ones(n_samples)
        logU = np.log(self.perplexity)
        
        for i in range(n_samples):
            # 计算条件概率
            betamin = -np.inf
            betamax = np.inf
            Di = D[i, np.concatenate((np.r_[0:i], np.r_[i+1:n_samples]))]
            
            # 二分搜索找到合适的beta
            tries = 0
            while tries < 50:
                # 计算当前beta下的条件概率
                Pi = np.exp(-Di * beta[i])
                sumPi = np.sum(Pi)
                if sumPi == 0:
                    Pi = np.maximum(Pi, 1e-12)
                    sumPi = np.sum(Pi)
                Pi = Pi / sumPi
                
                # 计算熵
                H = -np.sum(Pi * np.log2(Pi + 1e-12))
                Hdiff = H - logU
                
                if np.abs(Hdiff) < 1e-5:
                    break
                
                if Hdiff > 0:
                    betamin = beta[i]
                    if betamax == np.inf:
                        beta[i] = beta[i] * 2
                    else:
                        beta[i] = (beta[i] + betamax) / 2
                else:
                    betamax = beta[i]
                    if betamin == -np.inf:
                        beta[i] = beta[i] / 2
                    else:
                        beta[i] = (beta[i] + betamin) / 2
                
                tries += 1
            
            # 存储概率
            P[i, np.concatenate((np.r_[0:i], np.r_[i+1:n_samples]))] = Pi
        
        # 对称化概率矩阵并归一化
        P = (P + P.T) / (2 * n_samples)
        P = np.maximum(P, 1e-12)
        return P
    
    def _compute_q_distribution(self, Y):
        """计算低维空间的t分布"""
        n_samples = Y.shape[0]
        
        # 计算成对欧氏距离的平方
        sum_Y = np.sum(np.square(Y), axis=1)
        D = np.add(np.add(-2 * np.dot(Y, Y.T), sum_Y).T, sum_Y)
        D = np.maximum(D, 0)  # 确保非负
        
        # 计算Q分布（Student t-分布，自由度为1）
        Q = 1.0 / (1.0 + D)
        np.fill_diagonal(Q, 0)
        
        # 归一化
        Q = Q / np.sum(Q)
        Q = np.maximum(Q, 1e-12)
        
        return Q, D
    
    def fit_transform(self, X):
        """执行t-SNE降维"""
        if self.random_state is not None:
            np.random.seed(self.random_state)
            
        n_samples = X.shape[0]
        
        # 初始化低维嵌入（使用PCA初始化）
        pca = PCA(n_components=self.n_components)
        Y = pca.fit_transform(X)
        Y = Y * 0.0001  # 缩小初始分布
        
        # 计算高维空间的概率分布
        D = self._compute_pairwise_distances(X)
        P = self._compute_joint_probabilities(D)
        
        # 早期夸大（增加因子）
        P = P * 12
        
        # 初始化动量和学习率
        Y_momentum = np.zeros_like(Y)
        momentum = 0.5
        final_momentum = 0.8
        momentum_switch_iter = 125  # 减少动量切换时间
        
        # 学习率退火参数
        min_gain = 0.01
        gains = np.ones_like(Y)
        
        # 记录最佳结果
        best_cost = np.inf
        best_Y = Y.copy()
        
        # 设置迭代次数（可视化模式下减少迭代次数）
        n_iter = min(self.n_iter, 250) if self.visualization_mode else self.n_iter
        
        print(f"开始t-SNE优化 (最大迭代次数: {n_iter})")
        for iteration in range(n_iter):
            # 计算低维空间的概率分布
            Q, distances = self._compute_q_distribution(Y)
            
            # 计算梯度
            PQ = P - Q
            dY = np.zeros_like(Y)
            
            # 计算吸引力和排斥力
            for i in range(n_samples):
                # 计算梯度
                diff = Y[i] - Y
                dY[i] = 4 * np.sum(
                    (PQ[i, :, np.newaxis] * diff) / (1.0 + distances[i, :, np.newaxis]),
                    axis=0
                )
            
            # 自适应增益
            gains = (gains + 0.2) * ((dY * Y_momentum) <= 0) + \
                   (gains * 0.8) * ((dY * Y_momentum) > 0)
            gains[gains < min_gain] = min_gain
            
            # 更新动量
            if iteration >= momentum_switch_iter:
                momentum = final_momentum
            
            # 应用动量和增益
            Y_momentum = momentum * Y_momentum - self.learning_rate * (gains * dY)
            Y = Y + Y_momentum
            
            # 中心化嵌入
            Y = Y - np.mean(Y, axis=0)
            
            # 移除早期夸大（延长早期夸大阶段）
            if iteration == 100:
                P = P / 12
            
            # 计算当前损失
            if (iteration + 1) % 50 == 0:
                cost = np.sum(P * np.log(P / Q))
                print(f"迭代 {iteration+1}/{self.n_iter}, 损失: {cost:.4f}")
                
                # 更新最佳结果
                if cost < best_cost:
                    best_cost = cost
                    best_Y = Y.copy()
        
        return best_Y

def plot_embedding(X, y, title):
    """可视化降维结果"""
    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(X[:, 0], X[:, 1], c=y, cmap='viridis', alpha=0.6)
    plt.colorbar(scatter, label='类别')
    plt.xlabel('第一维')
    plt.ylabel('第二维')
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

# 生成数据
datasets = {
    'blobs': '高斯分布数据',
    'moons': '新月形数据',
    'circles': '同心圆数据'
}

# 基础t-SNE效果展示
print("\n生成并处理数据...")
X, y = generate_data('blobs')
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print("\n执行基础t-SNE降维...")
tsne = TSNE(perplexity=30.0, learning_rate=500.0, random_state=42, visualization_mode=True)
X_tsne = tsne.fit_transform(X_scaled)

plt.figure(figsize=(10, 6))
plot_embedding(X_tsne, y, 't-SNE降维示例')
plt.savefig('images/tsne_basic.png', dpi=300, bbox_inches='tight')
plt.close()

# 不同数据集的效果比较
print("\n比较不同数据集的效果...")
plt.figure(figsize=(15, 5))

for i, (dataset_type, dataset_name) in enumerate(datasets.items()):
    print(f"\n处理{dataset_name}数据集...")
    plt.subplot(1, 3, i+1)
    X, y = generate_data(dataset_type)
    X_scaled = scaler.fit_transform(X)
    tsne = TSNE(perplexity=30.0, learning_rate=500.0, random_state=42, visualization_mode=True)
    X_tsne = tsne.fit_transform(X_scaled)
    plot_embedding(X_tsne, y, f't-SNE ({dataset_name})')

plt.tight_layout()
plt.savefig('images/tsne_datasets_comparison.png', dpi=300, bbox_inches='tight')
plt.close()

# 不同困惑度的效果比较
perplexities = [5, 30, 50]
plt.figure(figsize=(15, 5))

for i, perplexity in enumerate(perplexities):
    plt.subplot(1, 3, i+1)
    tsne = TSNE(perplexity=perplexity, learning_rate=200.0, random_state=42)
    X_tsne = tsne.fit_transform(X_scaled)
    plot_embedding(X_tsne, y, f't-SNE (困惑度={perplexity})')

plt.tight_layout()
plt.savefig('images/tsne_perplexity_comparison.png', dpi=300, bbox_inches='tight')
plt.close()

# 不同学习率的效果比较
learning_rates = [200.0, 500.0, 1000.0]
plt.figure(figsize=(15, 5))

for i, lr in enumerate(learning_rates):
    plt.subplot(1, 3, i+1)
    tsne = TSNE(perplexity=30.0, learning_rate=lr, random_state=42)
    X_tsne = tsne.fit_transform(X_scaled)
    plot_embedding(X_tsne, y, f't-SNE (学习率={lr})')

plt.tight_layout()
plt.savefig('images/tsne_learning_rate_comparison.png', dpi=300, bbox_inches='tight')
plt.close()
