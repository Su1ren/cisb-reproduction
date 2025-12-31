#!/bin/bash

# log path
NEW_LOG="new.log"
OLD_LOG="old.log"

NEW_PY="effectiveness_evaluation.py"
OLD_PY="effectiveness_evaluation_old.py"

OPTION="./compiler_strategies/wall.txt"

# clean old log
rm -f "$NEW_LOG" "$OLD_LOG"

# execute first script
echo "Executing script1.py, output into $NEW_LOG..."
python3 "$NEW_PY" "-opt" "$OPTION" > "$NEW_LOG" 2>&1

# check if exec fails
if [ $? -ne 0 ]; then
    echo "Error: script1.py failed"
    exit 1
fi

# execute second script
echo "Executing script2.py, output into $OLD_LOG..."
python3 "$OLD_PY" "-opt" "$OPTION" > "$OLD_LOG" 2>&1

# check if exec fails
if [ $? -ne 0 ]; then
    echo "Error: script2.py failed"
    exit 1
fi

# Compare the content
echo "Compare $NEW_LOG and $OLD_LOG content..."
echo "========================================"
diff "$NEW_LOG" "$OLD_LOG"

# check diff status
DIFF_RESULT=$?
if [ $DIFF_RESULT -eq 0 ]; then
    echo "========================================"
    echo "Entirely the same"
elif [ $DIFF_RESULT -eq 1 ]; then
    echo "========================================"
    echo "Difference exists"
else
    echo "========================================"
    echo "diff failed"
fi

# print where log stored
echo "Logs stored in: "
echo "  - $NEW_LOG"
echo "  - $OLD_LOG"
