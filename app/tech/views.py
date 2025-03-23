from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, send_file
from ..models import Employee, AttendanceRecord, ZKMachine, db
from .utils import ZKConnector, logger
from config import Config
from datetime import datetime
from . import tech
import pandas as pd
from io import BytesIO
from datetime import timedelta
from pytz import timezone


cairo_tz = timezone('Africa/Cairo')

@tech.route('/')
def index():
    """
    Main page route
    """
    machines = ZKMachine.query.all()
    now = datetime.now()
    return render_template('index.html', machines=machines, now=now)

@tech.route('/machines')
def list_machines():
    """
    List all registered ZK machines
    """
    machines = ZKMachine.query.all()
    now = datetime.now()
    return render_template('machines.html', machines=machines, now=now)

@tech.route('/machines/add', methods=['GET', 'POST'])
def add_machine():
    """
    Add a new ZK machine
    """
    if request.method == 'POST':
        name = request.form.get('name')
        ip = request.form.get('ip')
        port = int(request.form.get('port', 4370))
        
        machine = ZKMachine(name=name, ip=ip, port=port)
        db.session.add(machine)
        db.session.commit()
        
        flash(f'Machine {name} added successfully!', 'success')
        return redirect(url_for('tech.list_machines'))
    
    now = datetime.now()
    return render_template('add_machine.html', now=now)

@tech.route('/attendance')
def attendance():
    """
    View attendance records
    """
    now = datetime.now()
    return render_template('attendance.html', now=now)

@tech.route('/api/get_attendance_data')
def get_attendance_data():
    """
    API endpoint to get attendance data from all machines
    """
    try:
        # Get data from all registered machines
        machines = ZKMachine.query.all()
        logger.info(f"Found {len(machines)} registered machines.")
        
        if not machines:
            # If no machines are registered, use the ones from config
            logger.info("No machines registered. Using machines from config.")
            for machine_config in Config.ZK_MACHINES:
                logger.info(f"Fetching data from machine: {machine_config['ip']}")
                machine_data = ZKConnector.get_attendance_data(machine_config)
                if machine_data:
                    logger.info(f"Fetched {len(machine_data['attendance'])} records from machine: {machine_config['ip']}")
                    ZKConnector.save_attendance_records(machine_data)
                else:
                    logger.error(f"Failed to fetch data from machine: {machine_config['ip']}")
        else:
            # Use registered machines
            logger.info("Using registered machines.")
            for machine in machines:
                machine_config = {
                    'ip': machine.ip,
                    'port': machine.port,
                    'timeout': 50,
                    'name': machine.name
                }
                logger.info(f"Fetching data from machine: {machine.ip}")
                machine_data = ZKConnector.get_attendance_data(machine_config)
                if machine_data:
                    logger.info(f"Fetched {len(machine_data['attendance'])} records from machine: {machine.ip}")
                    ZKConnector.save_attendance_records(machine_data)
                else:
                    logger.error(f"Failed to fetch data from machine: {machine.ip}")
        
        # Get combined data
        combined_data = ZKConnector.get_combined_attendance_data()
        logger.info(f"Combined attendance data: {len(combined_data)} records.")
        
        return jsonify({
            'status': 'success',
            'data': combined_data,
            'count': len(combined_data)
        })
    except Exception as e:
        logger.error(f"Error in get_attendance_data: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@tech.route('/api/employees')
def get_employees():
    """
    API endpoint to get all employees
    """
    employees = Employee.query.all()
    return jsonify({
        'status': 'success',
        'data': [emp.to_dict() for emp in employees]
    })

@tech.route('/employees')
def employees():
    """
    View employees
    """
    employees = Employee.query.all()
    now = datetime.now()
    return render_template('employees.html', now=now, employees=employees)

@tech.route('/employees/add', methods=['GET', 'POST'])
def add_employee():
    """
    Add a new employee
    """
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        name = request.form.get('name')
        department = request.form.get('department')
        title = request.form.get('title')

        logger.info(f"Adding new employee: {employee_id}, {name}")
        
        employee = Employee(
            employee_id=employee_id,
            name=name,
            department=department,
            title=title
        )
        db.session.add(employee)
        db.session.commit()


        # Check if there are attendance records with this zk_user_id
        records = AttendanceRecord.query.filter_by(zk_user_id=employee_id).all()
        if records:

            logger.info(f"Found {len(records)} records to associate with employee {employee_id}")


            # Associate the records with the new employee - fix Issue number #01
            for record in records:
                record.employee_id = employee_id
            db.session.commit()

        
        flash(f'Employee {name} added successfully!', 'success')
        return redirect(url_for('tech.employees'))
    now = datetime.now()
    return render_template('add_employee.html', now=now)

@tech.route('/api/associate_records', methods=['POST'])
def associate_records():
    """
    Associate unmatched attendance records with employees
    """
    data = request.json
    zk_user_id = data.get('zk_user_id')
    employee_id = data.get('employee_id')
    
    if not zk_user_id or not employee_id:
        return jsonify({
            'status': 'error',
            'message': 'Missing required fields'
        }), 400
    
    # Check if employee exists
    employee = Employee.query.filter_by(employee_id=employee_id).first()
    if not employee:
        return jsonify({
            'status': 'error',
            'message': f'Employee with ID {employee_id} not found'
        }), 404
    
    # Update all matching records
    records = AttendanceRecord.query.filter_by(zk_user_id=zk_user_id).all()
    count = 0
    
    for record in records:
        record.employee_id = employee_id
        count += 1
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': f'Updated {count} records successfully'
    })


