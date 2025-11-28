// Global variables
let tasks = [];
let users = [];
let tasksMeta = {};
let currentUserRole = window.currentUserRole || "developer";

let currentPage = 1;
let pageSize = 10;
let totalPages = 1;
let currentSortField = "created_at";
let currentSortDir = "desc";
let currentAssigneeFilter = "all";

// Initialize dashboard
document.addEventListener("DOMContentLoaded", () => {
  initializeControls();
  loadDashboardStats();
  loadTasks();
  if (currentUserRole === "admin") {
    loadUsers();
    loadAllUsers(); // Load all users for user management table
    setupTaskForm();
    setupEditForm();
    setupUserForms();
  }
});

// Load dashboard statistics
async function loadDashboardStats() {
  try {
    const response = await fetch("/api/dashboard/stats");
    const data = await response.json();

    if (data.success) {
      document.getElementById("statTotal").textContent = data.stats.total_tasks;
      document.getElementById("statCompleted").textContent =
        data.stats.completed_tasks;
      document.getElementById("statPending").textContent =
        data.stats.pending_tasks;
      document.getElementById("statInProgress").textContent =
        data.stats.in_progress_tasks;
      document.getElementById("statOverdue").textContent =
        data.stats.overdue_tasks;
    }
  } catch (error) {
    console.error("Error loading stats:", error);
  }
}

// Load all tasks
async function loadTasks() {
  try {
    const params = new URLSearchParams({
      page: currentPage,
      per_page: pageSize,
      sort_by: currentSortField,
      sort_dir: currentSortDir,
    });
    if (
      currentUserRole === "admin" &&
      currentAssigneeFilter &&
      currentAssigneeFilter !== "all"
    ) {
      params.append("assigned_to", currentAssigneeFilter);
    }
    const response = await fetch(`/api/tasks?${params.toString()}`);
    const data = await response.json();

    if (data.success) {
      tasks = data.tasks;
      tasksMeta = data.meta || {};
      currentPage = tasksMeta.page || currentPage;
      pageSize = tasksMeta.per_page || pageSize;
      totalPages = tasksMeta.total_pages || 1;
      syncControlsWithState();
      renderTasks();
      renderPagination();
    }
  } catch (error) {
    console.error("Error loading tasks:", error);
  }
}

// Render tasks table
function renderTasks() {
  const tbody = document.getElementById("tasksTableBody");
  const columnCount = currentUserRole === "admin" ? 9 : 8;

  if (tasks.length === 0) {
    tbody.innerHTML = `<tr><td colspan="${columnCount}" class="px-6 py-4 text-center text-gray-500">No tasks found</td></tr>`;
    return;
  }

  tbody.innerHTML = tasks
    .map((task) => {
      const isOverdue = task.is_overdue;
      const rowClass = isOverdue ? "bg-red-50" : "";
      const dueDateClass = isOverdue ? "text-red-600 font-semibold" : "";

      const priorityBadge = getPriorityBadge(task.priority);
      const statusBadge = getStatusBadge(task.status);

      // Format description - truncate if too long
      const description = task.description || "";
      const maxLength = 100;
      const truncatedDesc =
        description.length > maxLength
          ? description.substring(0, maxLength) + "..."
          : description;
      const descriptionCell =
        description.length > maxLength
          ? `<td class="px-6 py-4 text-sm text-gray-600 max-w-xs" title="${escapeHtml(
              description
            )}">
             <div class="truncate">${escapeHtml(truncatedDesc)}</div>
           </td>`
          : `<td class="px-6 py-4 text-sm text-gray-600 max-w-xs">
             ${escapeHtml(description || "-")}
           </td>`;

      const actions =
        currentUserRole === "admin"
          ? `<td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button onclick="openEditModal(${task.id})" class="text-blue-600 hover:text-blue-900 mr-3">Edit</button>
                <button onclick="deleteTask(${task.id})" class="text-red-600 hover:text-red-900">Delete</button>
               </td>`
          : "";

      return `
            <tr class="${rowClass}">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">#${
                  task.id
                }</td>
                <td class="px-6 py-4 text-sm text-gray-900">${escapeHtml(
                  task.title
                )}</td>
                ${descriptionCell}
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${
                  task.assigned_to_name || "Unassigned"
                }</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">${priorityBadge}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                    <select onchange="updateTaskStatus(${task.id}, this.value)" 
                        class="px-2 py-1 rounded text-xs font-medium ${getStatusSelectClass(
                          task.status
                        )}">
                        <option value="Pending" ${
                          task.status === "Pending" ? "selected" : ""
                        }>Pending</option>
                        <option value="In Progress" ${
                          task.status === "In Progress" ? "selected" : ""
                        }>In Progress</option>
                        <option value="Completed" ${
                          task.status === "Completed" ? "selected" : ""
                        }>Completed</option>
                        <option value="On Hold" ${
                          task.status === "On Hold" ? "selected" : ""
                        }>On Hold</option>
                    </select>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${
                  task.start_date ? formatDate(task.start_date) : "-"
                }</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm ${dueDateClass}">${
        task.due_date ? formatDate(task.due_date) : "-"
      }</td>
                ${actions}
            </tr>
        `;
    })
    .join("");
}

