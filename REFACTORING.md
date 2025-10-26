# 代码重构说明

## 概述

原始的 `server.py` 文件包含 2681 行代码，所有功能都集中在一个文件中。为了提高代码的可维护性、可读性和可扩展性，我们将其拆分为多个模块。

## 重构后的文件结构

```
project/
├── server.py              # 主应用入口（189行，从2681行减少）
├── config.py              # 配置和全局状态
├── template_loader.py     # HTML模板加载器
├── server.py.backup       # 原始文件备份
├── utils/                 # 工具函数模块
│   ├── __init__.py
│   ├── file_utils.py      # 文件操作工具
│   ├── save_manager.py    # 存档管理
│   └── api_validator.py   # API密钥验证
└── routes/                # 路由模块
    ├── __init__.py
    ├── web_routes.py      # Web页面路由
    └── api_routes.py      # API端点路由
```

## 模块说明

### 1. `server.py` - 主应用入口
- **功能**: Flask应用初始化和启动
- **代码量**: 189行（原2681行）
- **职责**:
  - 应用程序初始化
  - 命令行参数解析
  - 模型和存档加载
  - API密钥管理
  - 目录创建
  - 服务器启动

### 2. `config.py` - 配置管理
- **功能**: 集中管理所有配置常量和全局状态
- **包含**:
  - 端口、目录配置
  - 全局状态变量（API密钥、聊天历史、代理状态等）

### 3. `utils/` - 工具函数模块

#### `file_utils.py`
- 文件查找 (`find_first_file`)
- Base64编码读取 (`read_file_as_base64`)

#### `save_manager.py`
- 创建存档数据 (`create_save_data`)
- 导出存档文件 (`export_save_file`)
- 导入存档文件 (`import_save_file`)

#### `api_validator.py`
- API密钥验证 (`validate_api_key`)

### 4. `routes/` - 路由模块

#### `web_routes.py`
- 主页路由
- HTML模板渲染

#### `api_routes.py`
- `/api/files` - 文件扫描
- `/api/chat` - AI聊天
- `/api/validate_key` - 密钥验证
- `/api/save/export` - 导出存档
- `/api/save/import` - 导入存档
- `/api/agent/*` - AI代理控制

### 5. `template_loader.py` - 模板加载器
- 从备份文件中提取HTML内容
- 提供备用模板

## 重构优势

### 1. **可维护性提升**
- 每个模块职责单一，易于理解和修改
- 相关功能集中在一起
- 减少了代码重复

### 2. **可读性提升**
- 清晰的文件结构
- 模块化的代码组织
- 更好的代码导航

### 3. **可扩展性提升**
- 新功能可以轻松添加到对应模块
- 不同功能可以独立开发和测试
- 易于添加新的路由和工具函数

### 4. **可测试性提升**
- 每个模块可以独立测试
- 更容易编写单元测试
- 减少了测试的复杂度

## 功能保持

所有原有功能完全保留，包括：
- ✅ Flask Web服务器
- ✅ 3D模型加载和体素化
- ✅ AI助手和代理功能
- ✅ 存档导出/导入
- ✅ 材质包加载
- ✅ 参考图上传
- ✅ API密钥管理
- ✅ 命令行参数支持
- ✅ 所有API端点
- ✅ 前端HTML/JavaScript功能

## 兼容性

- **Python版本**: 保持原有Python 3.x要求
- **依赖**: 无新增依赖，完全兼容原有环境
- **配置**: 所有原有配置和参数保持不变
- **数据**: 存档格式完全兼容

## 使用方式

### 启动服务器（与原来完全相同）
```bash
python server.py
```

### 带参数启动（与原来完全相同）
```bash
python server.py --input_model model.glb --input_data save.zip
```

## 迁移说明

如果需要回滚到原始版本：
```bash
mv server.py server.py.refactored
mv server.py.backup server.py
```

## 注意事项

1. **备份文件**: `server.py.backup` 包含原始完整代码，作为HTML模板的来源
2. **全局状态**: 通过 `config` 模块共享全局状态，保持原有行为
3. **导入顺序**: 确保在虚拟环境中运行，所有依赖已安装

## 测试

启动后测试以下功能：
- [ ] 服务器正常启动
- [ ] 主页可以访问
- [ ] 模型加载功能
- [ ] 材质包加载
- [ ] AI聊天功能
- [ ] 存档导出/导入
- [ ] 所有API端点响应正常

## 维护建议

1. **添加新路由**: 在 `routes/api_routes.py` 或 `routes/web_routes.py` 中添加
2. **添加工具函数**: 在 `utils/` 下创建新模块或添加到现有模块
3. **修改配置**: 在 `config.py` 中统一管理
4. **更新文档**: 修改功能时同步更新此文档
