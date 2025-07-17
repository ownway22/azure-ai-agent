# Azure AI Agent

本專案示範如何使用 Azure AI Agent 進行各種 AI 任務，包含基礎、中階、進階與與 MCP 整合的應用。

## 專案下載與進入資料夾

1. 下載本專案：
   ```bash
   git clone <本專案的 GitHub 連結>
   ```
2. 進入專案資料夾：
   ```bash
   cd azure-ai-agent
   ```

## 環境建置步驟

### 1. 建立虛擬環境

建議使用 Python 3.9 以上版本。

Windows PowerShell 指令：
```powershell
python -m venv .venv
```

### 2. 啟用虛擬環境

Windows PowerShell 指令：
```powershell
.venv\Scripts\Activate
```

若使用 CMD：
```cmd
.venv\Scripts\activate.bat
```

若使用 macOS/Linux：
```bash
source .venv/bin/activate
```

### 3. 安裝所需套件

```bash
pip install -r requirements.txt
```

### 4. 使用 uv sync 快速建立虛擬環境（可選）

若您已安裝 uv（https://github.com/astral-sh/uv），可用以下方式快速建立與安裝虛擬環境：

```bash
uv venv .venv
uv sync
```

- `uv venv .venv`：建立虛擬環境
- `uv sync`：根據 requirements.txt 自動安裝所有套件

啟用虛擬環境後即可依前述步驟執行範例。

## 執行範例

1. 建議依序閱讀與執行下列檔案：
   - 01_ai-agent-basic.ipynb
   - 02_ai-agent-intermediate.py
   - 03_ai-agent-advanced.py
   - 04_ai-agent-with-mcp-client.py
   - 05_ai-agent-with-mcp-openAI.py

2. 若要執行 Jupyter Notebook（如 01_ai-agent-basic.ipynb）：
   ```bash
   pip install notebook
   jupyter notebook
   ```
   然後在瀏覽器中開啟 01_ai-agent-basic.ipynb。

3. 執行 Python 腳本範例：
   ```bash
   python 02_ai-agent-intermediate.py
   ```

## 其他說明

- 請參考各 .py 檔案內的註解與說明，根據需求調整參數。
- 若需設定環境變數，請參考 `.env-example` 檔案。

---

# Azure AI Agent (English Version)

This project demonstrates how to use Azure AI Agent for various AI tasks, including basic, intermediate, advanced, and MCP-integrated applications.

## Environment Setup Steps

### 1. Create a Virtual Environment

Python 3.9 or above is recommended.

Windows PowerShell command:
```powershell
python -m venv .venv
```

### 2. Activate the Virtual Environment

Windows PowerShell command:
```powershell
.venv\Scripts\Activate
```

For CMD:
```cmd
.venv\Scripts\activate.bat
```

For macOS/Linux:
```bash
source .venv/bin/activate
```

### 3. Install Required Packages

```bash
pip install -r requirements.txt
```

### 4. (Optional) Use uv sync for Quick Setup

If you have uv installed (https://github.com/astral-sh/uv), you can quickly set up and install dependencies with:

```bash
uv venv .venv
uv sync
```

- `uv venv .venv`: Create the virtual environment
- `uv sync`: Install all packages from requirements.txt automatically

After activating the environment, proceed with the following examples.

## Example Usage

1. It is recommended to read and run the following files in order:
   - 01_ai-agent-basic.ipynb
   - 02_ai-agent-intermediate.py
   - 03_ai-agent-advanced.py
   - 04_ai-agent-with-mcp-client.py
   - 05_ai-agent-with-mcp-openAI.py

2. To run the Jupyter Notebook (e.g., 01_ai-agent-basic.ipynb):
   ```bash
   pip install notebook
   jupyter notebook
   ```
   Then open 01_ai-agent-basic.ipynb in your browser.

3. To run Python script examples:
   ```bash
   python 02_ai-agent-intermediate.py
   ```

## Additional Notes

- Please refer to the comments and instructions in each .py file and adjust parameters as needed.
- For environment variable settings, refer to the `.env-example` file.

---

## Reference

1. [Quickstart - Create a new Azure AI Foundry Agent Service project](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/quickstart?pivots=programming-language-python-azure)
2. [azure-sdk-for-python by dargilco](https://github.com/Azure/azure-sdk-for-python/tree/azure-ai-projects_1.0.0b12/sdk/ai/azure-ai-agents/samples/agents_async)
3. [Getting Started - Build your code-first agent with Azure AI Foundry](https://microsoft.github.io/build-your-first-agent-with-azure-ai-agent-service-workshop/getting-started/)
4. [AI-Foundry-Agent-MCP by ccoellomsft](https://github.com/ccoellomsft/AI-Foundry-Agent-MCP)
5. [ai-foundry-agents-samples by eitansela](https://github.com/Azure-Samples/ai-foundry-agents-samples/tree/main)
