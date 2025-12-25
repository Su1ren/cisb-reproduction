#!/bin/bash

# 定义日志文件路径
NEW_LOG="new.log"
OLD_LOG="old.log"

NEW_PY="effectiveness_evaluation.py"
OLD_PY="effectiveness_evaluation_old.py"

OPTION="./compiler_strategies/wall.txt"

# 清理旧的日志文件（如果存在）
rm -f "$NEW_LOG" "$OLD_LOG"

# 执行第一个 Python 脚本并将输出保存到 new.log
echo "执行 script1.py，输出保存到 $NEW_LOG..."
python3 "$NEW_PY" "-opt" "$OPTION" > "$NEW_LOG" 2>&1

# 检查第一个脚本是否执行成功
if [ $? -ne 0 ]; then
    echo "错误: script1.py 执行失败"
    exit 1
fi

# 执行第二个 Python 脚本并将输出保存到 old.log
echo "执行 script2.py，输出保存到 $OLD_LOG..."
python3 "$OLD_PY" "-opt" "$OPTION" > "$OLD_LOG" 2>&1

# 检查第二个脚本是否执行成功
if [ $? -ne 0 ]; then
    echo "错误: script2.py 执行失败"
    exit 1
fi

# 比较两个日志文件
echo "比较 $NEW_LOG 和 $OLD_LOG 的内容..."
echo "========================================"

# 使用 diff 比较文件
diff "$NEW_LOG" "$OLD_LOG"

# 检查 diff 的退出状态
DIFF_RESULT=$?
if [ $DIFF_RESULT -eq 0 ]; then
    echo "========================================"
    echo "两个日志文件内容完全相同"
elif [ $DIFF_RESULT -eq 1 ]; then
    echo "========================================"
    echo "两个日志文件存在差异"
else
    echo "========================================"
    echo "diff 命令执行出错"
fi

# 可选：显示日志文件位置
echo "日志文件已保存到："
echo "  - $NEW_LOG"
echo "  - $OLD_LOG"
