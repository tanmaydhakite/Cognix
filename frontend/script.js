const BACKEND_URL = "http://localhost:8000";


// ============================================================
// BASIC UI
// ============================================================

function focusGoal() {
    const goal = document.getElementById("goal");

    if (!goal) return;

    goal.focus();

    goal.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });
}


function setConnectionStatus(text, online = false) {
    const status = document.getElementById("connection-status");

    if (!status) return;

    status.innerHTML = `
        <span
            class="status-dot"
            style="background: ${online ? "#18a66a" : "#98a1b2"}"
        ></span>
        ${escapeHtml(text)}
    `;
}


function setLoading(isLoading) {
    const button = document.getElementById("run-button");

    if (!button) return;

    button.disabled = isLoading;

    if (isLoading) {
        button.innerHTML = `
            <span>Running...</span>
            <span class="button-arrow">◌</span>
        `;
    } else {
        button.innerHTML = `
            <span>Run Agent</span>
            <span class="button-arrow">→</span>
        `;
    }
}


function showLoading() {
    const activity = document.getElementById("activity");

    if (!activity) return;

    activity.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>

            <div>
                Cognix is working...
                <br>
                <small>
                    Planning → Acting → Observing → Verifying
                </small>
            </div>
        </div>
    `;
}


// ============================================================
// CONFIRMATION
// ============================================================

function showConfirmation(confirmation) {
    const activity = document.getElementById("activity");

    if (!activity) return;

    const action = confirmation?.action || {};
    const tool = action.tool;

    let title = "Risky Action";
    let description = "";

    if (tool === "move_file") {

        title = "Move File";

        description = `
            <div class="confirmation-details">

                <p>
                    <strong>Source:</strong>
                    ${escapeHtml(action.source || "")}
                </p>

                <p>
                    <strong>Destination:</strong>
                    ${escapeHtml(action.destination || "")}
                </p>

            </div>
        `;

    } else if (tool === "rename_file") {

        title = "Rename File";

        description = `
            <div class="confirmation-details">

                <p>
                    <strong>File:</strong>
                    ${escapeHtml(action.source || "")}
                </p>

                <p>
                    <strong>New name:</strong>
                    ${escapeHtml(action.new_name || "")}
                </p>

            </div>
        `;
    }else if (tool === "send_email") {

    title = "Send Email";

    description = `
        <div class="confirmation-details">

            <p>
                <strong>To:</strong>
                ${escapeHtml(action.to || "")}
            </p>

            <p>
                <strong>Subject:</strong>
                ${escapeHtml(action.subject || "")}
            </p>

            <p>
                <strong>Message:</strong>
            </p>

            <div style="
                margin-top: 8px;
                padding: 12px;
                border-radius: 8px;
                background: #f6f7f9;
                white-space: pre-wrap;
            ">
                ${escapeHtml(action.body || "")}
            </div>

        </div>
    `;
}

    activity.innerHTML = `
        <div class="confirmation-card">

            <div class="confirmation-icon">
                ⚠️
            </div>

            <div class="confirmation-content">

                <h3>Approval Required</h3>

                <p>
                    Cognix wants to perform the following action:
                </p>

                <h4>${escapeHtml(title)}</h4>

                ${description}

                <div class="confirmation-actions">

                    <button
                        class="cancel-button"
                        type="button"
                        onclick="cancelConfirmation()"
                    >
                        Cancel
                    </button>

                    <button
                        class="approve-button"
                        type="button"
                        onclick="approveConfirmation()"
                    >
                        Approve
                    </button>

                </div>

            </div>

        </div>
    `;
}


async function approveConfirmation() {
    const activity = document.getElementById("activity");

    if (!activity) return;

    activity.innerHTML = `
        <div class="execution-card">

            <div class="result-heading">
                ⚙️ Executing...
            </div>

            <div class="search-answer">
                Cognix is performing the approved action.
            </div>

        </div>
    `;

    try {

        const response = await fetch(
            `${BACKEND_URL}/confirmation/approve`,
            {
                method: "POST"
            }
        );

        const data = await response.json();

        if (data.success) {

            activity.innerHTML = `
                <div class="execution-card">

                    <div class="result-heading">
                        ✅ Action Completed
                    </div>

                    <div class="search-answer">
                        ${escapeHtml(
                            data.result?.message ||
                            "The approved action was completed successfully."
                        )}
                    </div>

                </div>
            `;

            setConnectionStatus("Completed", true);

        } else {

            activity.innerHTML = `
                <div class="execution-card">

                    <div class="result-heading">
                        ❌ Action Failed
                    </div>

                    <div class="search-answer">
                        ${escapeHtml(
                            data.error ||
                            "The action could not be completed."
                        )}
                    </div>

                </div>
            `;
        }

    } catch (error) {

        activity.innerHTML = `
            <div class="execution-card">

                <div class="result-heading">
                    ❌ Connection Error
                </div>

                <div class="search-answer">
                    ${escapeHtml(error.message)}
                </div>

            </div>
        `;
    }
}


async function cancelConfirmation() {
    const activity = document.getElementById("activity");

    if (!activity) return;

    try {

        const response = await fetch(
            `${BACKEND_URL}/confirmation/cancel`,
            {
                method: "POST"
            }
        );

        const data = await response.json();

        activity.innerHTML = `
            <div class="execution-card">

                <div class="result-heading">
                    🛑 Action Cancelled
                </div>

                <div class="search-answer">
                    The requested file operation was cancelled.
                </div>

            </div>
        `;

        setConnectionStatus("Ready", true);

    } catch (error) {

        activity.innerHTML = `
            <div class="execution-card">

                <div class="result-heading">
                    ❌ Connection Error
                </div>

                <div class="search-answer">
                    ${escapeHtml(error.message)}
                </div>

            </div>
        `;
    }
}

function showExecutionTimeline(results) {

    const activity = document.getElementById("activity");

    if (!activity) return;

    activity.innerHTML = `
        <div class="timeline-card">

            <div class="timeline-title">
                🤖 Agent Execution
            </div>

            <div class="timeline">
                <div class="timeline-item completed">
                    <span class="timeline-icon">✓</span>
                    <div>
                        <strong>Goal received</strong>
                        <small>Task accepted by TaskPilot</small>
                    </div>
                </div>

                <div class="timeline-item completed">
                    <span class="timeline-icon">✓</span>
                    <div>
                        <strong>Plan created</strong>
                        <small>Agent generated an execution plan</small>
                    </div>
                </div>

                ${results.map((item, index) => {

                    const tool =
                        item?.step?.tool ||
                        "unknown";

                    const verified =
                        item?.verification?.verified;

                    const stage =
                        item?.stage ||
                        "completed";

                    let icon = "✓";

                    if (stage === "waiting_for_confirmation") {
                        icon = "⚠️";
                    }

                    if (!verified && stage !== "waiting_for_confirmation") {
                        icon = "❌";
                    }

                    return `
                        <div class="timeline-item ${
                            stage === "waiting_for_confirmation"
                                ? "waiting"
                                : verified
                                    ? "completed"
                                    : "failed"
                        }">

                            <span class="timeline-icon">
                                ${icon}
                            </span>

                            <div>
                                <strong>
                                    Step ${index + 1} — ${escapeHtml(tool)}
                                </strong>

                                <small>
                                    ${
                                        stage === "waiting_for_confirmation"
                                            ? "Waiting for human approval"
                                            : verified
                                                ? "Executed and verified"
                                                : "Execution or verification failed"
                                    }
                                </small>
                            </div>

                        </div>
                    `;

                }).join("")}

            </div>

        </div>
    `;
}


// ============================================================
// DISPLAY RESULTS
// ============================================================

function showResult(data) {
    const activity = document.getElementById("activity");

    if (!activity) {
        console.error("Activity container not found.");
        return;
    }

    if (!data) {
        showError("No response received from the backend.");
        return;
    }

    if (data.success === false) {
        showError(data.error || "The agent encountered an error.");
        return;
    }

    if (data.status === "waiting_for_confirmation") {
        showConfirmation(data.confirmation);
        return;
    }

    activity.innerHTML = "";

    const results = Array.isArray(data.results)
        ? data.results
        : [];

    if (results.length > 0) {
        showExecutionTimeline(results);
    }

    if (results.length === 0) {

        activity.innerHTML = `
            <div class="execution-card">

                <div class="result-heading">
                    ℹ️ No Result
                </div>

                <div class="search-answer">
                    The agent completed the request but returned no result.
                </div>

            </div>
        `;

        return;
    }

    results.forEach(item => {

        const step = item?.step || {};
        const tool = step.tool || "";
        const execution = item?.execution || {};
        const result = execution.result;

        const card = document.createElement("div");

        card.className = "execution-card";


        // ----------------------------------------------------
        // CALCULATOR
        // ----------------------------------------------------

        if (tool === "calculate") {

            let answer = result;

            if (
                typeof result === "object" &&
                result !== null
            ) {
                answer =
                    result.result ??
                    result.answer ??
                    result.value ??
                    result.output;
            }

            card.innerHTML = `
                <div class="result-heading">
                    🧮 Calculation
                </div>

                <div class="result-subtitle">
                    Your calculation:
                </div>

                <div class="calculation-answer">
                    ${escapeHtml(String(answer ?? ""))}
                </div>
            `;
        }


        // ----------------------------------------------------
        // FIND FILES
        // ----------------------------------------------------

        else if (tool === "find_files") {

            const files =
                result?.matches ||
                result?.files ||
                [];

            let html = `
                <div class="result-heading">
                    🔎 Files Found
                </div>

                <div class="result-subtitle">
                    I found
                    ${files.length}
                    matching file${files.length !== 1 ? "s" : ""}:
                </div>

                <div class="normal-file-list">
            `;

            if (files.length === 0) {

                html += `
                    <div class="normal-file">
                        No matching files found.
                    </div>
                `;

            } else {

                files.forEach(file => {

                    const name =
                        typeof file === "string"
                            ? file
                            : file.name ||
                              file.path ||
                              "";

                    html += `
                        <div class="normal-file">
                            <span>📄</span>
                            <span>
                                ${escapeHtml(name)}
                            </span>
                        </div>
                    `;
                });
            }

            html += `
                </div>

                <div class="result-count">
                    ${files.length}
                    file${files.length !== 1 ? "s" : ""}
                    found
                </div>
            `;

            card.innerHTML = html;
        }


        // ----------------------------------------------------
        // LIST FILES
        // ----------------------------------------------------

        else if (tool === "list_files") {

            const files =
                result?.files || [];

            const folders =
                result?.folders || [];

            let html = `
                <div class="result-heading">
                    📂 Files and Folders
                </div>

                <div class="normal-file-list">
            `;

            folders.forEach(folder => {

                const name =
                    typeof folder === "string"
                        ? folder
                        : folder.name ||
                          folder.path ||
                          "";

                html += `
                    <div class="normal-file">
                        <span>📁</span>
                        <span>
                            ${escapeHtml(name)}
                        </span>
                    </div>
                `;
            });

            files.forEach(file => {

                const name =
                    typeof file === "string"
                        ? file
                        : file.name ||
                          file.path ||
                          "";

                html += `
                    <div class="normal-file">
                        <span>📄</span>
                        <span>
                            ${escapeHtml(name)}
                        </span>
                    </div>
                `;
            });

            html += `
                </div>

                <div class="result-count">
                    ${files.length} files ·
                    ${folders.length} folders
                </div>
            `;

            card.innerHTML = html;
        }


        // ----------------------------------------------------
        // WEB SEARCH
        // ----------------------------------------------------

        else if (tool === "web_search") {

            const answer =
                result?.answer ||
                "Search completed successfully.";

            card.innerHTML = `
                <div class="result-heading">
                    🌐 Web Search
                </div>

                <div class="search-answer">
                    ${escapeHtml(answer)}
                </div>
            `;

            if (result?.sources?.length) {

                let sourcesHtml = `
                    <div class="result-subtitle">
                        Sources
                    </div>

                    <div class="normal-file-list">
                `;

                result.sources.forEach(source => {

                    sourcesHtml += `
                        <div class="normal-file">
                            <span>🔗</span>
                            <span>
                                ${escapeHtml(
                                    source.title ||
                                    source.url ||
                                    "Source"
                                )}
                            </span>
                        </div>
                    `;
                });

                sourcesHtml += `</div>`;

                card.innerHTML += sourcesHtml;
            }
        }


        // ----------------------------------------------------
        // TASK LIST
        // ----------------------------------------------------

        else if (tool === "list_tasks") {

            const tasks =
                Array.isArray(result)
                    ? result
                    : result?.tasks || [];

            let html = `
                <div class="result-heading">
                    📋 Your Tasks
                </div>

                <div class="normal-file-list">
            `;

            if (tasks.length === 0) {

                html += `
                    <div class="normal-file">
                        No tasks found.
                    </div>
                `;

            } else {

                tasks.forEach(task => {

                    html += `
                        <div class="normal-file">

                            <span>
                                ${task.completed ? "✅" : "⬜"}
                            </span>

                            <span>
                                ${escapeHtml(
                                    task.title ||
                                    "Untitled task"
                                )}
                            </span>

                        </div>
                    `;
                });
            }

            html += `
                </div>

                <div class="result-count">
                    ${tasks.length}
                    task${tasks.length !== 1 ? "s" : ""}
                </div>
            `;

            card.innerHTML = html;
        }


        // ----------------------------------------------------
        // CREATE TASK
        // ----------------------------------------------------

        else if (tool === "create_task") {

            card.innerHTML = `
                <div class="result-heading">
                    ✅ Task Created
                </div>

                <div class="search-answer">
                    ${escapeHtml(
                        result?.message ||
                        result?.title ||
                        "Task created successfully."
                    )}
                </div>
            `;
        }


        // ----------------------------------------------------
        // COMPLETE TASK
        // ----------------------------------------------------

        else if (tool === "complete_task") {

            card.innerHTML = `
                <div class="result-heading">
                    ✅ Task Completed
                </div>

                <div class="search-answer">
                    ${escapeHtml(
                        result?.message ||
                        "The task was completed successfully."
                    )}
                </div>
            `;
        }


        // ----------------------------------------------------
        // DELETE TASK
        // ----------------------------------------------------

        else if (tool === "delete_task") {

            card.innerHTML = `
                <div class="result-heading">
                    🗑️ Task Deleted
                </div>

                <div class="search-answer">
                    ${escapeHtml(
                        result?.message ||
                        "The task was deleted successfully."
                    )}
                </div>
            `;
        }


        // ----------------------------------------------------
        // RENAME / MOVE
        // ----------------------------------------------------

        else if (
            tool === "rename_file" ||
            tool === "move_file"
        ) {

            card.innerHTML = `
                <div class="result-heading">
                    ✅ File Operation Completed
                </div>

                <div class="search-answer">
                    ${escapeHtml(
                        result?.message ||
                        "The file operation was completed successfully."
                    )}
                </div>
            `;
        }


        // ----------------------------------------------------
        // GENERIC
        // ----------------------------------------------------

        else {

            let displayResult = result;

            if (
                typeof result === "object" &&
                result !== null
            ) {
                displayResult =
                    result.message ||
                    result.result ||
                    result.answer ||
                    JSON.stringify(result);
            }

            card.innerHTML = `
                <div class="result-heading">
                    ✓ Task Completed
                </div>

                <div class="search-answer">
                    ${escapeHtml(
                        String(
                            displayResult ??
                            "Operation completed successfully."
                        )
                    )}
                </div>
            `;
        }

        activity.appendChild(card);
    });
}


// ============================================================
// ERROR
// ============================================================

function showError(message) {
    const activity = document.getElementById("activity");

    if (!activity) return;

    activity.innerHTML = `
        <div class="execution-card">

            <div class="result-heading">
                ❌ Cognix encountered an error
            </div>

            <div class="search-answer">
                ${escapeHtml(message)}
            </div>

        </div>
    `;
}


// ============================================================
// HTML ESCAPING
// ============================================================

function escapeHtml(value) {

    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


// ============================================================
// MAIN AGENT FUNCTION
// ============================================================

window.runTaskPilot = async function () {

    const goalInput =
        document.getElementById("goal");

    const activity =
        document.getElementById("activity");


    if (!goalInput) {

        console.error(
            "ERROR: #goal textarea was not found."
        );

        return;
    }


    const goal =
        String(goalInput.value || "").trim();


    console.log(
        "GOAL VALUE:",
        goal
    );

    console.log(
        "GOAL TYPE:",
        typeof goal
    );


    if (!goal) {

        goalInput.focus();

        showError(
            "Please enter a goal first."
        );

        return;
    }


    setLoading(true);

    setConnectionStatus(
        "Agent running",
        true
    );

    showLoading();


    if (activity) {

        activity.innerHTML = `
            <div class="activity-card running">

                <div class="activity-icon">
                    ⚡
                </div>

                <div class="activity-content">

                    <h3>
                        Agent is working...
                    </h3>

                    <p>
                        Understanding your request
                        and executing the required tools.
                    </p>

                </div>

            </div>
        `;
    }


    try {

        // IMPORTANT:
        // goal is explicitly converted to a string.
        const payload = {
            goal: String(goal)
        };


        console.log(
            "SENDING PAYLOAD:",
            payload
        );

        console.log(
            "PAYLOAD JSON:",
            JSON.stringify(payload)
        );


        const response =
            await fetch(
                `${BACKEND_URL}/run`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(payload)
                }
            );


        const responseText =
            await response.text();


        console.log(
            "BACKEND STATUS:",
            response.status
        );

        console.log(
            "BACKEND RESPONSE:",
            responseText
        );


        if (!response.ok) {

            throw new Error(
                `Backend error ${response.status}: ${responseText}`
            );
        }


        let data;

        try {

            data =
                JSON.parse(responseText);

        } catch (parseError) {

            throw new Error(
                "Backend returned invalid JSON."
            );
        }


        console.log(
            "BACKEND DATA:",
            data
        );


        showResult(data);


        if (
            data.status ===
            "waiting_for_confirmation"
        ) {

            setConnectionStatus(
                "Waiting for approval",
                true
            );

        } else {

            setConnectionStatus(
                "Completed",
                true
            );
        }


    } catch (error) {

        console.error(
            "COGNIX ERROR:",
            error
        );


        showError(
            error.message ||
            "Something went wrong."
        );


        setConnectionStatus(
            "Connection error",
            false
        );


    } finally {

        setLoading(false);
    }
};


// ============================================================
// KEYBOARD SHORTCUT
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const goal =
            document.getElementById("goal");


        if (!goal) {
            return;
        }


        goal.addEventListener(
            "keydown",
            function (event) {

                if (
                    (event.ctrlKey ||
                     event.metaKey) &&
                    event.key === "Enter"
                ) {

                    event.preventDefault();

                    window.runTaskPilot();
                }
            }
        );
    }
);