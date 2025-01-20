import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import sys

# 设置随机种子以确保结果可重现
print("Setting up environment...")
np.random.seed(42)

# Configure matplotlib
print("Configuring matplotlib...")
plt.rcParams['font.family'] = ['WenQuanYi Zen Hei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 300

def save_figure(fig, filename):
    """Helper function to safely save figures"""
    try:
        fig.savefig(f'images/{filename}', dpi=300, bbox_inches='tight')
        plt.close(fig)
        print(f"Successfully saved {filename}")
    except Exception as e:
        print(f"Error saving {filename}: {e}", file=sys.stderr)
        plt.close(fig)  # Ensure figure is closed even if save fails

def generate_data(n_samples=1000):
    """
    生成用于XGBoost的示例数据
    n_samples: 样本数量
    """
    X = np.random.randn(n_samples, 2)
    # 生成非线性决策边界
    y = np.logical_xor(X[:, 0] > 0, X[:, 1] > 0)
    # 添加一些噪声
    mask = np.random.rand(n_samples) < 0.1
    y = np.logical_xor(y, mask)
    return X, y.astype(int)

class XGBoostTree:
    """XGBoost决策树实现"""
    def __init__(self, max_depth=3, min_samples_split=2, learning_rate=0.1):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.learning_rate = learning_rate
        self.tree = None
        
    def _calculate_weights(self, grad, hess):
        """计算叶子节点的权重"""
        return -np.sum(grad) / (np.sum(hess) + 1e-6)
    
    def _split_node(self, X, grad, hess, depth, max_iter=1000):
        """递归构建决策树"""
        print(f"Building tree at depth {depth}")
        
        # Base cases
        if depth >= self.max_depth:
            print(f"Reached maximum depth {self.max_depth}")
            return self._calculate_weights(grad, hess)
        if len(X) < self.min_samples_split:
            print(f"Reached minimum samples {self.min_samples_split}")
            return self._calculate_weights(grad, hess)
            
        best_gain = 0
        best_split = None
        
        # Optimize feature iteration
        features = range(X.shape[1])
        n_features = len(features)
        
        for i, feature in enumerate(features):
            if i % 10 == 0:  # Progress tracking
                print(f"Processing feature {i+1}/{n_features}")
                
            # Use percentiles instead of unique values for efficiency
            percentiles = np.percentile(X[:, feature], np.linspace(1, 99, 20))
            for threshold in percentiles:
                mask = X[:, feature] <= threshold
                n_left = np.sum(mask)
                n_right = len(mask) - n_left
                
                # Minimum samples check
                if n_left < 1 or n_right < 1:
                    continue
                    
                gain = self._calculate_gain(grad, hess, mask)
                if gain > best_gain:
                    best_gain = gain
                    best_split = (feature, threshold, mask)
        
        if best_split is None:
            print("No valid split found")
            return self._calculate_weights(grad, hess)
            
        feature, threshold, mask = best_split
        print(f"Split found at feature {feature}, threshold {threshold:.4f}")
        
        return {
            'feature': feature,
            'threshold': threshold,
            'left': self._split_node(X[mask], grad[mask], hess[mask], depth + 1),
            'right': self._split_node(X[~mask], grad[~mask], hess[~mask], depth + 1)
        }
    
    def _calculate_gain(self, grad, hess, mask):
        """计算分裂增益"""
        left_grad = grad[mask]
        left_hess = hess[mask]
        right_grad = grad[~mask]
        right_hess = hess[~mask]
        
        gain = (np.sum(left_grad) ** 2 / (np.sum(left_hess) + 1e-6) +
                np.sum(right_grad) ** 2 / (np.sum(right_hess) + 1e-6) -
                np.sum(grad) ** 2 / (np.sum(hess) + 1e-6)) / 2
        return gain
    
    def fit(self, X, grad, hess):
        """训练决策树"""
        self.tree = self._split_node(X, grad, hess, depth=0)
        return self
    
    def predict(self, X):
        """预测"""
        return np.array([self._predict_single(x, self.tree) for x in X])
    
    def _predict_single(self, x, node):
        """单样本预测"""
        if isinstance(node, dict):
            if x[node['feature']] <= node['threshold']:
                return self._predict_single(x, node['left'])
            return self._predict_single(x, node['right'])
        return node

class XGBoost:
    """XGBoost实现"""
    def __init__(self, n_estimators=100, max_depth=3, learning_rate=0.1):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.trees = []
        self.base_score = 0
    
    def _logistic_loss(self, y_pred, y):
        """计算逻辑损失"""
        y_pred = 1.0 / (1.0 + np.exp(-y_pred))
        grad = y_pred - y
        hess = y_pred * (1 - y_pred)
        return grad, hess
    
    def fit(self, X, y):
        """训练XGBoost模型"""
        print("\nStarting XGBoost training...")
        print(f"Data shape: X={X.shape}, y={y.shape}")
        print(f"Parameters: n_estimators={self.n_estimators}, max_depth={self.max_depth}, learning_rate={self.learning_rate}")
        
        # Initialize base score
        self.base_score = np.log(np.mean(y) / (1 - np.mean(y)))
        f = np.full(len(y), self.base_score)
        
        # Training loop with progress tracking
        for i in range(self.n_estimators):
            if i % 10 == 0:
                print(f"\nTraining tree {i+1}/{self.n_estimators}")
            
            # Calculate gradients
            grad, hess = self._logistic_loss(f, y)
            
            # Train single tree
            tree = XGBoostTree(
                max_depth=min(self.max_depth, 3),  # Limit depth for efficiency
                learning_rate=self.learning_rate
            )
            tree.fit(X, grad, hess)
            self.trees.append(tree)
            
            # Update predictions
            update = self.learning_rate * tree.predict(X)
            f += update
            
            # Print progress metrics
            if i % 10 == 0:
                pred = self.predict(X)
                accuracy = np.mean(pred == y)
                print(f"Current accuracy: {accuracy:.4f}")
        
        print("\nTraining completed successfully")
    
    def predict_proba(self, X):
        """预测概率"""
        f = np.full(len(X), self.base_score)
        for tree in self.trees:
            f += self.learning_rate * tree.predict(X)
        return 1.0 / (1.0 + np.exp(-f))
    
    def predict(self, X):
        """预测类别"""
        return (self.predict_proba(X) > 0.5).astype(int)

def plot_decision_boundary(X, y, model, title):
    """绘制决策边界"""
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 100),
                        np.linspace(y_min, y_max, 100))
    
    Z = model.predict_proba(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)
    
    plt.contourf(xx, yy, Z, alpha=0.4, cmap='RdYlBu')
    plt.scatter(X[:, 0], X[:, 1], c=y, cmap='RdYlBu', alpha=0.8)
    plt.xlabel('特征1')
    plt.ylabel('特征2')
    plt.title(title)
    plt.colorbar(label='预测概率')
    plt.grid(True)

