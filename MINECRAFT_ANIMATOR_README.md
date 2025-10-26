# Minecraft 动画制作器 - 使用指南

## 项目介绍

这是一个基于 Flask 和 Three.js 的 Minecraft 风格动画制作器，支持：
- 🎬 8种建筑动画效果
- ✨ 4种魔法主题特效
- 🤖 AI 助手集成（使用 Gemini API）
- 💾 存档导入/导出
- 🎨 材质包支持
- 📦 模型加载和编辑

## 快速开始

### 1. 安装依赖

```bash
pip install flask requests
```

### 2. 启动服务器

```bash
python minecraft_animator.py
```

或者使用命令行参数：

```bash
# 从URL加载模型
python minecraft_animator.py --input_model https://example.com/model.glb

# 从本地文件加载模型
python minecraft_animator.py --input_model ./models/house.glb

# 加载存档
python minecraft_animator.py --input_data ./saves/my_save.zip
```

### 3. 设置 API 密钥（可选）

如果要使用 AI 功能，创建一个 `key.txt` 文件并将您的 Gemini API 密钥放入其中：

```bash
echo "your-gemini-api-key-here" > key.txt
```

## 功能说明

### 🎬 动画效果

1. **渐变 (Gradient)** - 方块淡入出现
2. **旋涡 (Vortex)** - 方块螺旋飞入
3. **波纹 (Ripple)** - 从中心向外波纹状建造
4. **天降 (Rain Down)** - 方块从天而降
5. **从地升起 (Ground Up)** - 方块从地底升起
6. **逐层扫描 (Layer Scan)** - 逐层建造
7. **组装 (Assemble)** - 方块从两侧飞入组装
8. **闪现 (Simple)** - 方块快速出现

### ✨ 魔法主题

1. **符文能量** - 绿色粒子效果
2. **烈焰** - 红橙色火焰效果
3. **寒冰** - 蓝白色冰霜效果
4. **暗影** - 紫色暗影效果
5. **无** - 纯建筑动画

### 🎮 使用流程

1. **加载模型** - 上传或自动加载 .glb/.gltf 文件
2. **加载材质包** - 上传 Minecraft 材质包 .zip 文件
3. **选择动画** - 在"🎬 动画制作器"区域选择动画效果和魔法主题
4. **调整粒子密度** - 使用滑块调整粒子效果强度（0-100%）
5. **播放动画** - 点击"▶️ 播放动画"按钮

### 💾 存档功能

- **导出存档** - 保存当前场景、材质和状态为 .zip 文件
- **导入存档** - 从本地文件或 URL 导入存档
- **自动保存** - 场景状态自动保存到浏览器 localStorage

### 🤖 AI 助手

1. 点击"✨ AI 助手"按钮打开聊天面板
2. 输入问题或请求，AI 会帮助您：
   - 理解模型结构
   - 推荐材质组合
   - 解答使用问题

3. **AI 代理模式** - 自动为所有模型部件应用材质（需要参考图）

## 文件结构

```
project/
├── minecraft_animator.py    # 主服务器文件
├── key.txt                   # Gemini API 密钥（可选）
├── input/                    # 输入文件目录
│   ├── model.glb            # 3D 模型文件
│   └── reference.png        # 参考图片
├── cache/                    # 缓存目录
├── saves/                    # 存档目录
└── texture_pack.zip         # 材质包文件（放在根目录）
```

## 技术栈

- **后端**: Flask (Python)
- **前端**: TailwindCSS, Three.js
- **3D引擎**: Three.js r128
- **AI**: Google Gemini API

## 常见问题

### Q: 动画播放时卡顿怎么办？
A: 尝试降低粒子密度滑块的值，或选择较简单的动画效果。

### Q: 模型显示不正确？
A: 确保模型是 .glb 或 .gltf 格式，且文件未损坏。

### Q: AI 功能无法使用？
A: 检查是否正确配置了 Gemini API 密钥，并确保网络连接正常。

### Q: 如何获取 Gemini API 密钥？
A: 访问 https://makersuite.google.com/app/apikey 申请免费的 API 密钥。

## 开发者信息

- 基于原 Mine Builder 2 Server 项目开发
- 添加了参考代码中的动画制作器功能
- 集成了 AI 助手和自动材质应用功能

## 许可证

本项目基于原项目的许可证发布。

---

**享受创作的乐趣！** 🎮✨
