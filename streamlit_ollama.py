import streamlit as st
from openai import OpenAI
from datetime import datetime
import json
from pathlib import Path

from mysql_tools import MySQLTools
from file_tools import FileTools

# =============================================================================
# Constants Configuration
# =============================================================================
MODEL_NAME = "deepseek-r1:1.5b"

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'python_test'
}

CONVERSATIONS_FOLDER = Path(r"F:\project\conversations")


# =============================================================================
# Helper Functions
# =============================================================================

def build_system_prompt(name: str, personality: str) -> str:
    """Build system prompt for AI chat partner

    Args:
        name: Chat partner name
        personality: Personality description

    Returns:
        Formatted system prompt string
    """
    return f"""
你叫 {name}，现在是用户的真实伴侣，请完全代入伴侣角色。

规则：
1. 每次只回复 1 条消息
2. 禁止任何场景或状态描述性文字
3. 匹配用户的语言
4. 回复简短，像微信聊天一样
5. 有需要的话可以用❤️✨等 emoji 表达
6. 用符合伴侣性格的方式对话
7. 回复的内容，要充分体现出伴侣的性格特征

伴侣性格：
- {personality}

你必须严格遵守上述规则来回复用户。
"""


def sanitize_filename(name: str) -> str:
    """Remove invalid characters from filename

    Args:
        name: Original filename

    Returns:
        Sanitized filename
    """
    return "".join([c for c in name if c.isalnum() or c in (' ', '-', '_')]).rstrip()