// Render pagination controls
function renderPagination() {
  const container = document.getElementById("paginationControls");
  if (!container) return;

  if (!tasksMeta || (tasksMeta.total_pages || 0) <= 1) {
    container.innerHTML = "";
    return;
  }

  const totalItems = tasksMeta.total_items || 0;
  const startItem = totalItems === 0 ? 0 : (currentPage - 1) * pageSize + 1;
  const endItem = Math.min(currentPage * pageSize, totalItems);

  container.innerHTML = `
        <div class="text-sm text-gray-600">
            Showing <span class="font-semibold">${startItem}</span> to <span class="font-semibold">${endItem}</span> of <span class="font-semibold">${totalItems}</span> tasks
        </div>
        <div class="flex items-center gap-3">
            <button class="px-4 py-2 rounded-lg border text-sm ${
              tasksMeta.has_prev
                ? "text-gray-700 hover:bg-gray-100"
                : "text-gray-400 cursor-not-allowed"
            }"
                ${
                  tasksMeta.has_prev
                    ? `onclick="changePage(${currentPage - 1})"`
                    : "disabled"
                }>
                Previous
            </button>
            <span class="text-sm text-gray-600">Page ${currentPage} of ${totalPages}</span>
            <button class="px-4 py-2 rounded-lg border text-sm ${
              tasksMeta.has_next
                ? "text-gray-700 hover:bg-gray-100"
                : "text-gray-400 cursor-not-allowed"
            }"
                ${
                  tasksMeta.has_next
                    ? `onclick="changePage(${currentPage + 1})"`
                    : "disabled"
                }>
                Next
            </button>
        </div>
    `;
}

// Get priority badge HTML
function getPriorityBadge(priority) {
  const colors = {
    Low: "bg-green-100 text-green-800",
    Medium: "bg-yellow-100 text-yellow-800",
    High: "bg-red-100 text-red-800",
  };
  return `<span class="px-2 py-1 rounded-full text-xs font-medium ${
    colors[priority] || colors["Medium"]
  }">${priority}</span>`;
}

// Get status badge HTML
function getStatusBadge(status) {
  const colors = {
    Pending: "bg-gray-100 text-gray-800",
    "In Progress": "bg-blue-100 text-blue-800",
    Completed: "bg-green-100 text-green-800",
    "On Hold": "bg-yellow-100 text-yellow-800",
  };
  return `<span class="px-2 py-1 rounded-full text-xs font-medium ${
    colors[status] || colors["Pending"]
  }">${status}</span>`;
}

// Get status select class
function getStatusSelectClass(status) {
  const colors = {
    Pending: "bg-gray-100 text-gray-800",
    "In Progress": "bg-blue-100 text-blue-800",
    Completed: "bg-green-100 text-green-800",
    "On Hold": "bg-yellow-100 text-yellow-800",
  };
  return colors[status] || colors["Pending"];
}

// Load users (for admin - developers only for task assignment dropdown)
async function loadUsers() {
  try {
    const response = await fetch("/api/users");
    const data = await response.json();

    if (data.success) {
      // Filter to only developers for task assignment dropdown
      users = data.users.filter((user) => user.role === "developer");
      populateUserSelects();
    }
  } catch (error) {
    console.error("Error loading users:", error);
  }
}

