# calculatorAPP.py
import streamlit as st
import math
import base64
from pathlib import Path
from datetime import datetime
from typing import Optional

# ---------------- Page config ----------------
st.set_page_config(
    page_title="Bhanu's Scientific Calculator",
    page_icon="🧮",
    layout="centered"
)

# ---------------- Theme & card styling ----------------
CARD_CSS = """
<style>
[data-testid="stHeader"] { background: rgba(0,0,0,0); }
[data-testid="stToolbar"] { right: 2rem; }

.calc-card {
    background: rgba(255,255,255,0.92);
    border-radius: 12px;
    padding: 18px 16px;
    box-shadow: 0 6px 24px rgba(0,0,0,0.25);
    max-width: 720px;
    margin: 0 auto;
}
.section-title {
    font-weight: 600;
    margin-bottom: 8px;
}
.result-box {
    background: #f7f7f9;
    border: 1px solid #e6e6eb;
    border-radius: 8px;
    padding: 10px 12px;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
}
.copy-btn .stButton>button {
    width: 100%;
}
</style>
"""
st.markdown(CARD_CSS, unsafe_allow_html=True)

# ---------------- Responsive background ----------------
# Update these filenames to match the exact files you uploaded to your GitHub repo.
# If you only uploaded one image, set both to the same filename.
DESKTOP_IMG = Path("stormtrooper-on-pink-background-pop-art-desktop-wallpaper-4k.jpg")
MOBILE_IMG = Path("stormtrooper-on-pink-background-pop-art-desktop-wallpaper-4k.jpg")
# If you prefer to use a hosted URL for desktop background, set BG_URL to that string.
BG_URL: Optional[str] = None

def _to_data_uri(path: Optional[Path]) -> Optional[str]:
    if not path:
        return None
    if not path.exists():
        return None
    ext = path.suffix.lower().replace(".", "")
    if ext in ("webp",):
        mime = "image/webp"
    elif ext in ("jpg", "jpeg"):
        mime = "image/jpeg"
    elif ext in ("png",):
        mime = "image/png"
    else:
        mime = "application/octet-stream"
    with open(path, "rb") as f:
        data64 = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{data64}"