def generate_session_filename(session_name: str) -> str:
    """Generate timestamped session filename

    Args:
        session_name: Name of the session

    Returns:
        Filename with timestamp
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_name = sanitize_filename(session_name)
    return f"{timestamp}_{safe_name}.txt"


def create_session_json_data(session_name: str, messages: list, include_created: bool = True) -> dict:
    """Create JSON structure for session data

    Args:
        session_name: Name of the session
        messages: List of chat messages
        include_created: Whether to include created timestamp

    Returns:
        Dictionary with session data
    """
    data = {
        "session": session_name,
        "message_count": len(messages),
        "messages": messages
    }

    if include_created:
        data["created"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        data["updated"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return data


def save_json_to_file(file_tools: FileTools, filename: str, data: dict) -> tuple[bool, str]:
    """Save JSON data to file

    Args:
        file_tools: FileTools instance
        filename: Name of the file
        data: JSON data to save

    Returns:
        Tuple of (success status, filepath or error message)
    """
    try:
        content = json.dumps(data, ensure_ascii=False, indent=2, default=str)

        if file_tools.create_file(filename, content):
            filepath = str(file_tools.get_base_path() / filename)
            return True, filepath
        return False, "Failed to create file"

    except Exception as e:
        return False, f"Error saving to file: {e}"


def update_json_file(file_tools: FileTools, filename: str, data: dict) -> bool:
    """Update existing JSON file

    Args:
        file_tools: FileTools instance
        filename: Name of the file to update
        data: Updated JSON data

    Returns:
        True if successful
    """
    try:
        content = json.dumps(data, ensure_ascii=False, indent=2, default=str)
        return file_tools.update_file(filename, content)
    except Exception as e:
        print(f"Error updating file: {e}")
        st.error(f"Error updating conversation file: {e}")
        return False


def extract_name_and_personality(messages: list) -> tuple[str, str]:
    """Extract chat partner name and personality from system message

    Args:
        messages: List of chat messages

    Returns:
        Tuple of (name, personality)
    """
    for msg in messages:
        if isinstance(msg, dict) and msg.get('role') == 'system':
            system_text = msg.get('content', '')
            if system_text.startswith("You are"):
                parts = system_text.split('.', 1)
                name = parts[0].replace("You are", "").strip() if parts else ""
                personality = parts[1].strip() if len(parts) > 1 else ""
                return name, personality
    return "", ""


def load_messages_from_file(file_tools: FileTools, filename: str) -> tuple[list, str, str]:
    """Load messages from TXT/JSON file

    Args:
        file_tools: FileTools instance
        filename: Name of the file

    Returns:
        Tuple of (messages list, name, personality)
    """
    try:
        if not file_tools.get_base_path().exists():
            print(f"Base path does not exist: {file_tools.get_base_path()}")
            return [], "", ""

        content = file_tools.read_file(filename)
        if not content:
            print(f"Failed to read file content: {filename}")
            return [], "", ""

        # Try JSON format first
        try:
            json_data = json.loads(content)
            if isinstance(json_data, dict) and 'messages' in json_data:
                messages = json_data['messages']
                if isinstance(messages, list):
                    name, personality = extract_name_and_personality(messages)
                    print(f"Successfully loaded {len(messages)} messages from {filename} (JSON format)")
                    print(f"Extracted name: '{name}', personality: '{personality}'")
                    return messages, name, personality
                print(f"Messages field is not a list in {filename}")
                return [], "", ""
            print(f"Invalid JSON structure in {filename}")
            return [], "", ""
        except json.JSONDecodeError:
            pass

        # Fallback to text format parsing
        return parse_text_format_messages(content, filename)

    except Exception as e:
        print(f"Error loading from file: {e}")
        import traceback
        traceback.print_exc()
        st.error(f"Error loading conversation from file: {e}")
        return [], "", ""


def parse_text_format_messages(content: str, filename: str) -> tuple[list, str, str]:
    """Parse old text format messages (backward compatibility)

    Args:
        content: File content as string
        filename: Name of the file

    Returns:
        Tuple of (messages list, name, personality)
    """
    messages = []
    lines = content.split('\n')
    current_role = None
    current_content = []
    extracted_name = ""
    extracted_personality = ""

    for line in lines:
        line = line.strip()
        if not line or line.startswith('='):
            continue

        if line.startswith('[USER]:'):
            if current_role and current_content:
                messages.append({'role': current_role, 'content': '\n'.join(current_content)})
            current_role = 'user'
            current_content = [line.replace('[USER]:', '').strip()]
        elif line.startswith('[ASSISTANT]:'):
            if current_role and current_content:
                messages.append({'role': current_role, 'content': '\n'.join(current_content)})
            current_role = 'assistant'
            current_content = [line.replace('[ASSISTANT]:', '').strip()]
        elif line.startswith('[SYSTEM]:'):
            if current_role and current_content:
                messages.append({'role': current_role, 'content': '\n'.join(current_content)})
            current_role = 'system'
            system_text = line.replace('[SYSTEM]:', '').strip()

            if system_text.startswith("You are"):
                parts = system_text.split('.', 1)
                if parts:
                    extracted_name = parts[0].replace("You are", "").strip()
                if len(parts) > 1:
                    extracted_personality = parts[1].strip()
            current_content = []
        else:
            if current_content:
                current_content.append(line)

    if current_role and current_content:
        messages.append({'role': current_role, 'content': '\n'.join(current_content)})

    print(f"Successfully loaded {len(messages)} messages from {filename} (Text format)")
    print(f"Extracted name: '{extracted_name}', personality: '{extracted_personality}'")
    return messages, extracted_name, extracted_personality


def get_chat_response(client: OpenAI, model: str, messages: list,
                      temperature: float = 0.7, max_tokens: int = 1024) -> tuple[bool, str]:
    """Get AI chat response from Ollama

    Args:
        client: OpenAI client instance
        model: Model name
        messages: List of chat messages
        temperature: Temperature setting
        max_tokens: Maximum tokens

    Returns:
        Tuple of (success status, response or error message)
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return True, response.choices[0].message.content
    except Exception as e:
        error_msg = f"Error communicating with Ollama ({model}): {str(e)}"
        return False, error_msg


# =============================================================================
# Session Management Functions
# =============================================================================

def save_session_to_txt(file_tools: FileTools, session_name: str, messages: list) -> str | None:
    """Save chat session to TXT file in JSON format

    Args:
        file_tools: FileTools instance
        session_name: Name of the session
        messages: List of chat messages

    Returns:
        File path if successful, None otherwise
    """
    try:
        filename = generate_session_filename(session_name)
        session_data = create_session_json_data(session_name, messages)

        success, result = save_json_to_file(file_tools, filename, session_data)
        if success:
            return result
        print(f"Error saving to TXT: {result}")
        st.error(f"Error saving conversation to file: {result}")
        return None

    except Exception as e:
        print(f"Error saving to TXT: {e}")
        st.error(f"Error saving conversation to file: {e}")
        return None