// Populate user select dropdowns
function populateUserSelects() {
  const selects = ["taskAssignedTo", "editTaskAssignedTo"];
  selects.forEach((selectId) => {
    const select = document.getElementById(selectId);
    if (select) {
      select.innerHTML =
        '<option value="">Select Developer</option>' +
        users
          .map(
            (user) =>
              `<option value="${user.id}">${escapeHtml(user.name)}</option>`
          )
          .join("");
    }
  });

  const filterSelect = document.getElementById("assigneeFilter");
  if (filterSelect) {
    const previousValue = filterSelect.value;
    let options =
      '<option value="all">All Developers</option><option value="unassigned">Unassigned</option>';
    options += users
      .map(
        (user) => `<option value="${user.id}">${escapeHtml(user.name)}</option>`
      )
      .join("");
    filterSelect.innerHTML = options;
    if (previousValue === currentAssigneeFilter) {
      filterSelect.value = currentAssigneeFilter;
    } else {
      filterSelect.value =
        currentAssigneeFilter === "all" ? "all" : currentAssigneeFilter;
    }
  }
}

// Initialize sorting and pagination controls
function initializeControls() {
  const sortFieldSelect = document.getElementById("sortField");
  const sortDirectionSelect = document.getElementById("sortDirection");
  const pageSizeSelect = document.getElementById("pageSize");
  const assigneeFilterSelect = document.getElementById("assigneeFilter");

  if (sortFieldSelect) {
    sortFieldSelect.addEventListener("change", () => {
      currentSortField = sortFieldSelect.value;
      currentPage = 1;
      loadTasks();
    });
  }

  if (sortDirectionSelect) {
    sortDirectionSelect.addEventListener("change", () => {
      currentSortDir = sortDirectionSelect.value;
      currentPage = 1;
      loadTasks();
    });
  }

  if (pageSizeSelect) {
    pageSizeSelect.addEventListener("change", () => {
      pageSize = parseInt(pageSizeSelect.value, 10) || 10;
      currentPage = 1;
      loadTasks();
    });
  }

  if (assigneeFilterSelect) {
    assigneeFilterSelect.addEventListener("change", () => {
      currentAssigneeFilter = assigneeFilterSelect.value;
      currentPage = 1;
      loadTasks();
    });
  }
}

function changePage(newPage) {
  if (newPage < 1 || newPage > totalPages) return;
  currentPage = newPage;
  loadTasks();
}

function syncControlsWithState() {
  const sortFieldSelect = document.getElementById("sortField");
  const sortDirectionSelect = document.getElementById("sortDirection");
  const pageSizeSelect = document.getElementById("pageSize");
  const assigneeFilterSelect = document.getElementById("assigneeFilter");

  if (sortFieldSelect && sortFieldSelect.value !== currentSortField) {
    sortFieldSelect.value = currentSortField;
  }
  if (sortDirectionSelect && sortDirectionSelect.value !== currentSortDir) {
    sortDirectionSelect.value = currentSortDir;
  }
  if (pageSizeSelect && parseInt(pageSizeSelect.value, 10) !== pageSize) {
    pageSizeSelect.value = pageSize;
  }

  if (
    assigneeFilterSelect &&
    assigneeFilterSelect.value !== currentAssigneeFilter
  ) {
    assigneeFilterSelect.value = currentAssigneeFilter;
  }
}

// Setup task form
function setupTaskForm() {
  document.getElementById("taskForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const taskData = {
      title: document.getElementById("taskTitle").value,
      description: document.getElementById("taskDescription").value,
      assigned_to: document.getElementById("taskAssignedTo").value || null,
      priority: document.getElementById("taskPriority").value,
      status: document.getElementById("taskStatus").value,
      start_date: document.getElementById("taskStartDate").value || null,
      due_date: document.getElementById("taskDueDate").value || null,
    };

    const btn = document.getElementById("submitTaskBtn");
    btn.disabled = true;
    btn.textContent = "Creating...";

    try {
      const response = await fetch("/api/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(taskData),
      });

      const data = await response.json();

      if (data.success) {
        closeAddTaskModal();
        loadTasks();
        loadDashboardStats();
        alert("Task created successfully!");
      } else {
        alert("Error: " + data.message);
      }
    } catch (error) {
      alert("An error occurred. Please try again.");
      console.error(error);
    } finally {
      btn.disabled = false;
      btn.textContent = "Create Task";
    }
  });
}