def set_responsive_background(desktop_path: Path, mobile_path: Path, url: Optional[str] = None) -> None:
    """Set a responsive background using either repo images or a URL.
    Pass None for url to use local images embedded as data URIs."""
    desktop_uri = url if url else _to_data_uri(desktop_path)
    mobile_uri = _to_data_uri(mobile_path)

    # If neither source is available, do nothing (app continues without background)
    if not desktop_uri and not mobile_uri:
        st.warning("No background image found in the repo and no BG_URL provided.")
        return

    # Fallbacks: if mobile missing, use desktop; if desktop missing but URL provided, use URL
    if not mobile_uri:
        mobile_uri = desktop_uri

    css = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("{desktop_uri}");
        background-size: cover;
        background-position: center center;
        background-repeat: no-repeat;
        background-attachment: scroll;
        min-height: 100vh;
    }}

    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.10);
        pointer-events: none;
        z-index: 0;
    }}

    /* Ensure main content sits above overlay */
    .css-1d391kg, .css-1lcbmhc, .stApp, .main {{
        z-index: 1;
        position: relative;
    }}

    @media (max-width: 767px) {{
        [data-testid="stAppViewContainer"] {{
            background-image: url("{mobile_uri}");
            background-size: cover;
            background-position: center top;
            background-attachment: scroll;
            -webkit-background-size: cover;
        }}
    }}

    @media (max-width: 420px) {{
        [data-testid="stAppViewContainer"] {{
            background-position: center 20%;
        }}
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Call the responsive background function
set_responsive_background(DESKTOP_IMG, MOBILE_IMG, BG_URL)

# ---------------- App state ----------------
if "memory" not in st.session_state:
    st.session_state.memory = None
if "history" not in st.session_state:
    st.session_state.history = []
if "angle_unit" not in st.session_state:
    st.session_state.angle_unit = "Degrees"  # or "Radians"

# ---------------- Helpers ----------------
def add_history(operation: str, inputs: str, result):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.history.append({
        "time": ts,
        "op": operation,
        "inputs": inputs,
        "result": result
    })

def try_float_list(text: str):
    vals = []
    for t in text.split():
        try:
            vals.append(float(t))
        except ValueError:
            return None
    return vals

def show_result(result, operation: str, inputs: str):
    with st.container():
        st.markdown("<div class='section-title'>Result</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='result-box'>{result}</div>", unsafe_allow_html=True)
        add_history(operation, inputs, result)
        cols = st.columns([1,1])
        with cols[0]:
            if st.button("Copy result", key=f"copy_{operation}_{len(st.session_state.history)}"):
                st.code(str(result))
        with cols[1]:
            st.info("Result saved to history.")

def trig_value(x: float, func: str):
    # Handles degrees/radians based on toggle
    if st.session_state.angle_unit == "Degrees":
        x = math.radians(x)
    if func == "sin":
        return math.sin(x)
    if func == "cos":
        return math.cos(x)
    if func == "tan":
        return math.tan(x)
    raise ValueError("Invalid trig function")

# ---------------- UI ----------------
st.title("🧮 Bhanu's  Calculator")

# Angle unit toggle
use_radians = st.checkbox("Use radians (unchecked = degrees)", value=(st.session_state.angle_unit == "Radians"))
st.session_state.angle_unit = "Radians" if use_radians else "Degrees"

st.markdown("<div class='calc-card'>", unsafe_allow_html=True)

menu = [
    "Addition", "Subtraction", "Multiplication", "Division",
    "Power (x^y)", "Modulus (x % y)", "Square Root", "Cube Root",
    "Logarithm (base 10)", "Natural Log (ln)", "Exponential (e^x)",
    "Factorial", "Sine", "Cosine", "Tangent",
    "Degree → Radian", "Radian → Degree", "Pi (constant)",
    "Show Memory", "Memory Add (M+)", "Memory Subtract (M-)", "Memory Recall (MR)", "Memory Clear (MC)",
    "Percentage", "Average / Mean", "Median",
]

choice = st.selectbox("Choose an operation:", menu)

# ---------------- Operations ----------------

# Two-number ops
if choice in ["Addition","Subtraction","Multiplication","Division","Power (x^y)","Modulus (x % y)"]:
    num1 = st.number_input("Enter first number", value=0.0)
    num2 = st.number_input("Enter second number", value=0.0)
    if st.button("Calculate"):
        try:
            if choice == "Addition":
                result = num1 + num2
            elif choice == "Subtraction":
                result = num1 - num2
            elif choice == "Multiplication":
                result = num1 * num2
            elif choice == "Division":
                if num2 == 0:
                    st.error("Division by zero is not allowed.")
                    result = "Error: Division by zero"
                else:
                    result = num1 / num2
            elif choice == "Power (x^y)":
                result = math.pow(num1, num2)
            elif choice == "Modulus (x % y)":
                if num2 == 0:
                    st.error("Modulus by zero is not allowed.")
                    result = "Error: Modulus by zero"
                else:
                    result = num1 % num2
            show_result(result, choice, f"{num1}, {num2}")
            if isinstance(result, (int, float)) and not isinstance(result, bool):
                st.session_state.memory = result
        except Exception as e:
            st.error(f"Calculation error: {e}")

# One-number ops
elif choice in ["Square Root","Cube Root","Logarithm (base 10)","Natural Log (ln)","Exponential (e^x)","Factorial","Sine","Cosine","Tangent"]:
    num = st.number_input("Enter number", value=0.0)
    if st.button("Calculate"):
        try:
            if choice == "Square Root":
                if num < 0:
                    st.error("Square root of a negative number is not real.")
                    result = "Error: negative input"
                else:
                    result = math.sqrt(num)
            elif choice == "Cube Root":
                result = math.copysign(abs(num) ** (1/3), num)
            elif choice == "Logarithm (base 10)":
                if num <= 0:
                    st.error("Logarithm is defined for positive numbers only.")
                    result = "Error: non-positive input"
                else:
                    result = math.log10(num)
            elif choice == "Natural Log (ln)":
                if num <= 0:
                    st.error("Natural log is defined for positive numbers only.")
                    result = "Error: non-positive input"
                else:
                    result = math.log(num)
            elif choice == "Exponential (e^x)":
                result = math.exp(num)
            elif choice == "Factorial":
                if num < 0 or not float(num).is_integer():
                    st.error("Factorial is defined for non-negative integers only.")
                    result = "Error: invalid input"
                else:
                    result = math.factorial(int(num))
            elif choice == "Sine":
                result = trig_value(num, "sin")
            elif choice == "Cosine":
                result = trig_value(num, "cos")
            elif choice == "Tangent":
                result = trig_value(num, "tan")
            show_result(result, choice, f"{num}")
            if isinstance(result, (int, float)) and not isinstance(result, bool):
                st.session_state.memory = result
        except Exception as e:
            st.error(f"Calculation error: {e}")

# Conversions
elif choice == "Degree → Radian":
    deg = st.number_input("Enter angle in degrees", value=0.0)
    if st.button("Convert"):
        try:
            result = math.radians(deg)
            show_result(result, choice, f"{deg}°")
        except Exception as e:
            st.error(f"Conversion error: {e}")

elif choice == "Radian → Degree":
    rad = st.number_input("Enter angle in radians", value=0.0)
    if st.button("Convert"):
        try:
            result = math.degrees(rad)
            show_result(result, choice, f"{rad} rad")
        except Exception as e:
            st.error(f"Conversion error: {e}")

# Constant
elif choice == "Pi (constant)":
    if st.button("Show Pi"):
        result = math.pi
        show_result(result, choice, "π")

# Memory options
elif choice == "Show Memory":
    st.info(f"Memory: {st.session_state.memory}" if st.session_state.memory is not None else "Memory is empty")

elif choice == "Memory Add (M+)":
    val = st.number_input("Add value to memory (M+)", value=0.0, key="mplus")
    if st.button("Apply M+"):
        if st.session_state.memory is None:
            st.session_state.memory = val
        else:
            try:
                st.session_state.memory = float(st.session_state.memory) + float(val)
            except Exception:
                st.error("Memory currently holds a non-numeric value.")
        st.success(f"Memory updated: {st.session_state.memory}")

elif choice == "Memory Subtract (M-)":
    val = st.number_input("Subtract value from memory (M-)", value=0.0, key="mminus")
    if st.button("Apply M-"):
        if st.session_state.memory is None:
            st.session_state.memory = -val
        else:
            try:
                st.session_state.memory = float(st.session_state.memory) - float(val)
            except Exception:
                st.error("Memory currently holds a non-numeric value.")
        st.success(f"Memory updated: {st.session_state.memory}")

elif choice == "Memory Recall (MR)":
    if st.button("Recall Memory"):
        if st.session_state.memory is None:
            st.info("Memory is empty.")
        else:
            show_result(st.session_state.memory, "Memory Recall", f"MR -> {st.session_state.memory}")

elif choice == "Memory Clear (MC)":
    if st.button("Clear Memory"):
        st.session_state.memory = None
        st.success("Memory cleared.")

# Percentage
elif choice == "Percentage":
    base = st.number_input("Enter base number", value=0.0)
    percent = st.number_input("Enter percentage", value=0.0)
    if st.button("Calculate Percentage"):
        try:
            result = (base * percent) / 100.0
            show_result(result, "Percentage", f"{base}, {percent}%")
        except Exception as e:
            st.error(f"Calculation error: {e}")

# Average / Mean
elif choice == "Average / Mean":
    text = st.text_input("Enter numbers separated by spaces (e.g., 1 2 3 4)")
    if st.button("Compute Mean"):
        vals = try_float_list(text)
        if vals is None or len(vals) == 0:
            st.error("Please enter valid numbers separated by spaces.")
        else:
            result = sum(vals) / len(vals)
            show_result(result, "Average / Mean", text)

# Median
elif choice == "Median":
    text = st.text_input("Enter numbers separated by spaces (e.g., 1 2 3 4)")
    if st.button("Compute Median"):
        vals = try_float_list(text)
        if vals is None or len(vals) == 0:
            st.error("Please enter valid numbers separated by spaces.")
        else:
            vals.sort()
            n = len(vals)
            if n % 2 == 1:
                result = vals[n // 2]
            else:
                result = (vals[n//2 - 1] + vals[n//2]) / 2.0
            show_result(result, "Median", text)

# ---------------- Footer / history display ----------------
st.markdown("</div>", unsafe_allow_html=True)  # close calc-card

if st.expander("Show calculation history"):
    for item in reversed(st.session_state.history[-20:]):
        st.write(f"{item['time']} — **{item['op']}** — inputs: {item['inputs']} — result: `{item['result']}`")
