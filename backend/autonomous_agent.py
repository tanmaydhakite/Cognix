from backend.planner import create_plan
from backend.executor import TaskExecutor
from backend.verifier import Verifier


class AutonomousAgent:

    def __init__(self, max_replans=2):
        self.executor = TaskExecutor()
        self.verifier = Verifier()
        self.max_replans = max_replans

        # Pause / resume state
        self.paused_plan = None
        self.paused_results = []
        self.paused_step_index = 0

    # ==========================================================
    # FAST PATH
    # ==========================================================

    def _fast_path(self, goal):

        text = goal.lower().strip()

        if text.startswith("calculate "):
            return [
                {
                    "step": 1,
                    "tool": "calculate",
                    "arguments": {
                        "expression": goal[10:].strip()
                    }
                }
            ]

        if text in {
            "list tasks",
            "show tasks",
            "show my tasks",
            "what are my tasks",
            "what tasks do i have"
        }:
            return [
                {
                    "step": 1,
                    "tool": "list_tasks",
                    "arguments": {}
                }
            ]

        if text.startswith("find ") and "file" in text:

            pattern = "*"

            if "pdf" in text:
                pattern = "*.pdf"
            elif "txt" in text:
                pattern = "*.txt"
            elif "docx" in text:
                pattern = "*.docx"

            return [
                {
                    "step": 1,
                    "tool": "find_files",
                    "arguments": {
                        "pattern": pattern,
                        "directory": "."
                    }
                }
            ]

        if text in {
            "list files",
            "show files",
            "show my files"
        }:
            return [
                {
                    "step": 1,
                    "tool": "list_files",
                    "arguments": {
                        "directory": "."
                    }
                }
            ]

        return None

    # ==========================================================
    # CONTEXT INJECTION
    # ==========================================================

    def _inject_context(self, step, previous_results):

        if not previous_results:
            return step

        tool = step.get("tool")
        arguments = dict(step.get("arguments", {}))

        # ------------------------------------------------------
        # WRITE FILE CONTEXT
        # ------------------------------------------------------

        if tool == "write_file":

            content = arguments.get("content", "")

            if "CALCULATION_RESULT_FROM_PREVIOUS_STEP" in content:

                calculation_result = None

                for item in reversed(previous_results):

                    execution = item.get("execution", {})

                    if execution.get("tool") == "calculate":

                        if execution.get("success"):
                            calculation_result = execution.get("result")
                            break

                if calculation_result is not None:

                    result_value = calculation_result.get("result")

                    arguments["content"] = (
                        f"Cognix Currency Calculation\n\n"
                        f"Result: {result_value}\n"
                    )

                    print("\n[Context Injection]")
                    print(f"Calculation result: {result_value}")
                    print(
                        "Preparing file:",
                        arguments.get("filename")
                    )

            step["arguments"] = arguments

            return step

        # ------------------------------------------------------
        # CALCULATOR CONTEXT
        # ------------------------------------------------------

        # ==================================================
