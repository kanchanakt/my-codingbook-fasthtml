import os
from datetime import datetime
import pytz
from fasthtml.common import *
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

MAX_NAME_CHAR = 15
MAX_MESSAGE_CHAR = 50
TIMESTAMP_FMT = "%Y-%m-%d %I:%M:%S %p IST"

supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def get_ist_time():
    ist_tz = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist_tz)

def add_message(name, message):
    timestamp = get_ist_time().strftime(TIMESTAMP_FMT)
    supabase.table("my_codingbook").insert(
        {"name": name, "message": message, "timestamp": timestamp}
    ).execute()

def get_messages():
    response = supabase.table("my_codingbook").select("*").order("id", desc=True).execute()
    return response.data

def render_message(entry):
    return Article(
        Header(f"Name: {entry['name']}"),
        P(entry["message"]),
        Footer(Small(Em(f"Posted: {entry['timestamp']}"))),
    )

app, rt = fast_app(
    hdrs=(Link(rel="icon", type="image/jpeg", href="/assets/book.jpg"),),
)

def render_message_list():
    messages = get_messages()
    return Div(
        *[render_message(entry) for entry in messages],
        id="message-list",
    )

def render_content():
    form = Form(
        Fieldset(
            Input(
                type="text",
                name="name",
                placeholder="Name",
                required=True,
                maxlength=MAX_NAME_CHAR,
            ),
            Input(
                type="text",
                name="message",
                placeholder="Message",
                required=True,
                maxlength=MAX_MESSAGE_CHAR,
            ),
            Button("Submit", type="submit"),
            role="group",
        ),
        method="post",
        hx_post="/submit-message",
        hx_target="#message-list",
        hx_swap="outerHTML",
        hx_on__after_request="this.reset()",
    )
    return Div(
        P(Em("Write something nice!")),
        form,
        Div(
            "Made with ❤️ by ",
            A("Kanchana", href="#", target="_blank"),
        ),
        Hr(),
        render_message_list(),
    )

@rt("/", methods=["GET"])
def get():
    return Titled("My Codingbook", render_content())

@rt("/submit-message", methods=["POST"])
def post(name: str, message: str):
    add_message(name, message)
    return render_message_list()

serve()