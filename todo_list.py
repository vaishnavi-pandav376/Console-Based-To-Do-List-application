import json
import os
from datetime import datetime

# File to store tasks
FILE_NAME = "tasks.json"

# Priorities mapping for sorting
PRIORITY_MAP = {"High": 1, "Medium": 2, "Low": 3}

def load_tasks():
    """Load tasks from the JSON file."""
    if not os.path.exists(FILE_NAME):
        return []
    try:
        with open(FILE_NAME, "r") as file:
            return json.load(file)
    except (json.JSONDecodeError, IOError):
        print("Error reading tasks file. Starting with an empty list.")
        return []

def save_tasks(tasks):
    """Save tasks to the JSON file."""
    try:
        with open(FILE_NAME, "w") as file:
            json.dump(tasks, file, indent=4)
    except IOError:
        print("Error saving tasks to file.")

def display_header(title):
    """Display a formatted header."""
    print(f"\n{'=' * 50}")
    print(f"{title:^50}")
    print(f"{'=' * 50}")

def add_task(tasks):
    """Add a new task to the list."""
    display_header("ADD TASK")
    
    # Input Validation: Task Title
    while True:
        title = input("Enter task title: ").strip()
        if title:
            break
        print("Error: Task title cannot be empty.")

    # Input Validation: Priority
    priority = ""
    while priority not in ["High", "Medium", "Low"]:
        priority = input("Enter priority (High/Medium/Low): ").strip().capitalize()
        if priority not in ["High", "Medium", "Low"]:
            print("Invalid priority. Please enter High, Medium, or Low.")

    # Input Validation: Deadline
    deadline = None
    while True:
        deadline_input = input("Enter deadline (YYYY-MM-DD) or press Enter to skip: ").strip()
        if not deadline_input:
            break
        try:
            # Validate date format
            datetime.strptime(deadline_input, "%Y-%m-%d")
            deadline = deadline_input
            break
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")

    task = {
        "title": title,
        "completed": False,
        "priority": priority,
        "deadline": deadline
    }
    
    tasks.append(task)
    save_tasks(tasks)
    print("\nTask added successfully!")

def format_task_display(index, task):
    """Format a single task for display."""
    status = "[Completed]" if task["completed"] else "[Pending]  "
    priority = task["priority"]
    deadline = task.get("deadline")
    
    # Highlight overdue tasks
    overdue_mark = ""
    if not task["completed"] and deadline:
        try:
            deadline_date = datetime.strptime(deadline, "%Y-%m-%d").date()
            if datetime.now().date() > deadline_date:
                overdue_mark = " <-- OVERDUE!"
        except ValueError:
            pass

    deadline_str = f" | Deadline: {deadline}" if deadline else " | No Deadline"
    return f"{index:2d}. {status} {task['title']} [Priority: {priority:6s}]{deadline_str}{overdue_mark}"

def view_tasks(tasks, filter_type="all"):
    """Display tasks with optional filtering."""
    if filter_type == "all":
        display_header("ALL TASKS")
    elif filter_type == "completed":
        display_header("COMPLETED TASKS")
    elif filter_type == "pending":
        display_header("PENDING TASKS")

    if not tasks:
        print("No tasks found.")
        return

    filtered_tasks = []
    for i, task in enumerate(tasks, 1):
        if filter_type == "completed" and not task["completed"]:
            continue
        if filter_type == "pending" and task["completed"]:
            continue
        filtered_tasks.append((i, task))

    if not filtered_tasks:
        print(f"No {filter_type} tasks found.")
        return

    for i, task in filtered_tasks:
        print(format_task_display(i, task))

def complete_task(tasks):
    """Mark a task as completed."""
    view_tasks(tasks, filter_type="pending")
    
    # Check if there are any pending tasks to complete
    if not any(not t["completed"] for t in tasks):
        return

    try:
        choice = int(input("\nEnter task number to mark as completed: "))
        if 1 <= choice <= len(tasks):
            if tasks[choice - 1]["completed"]:
                print("Task is already completed.")
            else:
                tasks[choice - 1]["completed"] = True
                save_tasks(tasks)
                print("\nTask marked as completed!")
        else:
            print("Error: Invalid task number. Please enter a number from the list.")
    except ValueError:
        print("Error: Please enter a valid numerical value.")