// Setup edit form
function setupEditForm() {
  document
    .getElementById("editTaskForm")
    .addEventListener("submit", async (e) => {
      e.preventDefault();

      const taskId = document.getElementById("editTaskId").value;
      const taskData = {
        title: document.getElementById("editTaskTitle").value,
        description: document.getElementById("editTaskDescription").value,
        assigned_to:
          document.getElementById("editTaskAssignedTo").value || null,
        priority: document.getElementById("editTaskPriority").value,
        status: document.getElementById("editTaskStatus").value,
        start_date: document.getElementById("editTaskStartDate").value || null,
        due_date: document.getElementById("editTaskDueDate").value || null,
      };

      const btn = document.getElementById("updateTaskBtn");
      btn.disabled = true;
      btn.textContent = "Updating...";

      try {
        const response = await fetch(`/api/tasks/${taskId}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(taskData),
        });

        const data = await response.json();

        if (data.success) {
          closeEditModal();
          loadTasks();
          loadDashboardStats();
          alert("Task updated successfully!");
        } else {
          alert("Error: " + data.message);
        }
      } catch (error) {
        alert("An error occurred. Please try again.");
        console.error(error);
      } finally {
        btn.disabled = false;
        btn.textContent = "Update";
      }
    });
}

// Open add task modal
function openAddTaskModal() {
  document.getElementById("taskForm").reset();
  // Reset form fields
  document.getElementById("taskTitle").value = "";
  document.getElementById("taskDescription").value = "";
  document.getElementById("taskAssignedTo").value = "";
  document.getElementById("taskPriority").value = "Medium";
  document.getElementById("taskStatus").value = "Pending";
  document.getElementById("taskStartDate").value = "";
  document.getElementById("taskDueDate").value = "";

  document.getElementById("addTaskModal").classList.remove("hidden");
}

// Close add task modal
function closeAddTaskModal() {
  document.getElementById("addTaskModal").classList.add("hidden");
  document.getElementById("taskForm").reset();
}

// Open edit modal
function openEditModal(taskId) {
  const task = tasks.find((t) => t.id === taskId);
  if (!task) return;

  document.getElementById("editTaskId").value = task.id;
  document.getElementById("editTaskTitle").value = task.title;
  document.getElementById("editTaskDescription").value = task.description || "";
  document.getElementById("editTaskAssignedTo").value = task.assigned_to || "";
  document.getElementById("editTaskPriority").value = task.priority;
  document.getElementById("editTaskStatus").value = task.status;
  document.getElementById("editTaskStartDate").value = task.start_date || "";
  document.getElementById("editTaskDueDate").value = task.due_date || "";

  document.getElementById("editModal").classList.remove("hidden");
}

// Close edit modal
function closeEditModal() {
  document.getElementById("editModal").classList.add("hidden");
}

// Update task status
async function updateTaskStatus(taskId, newStatus) {
  try {
    const response = await fetch(`/api/tasks/${taskId}/status`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus }),
    });

    const data = await response.json();

    if (data.success) {
      loadTasks();
      loadDashboardStats();
    } else {
      alert("Error: " + data.message);
      loadTasks(); // Reload to revert change
    }
  } catch (error) {
    alert("An error occurred. Please try again.");
    loadTasks(); // Reload to revert change
    console.error(error);
  }
}

// Delete task
async function deleteTask(taskId) {
  if (!confirm("Are you sure you want to delete this task?")) {
    return;
  }

  try {
    const response = await fetch(`/api/tasks/${taskId}`, {
      method: "DELETE",
    });

    const data = await response.json();

    if (data.success) {
      loadTasks();
      loadDashboardStats();
      alert("Task deleted successfully!");
    } else {
      alert("Error: " + data.message);
    }
  } catch (error) {
    alert("An error occurred. Please try again.");
    console.error(error);
  }
}

// Logout
async function logout() {
  try {
    const response = await fetch("/api/logout");
    const data = await response.json();

    if (data.success) {
      window.location.href = "/login";
    }
  } catch (error) {
    window.location.href = "/login";
  }
}

// Utility functions
function formatDate(dateString) {
  if (!dateString) return "-";
  const date = new Date(dateString);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// ==================== USER MANAGEMENT FUNCTIONS ====================

let allUsers = [];

// Load all users for user management table
async function loadAllUsers() {
  if (currentUserRole !== "admin") return;

  try {
    const response = await fetch("/api/users");
    const data = await response.json();

    if (data.success) {
      allUsers = data.users;
      renderUsersTable();
    }
  } catch (error) {
    console.error("Error loading users:", error);
  }
}

// Render users table
function renderUsersTable() {
  const tbody = document.getElementById("usersTableBody");
  if (!tbody) return;

  if (allUsers.length === 0) {
    tbody.innerHTML =
      '<tr><td colspan="6" class="px-6 py-4 text-center text-gray-500">No users found</td></tr>';
    return;
  }

  tbody.innerHTML = allUsers
    .map((user) => {
      const roleBadge =
        user.role === "admin"
          ? '<span class="px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">Admin</span>'
          : '<span class="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">Developer</span>';

      const createdDate = user.created_at ? formatDate(user.created_at) : "-";

      return `
      <tr>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">#${
          user.id
        }</td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${escapeHtml(
          user.name
        )}</td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${escapeHtml(
          user.email
        )}</td>
        <td class="px-6 py-4 whitespace-nowrap text-sm">${roleBadge}</td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${createdDate}</td>
        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
          <button onclick="openEditUserModal(${
            user.id
          })" class="text-blue-600 hover:text-blue-900 mr-3">Edit</button>
          <button onclick="deleteUser(${
            user.id
          })" class="text-red-600 hover:text-red-900">Delete</button>
        </td>
      </tr>
    `;
    })
    .join("");
}

// Setup user forms
function setupUserForms() {
  // Add user form
  const addUserForm = document.getElementById("addUserForm");
  if (addUserForm) {
    addUserForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const userData = {
        name: document.getElementById("userName").value.trim(),
        email: document.getElementById("userEmail").value.trim().toLowerCase(),
        password: document.getElementById("userPassword").value,
        role: document.getElementById("userRole").value,
      };

      const btn = document.getElementById("createUserBtn");
      btn.disabled = true;
      btn.textContent = "Creating...";

      try {
        const response = await fetch("/api/users", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(userData),
        });

        const data = await response.json();

        if (data.success) {
          closeAddUserModal();
          loadAllUsers();
          loadUsers(); // Refresh developer list for task assignment
          alert("User created successfully!");
        } else {
          alert("Error: " + data.message);
        }
      } catch (error) {
        alert("An error occurred. Please try again.");
        console.error(error);
      } finally {
        btn.disabled = false;
        btn.textContent = "Create User";
      }
    });
  }

  // Edit user form
  const editUserForm = document.getElementById("editUserForm");
  if (editUserForm) {
    editUserForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const userId = document.getElementById("editUserId").value;
      const userData = {
        name: document.getElementById("editUserName").value.trim(),
        email: document
          .getElementById("editUserEmail")
          .value.trim()
          .toLowerCase(),
        role: document.getElementById("editUserRole").value,
      };

      // Only include password if provided
      const password = document.getElementById("editUserPassword").value;
      if (password) {
        userData.password = password;
      }

      const btn = document.getElementById("updateUserBtn");
      btn.disabled = true;
      btn.textContent = "Updating...";

      try {
        const response = await fetch(`/api/users/${userId}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(userData),
        });

        const data = await response.json();

        if (data.success) {
          closeEditUserModal();
          loadAllUsers();
          loadUsers(); // Refresh developer list for task assignment
          alert("User updated successfully!");
        } else {
          alert("Error: " + data.message);
        }
      } catch (error) {
        alert("An error occurred. Please try again.");
        console.error(error);
      } finally {
        btn.disabled = false;
        btn.textContent = "Update";
      }
    });
  }
}

