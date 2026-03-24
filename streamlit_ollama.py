import streamlit as st
from openai import OpenAI
from datetime import datetime
import json
from pathlib import Path

from mysql_tools import MySQLTools
from file_tools import FileTools

# Model name
MODEL_NAME = "deepseek-r1:1.5b"

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'python_test'
}

# Conversations folder path
CONVERSATIONS_FOLDER = Path(r"F:\project\conversations")

# Set page configuration
st.set_page_config(
    page_title="Local AI Chat - " + MODEL_NAME,
    page_icon="🤖",
    layout="wide"
)

system_prompt = """
你叫 %s，现在是用户的真实伴侣，请完全代入伴侣角色。

规则：
1. 每次只回复1条消息
2. 禁止任何场景或状态描述性文字
3. 匹配用户的语言
4. 回复简短，像微信聊天一样
5. 有需要的话可以用❤️✨等emoji表达
6. 用符合伴侣性格的方式对话
7. 回复的内容，要充分体现出伴侣的性格特征

伴侣性格：
- %s

你必须严格遵守上述规则来回复用户。
"""

sql = MySQLTools(**DB_CONFIG)
file_tools = FileTools(CONVERSATIONS_FOLDER)

if not CONVERSATIONS_FOLDER.exists():
    CONVERSATIONS_FOLDER.mkdir(parents=True, exist_ok=True)

