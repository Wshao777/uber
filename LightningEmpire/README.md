# ⚡ LightningEmpire ⚡

Welcome to the LightningEmpire project! This is a comprehensive, AI-powered automated dispatch system.

## 📖 Overview

This repository contains the full codebase for the LightningEmpire system, including the mobile frontend, Python backend server, AI core modules, and command-line tools for management and deployment.

## 🏗️ Project Structure

The project is organized into the following modules:

-   `mobile-app/`: The Expo (React Native) frontend application.
-   `server/`: The Python backend server (API, webhooks, etc.).
-   `ai-core/`: Contains the core AI models for dispatch logic and financial analysis.
-   `tasks/`: Scripts for automated tasks, such as the routing engine and Telegram bots.
-   `db/`: Houses the database schema (`schema.sql`) and the database file itself (e.g., `lightning_empire.db`).
-   `cli/`: A command-line interface for managing the project.

## 🚀 Getting Started

Follow these steps to get your local development environment set up.

### 1. Set Up Environment Variables

Create a `.env` file in this directory by copying the example template:

```bash
cp .env.example .env
```

After copying, open the `.env` file and fill in your actual credentials and settings (e.g., API tokens, database configuration).

### 2. Install Dependencies

This project uses Python for the backend and CLI. Install the required packages using pip:

```bash
pip install -r requirements.txt
```

*(For frontend setup, please refer to the `mobile-app/README.md`)*

### 3. Initialize the Database

Run the following command to create and initialize your database based on the schema. For now, only SQLite is supported out-of-the-box.

```bash
python3 -m cli.cli db init --db sqlite
```

This will create a `lightning_empire.db` file in the `db/` directory.

## ⚙️ Usage

The project is managed through a command-line interface (CLI).

-   **View all commands:**
    ```bash
    python3 -m cli.cli --help
    ```
-   **Initialize the database:**
    ```bash
    python3 -m cli.cli db init
    ```

More commands will be added as the project develops.
