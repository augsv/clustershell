import sys
import threading
import paramiko
import getpass

class HostManager:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.client = None
        self.output = []

    def connect(self):
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.host, username=self.username, password=self.password)
            return True
        except Exception as e:
            self.output.append(colorize(f"Failed to connect to {self.host}: {e}", 'red'))
            return False

    def execute_command(self, command):
        if self.client:
            try:
                stdin, stdout, stderr = self.client.exec_command(command)
                self.output.append(f"Output from {self.host}:\n{stdout.read().decode()}")
                error = stderr.read().decode()
                if error:
                    self.output.append(colorize(f"Error from {self.host}:\n{error}", 'red'))
            except Exception as e:
                self.output.append(colorize(f"Failed to execute on {self.host}: {e}", 'red'))

    def close(self):
        if self.client:
            self.client.close()

def worker(host_manager, command):
    if host_manager.connect():
        host_manager.execute_command(command)
        host_manager.close()

def colorize(text, color):
    """ Adds ANSI color codes to the text. """
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'end': '\033[0m',
    }
    return f"{colors[color]}{text}{colors['end']}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python cluster_manager.py <host1> <host2> ... <hostN>")
        sys.exit(1)

    username = input("Enter SSH username: ")
    password = getpass.getpass("Enter SSH password: ")
    hosts = sys.argv[1:]

    managers = [HostManager(host, username, password) for host in hosts]

    while True:
        command = input("Enter command to execute, or type 'exit' to quit: ")
        if command.lower() == 'exit':
            break

        threads = []

        for manager in managers:
            thread = threading.Thread(target=worker, args=(manager, command))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        for manager in managers:
            for output in manager.output:
                print(output)
            # Clear output after displaying
            manager.output = []

if __name__ == "__main__":
    main()