# SEND EMAIL CONTEXT INJECTION
# ==================================================

        if tool == "send_email":
        
            body = arguments.get("body", "")
        
            # Find previous web search result
            rate = None
        
            for item in reversed(previous_results):
            
                execution = item.get("execution", {})
        
                if execution.get("tool") == "web_search":
                    if execution.get("success"):
                    
                        search_result = execution.get("result", {})
        
                        if isinstance(search_result, dict):
                            answer = search_result.get("answer", "")
        
                            rate = self._extract_usd_inr_rate(answer)
        
                            if rate is not None:
                                break
                            
            # Find previous calculation result
            calculation_value = None
        
            for item in reversed(previous_results):
            
                execution = item.get("execution", {})
        
                if execution.get("tool") == "calculate":
                    if execution.get("success"):
                    
                        calculation_result = execution.get("result", {})
        
                        if isinstance(calculation_result, dict):
                            calculation_value = calculation_result.get("result")
        
                            if calculation_value is not None:
                                break
                            
            # Replace placeholders
            if rate is not None:
            
                body = body.replace(
                    "RATE_FROM_PREVIOUS_STEP",
                    str(rate)
                )
        
            if calculation_value is not None:
            
                body = body.replace(
                    "CALCULATION_RESULT_FROM_PREVIOUS_STEP",
                    str(calculation_value)
                )
        
            arguments["body"] = body
        
            print("\n[Context Injection - Email]")
            print(f"Exchange rate: {rate}")
            print(f"Calculation result: {calculation_value}")
            print(f"Email body: {body}")
        
            step["arguments"] = arguments
        
            return step
        
        
        if tool != "calculate":
            step["arguments"] = arguments
            return step

        expression = arguments.get("expression", "")

        if "RATE_FROM_PREVIOUS_STEP" not in expression:

            step["arguments"] = arguments

            return step

        import re

        search_result = None

        for item in reversed(previous_results):

            execution = item.get("execution", {})

            if execution.get("tool") == "web_search":

                if execution.get("success"):
                    search_result = execution.get("result")
                    break

        if not search_result:

            print(
                "[Context Injection] "
                "No web-search result found."
            )

            step["arguments"] = arguments

            return step

        answer = search_result.get("answer", "")

        rate = self._extract_usd_inr_rate(answer)

        if rate is None:

            print(
                "[Context Injection] "
                "Could not extract exchange rate."
            )

            step["arguments"] = arguments

            return step

        expression = expression.replace(
            "RATE_FROM_PREVIOUS_STEP",
            str(rate)
        )

        arguments["expression"] = expression

        print("\n[Context Injection]")
        print(f"Fresh USD/INR rate: {rate}")
        print(f"Final calculation: {expression}")

        step["arguments"] = arguments

        return step

    # ==========================================================
    # EXTRACT USD / INR RATE
    # ==========================================================

    def _extract_usd_inr_rate(self, text):

        import re

        if not text:
            return None

        patterns = [
            r"1(?:\.00)?\s*USD\s*=\s*₹?\s*(\d+(?:\.\d+)?)\s*INR",
            r"1\s*USD\s+equals\s+₹?\s*(\d+(?:\.\d+)?)\s*INR",
            r"USD\s*to\s*INR.*?₹?\s*(\d+(?:\.\d+)?)\s*INR",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE | re.DOTALL
            )

            if match:
                return float(match.group(1))

        return None

    # ==========================================================
    # EXECUTE PLAN
    # ==========================================================

    def execute_plan(self, plan):

        results = []
        previous_results = []

        # IMPORTANT:
        # steps must be created BEFORE using it.
        steps = plan.get("steps", [])

        print("\n" + "=" * 60)
        print("🤖 AUTONOMOUS EXECUTION")
        print("=" * 60)

        print(f"\n🎯 Goal: {plan.get('goal', 'Unknown')}")

        # ------------------------------------------------------
        # EMPTY PLAN
        # ------------------------------------------------------

        if not steps:

            print("\n❌ Plan contains no executable steps.")

            return [
                {
                    "stage": "planning_failed",
                    "execution": {
                        "success": False,
                        "error": "Planner returned no executable steps."
                    },
                    "verification": {
                        "verified": False,
                        "reason": "No steps were produced."
                    }
                }
            ], False

        # ------------------------------------------------------
        # SHOW PLAN
        # ------------------------------------------------------

        print("\n🧠 PLAN")

        for step in steps:

            print(
                f"  {step.get('step')}. "
                f"{step.get('tool')} "
                f"{step.get('arguments', {})}"
            )

        # ======================================================
        # EXECUTE EACH STEP
        # ======================================================

        for step_index, step in enumerate(steps):

            step = self._inject_context(
                step,
                previous_results
            )

            step_number = step.get(
                "step",
                step_index + 1
            )

            tool = step.get("tool")

            print("\n" + "-" * 60)

            print(f"▶ STEP {step_number}")
            print(f"🔧 Tool: {tool}")

            print(
                f"📦 Arguments: "
                f"{step.get('arguments', {})}"
            )

            # --------------------------------------------------
            # EXECUTE
            # --------------------------------------------------

            result = self.executor.execute_step(step)

            # --------------------------------------------------
            # HUMAN APPROVAL
            # --------------------------------------------------

            if result.get("requires_confirmation"):

                self.paused_plan = plan
                self.paused_results = results
                self.paused_step_index = step_index + 1

                print("\n⚠️ HUMAN APPROVAL REQUIRED")
                print("⏸ Agent paused.")

                item = {
                    "step": step,
                    "execution": result,
                    "verification": {
                        "verified": True,
                        "reason": "Waiting for human confirmation."
                    },
                    "stage": "waiting_for_confirmation"
                }

                results.append(item)

                return results, True

            # --------------------------------------------------
            # EXECUTION STATUS
            # --------------------------------------------------

            if result.get("success"):

                print(
                    f"   ✅ STEP "
                    f"{step_number} COMPLETED"
                )

            else:

                print(
                    f"   ❌ STEP "
                    f"{step_number} FAILED"
                )

                print(
                    f"Reason: "
                    f"{result.get('error') or result.get('result', {}).get('error', 'Unknown error')}"
                )

            # --------------------------------------------------
            # VERIFICATION
            # --------------------------------------------------

            print("🔍 VERIFYING")

            verification = self.verifier.verify_step(
                step,
                result
            )

            if verification.get("verified"):

                print("✅ VERIFICATION PASSED")

            else:

                print("❌ VERIFICATION FAILED")

                print(
                    f"Reason: "
                    f"{verification.get('reason', 'Unknown')}"
                )

            # --------------------------------------------------
            # SAVE RESULT
            # --------------------------------------------------

            item = {
                "step": step,
                "execution": result,
                "verification": verification,
                "stage": (
                    "completed"
                    if result.get("success")
                    and verification.get("verified")
                    else "failed"
                )
            }

            results.append(item)
            previous_results.append(item)

            # --------------------------------------------------
            # STOP IF EXECUTION FAILED
            # --------------------------------------------------

            if not result.get("success"):

                print("\n🛑 STEP FAILED")
                print(
                    "🔄 Returning failure "
                    "to autonomous agent."
                )

                return results, False

            # --------------------------------------------------
            # STOP IF VERIFICATION FAILED
            # --------------------------------------------------

            if not verification.get("verified"):

                print("\n🛑 VERIFICATION FAILED")
                print(
                    "🔄 Returning failure "
                    "to autonomous agent."
                )

                return results, False

        # ======================================================
        # EVERYTHING PASSED
        # ======================================================

        print("\n" + "=" * 60)
        print("🎉 ALL STEPS COMPLETED")
        print("=" * 60)

        return results, True

    # ==========================================================
    # RUN AGENT
    # ==========================================================

    def run(self, goal):

        print("\n")
        print("=" * 60)
        print("🤖 TASKPILOT AUTONOMOUS AGENT")
        print("=" * 60)

        print("\n🎯 GOAL")
        print(goal)

        # ======================================================
        # FAST PATH
        # ======================================================

        fast_steps = self._fast_path(goal)

        if fast_steps is not None:

            plan = {
                "goal": goal,
                "steps": fast_steps
            }

            print("\n⚡ FAST PLAN DETECTED")

            results, success = self.execute_plan(plan)

            return results

        # ======================================================
        # AI PLANNER
        # ======================================================

        previous_failure = None
        all_results = []

        for attempt in range(
            self.max_replans + 1
        ):

            print(
                f"\n🧠 PLANNING "
                f"(attempt {attempt + 1}/"
                f"{self.max_replans + 1})"
            )

            plan = create_plan(
                goal,
                previous_failure
            )

            print("\n📋 PLAN CREATED")

            import json

            print(
                json.dumps(
                    plan,
                    indent=2
                )
            )

            results, success = self.execute_plan(
                plan
            )

            all_results.extend(results)

            # ==================================================
            # SUCCESS
            # ==================================================

            if success:

                return all_results

            # ==================================================
            # FAILURE → REPLAN
            # ==================================================

            print("\n⚠️ PLAN FAILED")

            previous_failure = (
                results[-1]
                if results
                else {
                    "error":
                    "Plan produced no executable results."
                }
            )

            if attempt < self.max_replans:

                print("\n🔄 REPLANNING...")

        print("\n❌ AGENT FAILED")

        return all_results

    # ==========================================================
    # RESUME AFTER HUMAN APPROVAL
    # ==========================================================

    def resume_after_approval(self):

        if not self.paused_plan:

            return {
                "success": False,
                "error": "No paused task."
            }

        steps = self.paused_plan.get(
            "steps",
            []
        )

        remaining_steps = steps[
            self.paused_step_index:
        ]

        print("\n▶️ RESUMING TASK...")

        print(
            f"   Remaining steps: "
            f"{len(remaining_steps)}"
        )

        # ------------------------------------------------------
        # NO REMAINING STEPS
        # ------------------------------------------------------

        if not remaining_steps:

            self.paused_plan = None
            self.paused_results = []
            self.paused_step_index = 0

            print(
                "\n🎉 TASK COMPLETED SUCCESSFULLY"
            )

            return {
                "success": True,
                "message": "Task completed."
            }

        # ------------------------------------------------------
        # CREATE NEW PLAN
        # ------------------------------------------------------

        new_plan = {
            "goal": self.paused_plan.get("goal"),
            "steps": remaining_steps
        }

        # ------------------------------------------------------
        # EXECUTE REMAINING STEPS
        # ------------------------------------------------------

        results, success = self.execute_plan(
            new_plan
        )

        # ------------------------------------------------------
        # SUCCESS
        # ------------------------------------------------------

        if success:

            print(
                "\n🎉 TASK COMPLETED SUCCESSFULLY"
            )

            self.paused_plan = None
            self.paused_results = []
            self.paused_step_index = 0

        return {
            "success": success,
            "results": results
        }