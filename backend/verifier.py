class Verifier:

    def verify_step(self, step, result):

        tool = step.get("tool")

        # First check whether execution itself succeeded
        if not isinstance(result, dict):
            return {
                "verified": False,
                "reason": "Tool returned an invalid result."
            }

        if not result.get("success"):
            return {
                "verified": False,
                "reason": result.get(
                    "error",
                    "Tool execution failed."
                )
            }

        # Task listing
        if tool == "list_tasks":
            return {
                "verified": True,
                "reason": "Tasks were retrieved successfully."
            }

        # Task creation
        elif tool == "create_task":
            return {
                "verified": True,
                "reason": "Task was created successfully."
            }

        # Task completion
        elif tool == "complete_task":
            return {
                "verified": True,
                "reason": "Task was completed successfully."
            }

        # Task deletion
        elif tool == "delete_task":
            return {
                "verified": True,
                "reason": "Task was deleted successfully."
            }

        # Calculator
        elif tool == "calculate":
            return {
                "verified": True,
                "reason": "Calculation completed successfully."
            }

        # File manager
        elif tool == "list_files":
            return {
                "verified": True,
                "reason": "Files were listed successfully."
            }

        elif tool == "find_files":
            return {
                "verified": True,
                "reason": "File search completed successfully."
            }

        elif tool == "rename_file":
            return {
                "verified": True,
                "reason": "File was renamed successfully."
            }

        elif tool == "move_file":
            return {
                "verified": True,
                "reason": "File was moved successfully."
            }

        # Web search
        elif tool == "web_search":

            search_result = result.get("result", {})

            if isinstance(search_result, dict):

                if search_result.get("success"):
                    return {
                        "verified": True,
                        "reason": "Web search completed successfully."
                    }

                return {
                    "verified": False,
                    "reason": search_result.get(
                        "error",
                        "Web search failed."
                    )
                }

            return {
                "verified": False,
                "reason": "Web search returned an invalid result."
            }

        # Browser: open URL
        elif tool == "open_url":
            return {
                "verified": True,
                "reason": "Website opened successfully."
            }

        # Browser: extract text
        elif tool == "extract_text":

            browser_result = result.get("result", {})

            if isinstance(browser_result, dict):

                text = browser_result.get("text", "")

                if text and text.strip():
                    return {
                        "verified": True,
                        "reason": "Page text extracted successfully."
                    }

                return {
                    "verified": False,
                    "reason": "No text was extracted from the page."
                }

            return {
                "verified": False,
                "reason": "Browser extraction returned an invalid result."
            }

        # Browser: click
        elif tool == "click":
            return {
                "verified": True,
                "reason": "Page element clicked successfully."
            }

        # Browser: type text
        elif tool == "type_text":
            return {
                "verified": True,
                "reason": "Text entered successfully."
            }
        
                # Gmail: send email
        elif tool == "send_email":

            email_result = result.get("result", {})

            if isinstance(email_result, dict):

                if email_result.get("success"):
                    return {
                        "verified": True,
                        "reason": "Email sent successfully."
                    }

                return {
                    "verified": False,
                    "reason": email_result.get(
                        "error",
                        "Email sending failed."
                    )
                }

            return {
                "verified": False,
                "reason": "Email tool returned an invalid result."
            }
        
        # Write file
        elif tool == "write_file":
        
            file_result = result.get("result", {})
        
            if isinstance(file_result, dict):
            
                if file_result.get("success"):
                    return {
                        "verified": True,
                        "reason": "File written successfully."
                    }
        
                return {
                    "verified": False,
                    "reason": file_result.get(
                        "error",
                        "File writing failed."
                    )
                }
        
            return {
                "verified": False,
                "reason": "File tool returned an invalid result."
            }

        # Unknown tool
        return {
            "verified": False,
            "reason": f"No verifier available for tool: {tool}"
        }