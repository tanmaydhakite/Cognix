class ConfirmationManager:

    def __init__(self):
        self.pending_action = None

    def request_confirmation(self, action):
        self.pending_action = action

        return {
            "requires_confirmation": True,
            "action": action
        }

    def get_pending(self):
        return self.pending_action

    def confirm(self):
        if not self.pending_action:
            return {
                "success": False,
                "error": "No action is waiting for confirmation."
            }

        action = self.pending_action
        self.pending_action = None

        return {
            "confirmed": True,
            "action": action
        }

    def cancel(self):
        if not self.pending_action:
            return {
                "success": False,
                "error": "No action is waiting for confirmation."
            }

        action = self.pending_action
        self.pending_action = None

        return {
            "confirmed": False,
            "cancelled": True,
            "action": action
        }