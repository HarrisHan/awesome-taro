import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from scipy.stats import multivariate_normal

# 设置随机种子以确保结果可重现
np.random.seed(42)
plt.rcParams['font.family'] = ['WenQuanYi Zen Hei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 300

def generate_data(n_samples=300, n_components=3):
    """
    生成用于GMM的示例数据
    n_samples: 样本数量
    n_components: 高斯分量数量
    """
    # 生成三个不同的高斯分布
    means = [[-2, -2], [2, 2], [0, 0]]
    covs = [[[1, 0.5], [0.5, 1]], 
            [[1.5, -0.5], [-0.5, 1.5]], 
            [[1, 0], [0, 1]]]
    weights = [0.3, 0.4, 0.3]
    
    X = np.zeros((n_samples, 2))
    y = np.zeros(n_samples)
    
    # 根据权重生成样本
    current_idx = 0
    for i in range(n_components):
        n_samples_i = int(weights[i] * n_samples)
        X[current_idx:current_idx + n_samples_i] = np.random.multivariate_normal(
            means[i], covs[i], n_samples_i
        )
        y[current_idx:current_idx + n_samples_i] = i
        current_idx += n_samples_i
    
    return X, y

class GMM:
    def __init__(self, n_components=3, max_iters=200, tol=1e-6, min_covar=1e-5,
                 n_init=5, init_params='kmeans++'):
        """
        初始化高斯混合模型
        n_components: 高斯分量数量
        max_iters: 最大迭代次数
        tol: 收敛阈值
        min_covar: 最小协方差值，用于数值稳定性
        n_init: 不同初始化尝试的次数
        init_params: 初始化方法，可选 'kmeans++' 或 'random'
        """
        self.n_components = n_components
        self.max_iters = max_iters
        self.tol = tol
        self.min_covar = min_covar
        self.n_init = n_init
        self.init_params = init_params
        
        # 初始化模型参数为None
        self._initialize_parameters()
        
        # 最佳模型参数
        self.best_weights = None
        self.best_means = None
        self.best_covs = None
        self.best_score = -np.inf
        
    def _initialize_parameters(self):
        """
        初始化模型参数为默认值
        """
        self.weights = np.ones(self.n_components) / self.n_components
        self.means = None
        self.covs = None
        
    def _check_initialization(self, n_features):
        """
        检查并确保所有参数都已正确初始化
        """
        if self.means is None:
            self.means = np.zeros((self.n_components, n_features))
        if self.covs is None:
            self.covs = np.array([np.eye(n_features) for _ in range(self.n_components)])
        
    def initialize_parameters(self, X):
        """
        初始化模型参数
        X: 输入数据，形状为(n_samples, n_features)
        """
        n_samples, n_features = X.shape
        
        # 使用K-means++策略初始化均值
        self.means = np.zeros((self.n_components, n_features))
        
        # 随机选择第一个中心
        first_idx = np.random.choice(n_samples)
        self.means[0] = X[first_idx]
        
        # 选择剩余的中心
        for k in range(1, self.n_components):
            # 计算每个点到已有中心的最小距离
            min_distances = np.min([
                np.sum((X - center) ** 2, axis=1) 
                for center in self.means[:k]
            ], axis=0)
            
            # 按距离的平方作为概率选择下一个中心
            probs = min_distances / min_distances.sum()
            next_idx = np.random.choice(n_samples, p=probs)
            self.means[k] = X[next_idx]
        
        # 初始化协方差矩阵
        # 使用数据的协方差矩阵的一小部分作为初始值
        data_cov = np.cov(X.T) + 1e-6 * np.eye(n_features)
        self.covs = np.array([data_cov for _ in range(self.n_components)])
        
        # 为每个分量添加随机扰动以打破对称性
        for k in range(self.n_components):
            self.covs[k] = self.covs[k] * (0.8 + 0.4 * np.random.random())
        
    def e_step(self, X):
        """
        E步：计算后验概率（责任）
        X: 输入数据，形状为(n_samples, n_features)
        返回：responsibilities，形状为(n_samples, n_components)
        """
        n_samples = X.shape[0]
        log_resp = np.zeros((n_samples, self.n_components))
        
        try:
            # 在对数空间中计算以提高数值稳定性
            for k in range(self.n_components):
                gaussian = multivariate_normal(
                    mean=self.means[k],
                    cov=self.covs[k],
                    allow_singular=True
                )
                log_resp[:, k] = np.log(self.weights[k] + 1e-300) + gaussian.logpdf(X)
            
            # 使用log-sum-exp技巧
            log_resp_max = log_resp.max(axis=1, keepdims=True)
            log_norm = log_resp_max + np.log(
                np.sum(np.exp(log_resp - log_resp_max), axis=1, keepdims=True)
            )
            
            # 计算最终的责任值
            log_resp = log_resp - log_norm
            responsibilities = np.exp(log_resp)
            
            # 确保数值稳定性
            responsibilities = np.clip(responsibilities, 1e-300, 1.0)
            responsibilities /= responsibilities.sum(axis=1, keepdims=True)
            
            return responsibilities
            
        except (np.linalg.LinAlgError, ValueError) as e:
            print(f"警告：E步计算出错 - {str(e)}")
            # 返回均匀分布的责任值
            return np.ones((n_samples, self.n_components)) / self.n_components
    
    def m_step(self, X, responsibilities):
        """
        M步：更新模型参数
        X: 输入数据，形状为(n_samples, n_features)
        responsibilities: 责任矩阵，形状为(n_samples, n_components)
        """
        n_samples, n_features = X.shape
        
        # 计算每个分量的有效样本数
        Nk = responsibilities.sum(axis=0)
        
        # 防止除零
        Nk = np.maximum(Nk, 1e-10)
        
        # 更新权重
        self.weights = Nk / n_samples
        
        # 更新均值
        self.means = np.dot(responsibilities.T, X) / Nk[:, np.newaxis]
        
        # 初始化新的协方差矩阵数组
        new_covs = np.zeros((self.n_components, n_features, n_features))
        
        # 更新协方差矩阵
        for k in range(self.n_components):
            diff = X - self.means[k]
            weighted_diff = responsibilities[:, k:k+1] * diff
            new_covs[k] = np.dot(weighted_diff.T, diff) / Nk[k]
            
            # 添加正则化项以确保数值稳定性
            min_covar = 1e-6
            new_covs[k] += min_covar * np.eye(n_features)
            
            # 确保协方差矩阵是对称的
            new_covs[k] = (new_covs[k] + new_covs[k].T) / 2.0
        
        # 一次性更新所有协方差矩阵
        self.covs = new_covs
    
    def fit(self, X):
        """
        训练GMM模型
        X: 输入数据，形状为(n_samples, n_features)
        """
        n_samples, n_features = X.shape
        best_score = -np.inf
        
        for init in range(self.n_init):
            print(f"\n开始第 {init + 1}/{self.n_init} 次初始化...")
            
            # 重置参数
            self._initialize_parameters()
            self._check_initialization(n_features)
            
            # 初始化参数
            self.initialize_parameters(X)
            
            # 确保参数已正确初始化
            self._check_initialization(n_features)
            
            # EM算法迭代
            log_likelihood_old = -np.inf
            no_improvement_count = 0
            converged = False
            
            for iteration in range(self.max_iters):
                try:
                    # E步
                    responsibilities = self.e_step(X)
                    
                    # M步
                    self.m_step(X, responsibilities)
                    
                    # 计算对数似然
                    log_likelihood = self.compute_log_likelihood(X)
                    
                    # 计算相对改善
                    rel_improvement = abs((log_likelihood - log_likelihood_old) / 
                                       (abs(log_likelihood_old) + 1e-10))
                    
                    # 检查收敛
                    if rel_improvement < self.tol:
                        no_improvement_count += 1
                        if no_improvement_count >= 3:  # 连续3次改善很小则认为收敛
                            converged = True
                            break
                    else:
                        no_improvement_count = 0
                        
                    log_likelihood_old = log_likelihood
                    
                    if iteration % 10 == 0:
                        print(f'迭代 {iteration}, 对数似然: {log_likelihood:.4f}, '
                              f'相对改善: {rel_improvement:.6f}')
                        
                except np.linalg.LinAlgError:
                    print("警告：检测到数值不稳定性，尝试重新初始化...")
                    break
            
            # 保存最佳结果
            if converged and log_likelihood > best_score:
                best_score = log_likelihood
                # 确保参数存在且可复制
                if self.weights is not None and self.means is not None and self.covs is not None:
                    self.best_weights = np.array(self.weights)
                    self.best_means = np.array(self.means)
                    self.best_covs = np.array(self.covs)
                    print(f"找到新的最佳模型，对数似然: {best_score:.4f}")
        
        # 使用最佳参数
        if (self.best_means is not None and 
            self.best_weights is not None and 
            self.best_covs is not None):
            self.weights = np.array(self.best_weights)
            self.means = np.array(self.best_means)
            self.covs = np.array(self.best_covs)
            print(f"\n最终模型对数似然: {best_score:.4f}")
        else:
            print("\n警告：未找到有效的模型参数")
    
    def predict(self, X):
        """
        预测样本的类别
        """
        responsibilities = self.e_step(X)
        return np.argmax(responsibilities, axis=1)
    
    def compute_log_likelihood(self, X):
        """
        计算对数似然
        X: 输入数据，形状为(n_samples, n_features)
        返回：对数似然值
        """
        n_samples = X.shape[0]
        log_likelihood = np.zeros(n_samples)
        
        try:
            # 在对数空间中计算以提高数值稳定性
            log_prob = np.zeros((n_samples, self.n_components))
            
            for k in range(self.n_components):
                gaussian = multivariate_normal(
                    mean=self.means[k],
                    cov=self.covs[k],
                    allow_singular=True
                )
                log_prob[:, k] = np.log(self.weights[k] + 1e-300) + gaussian.logpdf(X)
            
            # 使用log-sum-exp技巧计算
            log_prob_max = log_prob.max(axis=1, keepdims=True)
            log_likelihood = log_prob_max.ravel() + np.log(
                np.sum(np.exp(log_prob - log_prob_max), axis=1)
            )
            
            return np.sum(log_likelihood)
            
        except (np.linalg.LinAlgError, ValueError) as e:
            print(f"警告：计算对数似然时出错 - {str(e)}")
            return -np.inf

def plot_gmm_results(X, y_true, gmm, title):
    """
    可视化GMM聚类结果
    """
    # 创建网格点
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 100),
                        np.linspace(y_min, y_max, 100))
    
    # 计算每个网格点的概率密度
    X_grid = np.c_[xx.ravel(), yy.ravel()]
    Z = np.zeros(X_grid.shape[0])
    
    for k in range(gmm.n_components):
        gaussian = multivariate_normal(
            mean=gmm.means[k],
            cov=gmm.covs[k]
        )
        Z += gmm.weights[k] * gaussian.pdf(X_grid)
    
    Z = Z.reshape(xx.shape)
    
    # 绘制概率密度等高线和数据点
    plt.contourf(xx, yy, Z, levels=10, alpha=0.3, cmap='viridis')
    plt.colorbar(label='概率密度')
    
    # 绘制数据点
    predictions = gmm.predict(X)
    plt.scatter(X[:, 0], X[:, 1], c=predictions, cmap='viridis', alpha=0.8)
    
    # 绘制均值点
    plt.scatter(gmm.means[:, 0], gmm.means[:, 1], 
               c='red', marker='*', s=200, label='分量中心')
    
    plt.xlabel('特征1')
    plt.ylabel('特征2')
    plt.title(title)
    plt.legend()
    plt.grid(True)

