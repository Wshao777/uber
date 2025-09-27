# Dynamic Pricing Simulator (C++)

This C++ application simulates the earnings for a delivery driver based on a dynamic pricing model. It is designed to be lightweight and compatible with environments like Cxxdroid on Android.

The simulation calculates potential earnings for two different scenarios:
1.  A weekly target of 20,000 TWD.
2.  A 4-day sprint target of 12,000 TWD.

The output is a detailed JSON log that can be used for analysis.

## Dependencies

This project has one external dependency:
- **nlohmann/json**: A header-only library for JSON manipulation in C++.

### Setting up the Dependency

1.  **Download the Library**: Go to the official repository and download the `json.hpp` file:
    [https://github.com/nlohmann/json/releases](https://github.com/nlohmann/json/releases)
    (Download the `json.hpp` file from the latest release).

2.  **Create Directory Structure**: In the same directory as `dynamic_pricing_simulator.cpp`, create a directory named `nlohmann`.

    ```
    .
    ├── dynamic_pricing_simulator.cpp
    └── nlohmann/
    ```

3.  **Place the Header File**: Place the downloaded `json.hpp` file inside the `nlohmann` directory.

    ```
    .
    ├── dynamic_pricing_simulator.cpp
    └── nlohmann/
        └── json.hpp
    ```
The C++ script is now ready to be compiled.

## Compilation and Execution

### On a Standard Linux Environment (with g++)

1.  **Compile**: Open a terminal in the project directory and run the following command. The `-I.` flag tells the compiler to look for headers in the current directory (which is necessary to find the `nlohmann` folder).

    ```bash
    g++ -std=c++11 -I. -o simulator dynamic_pricing_simulator.cpp
    ```

2.  **Run**: Execute the compiled program.

    ```bash
    ./simulator
    ```

### In Cxxdroid (on Android)

1.  **File Setup**:
    - Create a folder for your project in your device's storage (e.g., `/storage/emulated/0/MyCppProject/`).
    - Place `dynamic_pricing_simulator.cpp` inside this folder.
    - Create a subfolder named `nlohmann` inside `MyCppProject`.
    - Place the `json.hpp` file inside the `nlohmann` folder.

2.  **Compilation in Cxxdroid**:
    - Open `dynamic_pricing_simulator.cpp` in the Cxxdroid editor.
    - Go to **Settings > Compiler Options**.
    - In the "Compiler flags" section, add `-I.` to the flags. This is the most important step to ensure the compiler can find the `nlohmann/json.hpp` header.
    - Go back to the editor.

3.  **Run**:
    - Tap the "Run" button (the play icon). Cxxdroid will compile and run the script.

## Output

The script will print two large JSON objects to the console and save them to two files in a `logs/` directory (which will be created if it doesn't exist):
-   `logs/weekly_pricing_[timestamp].json`
-   `logs/four_day_pricing_[timestamp].json`

Each JSON file contains an array of objects, where each object represents a simulated hour of work. The last object in the array is a summary of the entire simulation, including whether the targets were achieved.