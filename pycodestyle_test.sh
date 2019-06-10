find . -type f -name "*.py" | while read line; do
    echo $line
    pycodestyle $line
done
