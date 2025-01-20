import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.font_manager as fm
import os

def check_plot_properties():
    """
    验证图像属性
    """
    # 确保images目录存在
    os.makedirs('images', exist_ok=True)

    # 重置matplotlib配置
    plt.rcdefaults()
    
    # 配置中文字体
    font_paths = [
        '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
        '/usr/share/fonts/wqy-zenhei/wqy-zenhei.ttc'
    ]

    font_found = False
    for font_path in font_paths:
        if os.path.exists(font_path):
            print(f"Found font at: {font_path}")
            fm.fontManager.addfont(font_path)
            plt.rcParams['font.family'] = ['WenQuanYi Zen Hei']
            font_found = True
            break

    if not font_found:
        print("Warning: Could not find WenQuanYi Zen Hei font")
        
    # 配置matplotlib
    plt.rcParams['figure.dpi'] = 300
    plt.rcParams['savefig.dpi'] = 300
    plt.rcParams['axes.unicode_minus'] = False
    
    # 清除并重新构建字体缓存
    fm.findfont('WenQuanYi Zen Hei', rebuild_if_missing=True)

    print("=== 检查matplotlib设置 ===")
    print(f"DPI设置: {plt.rcParams['figure.dpi']}")
    print(f"字体设置: {plt.rcParams['font.family']}")
    print(f"Unicode减号设置: {plt.rcParams['axes.unicode_minus']}")
    
    # 测试中文显示
    plt.figure(figsize=(6, 4))
    plt.plot([1, 2, 3], [1, 2, 3])
    plt.title('测试中文显示')
    plt.xlabel('测试 X 轴')
    plt.ylabel('测试 Y 轴')
    plt.savefig('images/test_font.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("\n=== 检查生成的图像 ===")
    files = [
        'lightgbm_basic.png',
        'lightgbm_learning_rate_comparison.png',
        'lightgbm_num_leaves_comparison.png'
    ]
    
    for file in files:
        img = mpimg.imread(f'images/{file}')
        print(f"\n{file}:")
        print(f"形状: {img.shape}")
        print(f"类型: {img.dtype}")

if __name__ == '__main__':
    check_plot_properties()