def delete_task(tasks):
    """Delete a task from the list."""
    view_tasks(tasks)
    if not tasks:
        return

    try:
        choice = int(input("\nEnter task number to delete: "))
        if 1 <= choice <= len(tasks):
            deleted_task = tasks.pop(choice - 1)
            save_tasks(tasks)
            print(f"\nTask '{deleted_task['title']}' deleted successfully!")
        else:
            print("Error: Invalid task number. Please enter a number from the list.")
    except ValueError:
        print("Error: Please enter a valid numerical value.")

def search_tasks(tasks):
    """Search for tasks by keyword."""
    display_header("SEARCH TASKS")
    if not tasks:
        print("No tasks to search.")
        return

    keyword = input("Enter keyword to search: ").strip().lower()
    
    if not keyword:
        print("Error: Keyword cannot be empty.")
        return
        
    found_tasks = []
    
    for i, task in enumerate(tasks, 1):
        if keyword in task["title"].lower():
            found_tasks.append((i, task))
            
    if found_tasks:
        print(f"\nFound {len(found_tasks)} matching task(s):")
        for i, task in found_tasks:
            print(format_task_display(i, task))
    else:
        print("No tasks found matching that keyword.")

def sort_tasks(tasks):
    """Sort tasks by priority or deadline."""
    display_header("SORT TASKS")
    if not tasks:
        print("No tasks to sort.")
        return

    print("1. Sort by Priority (High to Low)")
    print("2. Sort by Deadline (Earliest to Latest)")
    
    choice = input("\nEnter choice (1-2): ").strip()
    
    if choice == "1":
        tasks.sort(key=lambda x: PRIORITY_MAP.get(x["priority"], 4))
        save_tasks(tasks)
        print("\nTasks sorted by priority.")
        view_tasks(tasks)
    elif choice == "2":
        # Sort by deadline. Tasks without deadlines are pushed to the end using "9999-99-99"
        def get_deadline_sort_key(task):
            dl = task.get("deadline")
            if not dl:
                return "9999-99-99" 
            return dl
            
        tasks.sort(key=get_deadline_sort_key)
        save_tasks(tasks)
        print("\nTasks sorted by deadline.")
        view_tasks(tasks)
    else:
        print("Error: Invalid choice.")

def show_statistics(tasks):
    """Display task statistics."""
    display_header("STATISTICS")
    
    if not tasks:
        print("No tasks to show statistics for.")
        return
        
    total = len(tasks)
    completed = sum(1 for t in tasks if t["completed"])
    pending = total - completed

    print(f"Total Tasks:     {total}")
    print(f"Completed Tasks: {completed}")
    print(f"Pending Tasks:   {pending}")
    
    if total > 0:
        completion_rate = (completed / total) * 100
        print(f"Completion Rate: {completion_rate:.1f}%")

def main_menu():
    """Display the main menu and return the user's choice."""
    display_header("TO-DO LIST MENU")
    print("1. Add a new task")
    print("2. View all tasks")
    print("3. View pending tasks")
    print("4. View completed tasks")
    print("5. Mark a task as completed")
    print("6. Delete a task")
    print("7. Search tasks")
    print("8. Sort tasks")
    print("9. View statistics")
    print("0. Exit")
    print(f"{'=' * 50}")
    
    return input("Enter your choice (0-9): ").strip()

def main():
    """Main program execution loop."""
    print("Welcome to the Python To-Do List Application!")
    
    # Load existing tasks at startup
    tasks = load_tasks()
    
    while True:
        choice = main_menu()
        
        if choice == "1":
            add_task(tasks)
        elif choice == "2":
            view_tasks(tasks)
        elif choice == "3":
            view_tasks(tasks, filter_type="pending")
        elif choice == "4":
            view_tasks(tasks, filter_type="completed")
        elif choice == "5":
            complete_task(tasks)
        elif choice == "6":
            delete_task(tasks)
        elif choice == "7":
            search_tasks(tasks)
        elif choice == "8":
            sort_tasks(tasks)
        elif choice == "9":
            show_statistics(tasks)
        elif choice == "0":
            print("\nSaving tasks... Goodbye!")
            save_tasks(tasks)
            break
        else:
            print("\nError: Invalid choice. Please enter a number between 0 and 9.")

if __name__ == "__main__":
    main()
