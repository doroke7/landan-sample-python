import subprocess

o_result = subprocess.run(
    ["ls", "-la"],      # Windows 可以改成 ["cmd", "/c", "dir"]
    capture_output=True,
    text=True
)

print(o_result.stdout)
print(o_result.stderr)
print(o_result.returncode)