# Generate smaller dataset for testing
print("Generating data...")
X, y = generate_data(n_samples=500)  # Reduced sample size
print("Splitting data...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Standardizing data...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train base XGBoost model with reduced parameters
print("Training base XGBoost model...")
xgb = XGBoost(n_estimators=50, max_depth=3, learning_rate=0.1)  # Reduced n_estimators
xgb.fit(X_train_scaled, y_train)

# Generate basic visualization
print("Generating basic visualization...")
fig1 = plt.figure(figsize=(10, 6))
plot_decision_boundary(X_train_scaled, y_train, xgb, 'XGBoost分类示例')
save_figure(fig1, 'xgboost_basic.png')

# Compare different numbers of trees (reduced parameters)
print("Comparing different numbers of trees...")
n_estimators_list = [5, 10, 20]  # Reduced numbers
fig2 = plt.figure(figsize=(15, 5))

for i, n_estimators in enumerate(n_estimators_list):
    print(f"Training model with {n_estimators} trees...")
    plt.subplot(1, 3, i+1)
    xgb = XGBoost(n_estimators=n_estimators, max_depth=2)  # Reduced depth
    xgb.fit(X_train_scaled, y_train)
    plot_decision_boundary(X_train_scaled, y_train, xgb, 
                         f'XGBoost (树数量={n_estimators})')

plt.tight_layout()
save_figure(fig2, 'xgboost_n_estimators_comparison.png')

# Compare different maximum depths
print("Comparing different maximum depths...")
max_depths = [2, 3, 5]
fig3 = plt.figure(figsize=(15, 5))

for i, max_depth in enumerate(max_depths):
    print(f"Training model with max_depth={max_depth}...")
    plt.subplot(1, 3, i+1)
    xgb = XGBoost(n_estimators=100, max_depth=max_depth)
    xgb.fit(X_train_scaled, y_train)
    plot_decision_boundary(X_train_scaled, y_train, xgb,
                         f'XGBoost (最大深度={max_depth})')

plt.tight_layout()
save_figure(fig3, 'xgboost_depth_comparison.png')

# Compare different learning rates
print("Comparing different learning rates...")
learning_rates = [0.01, 0.1, 0.5]
fig4 = plt.figure(figsize=(15, 5))

for i, lr in enumerate(learning_rates):
    print(f"Training model with learning_rate={lr}...")
    plt.subplot(1, 3, i+1)
    xgb = XGBoost(n_estimators=100, max_depth=3, learning_rate=lr)
    xgb.fit(X_train_scaled, y_train)
    plot_decision_boundary(X_train_scaled, y_train, xgb,
                         f'XGBoost (学习率={lr})')

plt.tight_layout()
save_figure(fig4, 'xgboost_learning_rate_comparison.png')

print("All visualizations completed successfully")
