import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from tools.calculator import calculate

from database.task_database import (
    create_task,
    list_tasks,
    complete_task,
    delete_task
)

from backend.planner import create_plan
from backend.memory_analyzer import MemoryAnalyzer

from backend.memory import (
    save_memory,
    get_memory,
    list_memories,
    delete_memory
)

from backend.autonomous_agent import AutonomousAgent


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is not set in the .env file"
    )


# --------------------------------------------------
# Gemini Agent
# --------------------------------------------------

class TaskPilotAgent:

    def __init__(self):

        self.autonomous_agent = AutonomousAgent()

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = "gemini-3.5-flash-lite"

        self.memory_analyzer = MemoryAnalyzer(
            self.client,
            self.model
        )

        # --------------------------------------------------
        # System instructions
        # --------------------------------------------------

        self.system_instruction = """
You are TaskPilot AI, an autonomous personal assistant.

You have access to:
- calculator
- task manager
- persistent memory

MEMORY RULES:

1. If the user asks about information they previously
   asked you to remember, use get_memory.

2. Do NOT use task tools to answer questions about
   remembered information.

3. If the user asks what you remember, use list_memories.

4. If the user explicitly tells you to remember something,
   use save_memory.

5. If the user asks you to forget something,
   use delete_memory.

6. Use concise descriptive memory keys.

7. If you are unsure which memory key contains the requested
   information, use list_memories first.

8. Never claim to remember something unless the memory tool
   confirms it.

9. If the user asks about a previously remembered appointment,
   interview, meeting, preference, date, personal fact,
   or other stored information, prioritize memory tools.

10. Do not confuse memories with tasks.

TASK RULES:

1. Use task tools for actual tasks.

2. Use list_tasks when the user asks about their tasks.

3. Use create_task when the user wants to create a task.

4. Use complete_task when the user wants to complete a task.

5. Use delete_task when the user wants to delete a task.

CALCULATOR RULES:

1. Use calculate for mathematical calculations.

Always use the appropriate tool before answering when
stored information or external application data is needed.
"""


        # --------------------------------------------------
        # Tool declarations
        # --------------------------------------------------

        self.tools = types.Tool(
            function_declarations=[

                # ==================================================
                # CALCULATOR
                # ==================================================

                types.FunctionDeclaration(
                    name="calculate",
                    description=(
                        "Calculate a mathematical expression."
                    ),
                    parameters={
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": (
                                    "Mathematical expression to calculate."
                                )
                            }
                        },
                        "required": ["expression"]
                    }
                ),

                # ==================================================
                # CREATE TASK
                # ==================================================

                types.FunctionDeclaration(
                    name="create_task",
                    description=(
                        "Create a new task in the task manager."
                    ),
                    parameters={
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": (
                                    "The title of the task."
                                )
                            },
                            "due_date": {
                                "type": "string",
                                "description": (
                                    "Optional due date for the task."
                                )
                            }
                        },
                        "required": ["title"]
                    }
                ),

                # ==================================================
                # LIST TASKS
                # ==================================================

                types.FunctionDeclaration(
                    name="list_tasks",
                    description=(
                        "Get all tasks from the task manager. "
                        "Use this only when the user asks about "
                        "their tasks."
                    ),
                    parameters={
                        "type": "object",
                        "properties": {}
                    }
                ),

                # ==================================================
                # COMPLETE TASK
                # ==================================================

                types.FunctionDeclaration(
                    name="complete_task",
                    description=(
                        "Mark a task as completed."
                    ),
                    parameters={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": (
                                    "ID of the task to complete."
                                )
                            }
                        },
                        "required": ["task_id"]
                    }
                ),

                # ==================================================
                # DELETE TASK
                # ==================================================

                types.FunctionDeclaration(
                    name="delete_task",
                    description=(
                        "Delete a task from the task manager."
                    ),
                    parameters={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": (
                                    "ID of the task to delete."
                                )
                            }
                        },
                        "required": ["task_id"]
                    }
                ),

                # ==================================================
                # SAVE MEMORY
                # ==================================================

                types.FunctionDeclaration(
                    name="save_memory",
                    description=(
                        "Save an important piece of information "
                        "to persistent memory."
                    ),
                    parameters={
                        "type": "object",
                        "properties": {
                            "key": {
                                "type": "string",
                                "description": (
                                    "A short descriptive name "
                                    "for the memory."
                                )
                            },
                            "value": {
                                "type": "string",
                                "description": (
                                    "The information to remember."
                                )
                            }
                        },
                        "required": ["key", "value"]
                    }
                ),

                # ==================================================
                # GET MEMORY
                # ==================================================

                types.FunctionDeclaration(
                    name="get_memory",
                    description=(
                        "Retrieve a specific piece of information "
                        "from persistent memory. "
                        "USE THIS TOOL when the user asks about "
                        "something they previously told TaskPilot "
                        "to remember, such as appointments, "
                        "interviews, preferences, important dates, "
                        "personal information, or plans. "
                        "DO NOT use task tools to answer questions "
                        "about remembered information."
                    ),
                    parameters={
                        "type": "object",
                        "properties": {
                            "key": {
                                "type": "string",
                                "description": (
                                    "The memory key to retrieve. "
                                    "Use a concise descriptive key "
                                    "such as 'python_interview', "
                                    "'favorite_language', or "
                                    "'meeting_time'."
                                )
                            }
                        },
                        "required": ["key"]
                    }
                ),

                # ==================================================
                # LIST MEMORIES
                # ==================================================

                types.FunctionDeclaration(
                    name="list_memories",
                    description=(
                        "Retrieve all information currently stored "
                        "in persistent memory. "
                        "Use this when the user asks what you "
                        "remember about them or asks to see "
                        "their memories."
                    ),
                    parameters={
                        "type": "object",
                        "properties": {}
                    }
                ),

                # ==================================================
                # DELETE MEMORY
                # ==================================================

                types.FunctionDeclaration(
                    name="delete_memory",
                    description=(
                        "Delete a stored memory when the user "
                        "asks TaskPilot to forget information."
                    ),
                    parameters={
                        "type": "object",
                        "properties": {
                            "key": {
                                "type": "string",
                                "description": (
                                    "The key of the memory to delete."
                                )
                            }
                        },
                        "required": ["key"]
                    }
                )
            ]
        )


    # --------------------------------------------------
    # Run agent
    # --------------------------------------------------

    def run(self, user_input):


        # --------------------------------------------------
        # Automatic memory analysis
        # --------------------------------------------------

        memory_analysis = self.memory_analyzer.analyze(
            user_input
    )

        if memory_analysis.get("should_save"):

            key = memory_analysis.get("key")
            value = memory_analysis.get("value")

            if key and value:

                memory_result = save_memory(
                    key,
                    value
                )

                print(
                    f"\n[Automatic memory saved]"
                )

                print(
                    f"[Key: {key}]"
                )

                print(
                    f"[Value: {value}]"
                )

                print(
                    f"[Memory result: {memory_result}]\n"
                )

        # --------------------------------------------------
        # FIRST Gemini request
        # --------------------------------------------------

        response = self.client.models.generate_content(
            model=self.model,
            contents=user_input,
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                tools=[self.tools]
            )
        )

        # --------------------------------------------------
        # Check whether Gemini requested a tool
        # --------------------------------------------------

        if response.function_calls:

            function_call = response.function_calls[0]

            print(
                f"\n[Agent selected tool: "
                f"{function_call.name}]"
            )

            print(
                f"[Arguments: "
                f"{dict(function_call.args)}]"
            )

            # ==================================================
            # CALCULATOR
            # ==================================================

            if function_call.name == "calculate":

                result = calculate(
                    function_call.args["expression"]
                )

            # ==================================================
            # CREATE TASK
            # ==================================================

            elif function_call.name == "create_task":

                result = create_task(
                    function_call.args["title"],
                    function_call.args.get("due_date")
                )

            # ==================================================
            # LIST TASKS
            # ==================================================

            elif function_call.name == "list_tasks":

                result = list_tasks()

            # ==================================================
            # COMPLETE TASK
            # ==================================================

            elif function_call.name == "complete_task":

                result = complete_task(
                    function_call.args["task_id"]
                )

            # ==================================================
            # DELETE TASK
            # ==================================================

            elif function_call.name == "delete_task":

                result = delete_task(
                    function_call.args["task_id"]
                )

            # ==================================================
            # SAVE MEMORY
            # ==================================================

            elif function_call.name == "save_memory":

                result = save_memory(
                    function_call.args["key"],
                    function_call.args["value"]
                )

            # ==================================================
            # GET MEMORY
            # ==================================================

            elif function_call.name == "get_memory":

                result = get_memory(
                    function_call.args["key"]
                )

            # ==================================================
            # LIST MEMORIES
            # ==================================================

            elif function_call.name == "list_memories":

                result = list_memories()

            # ==================================================
            # DELETE MEMORY
            # ==================================================

            elif function_call.name == "delete_memory":

                result = delete_memory(
                    function_call.args["key"]
                )

            # ==================================================
            # UNKNOWN TOOL
            # ==================================================

            else:

                result = {
                    "error": (
                        f"Unknown tool: "
                        f"{function_call.name}"
                    )
                }

            print(
                f"[Tool result: {result}]\n"
            )

            # --------------------------------------------------
            # Send tool result back to Gemini
            # --------------------------------------------------

            tool_response = types.Part.from_function_response(
                name=function_call.name,
                response={
                    "result": result
                }
            )

            # --------------------------------------------------
            # SECOND Gemini request
            # --------------------------------------------------

            final_response = (
                self.client.models.generate_content(
                    model=self.model,
                    contents=[
                        user_input,
                        response.candidates[0].content,
                        tool_response
                    ],
                    config=types.GenerateContentConfig(
                        system_instruction=self.system_instruction,
                        tools=[self.tools]
                    )
                )
            )

            return final_response.text

        # --------------------------------------------------
        # No tool required
        # --------------------------------------------------

        return response.text