def update_txt_file(file_tools: FileTools, filepath: str, messages: list) -> bool:
    """Update existing TXT file with new messages

    Args:
        file_tools: FileTools instance
        filepath: Path to the TXT file
        messages: Updated list of chat messages

    Returns:
        True if successful
    """
    try:
        filename = Path(filepath).name
        session_name = filename.replace('.txt', '')
        session_data = create_session_json_data(session_name, messages, include_created=False)
        return update_json_file(file_tools, filename, session_data)
    except Exception as e:
        print(f"Error updating TXT file: {e}")
        st.error(f"Error updating conversation file: {e}")
        return False


def save_session_to_mysql(sql: MySQLTools, file_tools: FileTools,
                          session_name: str, messages: list,
                          session_id: int = None) -> bool:
    """Save current session to MySQL database

    Args:
        sql: MySQLTools instance
        file_tools: FileTools instance
        session_name: Name of the session
        messages: List of chat messages
        session_id: Optional session ID for updates

    Returns:
        True if successful
    """
    try:
        if session_id:
            sessions = sql.select_all("chat_sessions", {"id": session_id})
            if not sessions:
                return False

            file_path = sessions[0].get('file_path', '')
            session_data = {
                'create_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'session_name': session_name
            }

            result = sql.update("chat_sessions", session_data, {"id": session_id})
            if result and file_path:
                return update_txt_file(file_tools, file_path, messages)
            return result
        else:
            file_path = save_session_to_txt(file_tools, session_name, messages)
            if not file_path:
                return False

            session_data = {
                'file_path': file_path,
                'create_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'session_name': session_name
            }

            result = sql.insert("chat_sessions", session_data)
            return result is not None

    except Exception as e:
        print(f"Error saving session: {e}")
        st.error(f"Error saving session: {e}")
        return False


def load_sessions_from_mysql(sql: MySQLTools) -> list:
    """Load all sessions from MySQL database

    Args:
        sql: MySQLTools instance

    Returns:
        List of sessions
    """
    try:
        return sql.select_all("chat_sessions", order_by="create_time DESC")
    except Exception as e:
        st.error(f"Error loading sessions: {e}")
        return []


def delete_session_from_mysql(sql: MySQLTools, file_tools: FileTools, session_id: int) -> bool:
    """Delete a session from MySQL database and the TXT file

    Args:
        sql: MySQLTools instance
        file_tools: FileTools instance
        session_id: Session ID to delete

    Returns:
        True if successful
    """
    try:
        sessions = sql.select_all("chat_sessions", {"id": session_id})
        if not sessions:
            return False

        file_path = sessions[0].get('file_path', '')
        result = sql.delete("chat_sessions", {"id": session_id})

        if result and file_path:
            filename = Path(file_path).name
            file_tools.delete_file(filename)
            print(f"Deleted TXT file: {filename}")

        return result

    except Exception as e:
        st.error(f"Error deleting session: {e}")
        return False


# =============================================================================
# Streamlit UI Components
# =============================================================================

def render_sidebar_css():
    """Render custom CSS for sidebar styling"""
    st.markdown("""
<style>
    section[data-testid="stSidebar"] {
        font-size: 12px !important;
    }
    section[data-testid="stSidebar"] h1 {
        font-size: 1.3em !important;
    }
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] h4 {
        font-size: 1.1em !important;
    }
    section[data-testid="stSidebar"] .stButton > button {
        font-size: 12px !important;
    }
    section[data-testid="stSidebar"] input[type="text"],
    section[data-testid="stSidebar"] textarea {
        font-size: 12px !important;
    }
    section[data-testid="stSidebar"] label {
        font-size: 12px !important;
    }
</style>
""", unsafe_allow_html=True)


def render_chat_partner_config(chat_partner_name: str, chat_partner_personality: str, force_refresh: int):
    """Render chat partner configuration inputs in sidebar

    Args:
        chat_partner_name: Current chat partner name
        chat_partner_personality: Current personality description
        force_refresh: Refresh key value

    Returns:
        Tuple of (new_name, new_personality, should_update)
    """
    new_name = st.text_input(
        "Chat Partner Name",
        value=chat_partner_name,
        placeholder="",
        key=f"chat_partner_name_{force_refresh}"
    )

    new_personality = st.text_area(
        "Personality & Background",
        value=chat_partner_personality,
        placeholder="",
        height=100,
        key=f"chat_partner_personality_{force_refresh}"
    )

    should_update = (new_name != chat_partner_name or
                     new_personality != chat_partner_personality)

    return new_name, new_personality, should_update