# Add custom CSS for smaller sidebar font
st.markdown("""
<style>
    /* Reduce sidebar font size */
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

# Initialize Ollama client (OpenAI-compatible API)
client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1"
)


def save_session_to_txt(session_name, messages):
    """Save chat session to TXT file in JSON format

    Args:
        session_name: Name of the session
        messages: List of chat messages (already in JSON format)

    Returns:
        File path if successful, None otherwise
    """
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = "".join([c for c in session_name if c.isalnum() or c in (' ', '-', '_')]).rstrip()
        filename = f"{timestamp}_{safe_name}.txt"

        # Create JSON structure with messages already in JSON format
        session_data = {
            "session": session_name,
            "created": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "message_count": len(messages),
            "messages": messages  # Messages are already dict objects
        }

        # Convert to JSON string with proper formatting and UTF-8 support
        content = json.dumps(session_data, ensure_ascii=False, indent=2, default=str)

        if file_tools.create_file(filename, content):
            filepath = file_tools.get_base_path() / filename
            return str(filepath)
        return None

    except Exception as e:
        print(f"Error saving to TXT: {e}")
        st.error(f"Error saving conversation to file: {e}")
        return None


def update_txt_file(filepath, messages):
    """Update existing TXT file with new messages

    Args:
        filepath: Path to the TXT file
        messages: Updated list of chat messages

    Returns:
        True if successful, False otherwise
    """
    try:
        filename = Path(filepath).name

        # Create JSON structure
        session_data = {
            "session": filename.replace('.txt', ''),
            "updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "message_count": len(messages),
            "messages": messages
        }

        # Convert to JSON string
        content = json.dumps(session_data, ensure_ascii=False, indent=2, default=str)

        result = file_tools.update_file(filename, content)
        return result

    except Exception as e:
        print(f"Error updating TXT file: {e}")
        st.error(f"Error updating conversation file: {e}")
        return False


def load_messages_from_txt(filepath):
    """Load messages from TXT/JSON file

    Args:
        filepath: Path to the TXT file

    Returns:
        Tuple of (messages list, extracted_name, extracted_personality) if successful,
        (empty list, "", "") otherwise
    """
    try:
        if not filepath:
            return [], "", ""

        filename = Path(filepath).name

        if not file_tools.get_base_path().exists():
            print(f"Base path does not exist: {file_tools.get_base_path()}")
            return [], "", ""

        content = file_tools.read_file(filename)

        if not content:
            print(f"Failed to read file content: {filename}")
            return [], "", ""

        try:
            # Parse JSON
            json_data = json.loads(content)

            if isinstance(json_data, dict):
                # Check if it has our expected structure
                if 'messages' in json_data:
                    messages = json_data['messages']

                    # Validate that messages is a list
                    if not isinstance(messages, list):
                        print(f"Messages field is not a list in {filename}")
                        return [], "", ""

                    # Extract name and personality from system message
                    extracted_name = ""
                    extracted_personality = ""

                    for msg in messages:
                        if isinstance(msg, dict) and msg.get('role') == 'system':
                            system_text = msg.get('content', '')
                            if system_text.startswith("You are"):
                                parts = system_text.split('.', 1)
                                if len(parts) >= 1:
                                    name_part = parts[0].replace("You are", "").strip()
                                    extracted_name = name_part

                                if len(parts) > 1:
                                    extracted_personality = parts[1].strip()
                            break

                    print(f"Successfully loaded {len(messages)} messages from {filename} (JSON format)")
                    print(f"Extracted name: '{extracted_name}', personality: '{extracted_personality}'")
                    return messages, extracted_name, extracted_personality
                else:
                    # JSON but not our format
                    print(f"Invalid JSON structure in {filename}")
                    return [], "", ""
            else:
                print(f"JSON root is not an object in {filename}")
                return [], "", ""

        except json.JSONDecodeError as e:
            print(f"Not valid JSON in {filename}: {e}")
            # Not valid JSON, fall back to old text format parsing
            pass

        # Fallback: Parse old text format (for backward compatibility)
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
                    messages.append({
                        'role': current_role,
                        'content': '\n'.join(current_content)
                    })
                current_role = 'user'
                current_content = [line.replace('[USER]:', '').strip()]
            elif line.startswith('[ASSISTANT]:'):
                if current_role and current_content:
                    messages.append({
                        'role': current_role,
                        'content': '\n'.join(current_content)
                    })
                current_role = 'assistant'
                current_content = [line.replace('[ASSISTANT]:', '').strip()]
            elif line.startswith('[SYSTEM]:'):
                if current_role and current_content:
                    messages.append({
                        'role': current_role,
                        'content': '\n'.join(current_content)
                    })
                current_role = 'system'
                system_text = line.replace('[SYSTEM]:', '').strip()

                if system_text.startswith("You are"):
                    parts = system_text.split('.', 1)
                    if len(parts) >= 1:
                        name_part = parts[0].replace("You are", "").strip()
                        extracted_name = name_part

                    if len(parts) > 1:
                        extracted_personality = parts[1].strip()

                current_content = []
            else:
                if current_content:
                    current_content.append(line)

        if current_role and current_content:
            messages.append({
                'role': current_role,
                'content': '\n'.join(current_content)
            })

        print(f"Successfully loaded {len(messages)} messages from {filename} (Text format)")
        print(f"Extracted name: '{extracted_name}', personality: '{extracted_personality}'")
        return messages, extracted_name, extracted_personality

    except Exception as e:
        print(f"Error loading from TXT: {e}")
        import traceback
        traceback.print_exc()
        st.error(f"Error loading conversation from file: {e}")
        return [], "", ""


def save_session_to_mysql(session_name, messages, session_id=None):
    """Save current session to MySQL database (stores file path only)

    Args:
        session_name: Name of the session
        messages: List of chat messages
        session_id: Optional session ID for updates

    Returns:
        True if successful, False otherwise
    """
    try:
        if session_id:
            sessions = sql.select_all("chat_sessions", {"id": session_id})
            if sessions:
                file_path = sessions[0].get('file_path', '')

                session_data = {
                    'create_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'session_name': session_name
                }

                result = sql.update("chat_sessions", session_data, {"id": session_id})
                if result and file_path:
                    update_txt_file(file_path, messages)
                return result
            return False
        else:
            file_path = save_session_to_txt(session_name, messages)
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


def load_sessions_from_mysql():
    """Load all sessions from MySQL database"""
    try:
        sessions = sql.select_all("chat_sessions", order_by="create_time DESC")
        return sessions
    except Exception as e:
        st.error(f"Error loading sessions: {e}")
        return []


def delete_session_from_mysql(session_id):
    """Delete a session from MySQL database and the TXT file"""
    try:
        sessions = sql.select_all("chat_sessions", {"id": session_id})
        if sessions:
            file_path = sessions[0].get('file_path', '')

            result = sql.delete("chat_sessions", {"id": session_id})

            if result and file_path:
                filename = Path(file_path).name
                if file_tools.delete_file(filename):
                    print(f"Deleted TXT file: {filename}")

            return result
        return False

    except Exception as e:
        st.error(f"Error deleting session: {e}")
        return False


# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}

if "current_session" not in st.session_state:
    st.session_state.current_session = "New Session"

if "saved_sessions" not in st.session_state:
    st.session_state.saved_sessions = load_sessions_from_mysql()

if "chat_partner_name" not in st.session_state:
    st.session_state.chat_partner_name = "KELVIN"

if "chat_partner_personality" not in st.session_state:
    st.session_state.chat_partner_personality = "程序员"

if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None

if "force_refresh" not in st.session_state:
    st.session_state.force_refresh = 0

if "should_rerun" not in st.session_state:
    st.session_state.should_rerun = False


def load_saved_session(session_id, file_path, session_name):
    """Callback function to load a saved session"""
    print(f"Loading session {session_id} from {file_path}")

    if file_path and Path(file_path).exists():
        messages, extracted_name, extracted_personality = load_messages_from_txt(file_path)
        if messages:
            # Update all session state
            st.session_state.current_session = f"Loaded: {session_name}"
            st.session_state.messages = messages
            st.session_state.current_session_id = session_id

            # Auto-fill chat partner name and personality
            if extracted_name:
                st.session_state.chat_partner_name = extracted_name
                print(f"Set chat_partner_name to: '{extracted_name}'")

            if extracted_personality:
                st.session_state.chat_partner_personality = extracted_personality
                print(f"Set chat_partner_personality to: '{extracted_personality}'")

            # Set rerun flag instead of calling st.rerun() directly
            st.session_state.should_rerun = True
        else:
            st.error(f"Failed to load conversation from: {file_path}")
            st.info("File may be empty or corrupted")
    elif file_path:
        st.error(f"File not found: {file_path}")
        st.info("The conversation file has been deleted or moved")
    else:
        st.error("No file path found for this session")


# Check if we should rerun (set by callback)
if st.session_state.get("should_rerun", False):
    st.session_state.should_rerun = False
    st.session_state.force_refresh += 1
    st.rerun()

# Sidebar - Control Panel
with st.sidebar:
    # Chat Partner Configuration
    chat_partner_name = st.text_input(
        "Chat Partner Name",
        value=st.session_state.chat_partner_name,
        placeholder="",
        key=f"chat_partner_name_{st.session_state.force_refresh}"
    )

    chat_partner_personality = st.text_area(
        "Personality & Background",
        value=st.session_state.chat_partner_personality,
        placeholder="",
        height=100,
        key=f"chat_partner_personality_{st.session_state.force_refresh}"
    )

    # Auto-update when values change
    if chat_partner_name != st.session_state.chat_partner_name or \
            chat_partner_personality != st.session_state.chat_partner_personality:

        st.session_state.chat_partner_name = chat_partner_name
        st.session_state.chat_partner_personality = chat_partner_personality

        # Update system message with new personality
        system_message = {
            "role": "system",
            "content": system_prompt%(chat_partner_name,chat_partner_personality)
        }

        # Replace old system message or add new one
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
            if save_session_to_mysql(session_name, st.session_state.messages, st.session_state.current_session_id):
                st.session_state.saved_sessions = load_sessions_from_mysql()

        new_session_name = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        st.session_state.current_session = new_session_name
        st.session_state.chat_history[new_session_name] = []
        st.session_state.messages = [{
            "role": "system",
            "content": system_prompt%(chat_partner_name,chat_partner_personality)
        }]
        st.session_state.current_session_id = None
        st.rerun()

    st.divider()

    # Session History (In-memory)
    st.subheader("📚 Current Sessions")
    if st.session_state.chat_history:
        for session_name in list(st.session_state.chat_history.keys()):
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(f"💬 {session_name}", use_container_width=True, key=f"load_{session_name}"):
                    st.session_state.current_session = session_name
                    st.session_state.messages = st.session_state.chat_history[session_name].copy()
                    st.session_state.current_session_id = None
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"delete_{session_name}"):
                    del st.session_state.chat_history[session_name]
                    if st.session_state.current_session == session_name:
                        st.session_state.current_session = "New Session"
                        st.session_state.messages = []
                        st.session_state.current_session_id = None
                    st.rerun()
    else:
        st.info("No active sessions yet")

    st.divider()

    # Saved Sessions from Database
    st.subheader("💾 Saved Sessions (DB)")
    if st.session_state.saved_sessions:
        for session in st.session_state.saved_sessions:
            session_name = session['session_name']
            session_id = session['id']
            file_path = session.get('file_path', '')

            col1, col2 = st.columns([4, 1])
            with col1:
                display_name = f"{session_name[:20]}..." if len(session_name) > 20 else session_name
                if st.button(f"📋 {display_name}", use_container_width=True,
                             key=f"db_{session_id}_{st.session_state.force_refresh}",
                             on_click=load_saved_session,
                             args=(session_id, file_path, session_name)):
                    pass  # The actual loading happens in the callback
            with col2:
                if st.button("🗑️", key=f"db_delete_{session_id}"):
                    if delete_session_from_mysql(session_id):
                        st.session_state.saved_sessions = load_sessions_from_mysql()
                        if st.session_state.current_session_id == session_id:
                            st.session_state.current_session = "New Session"
                            st.session_state.messages = []
                            st.session_state.current_session_id = None
                        st.rerun()
    else:
        st.info("No saved sessions in database")

# Main chat area
st.title(f"💬 Local AI Chat - {st.session_state.chat_partner_name}")

# Initialize system message if first time
if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "system",
        "content": system_prompt%(chat_partner_name,chat_partner_personality)
    })

# Display chat messages from history (excluding system messages)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What would you like to discuss?"):
    # Display user message in chat
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Update session history
    if st.session_state.current_session:
        if st.session_state.current_session not in st.session_state.chat_history:
            st.session_state.chat_history[st.session_state.current_session] = []
        st.session_state.chat_history[st.session_state.current_session].append({"role": "user", "content": prompt})

    # Generate and display assistant response using Ollama
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=st.session_state.messages,
            temperature=0.7,
            max_tokens=1024
        )

        assistant_response = response.choices[0].message.content

        print(f"assistant_response:{assistant_response}")

        # Display assistant response in chat
        with st.chat_message("assistant"):
            st.markdown(assistant_response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})

        # Update session history
        if st.session_state.current_session:
            st.session_state.chat_history[st.session_state.current_session].append(
                {"role": "assistant", "content": assistant_response})

    except Exception as e:
        error_message = f"Error communicating with Ollama ({MODEL_NAME}): {str(e)}"
        with st.chat_message("assistant"):
            st.markdown(error_message)
        st.session_state.messages.append({"role": "assistant", "content": error_message})

        if st.session_state.current_session:
            st.session_state.chat_history[st.session_state.current_session].append(
                {"role": "assistant", "content": error_message})

# Add option to clear current chat
if st.session_state.messages and len(st.session_state.messages) > 1:
    if st.button("🗑️ Clear Current Chat"):
        st.session_state.messages = []
        if st.session_state.current_session:
            st.session_state.chat_history[st.session_state.current_session] = []
        st.rerun()
