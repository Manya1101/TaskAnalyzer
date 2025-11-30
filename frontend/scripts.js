// Global Task Storage
window.loadedTasks = [];


// Add Single Task

document.getElementById("taskForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const task = {
        title: document.getElementById("title").value,
        due_date: document.getElementById("due_date").value || null,
        estimated_hours: parseFloat(document.getElementById("estimated_hours").value) || 1,
        importance: parseInt(document.getElementById("importance").value) || 1,
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

        // normalize dependencies as array
        if (!Array.isArray(data.dependencies)) data.dependencies = [];
        data.score = data.score || 0;

        window.loadedTasks.push(data);
        renderTasks(window.loadedTasks);

        alert("✅ Task Added!");
        e.target.reset();
    } catch (err) {
        console.error(err);
        alert("❌ Failed to add task!");
    }
});


// Load Bulk Tasks

document.getElementById("loadBulk").addEventListener("click", async () => {
    const raw = document.getElementById("bulkInput").value;

    try {
        const tasks = JSON.parse(raw);

        const savedTasks = await Promise.all(
            tasks.map(task =>
                fetch("http://127.0.0.1:8000/api/tasks/", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(task)
                }).then(res => res.json())
            )
        );

        // normalize all tasks
        savedTasks.forEach(t => {
            if (!Array.isArray(t.dependencies)) t.dependencies = [];
            t.score = t.score || 0;
        });

        window.loadedTasks = savedTasks;
        renderTasks(savedTasks);

        alert("✅ Bulk Tasks Loaded!");
    } catch (err) {
        console.error(err);
        alert("❌ Invalid JSON or backend error!");
    }
});

// Render Tasks (Before Analysis)

function renderTasks(tasks) {
    const container = document.getElementById("taskList");
    container.innerHTML = "<h3>📋 Loaded Tasks</h3>";

    tasks.forEach((task, i) => {
        container.innerHTML += `
            <div class="task-box ${getPriorityClass(task.importance)}">
                <p><strong>${i + 1}. ${task.title}</strong></p>
                <p>📅 Due: ${task.due_date || "N/A"}</p>
                <p>⏳ Hours: ${task.estimated_hours}</p>
                <p>🔥 Importance: ${task.importance}</p>
                <p>🔗 Dependencies: ${task.dependencies.join(", ") || "None"}</p>
            </div>
        `;
    });
}


// Priority Colors

function getPriorityClass(score) {
    if (score >= 8) return "high";
    if (score >= 5) return "medium";
    return "low";
}


// Analyze Tasks (Backend Scoring)

document.getElementById("analyzeTasks").addEventListener("click", async () => {
    if (window.loadedTasks.length === 0) {
        alert("Load tasks first!");
        return;
    }

    try {
        const strategy = document.getElementById("sortStrategy").value;

        // Map strategy to backend mode
        const modeMap = {
            smart: "Smart Balance",
            fastest: "Fastest Wins",
            impact: "High Impact",
            deadline: "Deadline Driven"
        };
        const selectedMode = modeMap[strategy] || "Smart Balance";

        const res = await fetch("http://127.0.0.1:8000/api/tasks/analyze/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ tasks: window.loadedTasks, mode: selectedMode })
        });

        const data = await res.json();
        let tasks = data.tasks || [];

        // ensure all fields exist
        tasks.forEach(t => {
            t.dependencies = Array.isArray(t.dependencies) ? t.dependencies : [];
            t.score = t.score || 0;
        });

        tasks = applySortingStrategy(tasks, strategy);
        renderAnalyzedTasks(tasks);
    } catch (err) {
        console.error(err);
        alert("❌ Failed to analyze tasks!");
    }
});


// Sorting Strategies

function applySortingStrategy(tasks, strategy) {
    if (strategy === "fastest") {
        return tasks.sort((a, b) => a.estimated_hours - b.estimated_hours);
    }
    if (strategy === "impact") {
        return tasks.sort((a, b) => b.importance - a.importance);
    }
    if (strategy === "deadline") {
        return tasks.sort((a, b) => new Date(a.due_date || "2100-01-01") - new Date(b.due_date || "2100-01-01"));
    }
    // Default: Smart-Balance (score from backend)
    return tasks.sort((a, b) => b.score - a.score);
}


// Render Analyzed & Scored Tasks

function renderAnalyzedTasks(results) {
    const container = document.getElementById("taskList");
    container.innerHTML = "<h3>📊 Smart Analyzed Tasks</h3>";

    results.forEach((task, index) => {
        container.innerHTML += `
            <div class="task-box analyzed ${getPriorityClass(task.importance)}">
                <p><strong>${index + 1}. ${task.title}</strong></p>
                <p>📅 Due: ${task.due_date || "N/A"}</p>
                <p>⏳ Hours: ${task.estimated_hours}</p>
                <p>🔥 Importance: ${task.importance}</p>
                <p>🔗 Dependencies: ${task.dependencies.join(", ") || "None"}</p>
                <p>🧮 Score: ${task.score.toFixed(4)}</p>
                ${task.explanation ? `<p>💡 ${task.explanation}</p>` : ""}
            </div>
        `;
    });
}
