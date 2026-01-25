# Specification of the Assistant

1. **Supported File Formats**:
   - **txt** (plain text files)
   - **md** (Markdown files)
   - **File Size Limit**: Maximum file size is 5MB. If a file exceeds this size, notify the user and request a smaller file.

2. **Model Switching**:
   - Models that can be used:
     - **Bielik-11B-v2.6-Instruct**: Best suited for structured, document-based tasks.
     - **Bielik-11B-v2.3-Instruct**: Another variant for documentation tasks.
     - **openai/gpt-oss-120b**: A more general-purpose model, suitable for creative tasks and non-structured content.
     - **PLLuM-8x7B-chat**: A conversational model for dialogue-based tasks.
     - **Llama-3.1-8B-Instruct**: A versatile model for varied tasks.
     - **Llama-3.3-70B-Instruct**: A powerful model for complex analytical tasks.
     - **DeepSeek-R1-Distill-Llama-70B**: A high-performance model for deep analysis tasks.

3. **Terminal Interface**:
   - **Command Format**:
     - `aifr - $ask: <user_query> $file: <file_path>`
     - When the query is submitted with a file, the assistant will read the file, update the context, and use the selected model to process the query.
     - When the query is submitted without a file, the assistant will respond to the question directly.

4. **Context Management**:
   - The assistant will keep track of the context (previous tokens) between queries. Context is limited to a defined number of tokens per session.
   - When the terminal session is closed, the context is cleared.

5. **API Token**:
   - The API token for accessing the LLM models is stored in a configuration file. Ensure this token is securely managed.
   - Token management is automatic and requires no user interaction after setup.

6. **File Handling**:
   - Files will be read directly and their content passed to the assistant for analysis.
   - Large files (over 5MB) or unsupported file formats (e.g., PDF) will result in an error message.
