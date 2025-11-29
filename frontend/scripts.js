// ================================
// Global task storage
// ================================
window.loadedTasks = [];

// ================================
// Add single task
// ================================
document.getElementById("taskForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const task = {
        title: document.getElementById("title").value,
        due_date: document.getElementById("due_date").value,
        estimated_hours: parseFloat(document.getElementById("estimated_hours").value),
        importance: parseInt(document.getElementById("importance").value),
        dependencies: document.getElementById("dependencies").value
            .split(",")
            .map(d => d.trim())
            .filter(d => d !== "")
    };

    try {
        const res = await fetch("http://127.0.0.1:8000/api/tasks/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(task)
        });

        const data = await res.json();
        alert("✅ Task added: " + data.title);

        // Update global tasks and render
        window.loadedTasks.push(data);
        renderTasks(window.loadedTasks);

        e.target.reset();
    } catch (err) {
        console.error(err);
        alert("❌ Failed to add task to backend");
    }
});

// ================================
// Load Bulk Tasks
// ================================
document.getElementById("loadBulk").addEventListener("click", async function() {
    const raw = document.getElementById("bulkInput").value;

    try {
        const tasks = JSON.parse(raw);

        const promises = tasks.map(task =>
            fetch("http://127.0.0.1:8000/api/tasks/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(task)
            }).then(res => res.json())
        );

        const savedTasks = await Promise.all(promises);
        alert("✅ Loaded " + savedTasks.length + " tasks to backend!");

        // Update global tasks and render
        window.loadedTasks = savedTasks;
        renderTasks(savedTasks);

    } catch (err) {
        console.error(err);
        alert("❌ Invalid JSON or backend error!");
    }
});

// ================================
// Render Tasks
// ================================
function renderTasks(tasks) {
    const container = document.getElementById("taskList");
    container.innerHTML = "";

    tasks.forEach((task, index) => {
        const div = document.createElement("div");
        div.className = "task-box";
        div.style.borderLeft = "5px solid " + getPriorityColor(task.importance);
        div.innerHTML = `
            <p><strong>${index + 1}. ${task.title}</strong></p>
            <p>📅 Due: ${task.due_date}</p>
            <p>⏳ Hours: ${task.estimated_hours}</p>
            <p>🔥 Importance: ${task.importance}</p>
            <p>🔗 Dependencies: ${task.dependencies.join(", ")}</p>
        `;
        container.appendChild(div);
    });
}

// ================================
// Priority Color
// ================================
function getPriorityColor(importance) {
    if (importance >= 8) return "red";
    if (importance >= 5) return "orange";
    return "green";
}

// ================================
// Analyze Tasks via backend
// ================================
document.getElementById("analyzeTasks").addEventListener("click", async function() {
    if (!window.loadedTasks || window.loadedTasks.length === 0) {
        return alert("Load tasks first!");
    }

    const taskIds = window.loadedTasks.map(t => t.id);

    try {
        const res = await fetch("http://127.0.0.1:8000/api/tasks/analyze/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ task_ids: taskIds })
        });

        const data = await res.json();
        renderAnalyzedTasks(data);

    } catch (err) {
        console.error(err);
        alert("❌ Failed to analyze tasks via backend");
    }
});

// ================================
// Render Analyzed Tasks
// ================================
function renderAnalyzedTasks(results) {
    const container = document.getElementById("taskList");
    container.innerHTML = "<h3>📊 Analyzed Tasks</h3>";

    results.forEach((task, index) => {
        const div = document.createElement("div");
        div.className = "task-box analyzed";
        div.style.borderLeft = "5px solid " + getPriorityColor(task.importance);
        div.innerHTML = `
            <p><strong>${index + 1}. ${task.title}</strong></p>
            <p>📅 Due: ${task.due_date}</p>
            <p>⏳ Hours: ${task.estimated_hours}</p>
            <p>🔥 Importance: ${task.importance}</p>
            <p>🔗 Dependencies: ${task.dependencies.join(", ")}</p>
            <p>🧮 Score: ${task.score}</p>
            ${task.explanation ? `<p>💡 ${task.explanation}</p>` : ''}
        `;
        container.appendChild(div);
    });
}

