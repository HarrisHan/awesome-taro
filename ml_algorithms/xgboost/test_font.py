import matplotlib.pyplot as plt
import numpy as np

# Configure font settings
plt.rcParams['font.family'] = ['WenQuanYi Zen Hei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 300

# Create a simple plot with Chinese text
plt.figure(figsize=(8, 6))
x = np.linspace(0, 10, 100)
y = np.sin(x)
plt.plot(x, y)
plt.title('测试中文显示')
plt.xlabel('测试 X 轴')
plt.ylabel('测试 Y 轴')
plt.grid(True)
plt.savefig('images/test_font.png', dpi=300, bbox_inches='tight')
plt.close()

print("Font test completed. Check images/test_font.png")
