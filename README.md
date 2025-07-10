

# Multi-Project Progress & ETC Estimator

A simple, intuitive desktop application built with PyQt6 to help you track the progress of multiple projects, estimate their time to completion (ETC), and manage project details efficiently.

![android-chrome-512x512](https://github.com/user-attachments/assets/d3bacefc-90e8-48ae-a45d-40f057b5c273)


## ✨ Features

* **Multi-Project Management:** Create, select, and delete multiple projects.

* **Progress Tracking:** Define total work units and track current completed units for each project.

* **Real-time ETC Estimation:** Get an estimated time to completion based on your progress and elapsed time.

* **Timer Functionality:** Start and stop a timer for active projects to automatically update elapsed time.

* **Persistent Data:** All your project data is automatically saved and loaded, so you never lose your progress.

* **Customizable Details:** Add names and descriptions to your projects.

* **Modern Dark Theme:** A sleek, dark user interface for comfortable use.

* **Resizable Window:** Adjust the application window size to suit your workflow.

## ⬇️ Download & Installation (Windows Executable)

The easiest way to use the application is to download the pre-compiled executable.

1.  **Download the latest version:**

    * [Latest release](https://github.com/Agampodige/ProgressTracker/releases/latest)
    * **Direct Download:** [ `setup.exe` ](https://github.com/Agampodige/ProgressTracker/releases/download/v1.0.0/Setup.exe)

## 🚀 Usage

1.  **Launch the Application:** Run `progess.exe` (or launch via the Start Menu shortcut if you used the installer).

2.  **Add a Project:** Click the "Add Project" button on the left panel. A new project will appear in the list and its details will load on the right.

3.  **Select a Project:** Click on any project name in the left list to view and edit its details.

4.  **Edit Project Details:**

    * **Project Name:** Type in the "Project Name" field.

    * **Project Description:** Use the "Project Description" text area for more detailed notes.

    * **Total Work Units:** Enter the total amount of work for the project (e.g., 100, 500.5).

    * **Current Work Units:** Enter the amount of work completed so far.

        * *Note:* If you enter a value greater than "Total Work Units", it will be capped at the total. If you reach the total, the timer will automatically stop.

5.  **Start/Stop Timer:**

    * Click "Start Timer" to begin tracking elapsed time for the selected project. The button will change to "Stop Timer".

    * Click "Stop Timer" to pause tracking. The elapsed time will be saved.

6.  **Reset Project:** Click "Reset All" to clear the current and total work units, description, and timer for the selected project.

7.  **Delete Project:** Select a project and click "Delete Project" to remove it permanently. You will be asked for confirmation.

8.  **Resize Window:** Drag the edges or corners of the window to resize it. Use the standard minimize/maximize/close buttons in the title bar.

## 💾 Data Persistence

Your project data is automatically saved to a file named `projects.json` in your application's data directory.

* **Windows:** `C:\Users\<YourUsername>\AppData\Local\pyqt_progress_app\projects.json`

* **macOS:** `~/Library/Application Support/pyqt_progress_app/projects.json`

* **Linux:** `~/.local/share/pyqt_progress_app/projects.json` (or similar, depending on XDG Base Directory Specification)

## 📜 License

This project is licensed under the **GNU General Public License v3.0 (GPLv3)**. See the [LICENSE](LICENSE) file for details.
*(Note: PyQt6's default license is GPLv3. If you intend to use this code in a closed-source application, you would need to acquire a commercial license for PyQt from Riverbank Computing.)*
