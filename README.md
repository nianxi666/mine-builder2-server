# mine-builder2-server

## 本地表单演示 `/demo-form`
1. 启动 Flask 服务：
   ```bash
   python server.py
   ```
2. 打开浏览器访问 [http://localhost:5000/demo-form](http://localhost:5000/demo-form)，即可看到仅包含姓名与邮箱的演示表单。
3. 表单末尾保留验证码/人工确认占位区域，提交按钮被禁用，仅用于本地或已授权页面的学习演示。

## Selenium + Faker 自动填表脚本
仓库新增 `scripts/demo_autofill.py`，演示如何在受控页面上利用 Selenium 与 Faker 自动填充表单信息。脚本会在验证码/提交之前停止，并在终端打印生成的数据及安全提示。

### 安装依赖
```bash
pip install selenium webdriver-manager Faker
```

### 运行示例
```bash
python scripts/demo_autofill.py --url http://localhost:5000/demo-form --headful
```

- 默认使用无头模式；加上 `--headful` 可观察浏览器操作。
- 使用 `--selector` 可覆盖内置选择器，例如：
  ```bash
  python scripts/demo_autofill.py --selector 'name=input[name="name"]' --selector 'email=#contact-email'
  ```
- `--timeout` 控制等待表单字段的超时时间（秒），`--wait` 控制自动填充结束后保留浏览器的时间。

### 合规声明
- 该脚本及示例页面仅限自有或明确授权的站点与环境中使用。
- 禁止对任何第三方网站（例如 github.com）或带有风控的注册页面运行脚本。
- 脚本不会自动提交、不会尝试绕过验证码或任何安全机制；请在人工核对后自行处理后续步骤。