@tech.route('/machines/edit/<int:machine_id>', methods=['GET', 'POST'])
def edit_machine(machine_id):
    now = datetime.now()
    machine = ZKMachine.query.get_or_404(machine_id)
    if request.method == 'POST':
        machine.name = request.form.get('name')
        machine.ip = request.form.get('ip')
        machine.port = int(request.form.get('port', 4370))
        db.session.commit()
        flash(f'Machine {machine.name} updated successfully!', 'success')
        return redirect(url_for('tech.list_machines'))
    return render_template('edit_machine.html', machine=machine, now=now)

@tech.route('/machines/delete/<int:machine_id>', methods=['POST'])
def delete_machine(machine_id):
    machine = ZKMachine.query.get_or_404(machine_id)
    db.session.delete(machine)
    db.session.commit()
    flash(f'Machine {machine.name} deleted successfully!', 'success')
    return redirect(url_for('tech.list_machines'))

@tech.route('/machines/test/<int:machine_id>', methods=['POST'])
def test_machine(machine_id):
    machine = ZKMachine.query.get_or_404(machine_id)
    conn = ZKConnector.connect_to_machine(machine.ip, machine.port)
    if conn:
        conn.disconnect()
        return jsonify({'status': 'success', 'message': 'Connection successful!'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to connect to machine.'}), 500
    

@tech.route('/machines/toggle_status/<int:machine_id>', methods=['POST'])
def toggle_machine_status(machine_id):
    machine = ZKMachine.query.get_or_404(machine_id)
    machine.status = 'active' if machine.status == 'inactive' else 'inactive'
    db.session.commit()
    return jsonify({'status': 'success', 'message': f'Machine {machine.name} status updated to {machine.status}.'})


@tech.route('/employees/edit/<int:employee_id>', methods=['GET', 'POST'])
def edit_employee(employee_id):
    now = datetime.now()
    employee = Employee.query.get_or_404(employee_id)
    if request.method == 'POST':
        employee.employee_id = request.form.get('employee_id')
        employee.name = request.form.get('name')
        employee.department = request.form.get('department')
        employee.title = request.form.get('title')
        employee.branch = request.form.get('branch')
        db.session.commit()
        flash(f'Employee {employee.name} updated successfully!', 'success')
        return redirect(url_for('tech.employees'))
    return render_template('edit_employee.html', employee=employee, now=now)


@tech.route('/employees/delete/<int:employee_id>', methods=['POST'])
def delete_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    db.session.delete(employee)
    db.session.commit()
    flash(f'Employee {employee.name} deleted successfully!', 'success')
    return redirect(url_for('tech.employees'))

@tech.route('/api/import_employees', methods=['POST'])
def import_employees():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No file selected'}), 400
    
    try:
        # Read the Excel file
        df = pd.read_excel(file)
        
        # Ensure the required columns exist
        required_columns = ['employee_id', 'name', 'department', 'title', 'branch']
        if not all(column in df.columns for column in required_columns):
            return jsonify({'status': 'error', 'message': 'Missing required columns in the Excel file'}), 400
        
        count = 0
        for _, row in df.iterrows():
            employee_id = row['employee_id']
            name = row['name']
            department = row['department']
            title = row['title']
            branch = row['branch']
            
            # Check if the employee already exists
            existing = Employee.query.filter_by(employee_id=employee_id).first()
            if existing:
                # Update existing employee
                existing.name = name
                existing.department = department
                existing.title = title
                existing.branch = branch
            else:
                # Create new employee
                employee = Employee(
                    employee_id=employee_id,
                    name=name,
                    department=department,
                    title=title,
                    branch=branch
                )
                db.session.add(employee)
            
            count += 1
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Imported {count} employees successfully'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@tech.route('/api/export_attendance', methods=['GET'])
def export_attendance():
    attendance_records = AttendanceRecord.query.all()
    data = [{
        'zk_user_id': record.zk_user_id,
        'employee_id': record.employee_id,
        'name': record.employee.name if record.employee else 'N/A',
        'timestamp': record.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'machine_name': record.machine_name
    } for record in attendance_records]
    df = pd.DataFrame(data)
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name='attendance_records.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@tech.route('/api/export_employees', methods=['GET'])
def export_employees():
    try:
        employees = Employee.query.all()
        data = [{
            'employee_id': emp.employee_id,
            'name': emp.name,
            'department': emp.department,
            'title': emp.title,
            'branch': emp.branch
        } for emp in employees]
        df = pd.DataFrame(data)
        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        return send_file(output, as_attachment=True, download_name='employees.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@tech.route('/calculated_attendance')
def calculated_attendance():
    now = datetime.now()
    return render_template('calculated_attendance.html', now=now)


@tech.route('/api/calculate_attendance', methods=['POST'])
def calculate_attendance():
    start_date = request.json.get('start_date')
    end_date = request.json.get('end_date')
    employee_id = request.json.get('employee_id')

    if not start_date or not end_date:
        return jsonify({'status': 'error', 'message': 'Both start and end dates are required.'}), 400

    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    if start_date > end_date:
        return jsonify({'status': 'error', 'message': 'Start date must be before end date.'}), 400

    # Fetch employees
    if employee_id:
        employees = [Employee.query.filter_by(employee_id=employee_id).first()]
    else:
        employees = Employee.query.all()

    calculated_data = []
    for employee in employees:
        if not employee:
            continue

        for single_date in (start_date + timedelta(n) for n in range((end_date - start_date).days + 1)):
            day_name = single_date.strftime('%A')
            records = AttendanceRecord.query.filter(
                AttendanceRecord.employee_id == employee.employee_id,
                db.func.date(AttendanceRecord.timestamp) == single_date.date()
            ).order_by(AttendanceRecord.timestamp).all()

            check_in = records[0].timestamp if records else None
            check_out = records[-1].timestamp if records else None

            working_hours = timedelta()
            overtime = timedelta()
            punishment = 0.0

            if check_in and check_out:
                working_hours = check_out - check_in

                # Calculate punishment
                if working_hours < timedelta(hours=8, minutes=45):
                    if working_hours >= timedelta(hours=8, minutes=30):
                        punishment = 0.125
                    elif working_hours >= timedelta(hours=8, minutes=15):
                        punishment = 0.25
                    elif working_hours >= timedelta(hours=8):
                        punishment = 0.5
                    else:
                        punishment = 1.0

                # Calculate overtime
                if working_hours > timedelta(hours=9):
                    overtime = working_hours - timedelta(hours=9)

            calculated_data.append({
                'employee_id': employee.employee_id,
                'name': employee.name,
                'department': employee.department,
                'title': employee.title,
                'branch': employee.branch,
                'day': day_name,
                'date': single_date.strftime('%Y-%m-%d'),
                'check_in': check_in.strftime('%H:%M:%S') if check_in else 'N/A',
                'check_out': check_out.strftime('%H:%M:%S') if check_out else 'N/A',
                'working_hours': str(working_hours),
                'overtime': str(overtime),
                'punishment': punishment
            })

    return jsonify({'status': 'success', 'data': calculated_data})


@tech.route('/api/export_calculated_attendance', methods=['GET'])
def export_calculated_attendance():
    try:
        # Fetch query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        employee_id = request.args.get('employee_id')

        if not start_date or not end_date:
            return jsonify({'status': 'error', 'message': 'Both start and end dates are required.'}), 400

        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Invalid date format. Use YYYY-MM-DD.'}), 400

        if start_date > end_date:
            return jsonify({'status': 'error', 'message': 'Start date must be before end date.'}), 400

        # Fetch employees
        if employee_id:
            employees = [Employee.query.filter_by(employee_id=employee_id).first()]
        else:
            employees = Employee.query.all()

        calculated_data = []
        for employee in employees:
            if not employee:
                continue

            for single_date in (start_date + timedelta(n) for n in range((end_date - start_date).days + 1)):
                day_name = single_date.strftime('%A')
                records = AttendanceRecord.query.filter(
                    AttendanceRecord.employee_id == employee.employee_id,
                    db.func.date(AttendanceRecord.timestamp) == single_date.date()
                ).order_by(AttendanceRecord.timestamp).all()

                check_in = records[0].timestamp if records else None
                check_out = records[-1].timestamp if records else None

                working_hours = timedelta()
                overtime = timedelta()
                punishment = 0.0


                if check_in and check_out:
                    working_hours = check_out - check_in

                # Calculate punishment
                if working_hours < timedelta(hours=8, minutes=45):
                    if working_hours >= timedelta(hours=8, minutes=30):
                        punishment = 0.125
                    elif working_hours >= timedelta(hours=8, minutes=15):
                        punishment = 0.25
                    elif working_hours >= timedelta(hours=8):
                        punishment = 0.5
                    else:
                        punishment = 1.0

                # Calculate overtime
                if working_hours > timedelta(hours=9):
                    overtime = working_hours - timedelta(hours=9)

                calculated_data.append({
                    'Employee ID': employee.employee_id,
                    'Name': employee.name,
                    'Department': employee.department,
                    'Title': employee.title,
                    'Branch': employee.branch,
                    'Day': day_name,
                    'Date': single_date.strftime('%Y-%m-%d'),
                    'Check In': check_in.strftime('%H:%M:%S') if check_in else 'N/A',
                    'Check Out': check_out.strftime('%H:%M:%S') if check_out else 'N/A',
                    'Working Hours': str(working_hours),
                    'Overtime': str(overtime),
                    'Punishment': punishment
                })

        # Create a DataFrame
        df = pd.DataFrame(calculated_data)

        # Create an in-memory Excel file
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Calculated Attendance')

        # Prepare the response
        output.seek(0)
        return send_file(
            output,
            as_attachment=True,
            download_name='calculated_attendance.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        logger.error(f"Error exporting calculated attendance: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500



@tech.route('/api/import_attendance', methods=['POST'])
def import_attendance():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No file selected'}), 400
    
    try:
        # Read the Excel file
        df = pd.read_excel(file)
        
        # Ensure the required columns exist
        required_columns = ['employee_id', 'timestamp', 'punch_type', 'machine_name', 'machine_ip']
        if not all(column in df.columns for column in required_columns):
            return jsonify({'status': 'error', 'message': 'Missing required columns in the Excel file'}), 400
        
        count = 0
        for _, row in df.iterrows():
            employee_id = row['employee_id']
            timestamp = pd.to_datetime(row['timestamp']).replace(tzinfo=cairo_tz)  # Convert to Cairo time
            punch_type = row['punch_type']
            machine_name = row['machine_name']
            machine_ip = row['machine_ip']
            
            # Check if the record already exists
            existing = AttendanceRecord.query.filter_by(
                employee_id=employee_id,
                timestamp=timestamp,
                machine_ip=machine_ip
            ).first()
            
            if not existing:
                # Create new attendance record
                record = AttendanceRecord(
                    employee_id=employee_id,
                    timestamp=timestamp,
                    punch_type=punch_type,
                    machine_name=machine_name,
                    machine_ip=machine_ip
                )
                db.session.add(record)
                count += 1
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Imported {count} attendance records successfully'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    

@tech.route('/api/get_employee_data', methods=['GET'])
def get_employee_data():
    try:
        employees = Employee.query.all()
        data = [{
            'id': emp.id,
            'employee_id': emp.employee_id,
            'name': emp.name,
            'department': emp.department,
            'title': emp.title,
            'branch': emp.branch
        } for emp in employees]
        return jsonify({
            'status': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    