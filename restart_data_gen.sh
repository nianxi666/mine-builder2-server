#!/usr/bin/expect -f
# 重启数据生成

set timeout 60
spawn ssh -p 30022 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root4563@root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com

expect "password:"
send "liu20062020\r"

expect "#"
send "echo '=== 停止旧的数据生成 ==='\r"
expect "#"

send "screen -X -S data_gen quit\r"
expect "#"

send "echo '等待3秒...'\r"
send "sleep 3\r"
expect "#"

send "echo '=== 上传修复版生成器 ==='\r"
expect "#"

send "cd /gemini/code/upload_package\r"
expect "#"

# 通过cat上传文件内容
send "cat > generate_dataset_glm4_fixed.py << 'PYTHON_EOF'\r"
sleep 1
