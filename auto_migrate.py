import subprocess

print("Running makemigrations with auto-answers...")
proc = subprocess.run(
    ['.venv/Scripts/python.exe', 'manage.py', 'makemigrations'],
    input="1\n" * 50,
    text=True,
    capture_output=True
)

print("STDOUT:")
print(proc.stdout)
print("STDERR:")
print(proc.stderr)