# --------------------------------------------------
# Main application
# --------------------------------------------------

def main():

    agent = TaskPilotAgent()

    print("======================================")
    print("          TaskPilot AI")
    print("======================================")
    print()

    print("Commands:")
    print("  plan <goal>  - Create a plan")
    print("  exit         - Quit")
    print()

    while True:

        try:

            user_input = input(
                "You: "
            ).strip()

            if not user_input:
                continue

            # ==================================================
            # EXIT
            # ==================================================

            if user_input.lower() == "exit":

                print(
                    "TaskPilot AI shutting down..."
                )

                break

            if user_input.lower().startswith("plan "):
                goal = user_input[5:].strip()
            
                plan = create_plan(goal)
            
                print("\nPlan:")
                print(f"Goal: {plan['goal']}")
            
                for step in plan["steps"]:
                    print(
                        f"Step {step['step']}: "
                        f"{step['tool']} "
                        f"{step['arguments']}"
                    )
            
                return

            # ==================================================
            # PLANNING COMMAND
            # ==================================================

            if user_input.lower().startswith("plan "):

                goal = user_input[5:].strip()

                if not goal:

                    print(
                        "Please provide a goal "
                        "after 'plan'."
                    )

                    continue

                print(
                    "\n[Creating plan...]\n"
                )

                plan = create_plan(goal)

                print("PLAN:")

                print(
                    f"Goal: {plan['goal']}"
                )

                print()

                for step in plan["steps"]:

                    print(
                        f"{step['step']}. "
                        f"{step['tool']} "
                        f"{step['arguments']}"
                    )

                print()

                continue

            # ==================================================
            # NORMAL AGENT REQUEST
            # ==================================================

            answer = agent.run(
                user_input
            )

            print(
                f"TaskPilot: {answer}"
            )

            print()

        except KeyboardInterrupt:

            print(
                "\n\nTaskPilot AI stopped."
            )

            break

        except Exception as e:

            print(
                f"\nERROR: {e}\n"
            )


# --------------------------------------------------
# Start application
# --------------------------------------------------

if __name__ == "__main__":

    main()