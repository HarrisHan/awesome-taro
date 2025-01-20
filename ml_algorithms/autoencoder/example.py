import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

# 设置随机种子以确保结果可重现
np.random.seed(42)
torch.manual_seed(42)
plt.rcParams['font.family'] = ['WenQuanYi Zen Hei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 300

class Autoencoder(nn.Module):
    """
    自编码器实现
    """
    def __init__(self, input_dim=784, hidden_dim=128):
        super(Autoencoder, self).__init__()
        
        # 编码器
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, hidden_dim),
            nn.ReLU()
        )
        
        # 解码器
        self.decoder = nn.Sequential(
            nn.Linear(hidden_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 512),
            nn.ReLU(),
            nn.Linear(512, input_dim),
            nn.Sigmoid()
        )
        
    def forward(self, x):
        """前向传播"""
        # 编码
        encoded = self.encoder(x)
        # 解码
        decoded = self.decoder(encoded)
        return encoded, decoded

def train_autoencoder(model, train_loader, num_epochs=50, learning_rate=1e-3):
    """
    训练自编码器
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    losses = []
    
    for epoch in range(num_epochs):
        model.train()
        total_loss = 0
        for data in train_loader:
            img, _ = data
            img = img.view(img.size(0), -1).to(device)
            
            # 前向传播
            _, reconstructed = model(img)
            loss = criterion(reconstructed, img)
            
            # 反向传播和优化
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        avg_loss = total_loss / len(train_loader)
        losses.append(avg_loss)
        
        if (epoch + 1) % 10 == 0:
            print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {avg_loss:.4f}')
    
    return losses

def plot_loss(losses):
    """绘制损失曲线"""
    plt.figure(figsize=(10, 6))
    plt.plot(losses)
    plt.xlabel('迭代次数')
    plt.ylabel('重构损失')
    plt.title('自编码器训练损失')
    plt.grid(True)
    plt.savefig('images/autoencoder_loss.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_reconstruction(model, test_loader, n_images=10):
    """可视化重构结果"""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.eval()
    
    with torch.no_grad():
        for data in test_loader:
            img, _ = data
            img = img.view(img.size(0), -1).to(device)
            _, reconstructed = model(img)
            
            # 选择n_images个样本进行可视化
            fig, axes = plt.subplots(2, n_images, figsize=(20, 4))
            
            for i in range(n_images):
                # 原始图像
                axes[0, i].imshow(img[i].cpu().view(28, 28), cmap='gray')
                axes[0, i].axis('off')
                if i == 0:
                    axes[0, i].set_title('原始图像')
                
                # 重构图像
                axes[1, i].imshow(reconstructed[i].cpu().view(28, 28), cmap='gray')
                axes[1, i].axis('off')
                if i == 0:
                    axes[1, i].set_title('重构图像')
            
            plt.tight_layout()
            plt.savefig('images/autoencoder_reconstruction.png', dpi=300, bbox_inches='tight')
            plt.close()
            break

def plot_latent_space(model, test_loader):
    """可视化潜在空间"""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.eval()
    
    encoded_data = []
    labels = []
    
    with torch.no_grad():
        for data in test_loader:
            img, label = data
            img = img.view(img.size(0), -1).to(device)
            encoded, _ = model(img)
            encoded_data.append(encoded.cpu().numpy())
            labels.append(label.numpy())
    
    encoded_data = np.concatenate(encoded_data, axis=0)
    labels = np.concatenate(labels, axis=0)
    
    # 选择前两个维度进行可视化
    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(encoded_data[:, 0], encoded_data[:, 1], 
                         c=labels, cmap='tab10', alpha=0.6)
    plt.colorbar(scatter, label='类别')
    plt.xlabel('潜在维度1')
    plt.ylabel('潜在维度2')
    plt.title('自编码器潜在空间可视化')
    plt.grid(True)
    plt.savefig('images/autoencoder_latent_space.png', dpi=300, bbox_inches='tight')
    plt.close()

# 加载MNIST数据集
transform = transforms.Compose([
    transforms.ToTensor()
])

train_dataset = datasets.MNIST(root='./data', train=True,
                             download=True, transform=transform)
test_dataset = datasets.MNIST(root='./data', train=False,
                            download=True, transform=transform)

train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=128, shuffle=False)

# 创建和训练模型
model = Autoencoder(input_dim=784, hidden_dim=128)
losses = train_autoencoder(model, train_loader)

# 生成可视化结果
plot_loss(losses)
plot_reconstruction(model, test_loader)
plot_latent_space(model, test_loader)