// Open add user modal
function openAddUserModal() {
  document.getElementById("addUserForm").reset();
  document.getElementById("addUserModal").classList.remove("hidden");
}

// Close add user modal
function closeAddUserModal() {
  document.getElementById("addUserModal").classList.add("hidden");
  document.getElementById("addUserForm").reset();
}

// Open edit user modal
function openEditUserModal(userId) {
  const user = allUsers.find((u) => u.id === userId);
  if (!user) return;

  document.getElementById("editUserId").value = user.id;
  document.getElementById("editUserName").value = user.name;
  document.getElementById("editUserEmail").value = user.email;
  document.getElementById("editUserRole").value = user.role;
  document.getElementById("editUserPassword").value = "";

  document.getElementById("editUserModal").classList.remove("hidden");
}

// Close edit user modal
function closeEditUserModal() {
  document.getElementById("editUserModal").classList.add("hidden");
  document.getElementById("editUserForm").reset();
}

// Delete user
async function deleteUser(userId) {
  if (
    !confirm(
      "Are you sure you want to delete this user? This action cannot be undone."
    )
  ) {
    return;
  }

  try {
    const response = await fetch(`/api/users/${userId}`, {
      method: "DELETE",
    });

    const data = await response.json();

    if (data.success) {
      loadAllUsers();
      loadUsers(); // Refresh developer list for task assignment
      alert("User deleted successfully!");
    } else {
      alert("Error: " + data.message);
    }
  } catch (error) {
    alert("An error occurred. Please try again.");
    console.error(error);
  }
}
