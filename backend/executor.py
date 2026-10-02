from database.task_database import (
    create_task,
    list_tasks,
    complete_task,
    delete_task
)

from tools.calculator import calculate
from tools.web_search import search_web
from tools.file_manager import FileManager
from tools.gmail import send_email

from backend.confirmation import ConfirmationManager

from tools.browser import BrowserTool



class TaskExecutor:

    def __init__(self):
        self.file_manager = FileManager()
        self.confirmation = ConfirmationManager()
        self.browser = BrowserTool()

    def execute_step(self, step):

        tool = step.get("tool")
        arguments = step.get("arguments", {})

        print("\n[Executor]")
        print(f"Tool: {tool}")
        print(f"Arguments: {arguments}")

        try:

            # ----------------------------------
            # TASKS
            # ----------------------------------

            if tool == "list_tasks":

                result = list_tasks()

            elif tool == "create_task":

                result = create_task(
                    title=arguments.get("title"),
                    due_date=arguments.get("due_date")
                )

            elif tool == "complete_task":

                result = complete_task(
                    arguments.get("task_id")
                )

            elif tool == "delete_task":

                result = delete_task(
                    arguments.get("task_id")
                )

                        # ----------------------------------
            # SEND EMAIL
            # REQUIRES CONFIRMATION
            # ----------------------------------

            elif tool == "send_email":

                return self.confirmation.request_confirmation({
                    "tool": "send_email",
                    "to": arguments.get("to"),
                    "subject": arguments.get("subject"),
                    "body": arguments.get("body")
                })

            # ----------------------------------
            # CALCULATOR
            # ----------------------------------

            elif tool == "calculate":

                result = calculate(
                    arguments.get("expression")
                )

            elif tool == "write_file":
                result = self.file_manager.write_file(
                    arguments.get("filename"),
                    arguments.get("content")
                )

            

            # ----------------------------------
            # WEB SEARCH
            # ----------------------------------

            elif tool == "web_search":

                result = search_web(
                    arguments.get("query")
                )

            # ----------------------------------
            # FILE LIST
            # ----------------------------------

            elif tool == "list_files":

                result = self.file_manager.list_files(
                    arguments.get("directory", ".")
                )

            # ----------------------------------
            # FILE SEARCH
            # ----------------------------------

            elif tool == "find_files":

                result = self.file_manager.find_files(
                    arguments.get("pattern"),
                    arguments.get("directory", ".")
                )

            # ----------------------------------
            # RENAME FILE
            # REQUIRES CONFIRMATION
            # ----------------------------------

            elif tool == "rename_file":

                return self.confirmation.request_confirmation({
                    "tool": "rename_file",
                    "source": arguments.get("source"),
                    "new_name": arguments.get("new_name")
                })

            # ----------------------------------
            # MOVE FILE
            # REQUIRES CONFIRMATION
            # ----------------------------------

            elif tool == "move_file":

                return self.confirmation.request_confirmation({
                    "tool": "move_file",
                    "source": arguments.get("source"),
                    "destination": arguments.get("destination")
                })
            
            elif tool == "open_url":
                result = self.browser.open_url(
                    arguments.get("url")
                )

            elif tool == "click":
                result = self.browser.click(
                    arguments.get("url"),
                    arguments.get("selector")
                )

            elif tool == "extract_text":
                result = self.browser.extract_text(
                    arguments.get("url"),
                    arguments.get("selector", "body")
                )

            elif tool == "type_text":
                result = self.browser.type_text(
                    arguments.get("url"),
                    arguments.get("selector"),
                    arguments.get("text")
                )

            # ----------------------------------
            # UNKNOWN TOOL
            # ----------------------------------

            else:

                return {
                    "success": False,
                    "tool": tool,
                    "error": f"Unknown tool: {tool}"
                }

            print(f"[Result: {result}]")

            # Some tools return their own success/failure status.
            # Preserve that status so the autonomous agent can
            # detect failures and trigger replanning.

            if isinstance(result, dict) and "success" in result:
            
                return {
                    "success": result["success"],
                    "tool": tool,
                    "result": result,
                    "error": result.get("error")
                }

            return {
                "success": True,
                "tool": tool,
                "result": result
            }

        except Exception as e:

            return {
                "success": False,
                "tool": tool,
                "error": str(e)
            }

    def confirm_pending_action(self):

        confirmation = self.confirmation.confirm()

        if not confirmation.get("confirmed"):
            return confirmation

        action = confirmation["action"]

        try:

            if action["tool"] == "rename_file":

                result = self.file_manager.rename_file(
                    action["source"],
                    action["new_name"]
                )

            elif action["tool"] == "move_file":

                result = self.file_manager.move_file(
                    action["source"],
                    action["destination"]
                )

            elif action["tool"] == "send_email":

                result = send_email(
                    action["to"],
                    action["subject"],
                    action["body"]
                )

            else:

                return {
                    "success": False,
                    "error": f"Unsupported confirmed action: {action['tool']}"
                }

            operation_success = (
                result.get("success", False)
                if isinstance(result, dict)
                else True
            )

            response = {
                "success": operation_success,
                "confirmed": True,
                "tool": action["tool"],
                "result": result
            }

            if not operation_success and isinstance(result, dict):
                response["error"] = result.get(
                    "error",
                    "The approved action failed."
                )

            return response

        except Exception as e:

            return {
                "success": False,
                "confirmed": True,
                "tool": action["tool"],
                "error": str(e)
            }

    def cancel_pending_action(self):

        return self.confirmation.cancel()

    def get_pending_confirmation(self):

        return self.confirmation.get_pending()


if __name__ == "__main__":

    executor = TaskExecutor()

    print("Executor initialized successfully.")