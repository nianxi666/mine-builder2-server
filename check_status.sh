#!/bin/bash
# 检查远程服务器状态

expect << 'EXPECT_SCRIPT'
set timeout 30
spawn ssh -p 30022 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root4563@root@ssh-06aace8d2b864475e7b3e2eb54a8107e.zlrast8j3bxb@direct.virtaicloud.com

expect "password:"
send "liu20062020\r"

expect "#"
send "echo '=== Screen会话状态 ==='\r"
expect "#"
send "screen -ls\r"
expect "#"

send "echo ''\r"
send "echo '=== 数据生成进度 ==='\r"
expect "#"
send "ls -d /gemini/code/dataset_glm4/sample_* 2>/dev/null | wc -l\r"
expect "#"

send "echo ''\r"
send "echo '=== 数据生成日志（最新20行）==='\r"
expect "#"
send "tail -20 /gemini/code/data_gen_glm4.log 2>/dev/null\r"
expect "#"

send "echo ''\r"
send "echo '=== 训练日志（最新20行）==='\r"
expect "#"
send "tail -20 /gemini/code/training_glm4.log 2>/dev/null\r"
expect "#"

send "exit\r"
expect eof
EXPECT_SCRIPT
