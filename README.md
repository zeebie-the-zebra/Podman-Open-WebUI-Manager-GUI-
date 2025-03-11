#Program Description: Leona's OpenWebUI Manager 

(Description written by LLM - Its really not that flash)

Leona's OpenWebUI Manager is a graphical user interface (GUI) application designed to manage and monitor a containerized instance of the OpenWebUI platform. The program simplifies interactions with Docker containers, specifically tailored for running an OpenWebUI environment. Here’s a detailed breakdown of its features and functionalities: 

1. Key Features 
 

    Container Management: 
         Start/Stop/OpenWebUI Container: Users can easily start or stop the container using dedicated buttons.
         Update Container: The program allows users to pull the latest version of the OpenWebUI image, ensuring they always have access to the most up-to-date features and security updates.
        
     

    Log Monitoring: 
         Real-time Logs: The application provides two log windows:
             Status Log: Displays general system messages and command outputs.
             Container Log: Shows real-time logs from the OpenWebUI container, helping users troubleshoot issues or monitor ongoing processes.
             
         
     

    Environment Configuration: 
         Users can adjust environment variables that control how Ollama (the underlying AI framework) operates. These include settings for:
             Flash attention optimizations.
             KV cache type.
             CUDA usage (enabling GPU acceleration).
             
         
     

    Port Forwarding: 
         The program supports dynamic port forwarding, allowing users to reroute traffic from a specified host port (e.g., 3000) to the container's internal port (e.g., 8080). This is particularly useful for accessing services running inside containers on non-standard ports.
         
     

    Log Management: 
         Clear Logs: Users can easily clear both the status log and container log windows.
         View Full Log File: The program displays the complete log history in a separate window, making it easier to review past activity.
         
     

2. Technical Details 

     

    Programming Language: Python 
         Built using Tkinter for the GUI components.
         Leverages threading for handling long-running operations (e.g., container management) without blocking the UI.
         
     

    Container Runtime: Podman 
         The program uses Podman to manage containers, which is a CNCF project focused on container orchestration and runtime.
         Supports GPU acceleration via nvidia-container-runtime, allowing users to leverage CUDA-enabled GPUs for improved performance.
         
     

    Environment Variables: 
         Configurable variables include:
             OLLAMA_FLASH_ATTENTION
             OLLAMA_KV_CACHE_TYPE
             OLLAMA_USE__cuda
             USE_ cuda _DOCKER
             
         
     

3. User Interface 

The application features a clean and intuitive interface: 
   
    Buttons: 
         Actions like Start, Stop, Update, Logs, etc., are accessible via buttons arranged in a top frame.
    
    Text Boxes: 
         Two scrollable text boxes display logs:
             The status log box shows general system messages.
             The container log box provides real-time output from the OpenWebUI container.  
             
    Options Window: 
         Users can access an options window to modify environment variables. String-based variables (e.g., cache types) are configured via dropdown menus, while boolean variables use checkboxes.
         
     

4. Log Management 

The program maintains a log file (Update_OpenWebUI_Logs.log) that records all user actions and system messages. This file is stored in the same directory as the script and serves as an audit trail for debugging or review purposes. 
5. System Requirements 

     Operating System: Linux (tested with Podman)
     Dependencies:
         Python 3.x
         Tkinter
         Subprocess Module
         Threading Module
         CUDA Drivers (for GPU support)
         
     

6. Use Cases 

This application is ideal for: 

     Users running OpenWebUI in a production or development environment.
     Developers who need fine-grained control over Ollama's settings without accessing the command line directly.
     Teams that want a centralized tool to manage and monitor their containerized AI applications.
     

7. Benefits of Using Leona's OpenWebUI Manager 

     Ease of Use: Simplifies container management tasks through a graphical interface.
     Real-time Monitoring: Provides immediate feedback through logs, enabling faster troubleshooting.
     Customizable Settings: Allows users to fine-tune Ollama's performance using environment variables.
     Portability: The application is self-contained and runs on any system with Python and Podman installed.
     

![Preview](https://github.com/zeebie-the-zebra/Podman-Open-WebUI-Manager-GUI-/blob/main/Screenshot_20250312_084105.png)
