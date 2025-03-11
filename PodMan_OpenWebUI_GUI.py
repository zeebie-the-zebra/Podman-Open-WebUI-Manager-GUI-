import os
import subprocess
import threading
import queue
from datetime import datetime
import tkinter as tk
from tkinter import ttk

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Leona's OpenWebUI Manager")

        # Setup log file path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.LOG_FILE = os.path.join(script_dir, "Update_OpenWebUI_Logs.log")

        # Environment variables state
        self.env_vars = {
            "OLLAMA_FLASH_ATTENTION": tk.StringVar(value="1"),
            "OLLAMA_KV_CACHE_TYPE": tk.StringVar(value="Q4_0"),
            "OLLAMA_USE_CUDA": tk.StringVar(value="1"),
            "USE_CUDA_DOCKER": tk.StringVar(value="true"),
            #"CUDA_VISIBLE_DEVICES": tk.StringVar(value="all"), #disabled because conflicts with "--gpus", "all", causing ollama to be cpu bound
        }

        # Create UI components
        self.create_widgets()

        # Initialize the log queue and polling
        self.log_queue = queue.Queue()
        self.container_log_queue = queue.Queue()  # Separate queue for container logs
        self.poll_log_queue()

    def create_widgets(self):
        button_frame = ttk.Frame(self.root)
        button_frame.pack(padx=10, pady=10)

        buttons_info = [
            ("Start", self.start_container),
            ("Stop", self.stop_container),
            ("Update", self.update_container),
            ("Logs", self.show_logs),
            ("Clear Logs", self.clear_logs),
            ("Options", self.show_options),
            ("Toggle Port Forwarding", self.toggle_port_forwarding),
        ]

        for text, command in buttons_info:
            btn = ttk.Button(button_frame, text=text,
                             command=lambda cmd=command: threading.Thread(target=cmd, daemon=True).start())
            btn.pack(side=tk.LEFT, padx=5)

        # Status log display (original log box)
        self.status_text = tk.Text(self.root, height=10, width=80)
        self.status_scrollbar = ttk.Scrollbar(
            self.root,
            orient=tk.VERTICAL,
            command=self.status_text.yview
        )
        self.status_text.config(yscrollcommand=self.status_scrollbar.set)

        self.status_text.pack(padx=10, pady=5, side=tk.TOP, fill=tk.X)
        self.status_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Container log display (secondary log box)
        self.container_log_text = tk.Text(self.root, height=10, width=80)
        self.container_log_scrollbar = ttk.Scrollbar(
            self.root,
            orient=tk.VERTICAL,
            command=self.container_log_text.yview
        )
        self.container_log_text.config(yscrollcommand=self.container_log_scrollbar.set)

        self.container_log_text.pack(padx=10, pady=5, side=tk.TOP, fill=tk.X)
        self.container_log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def log_message(self, message):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_msg = f"[{current_time}] {message}"

        with open(self.LOG_FILE, 'a') as log_file:
            log_file.write(full_msg + '\n')

        self.log_queue.put(full_msg)

    def poll_log_queue(self):
        try:
            msg = self.log_queue.get_nowait()
            self.append_to_logs(msg)
        except queue.Empty:
            pass

        try:
            container_msg = self.container_log_queue.get_nowait()
            self.append_to_container_logs(container_msg)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.poll_log_queue)  # Poll again after 100ms

    def append_to_logs(self, message):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)

    def append_to_container_logs(self, message):
        self.container_log_text.config(state=tk.NORMAL)
        self.container_log_text.insert(tk.END, f"{message}\n")
        self.container_log_text.see(tk.END)
        self.container_log_text.config(state=tk.DISABLED)

    def run_command(self, cmd_list):
        try:
            self.log_message(f"Running command: {' '.join(cmd_list)}")  # Debug log for the command being run
            process = subprocess.Popen(
                cmd_list,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            while True:
                output_line = process.stdout.readline()
                if not output_line and process.poll() is not None:
                    break
                elif output_line.strip():
                    self.log_message(f"Command Output: {output_line.strip()}")

            return process.wait()
        except Exception as e:
            self.log_message(f"Error executing command: {str(e)}")
            return -1

    def fetch_container_logs(self):
        self.log_message("Starting to fetch container logs...")  # Debug log
        cmd = ["pkexec", "podman", "logs", "-f", "open-webui"]

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            while True:
                output_line = process.stdout.readline()
                if not output_line and process.poll() is not None:
                    break
                elif output_line.strip():
                    self.container_log_queue.put(output_line.strip())  # Use the separate queue for container logs
        except Exception as e:
            self.log_message(f"Error fetching container logs: {str(e)}")

    def start_container(self):
        threading.Thread(target=self._start_container, daemon=True).start()

    def _start_container(self):
        env_vars = self.get_env_vars()
        cmd = [
            "pkexec", "podman", "run", "-d",
            "-p", "3000:8080",
            "--runtime", "/usr/bin/nvidia-container-runtime",
            "--gpus", "all",
            "-v", "ollama:/root/.ollama",
            "-v", "open-webui:/app/backend/data",
            *env_vars,  # Add environment variables here
            "--name", "open-webui",
            "--restart", "always",
            "ghcr.io/open-webui/open-webui:ollama"
        ]

        self.log_message("Starting container...")
        rc = self.run_command(cmd)
        if rc == 0:
            threading.Thread(target=self.fetch_container_logs, daemon=True).start()  # Start fetching logs
        else:
            self.log_message(f"Failed to start (exit code {rc})")

    def stop_container(self):
        threading.Thread(target=self._stop_container, daemon=True).start()

    def _stop_container(self):
        cmd = ["pkexec", "podman", "rm", "-f", "open-webui"]

        self.log_message("Stopping container...")
        rc = self.run_command(cmd)
        if rc != 0:
            self.log_message(f"Stop failed (exit code {rc})")

    def update_container(self):
        threading.Thread(target=self._update_container, daemon=True).start()

    def _update_container(self):
        try:
            self.log_message("Starting update process...")

            # Only pull the latest image, do not start the container
            pull_rc = self.run_command([
                "pkexec",
                "podman",
                "pull",
                "ghcr.io/open-webui/open-webui:ollama"
            ])

            if pull_rc != 0:
                self.log_message("Pull failed - update aborted")
                return
            else:
                self.log_message("Update completed successfully!")
        except Exception as e:
            self.log_message(f"Error during update: {str(e)}")

    def show_logs(self):
        try:
            with open(self.LOG_FILE, 'r') as f:
                logs = f.read()

            log_window = tk.Toplevel(self.root)
            log_window.title("Full Logs")

            text_area = tk.Text(log_window, wrap='word', height=20, width=80)
            scrollbar = ttk.Scrollbar(
                log_window,
                orient=tk.VERTICAL,
                command=text_area.yview
            )

            text_area.config(yscrollcommand=scrollbar.set)
            text_area.insert(tk.END, logs)
            text_area.config(state='disabled')

            text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        except Exception as e:
            self.log_message(f"Failed to display logs: {str(e)}")

    def get_env_vars(self):
        env_vars = []
        for var, var_obj in self.env_vars.items():
            if isinstance(var_obj, tk.BooleanVar):
                env_vars.append(f"-e {var}={'1' if var_obj.get() else '0'}")
            elif isinstance(var_obj, tk.StringVar):
                env_vars.append(f"-e {var}={var_obj.get()}")
        return env_vars

    def show_options(self):
        options_window = tk.Toplevel(self.root)
        options_window.title("Environment Options")


        for var, var_obj in self.env_vars.items():
            if isinstance(var_obj, tk.BooleanVar):
                chk = ttk.Checkbutton(
                    options_window, text=var, variable=var_obj
                )
                chk.pack(anchor=tk.W, padx=250, pady=50)
            elif isinstance(var_obj, tk.StringVar):
                # Drop-down menu for string-based settings
                frame = ttk.Frame(options_window)
                frame.pack(anchor=tk.W, padx=250, pady=50)

                label = ttk.Label(frame, text=var)
                label.pack(side=tk.LEFT)

                # Different options for each string-based variable
                if var == "OLLAMA_KV_CACHE_TYPE":
                    options = ["Q4_0", "Q8_0", "f16"]
                #elif var == "CUDA_VISIBLE_DEVICES": #disabled because conflicts with "--gpus", "all", causing ollama to be cpu bound
                    #options = ["0,1", "0", "1", "2", "all", "none"]
                else:
                    options = ["default"]

                dropdown = ttk.Combobox(frame, textvariable=var_obj, values=options, state="readonly")
                dropdown.pack(side=tk.RIGHT)

    def toggle_port_forwarding(self):
        # Check if socat is running and toggle accordingly
        cmd = "pgrep -fl 'socat TCP-LISTEN:3000,fork TCP:127.0.0.1:3000'"
        result = subprocess.run(cmd, shell=True, text=True, capture_output=True)

        if result.stdout.strip():  # socat is already running
            self.log_message("Stopping port forwarding...")
            subprocess.run("pkill -f 'socat TCP-LISTEN:3000,fork TCP:127.0.0.1:3000'", shell=True)
        else:  # socat is not running, so start it
            self.log_message("Starting port forwarding...")
            subprocess.Popen("socat TCP-LISTEN:3000,fork TCP:127.0.0.1:3000 &", shell=True)

    def clear_logs(self):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state=tk.DISABLED)

        self.container_log_text.config(state=tk.NORMAL)
        self.container_log_text.delete(1.0, tk.END)
        self.container_log_text.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
