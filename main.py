# ... (previous imports and code remain the same)

from datetime import datetime, timedelta

# ... (previous routes and functions remain the same)

@app.route('/garden_tasks', methods=['GET', 'POST'])
@login_required
def garden_tasks():
    if request.method == 'POST':
        task = request.form.get('task')
        due_date = request.form.get('due_date')
        
        new_task = GardenTask(user_id=current_user.id, task=task, due_date=due_date)
        db.session.add(new_task)
        db.session.commit()
        
        return jsonify({'success': True, 'task': task, 'due_date': due_date})
    
    tasks = GardenTask.query.filter_by(user_id=current_user.id).order_by(GardenTask.due_date).all()
    suggested_tasks = generate_suggested_tasks(current_user)
    
    return render_template('garden_tasks.html', user=current_user, tasks=tasks, suggested_tasks=suggested_tasks)

def generate_suggested_tasks(user):
    current_date = datetime.now()
    suggested_tasks = []
    
    # Spring tasks (March to May)
    if 3 <= current_date.month <= 5:
        suggested_tasks.extend([
            ("Prepare garden beds", (current_date + timedelta(days=7)).strftime("%Y-%m-%d")),
            ("Start seeds indoors", (current_date + timedelta(days=14)).strftime("%Y-%m-%d")),
            ("Prune fruit trees", (current_date + timedelta(days=21)).strftime("%Y-%m-%d"))
        ])
    
    # Summer tasks (June to August)
    elif 6 <= current_date.month <= 8:
        suggested_tasks.extend([
            ("Water plants regularly", (current_date + timedelta(days=1)).strftime("%Y-%m-%d")),
            ("Harvest vegetables", (current_date + timedelta(days=7)).strftime("%Y-%m-%d")),
            ("Monitor for pests", (current_date + timedelta(days=14)).strftime("%Y-%m-%d"))
        ])
    
    # Fall tasks (September to November)
    elif 9 <= current_date.month <= 11:
        suggested_tasks.extend([
            ("Plant fall crops", (current_date + timedelta(days=7)).strftime("%Y-%m-%d")),
            ("Collect seeds", (current_date + timedelta(days=14)).strftime("%Y-%m-%d")),
            ("Prepare for frost", (current_date + timedelta(days=21)).strftime("%Y-%m-%d"))
        ])
    
    # Winter tasks (December to February)
    else:
        suggested_tasks.extend([
            ("Plan next year's garden", (current_date + timedelta(days=14)).strftime("%Y-%m-%d")),
            ("Maintain tools", (current_date + timedelta(days=21)).strftime("%Y-%m-%d")),
            ("Order seeds", (current_date + timedelta(days=28)).strftime("%Y-%m-%d"))
        ])
    
    return suggested_tasks

# ... (rest of the file remains the same)