# 生成数据
X, y_true = generate_data()

# 标准化数据
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 基础GMM效果展示
gmm = GMM(n_components=3)
gmm.fit(X_scaled)

plt.figure(figsize=(10, 6))
plot_gmm_results(X_scaled, y_true, gmm, 'GMM聚类示例')
plt.savefig('images/gmm_basic.png', dpi=300, bbox_inches='tight')
plt.close()

# 不同分量数量的效果比较
n_components_list = [2, 3, 4]
plt.figure(figsize=(15, 5))

for i, n_components in enumerate(n_components_list):
    plt.subplot(1, 3, i+1)
    gmm = GMM(n_components=n_components)
    gmm.fit(X_scaled)
    plot_gmm_results(X_scaled, y_true, gmm, f'GMM (K={n_components})')

plt.tight_layout()
plt.savefig('images/gmm_components_comparison.png', dpi=300, bbox_inches='tight')
plt.close()

# 不同协方差结构的效果比较
covs_list = [
    [[[0.5, 0], [0, 0.5]], [[0.5, 0], [0, 0.5]], [[0.5, 0], [0, 0.5]]],  # 球形
    [[[1, 0], [0, 0.3]], [[0.3, 0], [0, 1]], [[0.7, 0], [0, 0.7]]],      # 对角
    [[[1, 0.5], [0.5, 1]], [[1.5, -0.5], [-0.5, 1.5]], [[1, 0], [0, 1]]] # 完全
]

plt.figure(figsize=(15, 5))

for i, covs in enumerate(covs_list):
    # 生成特定协方差结构的数据
    X_temp = np.zeros((300, 2))
    current_idx = 0
    for k in range(3):
        n_samples_k = 100
        X_temp[current_idx:current_idx + n_samples_k] = np.random.multivariate_normal(
            [2*k-2, 2*k-2], covs[k], n_samples_k
        )
        current_idx += n_samples_k
    
    X_temp_scaled = scaler.fit_transform(X_temp)
    
    plt.subplot(1, 3, i+1)
    gmm = GMM(n_components=3)
    gmm.fit(X_temp_scaled)
    
    cov_types = ['球形协方差', '对角协方差', '完全协方差']
    plot_gmm_results(X_temp_scaled, None, gmm, f'GMM ({cov_types[i]})')

plt.tight_layout()
plt.savefig('images/gmm_covariance_comparison.png', dpi=300, bbox_inches='tight')
plt.close()