def render_session_buttons():
    """Render session control buttons in sidebar"""
    if st.button("➕ New Session", use_container_width=True):
        return "new"

    st.divider()
    return None


def render_current_sessions(chat_history: dict, current_session: str, current_session_id: int):
    """Render current sessions list in sidebar

    Args:
        chat_history: Dictionary of chat histories
        current_session: Current active session name
        current_session_id: Current session ID

    Returns:
        Tuple of (action_type, session_name) if action triggered
    """
    st.subheader("📚 Current Sessions")

    if not chat_history:
        st.info("No active sessions yet")
        return None, None

    for session_name in list(chat_history.keys()):
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(f"💬 {session_name}", use_container_width=True,
                         key=f"load_{session_name}"):
                return "load_current", session_name
        with col2:
            if st.button("🗑️", key=f"delete_{session_name}"):
                return "delete_current", session_name

    return None, None


def render_saved_sessions(saved_sessions: list, current_session_id: int, force_refresh: int):
    """Render saved sessions list in sidebar

    Args:
        saved_sessions: List of saved sessions from database
        current_session_id: Current session ID
        force_refresh: Refresh key value

    Returns:
        Tuple of (action_type, session_data) if action triggered
    """
    st.subheader("💾 Saved Sessions (DB)")

    if not saved_sessions:
        st.info("No saved sessions in database")
        return None, None

    for session in saved_sessions:
        session_name = session['session_name']
        session_id = session['id']
        file_path = session.get('file_path', '')

        col1, col2 = st.columns([4, 1])
        with col1:
            display_name = f"{session_name[:20]}..." if len(session_name) > 20 else session_name
            if st.button(f"📋 {display_name}", use_container_width=True,
                         key=f"db_{session_id}_{force_refresh}"):
                return "load_saved", session
        with col2:
            if st.button("🗑️", key=f"db_delete_{session_id}"):
                return "delete_saved", session_id

    return None, None


# =============================================================================
# Main Application
# =============================================================================

# Initialize tools
sql = MySQLTools(**DB_CONFIG)
file_tools = FileTools(CONVERSATIONS_FOLDER)

if not CONVERSATIONS_FOLDER.exists():
    CONVERSATIONS_FOLDER.mkdir(parents=True, exist_ok=True)

# Set page configuration
st.set_page_config(
    page_title="Local AI Chat - " + MODEL_NAME,
    page_icon="🤖",
    layout="wide"
)

# Render sidebar CSS
render_sidebar_css()

# Initialize OpenAI client (Ollama-compatible API)
client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1"
)

# Initialize session state
session_defaults = {
    "messages": [],
    "chat_history": {},
    "current_session": "New Session",
    "saved_sessions": [],
    "chat_partner_name": "KELVIN",
    "chat_partner_personality": "程序员",
    "current_session_id": None,
    "force_refresh": 0,
    "should_rerun": False
}

for key, default_value in session_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

# Load saved sessions on first run
if not st.session_state.saved_sessions:
    st.session_state.saved_sessions = load_sessions_from_mysql(sql)


def load_saved_session_callback(session_id: int, file_path: str, session_name: str):
    """Callback function to load a saved session

    Args:
        session_id: Session ID
        file_path: Path to conversation file
        session_name: Name of the session
    """
    print(f"Loading session {session_id} from {file_path}")

    if file_path and Path(file_path).exists():
        messages, extracted_name, extracted_personality = load_messages_from_file(
            file_tools, Path(file_path).name
        )

        if messages:
            st.session_state.current_session = f"Loaded: {session_name}"
            st.session_state.messages = messages
            st.session_state.current_session_id = session_id

            if extracted_name:
                st.session_state.chat_partner_name = extracted_name
                print(f"Set chat_partner_name to: '{extracted_name}'")

            if extracted_personality:
                st.session_state.chat_partner_personality = extracted_personality
                print(f"Set chat_partner_personality to: '{extracted_personality}'")

            st.session_state.should_rerun = True
        else:
            st.error(f"Failed to load conversation from: {file_path}")
            st.info("File may be empty or corrupted")
    elif file_path:
        st.error(f"File not found: {file_path}")
        st.info("The conversation file has been deleted or moved")
    else:
        st.error("No file path found for this session")


