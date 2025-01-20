import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # Required for 3D plotting
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import lightgbm as lgb
import matplotlib.font_manager as fm
import os

# 设置随机种子以确保结果可重现
np.random.seed(42)

# 确保images目录存在
os.makedirs('images', exist_ok=True)

# 配置matplotlib
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['axes.unicode_minus'] = False

# 配置中文字体
font_paths = [
    '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
    '/usr/share/fonts/wqy-zenhei/wqy-zenhei.ttc'
]

font_found = False
for font_path in font_paths:
    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        plt.rcParams['font.family'] = ['WenQuanYi Zen Hei']
        font_found = True
        break

if not font_found:
    print("Warning: Could not find WenQuanYi Zen Hei font")

def generate_data(n_samples=1000):
    """
    生成非线性回归数据
    """
    X = np.random.randn(n_samples, 2)
    y = 0.5 * X[:, 0]**2 + 2 * np.sin(2 * X[:, 1]) + np.random.normal(0, 0.1, n_samples)
    return X, y

def train_lightgbm(X_train, y_train, X_val=None, y_val=None, params=None):
    """
    训练LightGBM模型
    """
    if params is None:
        params = {
            'objective': 'regression',
            'metric': 'rmse',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.9,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': -1
        }
    
    train_data = lgb.Dataset(X_train, label=y_train)
    valid_sets = [train_data]
    valid_names = ['train']
    
    if X_val is not None and y_val is not None:
        valid_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
        valid_sets.append(valid_data)
        valid_names.append('valid')
    
    model = lgb.train(
        params,
        train_data,
        num_boost_round=100,
        valid_sets=valid_sets,
        valid_names=valid_names,
        callbacks=[lgb.early_stopping(10)] if X_val is not None else None
    )
    
    return model

def plot_prediction_surface(X, y, model, title):
    """
    绘制预测表面
    """
    # 创建预测网格
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.1),
                        np.arange(y_min, y_max, 0.1))
    
    X_grid = np.c_[xx.ravel(), yy.ravel()]
    Z = model.predict(X_grid)
    Z = Z.reshape(xx.shape)
    
    # 创建2D等高线图
    plt.contourf(xx, yy, Z, levels=20, cmap='viridis', alpha=0.6)
    plt.colorbar(label='预测值')
    
    # 绘制训练数据点
    scatter = plt.scatter(X[:, 0], X[:, 1], c=y, 
                         cmap='coolwarm', alpha=0.6, 
                         s=50, label='训练数据')
    plt.colorbar(scatter, label='实际值')
    
    plt.xlabel('特征1')
    plt.ylabel('特征2')
    plt.title(title)
    plt.grid(True)

# 生成数据
X, y = generate_data()

# 数据标准化
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 划分训练集和验证集
X_train, X_val, y_train, y_val = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# 基础LightGBM效果展示
model = train_lightgbm(X_train, y_train, X_val, y_val)

plt.figure(figsize=(10, 6))
plot_prediction_surface(X_scaled, y, model, 'LightGBM回归示例')
plt.savefig('images/lightgbm_basic.png', dpi=300, bbox_inches='tight')
plt.close()

# 不同学习率的效果比较
learning_rates = [0.01, 0.1, 0.5]
plt.figure(figsize=(15, 5))

for i, lr in enumerate(learning_rates):
    params = {
        'objective': 'regression',
        'metric': 'rmse',
        'num_leaves': 31,
        'learning_rate': lr,
        'feature_fraction': 0.9,
        'bagging_fraction': 0.8,
        'bagging_freq': 5,
        'verbose': -1
    }
    
    model = train_lightgbm(X_train, y_train, X_val, y_val, params)
    
    plt.subplot(1, 3, i+1)
    plot_prediction_surface(X_scaled, y, model, f'LightGBM (学习率={lr})')

plt.tight_layout()
plt.savefig('images/lightgbm_learning_rate_comparison.png', dpi=300, bbox_inches='tight')
plt.close()

# 不同叶子数量的效果比较
num_leaves_list = [7, 31, 127]
plt.figure(figsize=(15, 5))

for i, num_leaves in enumerate(num_leaves_list):
    params = {
        'objective': 'regression',
        'metric': 'rmse',
        'num_leaves': num_leaves,
        'learning_rate': 0.05,
        'feature_fraction': 0.9,
        'bagging_fraction': 0.8,
        'bagging_freq': 5,
        'verbose': -1
    }
    
    model = train_lightgbm(X_train, y_train, X_val, y_val, params)
    
    plt.subplot(1, 3, i+1)
    plot_prediction_surface(X_scaled, y, model, f'LightGBM (叶子数={num_leaves})')

plt.tight_layout()
plt.savefig('images/lightgbm_num_leaves_comparison.png', dpi=300, bbox_inches='tight')
plt.close()
