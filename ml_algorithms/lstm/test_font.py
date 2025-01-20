import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os

# Add system font directories
font_dirs = ['/usr/share/fonts/']
font_files = fm.findSystemFonts(fontpaths=font_dirs)

# Load fonts
for font_file in font_files:
    try:
        fm.fontManager.addfont(font_file)
    except:
        pass

# Configure font settings
plt.rcParams['font.family'] = ['WenQuanYi Zen Hei']
plt.rcParams['axes.unicode_minus'] = False  # Fix minus sign display
plt.rcParams['figure.dpi'] = 300

# Print available font families for debugging
print("Available font families:")
for font in fm.fontManager.ttflist:
    print(font.name)

plt.figure(figsize=(10, 6))
plt.plot(np.random.randn(10))
plt.title('测试中文显示')
plt.xlabel('测试')
plt.ylabel('测试')
plt.savefig('test_chinese.png', dpi=300, bbox_inches='tight')
plt.close()