# Check if rerun is needed
if st.session_state.get("should_rerun", False):
    st.session_state.should_rerun = False
    st.session_state.force_refresh += 1
    st.rerun()

# Sidebar
with st.sidebar:
    # Chat Partner Configuration
    new_name, new_personality, should_update = render_chat_partner_config(
        st.session_state.chat_partner_name,
        st.session_state.chat_partner_personality,
        st.session_state.force_refresh
    )

    if should_update:
        st.session_state.chat_partner_name = new_name
        st.session_state.chat_partner_personality = new_personality

        system_message = {
            "role": "system",
            "content": build_system_prompt(new_name, new_personality)
        }

        if st.session_state.messages and st.session_state.messages[0]["role"] == "system":
            st.session_state.messages[0] = system_message
        else:
            st.session_state.messages.insert(0, system_message)

        st.rerun()

    st.divider()

    # New Session Button
    if st.button("➕ New Session", use_container_width=True):
        if st.session_state.messages and len(st.session_state.messages) > 1:
            session_name = f"{datetime.now().strftime('%Y-%m-%d %H:%M')}"
            if save_session_to_mysql(sql, file_tools, session_name,
                                     st.session_state.messages,
                                     st.session_state.current_session_id):
                st.session_state.saved_sessions = load_sessions_from_mysql(sql)

        new_session_name = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        st.session_state.current_session = new_session_name
        st.session_state.chat_history[new_session_name] = []
        st.session_state.messages = [{
            "role": "system",
            "content": build_system_prompt(
                st.session_state.chat_partner_name,
                st.session_state.chat_partner_personality
            )
        }]
        st.session_state.current_session_id = None
        st.rerun()

    st.divider()

    # Current Sessions
    action, session_data = render_current_sessions(
        st.session_state.chat_history,
        st.session_state.current_session,
        st.session_state.current_session_id
    )

    if action == "load_current":
        st.session_state.current_session = session_data
        st.session_state.messages = st.session_state.chat_history[session_data].copy()
        st.session_state.current_session_id = None
        st.rerun()
    elif action == "delete_current":
        del st.session_state.chat_history[session_data]
        if st.session_state.current_session == session_data:
            st.session_state.current_session = "New Session"
            st.session_state.messages = []
            st.session_state.current_session_id = None
        st.rerun()

    st.divider()

    # Saved Sessions
    action, session_data = render_saved_sessions(
        st.session_state.saved_sessions,
        st.session_state.current_session_id,
        st.session_state.force_refresh
    )

    if action == "load_saved":
        load_saved_session_callback(
            session_data['id'],
            session_data.get('file_path', ''),
            session_data['session_name']
        )
    elif action == "delete_saved":
        if delete_session_from_mysql(sql, file_tools, session_data):
            st.session_state.saved_sessions = load_sessions_from_mysql(sql)
            if st.session_state.current_session_id == session_data:
                st.session_state.current_session = "New Session"
                st.session_state.messages = []
                st.session_state.current_session_id = None
            st.rerun()

# Main chat area
st.title(f"💬 Local AI Chat - {st.session_state.chat_partner_name}")

# Initialize system message if empty
if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "system",
        "content": build_system_prompt(
            st.session_state.chat_partner_name,
            st.session_state.chat_partner_personality
        )
    })

# Display chat messages (excluding system)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("What would you like to discuss?"):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    if st.session_state.current_session:
        if st.session_state.current_session not in st.session_state.chat_history:
            st.session_state.chat_history[st.session_state.current_session] = []
        st.session_state.chat_history[st.session_state.current_session].append(
            {"role": "user", "content": prompt}
        )

    # Get AI response
    success, response = get_chat_response(client, MODEL_NAME, st.session_state.messages)

    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

    if st.session_state.current_session:
        st.session_state.chat_history[st.session_state.current_session].append(
            {"role": "assistant", "content": response}
        )

# Clear chat option
if st.session_state.messages and len(st.session_state.messages) > 1:
    if st.button("🗑️ Clear Current Chat"):
        st.session_state.messages = []
        if st.session_state.current_session:
            st.session_state.chat_history[st.session_state.current_session] = []
        st.rerun()
